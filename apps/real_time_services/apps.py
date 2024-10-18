from django.apps import AppConfig
import asyncio
import threading

class RealTimeServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.real_time_services'

    def ready(self):
        from .utils import start_background_tasks
        asyncio.create_task(start_background_tasks())
