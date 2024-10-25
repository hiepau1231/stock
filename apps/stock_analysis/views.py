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
        stock_service = StockService()
        market_overview = stock_service.get_market_overview()
        industry_analysis = stock_service.get_industry_analysis()
        top_gainers = stock_service.get_top_gainers()
        top_losers = stock_service.get_top_losers()
        
        context = {}
        
        if market_overview is None or industry_analysis is None:
            messages.error(request, "Unable to fetch market data. Please try again later.")
        
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
        
        return render(request, self.template_name, context)

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
        
        # Lấy dữ liệu intraday
        intraday_data = stock_service.get_stock_intraday(symbol)
        context['intraday_data'] = intraday_data.to_dict('records') if intraday_data is not None else []
        
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

@login_required
def add_portfolio_stock(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    if request.method == 'POST':
        # Implement logic to add stock to portfolio
        pass
    return redirect('stock_analysis:portfolio_detail', pk=pk)

@login_required
def remove_portfolio_stock(request, pk, stock_id):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    stock = get_object_or_404(Stock, pk=stock_id)
    PortfolioItem.objects.filter(portfolio=portfolio, stock=stock).delete()
    return redirect('stock_analysis:portfolio_detail', pk=pk)

class WatchListView(LoginRequiredMixin, ListView):
    model = WatchList
    template_name = 'stock_analysis/watchlist.html'
    context_object_name = 'watchlist'

    def get_queryset(self):
        return WatchList.objects.filter(user=self.request.user)

@login_required
def add_to_watchlist(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    WatchList.objects.get_or_create(user=request.user, stock=stock)
    return redirect('stock_analysis:watchlist')

@login_required
def remove_from_watchlist(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    WatchList.objects.filter(user=request.user, stock=stock).delete()
    return redirect('stock_analysis:watchlist')
