from django.shortcuts import render

def home_view(request):
    return render(request, 'base.html')

def stock_list(request):
    # Logic to fetch stock data
    return render(request, 'stock_analysis/stock_list.html')
