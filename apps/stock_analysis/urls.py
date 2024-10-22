from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='stock_dashboard'),
    path('list/', views.stock_list, name='stock_list'),
    path('<str:symbol>/', views.stock_detail, name='stock_detail'),
]
