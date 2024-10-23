from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Stock, StockPrice
import pandas as pd
import numpy as np
from .web_scraping_script import scrape_stock_data, scrape_index_data
import logging

logger = logging.getLogger(__name__)

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
    try:
        if scrape_index_data():
            messages.success(request, "Dữ liệu chỉ số đã được cập nhật thành công.")
        else:
            messages.error(request, "Không thể cập nhật dữ liệu chỉ số.")
    except Exception as e:
        messages.error(request, f"Lỗi khi cập nhật dữ liệu: {str(e)}")
    return redirect('stock_analysis:stock_dashboard')

def dashboard(request):
    try:
        index_symbols = ['HNXINDEX', 'UPCOM']
        stock_data = []
        
        for symbol in index_symbols:
            try:
                stock = Stock.objects.get(symbol=symbol)
                latest_price = stock.prices.order_by('-date').first()
                if latest_price:
                    previous_price = stock.prices.order_by('-date')[1] if stock.prices.count() > 1 else None
                    change = latest_price.close_price - previous_price.close_price if previous_price else 0
                    change_percent = (change / previous_price.close_price * 100) if previous_price else 0
                    
                    stock_data.append({
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'price': latest_price.close_price,
                        'date': latest_price.date,
                        'change': change,
                        'change_percent': change_percent,
                        'volume': latest_price.volume
                    })
                    logger.info(f"Found data for {symbol}: Price={latest_price.close_price}, Date={latest_price.date}")
                else:
                    logger.warning(f"No price data found for {symbol}")
            except Stock.DoesNotExist:
                logger.warning(f"Stock {symbol} not found in database")
            except Exception as e:
                logger.error(f"Error processing {symbol}: {str(e)}")
        
        context = {'stock_data': stock_data}
        return render(request, 'stock_analysis/dashboard.html', context)
    except Exception as e:
        logger.error(f"Error in dashboard view: {str(e)}")
        messages.error(request, "Có lỗi khi hiển thị dữ liệu")
        return render(request, 'stock_analysis/dashboard.html', {'stock_data': []})
