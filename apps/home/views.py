# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, TemplateDoesNotExist
from django.urls import reverse
from django.shortcuts import render
from apps.stock_analysis.models import Stock, StockPrice
from django.utils import timezone
from datetime import timedelta
import logging
# Thêm imports này
from apps.stock_analysis.services.stock_service import StockService 
from apps.stock_analysis.services.recommendation_service import RecommendationService
logger = logging.getLogger(__name__)

@login_required
def index(request):
    stock_service = StockService()
    recommendation_service = RecommendationService()
    # Lấy dữ liệu thị trường tổng quan
    market_overview = stock_service.get_market_overview()
    # In ra log để kiểm tra dữ liệu
    print("Market Overview:", market_overview)
    # Lấy top tăng giá và giảm giá
    top_gainers = stock_service.get_top_gainers(limit=5)
    top_losers = stock_service.get_top_losers(limit=5)
    # Lấy khuyến nghị mới nhất
    recommendations = recommendation_service.get_latest_recommendations(limit=5)
    # Lấy tin tức thị trường
    market_news = stock_service.get_market_news(limit=3)
    context = {
        'market_overview': market_overview,
        'top_gainers': top_gainers,
        'top_losers': top_losers,
        'recommendations': recommendations,
        'market_news': market_news,
    }
    return render(request, 'home/index.html', context)

@login_required
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponse(status=404)
        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

@login_required
def profile(request):
    return render(request, 'home/profile.html')

@login_required
def map_view(request):
    return render(request, 'home/map.html')

def home(request):
    return render(request, 'home/index.html')

def dashboard(request):
    # Lấy dữ liệu chỉ số mới nhất
    try:
        hnx_stock = Stock.objects.get(symbol='HNXINDEX')
        hnx_price = hnx_stock.prices.order_by('-date').first()
        hnx_index = hnx_price.close_price if hnx_price else None
        # Lấy dữ liệu lịch sử cho biểu đồ
        hnx_history = hnx_stock.prices.order_by('-date')[:30]
        hnx_data = {
            'dates': [price.date.strftime('%d/%m') for price in hnx_history],
            'prices': [float(price.close_price) for price in hnx_history]
        }
    except Stock.DoesNotExist:
        hnx_index = None
        hnx_data = {'dates': [], 'prices': []}
    try:
        upcom_stock = Stock.objects.get(symbol='UPCOM')
        upcom_price = upcom_stock.prices.order_by('-date').first()
        upcom_index = upcom_price.close_price if upcom_price else None
        # Lấy dữ liệu lịch sử cho biểu đồ
        upcom_history = upcom_stock.prices.order_by('-date')[:30]
        upcom_data = {
            'dates': [price.date.strftime('%d/%m') for price in upcom_history],
            'prices': [float(price.close_price) for price in upcom_history]
        }
    except Stock.DoesNotExist:
        upcom_index = None
        upcom_data = {'dates': [], 'prices': []}
    # Lấy thời gian cập nhật cuối cùng
    last_update = StockPrice.objects.order_by('-date').first()
    if last_update:
        last_update = last_update.date
    # Tính toán giá trị giao dịch theo tháng
    try:
        # Lấy dữ liệu giao dịch 8 tháng gần nhất
        trading_data = StockPrice.objects.raw('''
            SELECT id, 
                   strftime('%Y-%m', date) as month,
                   SUM(volume * close_price) as trading_value
            FROM stock_analysis_stockprice
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month DESC
            LIMIT 8
        ''')
        trading_values = [float(data.trading_value) / 1_000_000 for data in trading_data]  # Chuyển đổi sang tỷ VND
        trading_months = [data.month for data in trading_data]
    except Exception as e:
        logger.error(f"Error getting trading data: {str(e)}")
        trading_values = []
        trading_months = []
    context = {
        'hnx_index': hnx_index,
        'upcom_index': upcom_index,
        'last_update': last_update,
        'hnx_data': hnx_data,
        'upcom_data': upcom_data,
        'trading_values': trading_values,
        'trading_months': trading_months
    }
    return render(request, 'home/dashboard.html', context)

def introduction(request):
    context = {
        'algorithms': [
            {
                'name': 'Technical Analysis',
                'description': '...',
                'use_cases': '...'
            },
            # Thêm các thuật toán khác
        ],
        'user_guides': [
            {
                'title': 'Bắt đầu',
                'content': '...'
            },
            # Thêm các hướng dẫn khác
        ]
    }
    return render(request, 'home/introduction.html', context)
