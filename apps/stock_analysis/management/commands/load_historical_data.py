from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import yfinance as yf
import logging
from apps.stock_analysis.models import Stock, HistoricalData

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Tải dữ liệu lịch sử cho các mã cổ phiếu'

    def handle(self, *args, **options):
        stocks = Stock.objects.all()
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)  # Lấy dữ liệu 1 năm

        for stock in stocks:
            try:
                self.stdout.write(f'Đang tải dữ liệu cho {stock.symbol}...')
                
                # Lấy dữ liệu từ yfinance
                ticker = yf.Ticker(f"{stock.symbol}.VN")
                df = ticker.history(start=start_date, end=end_date)
                
                # Lưu vào database
                for index, row in df.iterrows():
                    HistoricalData.objects.update_or_create(
                        stock=stock,
                        date=index.date(),
                        defaults={
                            'open_price': float(row['Open']),
                            'high_price': float(row['High']),
                            'low_price': float(row['Low']),
                            'close_price': float(row['Close']),
                            'volume': int(row['Volume'])
                        }
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Đã tải xong dữ liệu cho {stock.symbol}'))
                
            except Exception as e:
                logger.error(f"Lỗi khi tải dữ liệu cho {stock.symbol}: {str(e)}")
                self.stdout.write(self.style.ERROR(f'Lỗi khi tải dữ liệu cho {stock.symbol}: {str(e)}'))
                continue

        self.stdout.write(self.style.SUCCESS('Hoàn thành tải dữ liệu lịch sử'))
