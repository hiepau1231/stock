import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import apps.real_time_services.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.real_time_services.routing.websocket_urlpatterns
        )
    ),
})
