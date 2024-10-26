from celery import shared_task
from django.core.management import call_command
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from .services.stock_service import StockService



@shared_task

def update_stock_data():

    stock_service = StockService()

    return stock_service.update_stock_data()





@shared_task
def update_historical_data():
    try:
        logger.info(f"Starting historical data update at {datetime.now()}")
        call_command('load_historical_data')
        logger.info("Historical data update completed successfully")
    except Exception as e:
        logger.error(f"Error updating historical data: {str(e)}")








@shared_task
def update_recommendations():
    """Cập nhật danh sách khuyến nghị hàng tuần"""
    call_command('update_recommendations')







