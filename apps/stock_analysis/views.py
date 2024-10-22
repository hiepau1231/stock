from django.shortcuts import render, get_object_or_404
from .models import Stock, StockPrice
from django.db.models import Avg, Max, Min
import pandas as pd

def home_view(request):
    return render(request, 'base.html')

def stock_detail(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol)
    prices = StockPrice.objects.filter(stock=stock).order_by('-date')[:30]
    
    df = pd.DataFrame(list(prices.values()))
    
    if not df.empty:
        avg_price = df['close_price'].mean()
        max_price = df['high_price'].max()
        min_price = df['low_price'].min()
        
        df['price_change'] = df['close_price'].diff()
        df['gain'] = df['price_change'].clip(lower=0)
        df['loss'] = -1 * df['price_change'].clip(upper=0)
        avg_gain = df['gain'].mean()
        avg_loss = df['loss'].mean()
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
    else:
        avg_price = max_price = min_price = rsi = 0
    
    context = {
        'stock': stock,
        'prices': prices,
        'avg_price': avg_price,
        'max_price': max_price,
        'min_price': min_price,
        'rsi': rsi,
    }
    return render(request, 'stock_analysis/stock_detail.html', context)

def stock_list(request):
    stocks = Stock.objects.all()
    return render(request, 'stock_analysis/stock_list.html', {'stocks': stocks})

def dashboard(request):
    return render(request, 'stock_analysis/dashboard.html')
