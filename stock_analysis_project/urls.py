# stock_analysis_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/authentication/', include('apps.authentication.urls')),
    path('api/predictions/', include('apps.predictions.urls')),
    path('api/real-time-services/', include('apps.real_time_services.urls')),
    path('api/stock-analysis/', include('apps.stock_analysis.urls')),
    path('api/mock-api/', include('apps.mock_api.urls')),  # Added mock_api URLs
    path('api/stock_analysis/', include('apps.stock_analysis.urls')),  # Added stock_analysis URLs
]
