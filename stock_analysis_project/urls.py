from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.home.views import custom_page_not_found_view, custom_error_view

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Apps URLs
    path('', include('apps.home.urls')),
    path('', include('apps.authentication.urls')),
    path('stock/', include('apps.stock_analysis.urls', namespace='stock_analysis')),
    path('predictions/', include('apps.predictions.urls')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = custom_page_not_found_view
handler500 = custom_error_view
