from django.urls import path
from . import views

app_name = 'stock_analysis'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('stocks/', views.StockListView.as_view(), name='stock_list'),
    path('stock/<str:symbol>/', views.StockDetailView.as_view(), name='stock_detail'),
    path('portfolio/', views.PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolio/create/', views.PortfolioCreateView.as_view(), name='portfolio_create'),
    path('portfolio/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('portfolio/<int:pk>/add/', views.add_portfolio_stock, name='add_portfolio_stock'),
    path('portfolio/<int:pk>/remove/<int:stock_id>/', views.remove_portfolio_stock, name='remove_portfolio_stock'),
    path('portfolio/<int:pk>/export/pdf/', views.export_portfolio_pdf, name='export_portfolio_pdf'),
    path('portfolio/<int:pk>/export/excel/', views.export_portfolio_excel, name='export_portfolio_excel'),
    path('watchlist/', views.WatchListView.as_view(), name='watchlist'),
    path('watchlist/add/<str:symbol>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<str:symbol>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('compare/', views.compare_stocks, name='compare_stocks'),
    path('industry-analysis/', views.industry_analysis, name='industry_analysis'),
    path('stock/<str:symbol>/intraday/', views.stock_intraday, name='stock_intraday'),
    path('stock/<str:symbol>/indicators/', views.get_technical_indicators, name='technical_indicators'),
    path('alerts/', views.PriceAlertListView.as_view(), name='price_alert_list'),
    path('alerts/add/<str:symbol>/', views.add_price_alert, name='add_price_alert'),
    path('alerts/remove/<int:alert_id>/', views.remove_price_alert, name='remove_price_alert'),
]
