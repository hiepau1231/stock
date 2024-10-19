from django.apps import AppConfig

class RealTimeServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.real_time_services'

    def ready(self):
        # Import and start background tasks here to avoid circular imports
        from .utils import start_background_tasks
        import asyncio
        import threading
        
        def run_async():
            asyncio.run(start_background_tasks())

        threading.Thread(target=run_async, daemon=True).start()
