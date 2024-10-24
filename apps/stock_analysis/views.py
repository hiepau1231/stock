from django.shortcuts import render, get_object_or_404, redirect

from django.views.generic import ListView, DetailView, CreateView, View

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

from django.contrib import messages

from django.urls import reverse_lazy



from .models import Stock, Portfolio, PortfolioItem, WatchList

from .services.stock_service import StockService



import logging



logger = logging.getLogger(__name__)



# Dashboard Views

class DashboardView(LoginRequiredMixin, View):

    template_name = 'stock_analysis/dashboard.html'

    

    def get(self, request):

        stock_service = StockService()

        market_overview = stock_service.get_market_overview()

        industry_analysis = stock_service.get_industry_analysis()

        

        context = {

            'market_overview': market_overview.to_dict('records') if market_overview is not None else [],

            'industry_analysis': industry_analysis.to_dict('records') if industry_analysis is not None else []

        }

        return render(request, self.template_name, context)



# Stock Views

class StockListView(LoginRequiredMixin, ListView):

    template_name = 'stock_analysis/stock_list.html'
    context_object_name = 'stocks'
    
    def get_queryset(self):
        stock_service = StockService()
        stock_list = stock_service.get_stock_list()
        if stock_list is not None and not stock_list.empty:
            return stock_list.to_dict('records')
        return []

    

class StockDetailView(LoginRequiredMixin, DetailView):

    template_name = 'stock_analysis/stock_detail.html'

    context_object_name = 'stock'

    

    def get_object(self):

        symbol = self.kwargs.get('symbol')

        stock_service = StockService()

        return stock_service.get_company_info(symbol)

    

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        symbol = self.kwargs.get('symbol')

        stock_service = StockService()

        

        historical_data = stock_service.get_stock_historical_data(symbol)

        financial_info = stock_service.get_financial_info(symbol)

        intraday_data = stock_service.get_stock_intraday(symbol)

        

        context.update({

            'historical_data': historical_data.to_dict('records') if historical_data is not None else [],

            'financial_info': financial_info.to_dict('records')[0] if financial_info is not None else {},

            'intraday_data': intraday_data.to_dict('records')[0] if intraday_data is not None else {}

        })

        return context



# Market Data API Views

@login_required

def market_overview(request):

    stock_service = StockService()

    data = stock_service.get_market_overview()

    return JsonResponse(

        data.to_dict('records') if data is not None else {'error': 'Failed to fetch market overview'}, 

        safe=False

    )



@login_required

def industry_analysis(request):

    stock_service = StockService()

    data = stock_service.get_industry_analysis()

    return JsonResponse(

        data.to_dict('records') if data is not None else {'error': 'Failed to fetch industry analysis'}, 

        safe=False

    )



@login_required

def stock_intraday(request, symbol):

    stock_service = StockService()

    data = stock_service.get_stock_intraday(symbol)

    return JsonResponse(

        data.to_dict('records')[0] if data is not None else {'error': f'Failed to fetch intraday data for {symbol}'}

    )



# Portfolio Views

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

    

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        portfolio = self.get_object()

        stock_service = StockService()

        

        for item in portfolio.portfolioitem_set.all():

            current_data = stock_service.get_stock_intraday(item.stock.symbol)

            if current_data is not None:

                item.current_price = current_data['price']

                item.profit_loss = (item.current_price - item.purchase_price) * item.quantity

        

        return context



@login_required

def add_portfolio_stock(request, pk):

    if request.method == 'POST':

        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)

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

        messages.success(request, f'Added {symbol} to portfolio')

    return redirect('stock_analysis:portfolio_detail', pk=pk)



@login_required

def remove_portfolio_stock(request, pk, stock_id):

    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)

    item = get_object_or_404(PortfolioItem, portfolio=portfolio, stock_id=stock_id)

    item.delete()

    messages.success(request, f'Removed {item.stock.symbol} from portfolio')

    return redirect('stock_analysis:portfolio_detail', pk=pk)



# Watchlist Views

class WatchListView(LoginRequiredMixin, ListView):

    template_name = 'stock_analysis/watchlist.html'

    context_object_name = 'watchlist_stocks'

    

    def get_queryset(self):

        watchlist, _ = WatchList.objects.get_or_create(user=self.request.user)

        return watchlist.stocks.all()



@login_required

def add_to_watchlist(request, symbol):

    watchlist, _ = WatchList.objects.get_or_create(user=request.user)

    stock = get_object_or_404(Stock, symbol=symbol)

    watchlist.stocks.add(stock)

    messages.success(request, f'Added {symbol} to watchlist')

    return redirect('stock_analysis:watchlist')



@login_required

def remove_from_watchlist(request, symbol):

    watchlist = get_object_or_404(WatchList, user=request.user)

    stock = get_object_or_404(Stock, symbol=symbol)

    watchlist.stocks.remove(stock)

    messages.success(request, f'Removed {symbol} from watchlist')

    return redirect('stock_analysis:watchlist')


