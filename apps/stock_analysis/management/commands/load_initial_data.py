from django.core.management.base import BaseCommand
from apps.stock_analysis.services.stock_service import StockService
from apps.stock_analysis.models import Stock, HistoricalData
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Loads initial stock data from yfinance'

    def handle(self, *args, **kwargs):
        service = StockService()
        
        # 1. Tạo dữ liệu chỉ số thị trường
        self.stdout.write('Creating market indices...')
        indices = [
            {'symbol': 'VNINDEX', 'name': 'VN-Index', 'price': 1200, 'change': 5.2, 'change_percent': 0.43},
            {'symbol': 'VN30', 'name': 'VN30-Index', 'price': 1180, 'change': 4.8, 'change_percent': 0.41},
            {'symbol': 'HNX', 'name': 'HNX-Index', 'price': 230, 'change': 1.5, 'change_percent': 0.65},
            {'symbol': 'UPCOM', 'name': 'UPCOM-Index', 'price': 85, 'change': 0.3, 'change_percent': 0.35}
        ]
        
        for index in indices:
            Stock.objects.update_or_create(
                symbol=index['symbol'],
                defaults={
                    'name': index['name'],
                    'exchange': 'INDEX',
                    'current_price': index['price'],
                    'change': index['change'],
                    'percent_change': index['change_percent']
                }
            )
        
        # 2. Tạo dữ liệu cổ phiếu mẫu nếu không lấy được từ API
        sample_stocks = [
            {'symbol': 'VNM', 'name': 'Vinamilk', 'exchange': 'HOSE', 'price': 80000},
            {'symbol': 'VIC', 'name': 'Vingroup', 'exchange': 'HOSE', 'price': 75000},
            {'symbol': 'FPT', 'name': 'FPT Corp', 'exchange': 'HOSE', 'price': 90000},
            # Thêm các cổ phiếu mẫu khác
        ]
        
        for stock_info in sample_stocks:
            stock, created = Stock.objects.update_or_create(
                symbol=stock_info['symbol'],
                defaults={
                    'name': stock_info['name'],
                    'exchange': stock_info['exchange'],
                    'current_price': stock_info['price'],
                    'change': 0,
                    'percent_change': 0
                }
            )
            
            # Tạo dữ liệu lịch sử mẫu
            for i in range(30):
                date = timezone.now() - timedelta(days=i)
                HistoricalData.objects.update_or_create(
                    stock=stock,
                    date=date.date(),
                    defaults={
                        'open_price': stock_info['price'] * (1 + (i % 5 - 2) / 100),
                        'high_price': stock_info['price'] * (1 + (i % 5) / 100),
                        'low_price': stock_info['price'] * (1 - (i % 5) / 100),
                        'close_price': stock_info['price'] * (1 + (i % 5 - 1) / 100),
                        'volume': 1000000 + (i * 10000)
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))
