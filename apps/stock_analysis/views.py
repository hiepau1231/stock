from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Stock, StockPrice, StockIndex, Portfolio, PortfolioItem
import pandas as pd
import numpy as np
from .web_scraping_script import scrape_stock_data, scrape_index_data
from .forms import UpdateDataForm
import logging
import plotly.graph_objs as go
from plotly.offline import plot
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv
from django.http import HttpResponse
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

class CompareStocksForm(forms.Form):
    stock1 = forms.CharField(max_length=10, label="Cổ phiếu 1")
    stock2 = forms.CharField(max_length=10, label="Cổ phiếu 2")
    stock3 = forms.CharField(max_length=10, required=False, label="Cổ phiếu 3")

def stock_detail(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    prices = StockPrice.objects.filter(stock=stock).order_by('-date')[:30]
    
    df = pd.DataFrame(list(prices.values()))
    
    if not df.empty:
        # Tính toán các chỉ số kỹ thuật
        df['SMA_20'] = df['close_price'].rolling(window=20).mean()
        df['EMA_20'] = df['close_price'].ewm(span=20, adjust=False).mean()
        
        # Tính RSI
        delta = df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        latest_price = df.iloc[0]
        context = {
            'stock': stock,
            'latest_price': latest_price,
            'prices': prices,
            'sma_20': latest_price['SMA_20'],
            'ema_20': latest_price['EMA_20'],
            'rsi': latest_price['RSI'],
        }
    else:
        context = {'stock': stock, 'prices': []}
    
    return render(request, 'stock_analysis/stock_detail.html', context)

@cache_page(60 * 15)
@vary_on_cookie
def dashboard(request):
    if request.GET.get('refresh'):
        cache.clear()
    
    try:
        indices = StockIndex.objects.filter(name__in=["VNINDEX", "HNX", "UPCOM"]).order_by('-last_updated')
        
        vn_index = indices.filter(name="VNINDEX").first()
        hnx_index = indices.filter(name="HNX").first()
        upcom_index = indices.filter(name="UPCOM").first()

        # Lấy dữ liệu lịch sử cho biểu đồ
        vn_history = StockIndex.objects.filter(name="VNINDEX").order_by('-last_updated')[:30]
        hnx_history = StockIndex.objects.filter(name="HNX").order_by('-last_updated')[:30]
        upcom_history = StockIndex.objects.filter(name="UPCOM").order_by('-last_updated')[:30]

        # Tạo biểu đồ
        fig = go.Figure()
        for history, name in [(vn_history, 'VN-Index'), (hnx_history, 'HNX-Index'), (upcom_history, 'UPCOM-Index')]:
            if history:
                fig.add_trace(go.Scatter(
                    x=[index.last_updated for index in history],
                    y=[index.value for index in history],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title='Biến động chỉ số thị trường',
            xaxis_title='Thời gian',
            yaxis_title='Giá trị',
            legend_title='Chỉ số',
            hovermode='x unified'
        )
        
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)

        context = {
            'vn_index': vn_index,
            'hnx_index': hnx_index,
            'upcom_index': upcom_index,
            'update_form': UpdateDataForm(),
            'plot_div': plot_div,
        }
        return render(request, 'stock_analysis/dashboard.html', context)
    except Exception as e:
        logger.error(f"Error in dashboard view: {str(e)}")
        messages.error(request, "Có lỗi xảy ra khi tải dữ liệu dashboard.")
        return redirect(reverse('home'))

@cache_page(60 * 60)  # Cache for 1 hour
def stock_list(request):
    query = request.GET.get('q')
    if query:
        stocks = Stock.objects.filter(
            Q(symbol__icontains=query) | Q(name__icontains=query)
        )
    else:
        stocks = Stock.objects.all()
    
    paginator = Paginator(stocks, 20)  # Hiển thị 20 cổ phiếu mỗi trang
    page = request.GET.get('page')
    try:
        stocks = paginator.page(page)
    except PageNotAnInteger:
        stocks = paginator.page(1)
    except EmptyPage:
        stocks = paginator.page(paginator.num_pages)
    
    return render(request, 'stock_analysis/stock_list.html', {'stocks': stocks})

def update_stock_data(request):
    if request.method == 'POST':
        form = UpdateDataForm(request.POST)
        if form.is_valid() and form.cleaned_data['confirm']:
            try:
                if scrape_index_data():
                    messages.success(request, "Dữ liệu chỉ số đã được cập nhật thành công.")
                else:
                    messages.error(request, "Không thể cập nhật dữ liệu chỉ số.")
            except Exception as e:
                logger.error(f"Error updating stock data: {str(e)}")
                messages.error(request, f"Lỗi khi cập nhật dữ liệu: {str(e)}")
        else:
            messages.warning(request, "Vui lòng xác nhận trước khi cập nhật dữ liệu.")
    else:
        form = UpdateDataForm()
    
    return render(request, 'stock_analysis/update_data.html', {'form': form})

def export_stock_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stock_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Symbol', 'Name', 'Sector', 'Industry'])

    stocks = Stock.objects.all().values_list('symbol', 'name', 'sector', 'industry')
    for stock in stocks:
        writer.writerow(stock)

    return response

def compare_stocks(request):
    form = CompareStocksForm(request.GET or None)
    stocks = []
    
    if form.is_valid():
        symbols = [form.cleaned_data['stock1'], form.cleaned_data['stock2']]
        if form.cleaned_data['stock3']:
            symbols.append(form.cleaned_data['stock3'])
        
        for symbol in symbols:
            stock = Stock.objects.filter(symbol=symbol).first()
            if stock:
                latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
                if latest_price:
                    stock.latest_price = latest_price
                    stock.price_change_percent = ((latest_price.close_price - latest_price.open_price) / latest_price.open_price) * 100
                stocks.append(stock)
    
    context = {
        'form': form,
        'stocks': stocks
    }
    return render(request, 'stock_analysis/compare.html', context)

@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'stock_analysis/portfolio_list.html', {'portfolios': portfolios})

@login_required
def portfolio_detail(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    items = PortfolioItem.objects.filter(portfolio=portfolio)
    return render(request, 'stock_analysis/portfolio_detail.html', {'portfolio': portfolio, 'items': items})

@login_required
def add_portfolio(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Portfolio.objects.create(user=request.user, name=name)
            messages.success(request, "Danh mục đầu tư đã được tạo thành công.")
        else:
            messages.error(request, "Vui lòng nhập tên cho danh mục đầu tư.")
    return redirect('stock_analysis:portfolio_list')

@login_required
def add_portfolio_item(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    if request.method == 'POST':
        stock_symbol = request.POST.get('stock_symbol')
        quantity = request.POST.get('quantity')
        purchase_price = request.POST.get('purchase_price')
        purchase_date = request.POST.get('purchase_date')
        
        stock = get_object_or_404(Stock, symbol=stock_symbol)
        
        PortfolioItem.objects.create(
            portfolio=portfolio,
            stock=stock,
            quantity=quantity,
            purchase_price=purchase_price,
            purchase_date=purchase_date
        )
        messages.success(request, "Cổ phiếu đã được thêm vào danh mục đầu tư.")
    return redirect('stock_analysis:portfolio_detail', portfolio_id=portfolio_id)
