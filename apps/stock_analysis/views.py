from django.shortcuts import render, get_object_or_404, redirect

from django.views.generic import ListView, DetailView, CreateView, View

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

from django.contrib import messages

from django.urls import reverse_lazy

from django.views.decorators.cache import cache_page
from .utils.performance import query_debugger, optimize_queryset



import pandas as pd

import json



from .models import Stock, Portfolio, PortfolioItem, WatchList

from .services.stock_service import StockService



import logging



logger = logging.getLogger(__name__)



stock_service = StockService()



class DashboardView(LoginRequiredMixin, View):

    template_name = 'stock_analysis/dashboard.html'

    

    def get(self, request):

        try:

            market_overview = stock_service.get_market_overview()

            if not market_overview:

                messages.warning(request, "Unable to fetch market data. Please try again later.")

            

            top_gainers = stock_service.get_top_gainers()

            top_losers = stock_service.get_top_losers()

            

            context = {

                'market_overview': market_overview,

                'top_gainers': top_gainers[:5] if top_gainers else [],

                'top_losers': top_losers[:5] if top_losers else [],

            }

            return render(request, self.template_name, context)

        except Exception as e:

            logger.error(f"Error in DashboardView: {str(e)}")

            messages.error(request, "An error occurred while loading the dashboard. Please try again later.")

            return render(request, self.template_name, {})



class StockListView(ListView):

    model = Stock

    template_name = 'stock_analysis/stock_list.html'

    context_object_name = 'stocks'

    @cache_page(60 * 15)  # Cache trong 15 phút
    @query_debugger
    def get(self, request):
        stocks = optimize_queryset(
            Stock.objects.all(),
            select_related=['latest_price'],
            prefetch_related=['historical_data']
        )
        context = {'stocks': stocks}
        return render(request, 'stock_analysis/stock_list.html', context)



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['segment'] = 'stock_list'

        return context



@login_required

def dashboard(request):

    market_overview = stock_service.get_market_overview()

    top_gainers = stock_service.get_top_gainers()

    top_losers = stock_service.get_top_losers()

    

    context = {

        'market_overview': market_overview,

        'top_gainers': top_gainers,

        'top_losers': top_losers,

    }

    return render(request, 'stock_analysis/dashboard.html', context)



@login_required

def stock_list(request):
    stocks = optimize_queryset(
        Stock.objects.all(),
        select_related=['latest_price'],
        prefetch_related=['historical_data']
    )
    context = {'stocks': stocks}
    return render(request, 'stock_analysis/stock_list.html', context)



@login_required

