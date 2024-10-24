from django.urls import path
from . import views

app_name = 'stock_analysis'

urlpatterns = [
    path('', views.dashboard, name='stock_dashboard'),
    path('stocks/', views.stock_list, name='stock_list'),
    path('stock/<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('update-data/', views.update_stock_data, name='update_stock_data'),
    path('export-stock-data/', views.export_stock_data, name='export_stock_data'),
    path('compare/', views.compare_stocks, name='compare_stocks'),
    path('portfolios/', views.portfolio_list, name='portfolio_list'),
    path('portfolios/<int:portfolio_id>/', views.portfolio_detail, name='portfolio_detail'),
    path('portfolios/add/', views.add_portfolio, name='add_portfolio'),
    path('portfolios/<int:portfolio_id>/add-item/', views.add_portfolio_item, name='add_portfolio_item'),
]

from . import views







app_name = 'stock_analysis'







urlpatterns = [



    path('', views.dashboard, name='stock_dashboard'),



    path('stocks/', views.stock_list, name='stock_list'),



    path('stock/<str:symbol>/', views.stock_detail, name='stock_detail'),



    path('update-data/', views.update_stock_data, name='update_stock_data'),



    path('export-stock-data/', views.export_stock_data, name='export_stock_data'),



    path('compare/', views.compare_stocks, name='compare_stocks'),



    path('portfolios/', views.portfolio_list, name='portfolio_list'),



    path('portfolios/<int:portfolio_id>/', views.portfolio_detail, name='portfolio_detail'),



    path('portfolios/add/', views.add_portfolio, name='add_portfolio'),



    path('portfolios/<int:portfolio_id>/add-item/', views.add_portfolio_item, name='add_portfolio_item'),



]






