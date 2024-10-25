from django.core.management.base import BaseCommand
from apps.stock_analysis.models import Stock, StockPrice, MarketIndex
from apps.stock_analysis.services.stock_service import StockService
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generates sample stock data and saves it to the database'

    def handle(self, *args, **options):
        stock_service = StockService()
        
        self.update_market_indices(stock_service)
        self.update_stocks(stock_service)

    def update_market_indices(self, stock_service):
        market_overview = stock_service.get_market_overview()
        for index in market_overview.to_dict('records'):
            MarketIndex.objects.update_or_create(
                name=index['index_name'],
                defaults={
                    'value': index['value'],
                    'change': f"{index['change_percent']}%",
                    'timestamp': timezone.now()
                }
            )
        self.stdout.write(self.style.SUCCESS("Market indices updated successfully"))

    def update_stocks(self, stock_service):
        stock_list = stock_service.get_stock_list()
        
        for stock_data in stock_list:
            symbol = stock_data['symbol']
            stock, created = Stock.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': stock_data['name'],
                    'exchange': stock_data['exchange'],
                }
            )
            
            self.stdout.write(f"{'Created' if created else 'Updated'} stock: {symbol}")

            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=30)
            
            historical_data = stock_service.get_historical_data(symbol, start_date, end_date)
            
            for data in historical_data:
                StockPrice.objects.update_or_create(
                    stock=stock,
                    date=data['date'],
                    defaults={
                        'open': data['open'],
                        'high': data['high'],
                        'low': data['low'],
                        'close': data['close'],
                        'volume': data['volume']
                    }
                )
            self.stdout.write(f"Updated price data for stock: {symbol}")

        self.stdout.write(self.style.SUCCESS(f"Processed {len(stock_list)} stocks"))
