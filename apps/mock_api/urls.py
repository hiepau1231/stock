# apps/mock_api/urls.py
from django.urls import path
from .views import mock_stock_data

urlpatterns = [
    path('mock-stock-data/', mock_stock_data, name='mock_stock_data'),
]
