from django.core.management.base import BaseCommand
from apps.stock_analysis.models import Stock
from apps.stock_analysis.services.stock_service import StockService

class Command(BaseCommand):
    help = 'Fetches stock data from Yahoo Finance'

    def handle(self, *args, **options):
        stock_service = StockService()
        stocks = Stock.objects.all()

        for stock in stocks:
            data = stock_service.get_stock_data(f"{stock.symbol}.VN")
            if data:
                stock.update_price(
                    price=data['price'],
                    change=data['change'],
                    percent_change=data['change_percent']
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully updated {stock.symbol}'))
            else:
                self.stdout.write(self.style.WARNING(f'Failed to update {stock.symbol}'))

        self.stdout.write(self.style.SUCCESS('Stock data update completed'))
