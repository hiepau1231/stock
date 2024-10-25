from celery import shared_task
from .services.stock_service import StockService

@shared_task
def update_stock_data():
    stock_service = StockService()
    return stock_service.update_stock_data()

