import asyncio
import threading
from .utils import start_background_tasks

def initialize_background_tasks():
    def run_async():
        asyncio.run(start_background_tasks())

    threading.Thread(target=run_async, daemon=True).start()
