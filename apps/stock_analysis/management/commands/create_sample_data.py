from django.core.management.base import BaseCommand
from apps.stock_analysis.models import Stock, StockPrice
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Creates sample data for HNXINDEX and UPCOM'

    def handle(self, *args, **options):
        # Tạo dữ liệu cho HNXINDEX
        hnx, created = Stock.objects.get_or_create(
            symbol='HNXINDEX',
            defaults={'name': 'HNX Index', 'sector': 'Index', 'industry': 'Market Index'}
        )

        # Tạo dữ liệu cho UPCOM
        upcom, created = Stock.objects.get_or_create(
            symbol='UPCOM',
            defaults={'name': 'UPCOM Index', 'sector': 'Index', 'industry': 'Market Index'}
        )

        # Tạo dữ liệu giá mẫu cho 30 ngày gần nhất
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        for stock in [hnx, upcom]:
            base_price = 100.0 if stock.symbol == 'HNXINDEX' else 50.0
            current_date = start_date
            previous_close = base_price

            while current_date <= end_date:
                # Tạo biến động giá ngẫu nhiên
                change = random.uniform(-2, 2)
                close_price = previous_close + change
                high_price = close_price + random.uniform(0, 1)
                low_price = close_price - random.uniform(0, 1)
                open_price = previous_close + random.uniform(-1, 1)
                volume = random.randint(1000000, 5000000)

                StockPrice.objects.get_or_create(
                    stock=stock,
                    date=current_date,
                    defaults={
                        'open_price': open_price,
                        'high_price': high_price,
                        'low_price': low_price,
                        'close_price': close_price,
                        'volume': volume
                    }
                )

                previous_close = close_price
                current_date += timedelta(days=1)

            self.stdout.write(self.style.SUCCESS(f'Successfully created sample data for {stock.symbol}'))
