from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Stock, StockPrice
import pandas as pd
import numpy as np
from .web_scraping_script import scrape_stock_data

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

def stock_list(request):
    stocks = Stock.objects.all()
    return render(request, 'stock_analysis/stock_list.html', {'stocks': stocks})

def update_stock_data(request):
    stocks = Stock.objects.all()
    for stock in stocks:
        try:
            scrape_stock_data(stock.symbol)
            messages.success(request, f"Dữ liệu cho {stock.symbol} đã được cập nhật.")
        except Exception as e:
            messages.error(request, f"Lỗi khi cập nhật dữ liệu cho {stock.symbol}: {str(e)}")
    return redirect('stock_analysis:stock_dashboard')

def dashboard(request):
    stocks = Stock.objects.all()
    stock_data = []
    for stock in stocks:
        latest_price = stock.prices.order_by('-date').first()
        if latest_price:
            stock_data.append({
                'symbol': stock.symbol,
                'name': stock.name,
                'price': latest_price.close_price,
                'date': latest_price.date,
                'change': latest_price.close_price - stock.prices.order_by('-date')[1].close_price if stock.prices.count() > 1 else 0
            })
    context = {'stock_data': stock_data}
    return render(request, 'stock_analysis/dashboard.html', context)
