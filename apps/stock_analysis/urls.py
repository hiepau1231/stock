from django.urls import path
from . import views

app_name = 'stock_analysis'

# URL patterns cho ứng dụng stock_analysis
urlpatterns = [
    # Các trang chính (Main pages)
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('stocks/', views.StockListView.as_view(), name='stock_list'),
    path('stocks/<str:symbol>/', views.StockDetailView.as_view(), name='stock_detail'),

    # Các API endpoints cho phân tích thị trường
    path('api/market-overview/', views.market_overview, name='market_overview'),
    path('api/industry-analysis/', views.industry_analysis, name='industry_analysis'),
    path('api/stock-intraday/<str:symbol>/', views.stock_intraday, name='stock_intraday'),

    # Quản lý danh mục đầu tư (Portfolio management)
    path('portfolio/', views.PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolio/create/', views.PortfolioCreateView.as_view(), name='portfolio_create'),
    path('portfolio/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('portfolio/<int:pk>/add-stock/', views.add_portfolio_stock, name='add_portfolio_stock'),
    path('portfolio/<int:pk>/remove-stock/<int:stock_id>/', views.remove_portfolio_stock, name='remove_portfolio_stock'),

    # Quản lý danh sách theo dõi (Watchlist management)
    path('watchlist/', views.WatchListView.as_view(), name='watchlist'),
    path('watchlist/add/<str:symbol>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<str:symbol>/', views.remove_from_watchlist, name='remove_from_watchlist'),
]
