from django.contrib import admin
from django.urls import path, include  # Added include
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.home.views import custom_page_not_found_view, custom_error_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.home.urls')),
    path("", include("apps.authentication.urls")),
    path("", include("apps.home.urls")),
    # Add other app URLs here
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = custom_page_not_found_view
handler500 = custom_error_view
