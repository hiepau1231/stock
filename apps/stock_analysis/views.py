from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy

import pandas as pd
import json

from .models import Stock, Portfolio, PortfolioItem, WatchList
from .services.stock_service import StockService

import logging

logger = logging.getLogger(__name__)

class DashboardView(LoginRequiredMixin, View):
    template_name = 'stock_analysis/dashboard.html'
    
    def get(self, request):
        try:
            stock_service = StockService()
            market_overview = stock_service.get_market_overview()
            industry_analysis = stock_service.get_industry_analysis()
            top_gainers = stock_service.get_top_gainers()
            top_losers = stock_service.get_top_losers()
            
            context = self.prepare_dashboard_context(market_overview, industry_analysis, top_gainers, top_losers)
            return render(request, self.template_name, context)
        except Exception as e:
            logger.error(f"Error in DashboardView: {str(e)}")
            messages.error(request, "An error occurred while loading the dashboard. Please try again later.")
            return render(request, self.template_name, {})

    def prepare_dashboard_context(self, market_overview, industry_analysis, top_gainers, top_losers):
        context = {}
        
        if market_overview is None or industry_analysis is None:
            logger.warning("Failed to fetch market data")
            messages.warning(self.request, "Unable to fetch market data. Some information may be missing.")
        
        # Prepare data for charts
        if market_overview is not None and not market_overview.empty:
            market_overview_labels = json.dumps([item['index_name'] for item in market_overview.to_dict('records')])
            market_overview_values = json.dumps([item['value'] for item in market_overview.to_dict('records')])
            context.update({
                'market_overview': market_overview.to_dict('records'),
                'market_overview_labels': market_overview_labels,
                'market_overview_values': market_overview_values,
            })
        
        if industry_analysis is not None and not industry_analysis.empty:
            industry_analysis_labels = json.dumps([item['industry_name'] for item in industry_analysis.to_dict('records')])
            industry_analysis_values = json.dumps([item['market_cap'] for item in industry_analysis.to_dict('records')])
            context.update({
                'industry_analysis': industry_analysis.to_dict('records'),
                'industry_analysis_labels': industry_analysis_labels,
                'industry_analysis_values': industry_analysis_values,
            })
        
        context.update({
            'top_gainers': top_gainers.to_dict('records') if top_gainers is not None else [],
            'top_losers': top_losers.to_dict('records') if top_losers is not None else [],
        })
        
        return context

class StockListView(LoginRequiredMixin, ListView):
    template_name = 'stock_analysis/stock_list.html'
    context_object_name = 'stocks'
    paginate_by = 20

    def get_queryset(self):
        stock_service = StockService()
        stock_list = stock_service.get_stock_list()
        
        if stock_list is None or (isinstance(stock_list, pd.DataFrame) and stock_list.empty):
            return []

        # Chuyển đổi DataFrame thành list of dicts
        stocks = stock_list.to_dict('records')

        # Tìm kiếm
        search_query = self.request.GET.get('search')
        if search_query:
            stocks = [stock for stock in stocks if search_query.lower() in str(stock.get('ticker', '')).lower() or search_query.lower() in str(stock.get('company_name', '')).lower()]

        # Lọc theo ngành
        industry = self.request.GET.get('industry')
        if industry:
            stocks = [stock for stock in stocks if stock.get('industry') == industry]

        # Sắp xếp
        sort_by = self.request.GET.get('sort', 'ticker')
        reverse = False
        if sort_by.startswith('-'):
            sort_by = sort_by[1:]
            reverse = True
        
        # Sử dụng get() để tránh KeyError và đảm bảo 'symbol' luôn tồn tại
        stocks = sorted(stocks, key=lambda x: x.get(sort_by, ''), reverse=reverse)
        
        # Đảm bảo mỗi stock có trường 'symbol'
        for stock in stocks:
            if 'symbol' not in stock:
                stock['symbol'] = stock.get('ticker', '')  # Sử dụng 'ticker' nếu có, nếu không thì để trống

        return stocks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_service = StockService()
        all_stocks = stock_service.get_stock_list()
        if all_stocks is not None and not all_stocks.empty:
            context['industries'] = sorted(all_stocks['industry'].unique())
        return context

@login_required
def market_overview(request):
    stock_service = StockService()
    data = stock_service.get_market_overview()
    if data is None:
        return JsonResponse({'error': 'Failed to fetch market overview'}, status=503)
    return JsonResponse(data.to_dict('records'), safe=False)

@login_required
def industry_analysis(request):
    stock_service = StockService()
    data = stock_service.get_industry_analysis()
    if data is None:
        return JsonResponse({'error': 'Failed to fetch industry analysis'}, status=503)
    return JsonResponse(data.to_dict('records'), safe=False)

@login_required
def stock_intraday(request, symbol):
    stock_service = StockService()
    data = stock_service.get_stock_intraday(symbol)
    if data is None:
        return JsonResponse({'error': f'Failed to fetch intraday data for {symbol}'}, status=503)
    return JsonResponse(data.to_dict('records'), safe=False)

class StockDetailView(LoginRequiredMixin, DetailView):
    model = Stock
    template_name = 'stock_analysis/stock_detail.html'
    context_object_name = 'stock'
    slug_field = 'symbol'
    slug_url_kwarg = 'symbol'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_service = StockService()
        symbol = self.object.symbol
        
        # Lấy dữ liệu lịch sử
        historical_data = stock_service.get_stock_historical_data(symbol)
        context['historical_data'] = historical_data.to_dict('records') if historical_data is not None else []
        
        # Chuẩn bị dữ liệu cho biểu đồ
        if historical_data is not None and not historical_data.empty:
            context['dates'] = json.dumps(historical_data['date'].tolist())
            context['prices'] = json.dumps(historical_data['close'].tolist())
        
        # Lấy dữ liệu intraday
        intraday_data = stock_service.get_stock_intraday(symbol)
        context['intraday_data'] = intraday_data.to_dict('records') if intraday_data is not None else []
        
        # Lấy các chỉ số kỹ thuật
        technical_indicators = stock_service.get_technical_indicators(symbol)
        context['technical_indicators'] = technical_indicators
        
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
        symbols = request.POST.getlist('compare')
        stock_service = StockService()
        comparison_data = []

        for symbol in symbols:
            stock_data = stock_service.get_stock_data(symbol)
            if stock_data is not None:
                comparison_data.append(stock_data)

        context = {
            'comparison_data': comparison_data
        }
        return render(request, 'stock_analysis/stock_comparison.html', context)
    return redirect('stock_analysis:stock_list')
