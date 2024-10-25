from django.core.management.base import BaseCommand
from apps.stock_analysis.services.stock_service import StockService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates stock data periodically'

    def handle(self, *args, **kwargs):
        service = StockService()
        try:
            updated_count = service.update_stock_data()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} stocks')
            )
        except Exception as e:
            logger.error(f"Error updating stock data: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error updating stock data: {str(e)}')
            )
