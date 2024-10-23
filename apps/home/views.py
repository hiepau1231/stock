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





@login_required

def index(request):

    return render(request, 'home/index.html')





@login_required

def pages(request, template_name):

    context = {}

    try:

        load_template = template_name

        if template_name == 'admin':

            return HttpResponseRedirect(reverse('admin:index'))

        context['segment'] = load_template

        html_template = loader.get_template(f'home/{load_template}.html')

        return render(request, f'home/{load_template}.html', context)

    except TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')

        return render(request, 'home/page-404.html', context, status=404)

    except Exception:

        html_template = loader.get_template('home/page-500.html')

        return render(request, 'home/page-500.html', context, status=500)





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
    except Stock.DoesNotExist:
        hnx_index = None

    try:
        upcom_stock = Stock.objects.get(symbol='UPCOM')
        upcom_price = upcom_stock.prices.order_by('-date').first()
        upcom_index = upcom_price.close_price if upcom_price else None
    except Stock.DoesNotExist:
        upcom_index = None

    # Lấy thời gian cập nhật cuối cùng
    last_update = StockPrice.objects.order_by('-date').first()
    if last_update:
        last_update = last_update.date

    context = {
        'hnx_index': hnx_index,
        'upcom_index': upcom_index,
        'last_update': last_update,
    }
    
    return render(request, 'home/dashboard.html', context)