def stock_detail(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    historical_data = optimize_queryset(
        stock.historical_data.all().order_by('-date')[:30]
    )
    context = {
        'stock': stock,
        'historical_data': historical_data
    }
    return render(request, 'stock_analysis/stock_detail.html', context)



class StockDetailView(LoginRequiredMixin, DetailView):

    model = Stock

    template_name = 'stock_analysis/stock_detail.html'

    context_object_name = 'stock'

    slug_field = 'symbol'

    slug_url_kwarg = 'symbol'



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        symbol = self.object.symbol

        

        # Lấy dữ liệu lịch sử

        historical_data = stock_service.get_historical_data(symbol, '2023-01-01', '2023-12-31')

        context['historical_data'] = historical_data

        

        # Chuẩn bị dữ liệu cho biểu đồ

        if historical_data:

            context['dates'] = json.dumps([item['date'] for item in historical_data])

            context['prices'] = json.dumps([item['close'] for item in historical_data])

        

        # Lấy dữ liệu intraday

        intraday_data = stock_service.get_stock_intraday(symbol)

        context['intraday_data'] = intraday_data.to_dict('records') if intraday_data is not None else []

        

        # Lấy thông tin tổng quan về công ty

        company_overview = stock_service.get_company_overview(symbol)

        context['company_overview'] = company_overview

        

        return context



# Thêm các view khác như PortfolioListView, PortfolioCreateView, PortfolioDetailView, WatchListView, etc.



class PortfolioListView(LoginRequiredMixin, ListView):

    model = Portfolio

    template_name = 'stock_analysis/portfolio_list.html'

    context_object_name = 'portfolios'



    def get_queryset(self):

        return Portfolio.objects.filter(user=self.request.user)



class PortfolioCreateView(LoginRequiredMixin, CreateView):

    model = Portfolio

    template_name = 'stock_analysis/portfolio_create.html'

    fields = ['name']

    success_url = reverse_lazy('stock_analysis:portfolio_list')



    def form_valid(self, form):

        form.instance.user = self.request.user

        return super().form_valid(form)



class PortfolioDetailView(LoginRequiredMixin, DetailView):

    model = Portfolio

    template_name = 'stock_analysis/portfolio_detail.html'

    context_object_name = 'portfolio'

    @cache_page(60 * 5)  # Cache trong 5 phút
    @query_debugger
    def get(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        items = portfolio.portfolioitem_set.all()
        total_value = sum(item.quantity * item.stock.current_price for item in items)
        context = {'portfolio': portfolio, 'items': items, 'total_value': total_value}
        return render(request, 'stock_analysis/portfolio_detail.html', context)



    def get_queryset(self):

        return Portfolio.objects.filter(user=self.request.user)



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        portfolio = self.object

        items = portfolio.portfolioitem_set.all()

        total_value = sum(item.quantity * item.stock.current_price for item in items)

        context['items'] = items

        context['total_value'] = total_value

        return context



@login_required

def add_portfolio_stock(request, pk):

    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)

    if request.method == 'POST':

        symbol = request.POST.get('symbol')

        quantity = int(request.POST.get('quantity'))

        purchase_price = float(request.POST.get('purchase_price'))

        purchase_date = request.POST.get('purchase_date')

        

        stock = get_object_or_404(Stock, symbol=symbol)

        PortfolioItem.objects.create(

            portfolio=portfolio,

            stock=stock,

            quantity=quantity,

            purchase_price=purchase_price,

            purchase_date=purchase_date

        )

        messages.success(request, f"{symbol} đã được thêm vào danh mục đầu tư của bạn.")

    return redirect('stock_analysis:portfolio_detail', pk=pk)



@login_required

def remove_portfolio_stock(request, pk, stock_id):

    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)

    item = get_object_or_404(PortfolioItem, portfolio=portfolio, stock_id=stock_id)

    item.delete()

    messages.success(request, f"{item.stock.symbol} đã được xóa khỏi danh mục đầu tư của bạn.")

    return redirect('stock_analysis:portfolio_detail', pk=pk)



class WatchListView(LoginRequiredMixin, ListView):

    model = WatchList

    template_name = 'stock_analysis/watchlist.html'

    context_object_name = 'watchlist'



    def get_queryset(self):

        watchlist, created = WatchList.objects.get_or_create(user=self.request.user)

        return watchlist.stocks.all()



@login_required

def add_to_watchlist(request, symbol):

    stock = get_object_or_404(Stock, symbol=symbol)

    watchlist, created = WatchList.objects.get_or_create(user=request.user)

    watchlist.stocks.add(stock)

    messages.success(request, f"{symbol} đã được thêm vào danh sách theo dõi của bạn.")

    return redirect('stock_analysis:watchlist')



@login_required

def remove_from_watchlist(request, symbol):

    stock = get_object_or_404(Stock, symbol=symbol)

    watchlist = get_object_or_404(WatchList, user=request.user)

    watchlist.stocks.remove(stock)

    messages.success(request, f"{symbol} đã được xóa khỏi danh sách theo dõi của bạn.")

    return redirect('stock_analysis:watchlist')



@login_required

def compare_stocks(request):

    if request.method == 'POST':

        symbols = request.POST.getlist('symbols')

        comparison_data = []

        for symbol in symbols:

            data = stock_service.get_stock_data(symbol)

            if data:

                comparison_data.append(data)

        return render(request, 'stock_analysis/compare_stocks.html', {'comparison_data': comparison_data})

    return render(request, 'stock_analysis/compare_stocks.html')



# Thêm function này vào cuối file views.py

@login_required

def industry_analysis(request):

    # Đây là một phiên bản đơn giản, bạn cần thực hiện phân tích ngành thực tế ở đây

    industry_data = {

        'technology': {'growth': 5.2, 'market_cap': 1000000000},

        'healthcare': {'growth': 3.8, 'market_cap': 800000000},

        'finance': {'growth': 2.5, 'market_cap': 1200000000},

    }

    return JsonResponse(industry_data)



# Thêm function này nếu chưa có

@login_required

def stock_intraday(request, symbol):

    intraday_data = stock_service.get_stock_intraday(symbol)

    if intraday_data is not None:

        return JsonResponse(intraday_data.to_dict('records'), safe=False)

    else:

        return JsonResponse({'error': 'Unable to fetch intraday data'}, status=400)






