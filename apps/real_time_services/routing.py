from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('real-time/', include('apps.real_time_services.urls')),
    # Add other app URLs here as needed
]

# WebSocket URL patterns
from apps.real_time_services import routing
websocket_urlpatterns = routing.websocket_urlpatterns
