from django.core.management.base import BaseCommand
from django.db import transaction
from apps.stock_analysis.models import Stock, StockPrice, Industry, MarketIndex
from apps.stock_analysis.services.stock_service import StockService
import logging
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Automatically update stock data from yfinance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days of historical data to fetch'
        )

    def handle(self, *args, **options):
        days = options['days']
        
        # Danh sách các ngành và mã cổ phiếu
        INDUSTRIES = {
            'Bất động sản': ['VIC', 'NVL', 'PDR', 'DXG', 'KDH'],
            'Ngân hàng': ['VCB', 'BID', 'CTG', 'TCB', 'MBB', 'ACB'],
            'Chứng khoán': ['SSI', 'VND', 'HCM', 'VCI'],
            'Bảo hiểm': ['BVH', 'BMI'],
            'Dầu khí': ['GAS', 'PLX', 'PVD'],
            'Xây dựng': ['CTD', 'HBC', 'VCG'],
            'Thép': ['HPG', 'HSG', 'NKG'],
            'Điện': ['POW', 'PPC', 'NT2'],
            'Công nghệ': ['FPT', 'CMG'],
            'Bán lẻ': ['MWG', 'PNJ', 'VRE'],
            'Dược phẩm': ['DHG', 'DMC', 'IMP']
        }

        try:
            with transaction.atomic():
                self.stdout.write('Starting data update...')
                
                # Đếm số lượng record trước khi cập nhật
                initial_stock_count = Stock.objects.count()
                initial_price_count = StockPrice.objects.count()
                
                # 1. Cập nhật chỉ số thị trường
                self.update_market_indices()

                # 2. Cập nhật dữ liệu cổ phiếu
                service = StockService()
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')

                # Tạo/cập nhật ngành
                for industry_name, symbols in INDUSTRIES.items():
                    industry, _ = Industry.objects.get_or_create(name=industry_name)
                    
                    for symbol in symbols:
                        self.stdout.write(f'Processing {symbol}...')
                        
                        # Lấy thông tin cổ phiếu từ yfinance
                        try:
                            ticker = yf.Ticker(f"{symbol}.VN")
                            info = ticker.info  # Lấy info trước
                            
                            # Lấy dữ liệu gần nhất
                            today_data = ticker.history(period='1d')
                            if not today_data.empty:
                                current_price = float(today_data['Close'].iloc[-1])
                                open_price = float(today_data['Open'].iloc[-1])
                                change = current_price - open_price
                                percent_change = (change / open_price) * 100
                                volume = int(today_data['Volume'].iloc[-1])
                            else:
                                # Sử dụng dữ liệu từ info nếu không có dữ liệu today
                                current_price = info.get('regularMarketPrice', 0)
                                change = info.get('regularMarketChange', 0)
                                percent_change = info.get('regularMarketChangePercent', 0)
                                volume = info.get('regularMarketVolume', 0)

                            # Xử lý NaN values
                            current_price = 0 if pd.isna(current_price) else float(current_price)
                            change = 0 if pd.isna(change) else float(change)
                            percent_change = 0 if pd.isna(percent_change) else float(percent_change)
                            volume = 0 if pd.isna(volume) else int(volume)

                            # Cập nhật hoặc tạo mới cổ phiếu
                            stock, created = Stock.objects.update_or_create(
                                symbol=symbol,
                                defaults={
                                    'name': info.get('longName', symbol),
                                    'industry': industry,
                                    'current_price': current_price,
                                    'change': change,
                                    'percent_change': percent_change,
                                    'volume': volume,
                                    'market_cap': info.get('marketCap', 0)
                                }
                            )

                            # Lấy và lưu dữ liệu lịch sử
                            hist_data = service.get_historical_data(symbol, start_date, end_date)
                            if hist_data is not None and not hist_data.empty:
                                price_objects = []
                                for _, row in hist_data.iterrows():
                                    # Kiểm tra và xử lý giá trị NaN
                                    open_price = 0 if pd.isna(row['Open']) else float(row['Open'])
                                    high_price = 0 if pd.isna(row['High']) else float(row['High'])
                                    low_price = 0 if pd.isna(row['Low']) else float(row['Low'])
                                    close_price = 0 if pd.isna(row['Close']) else float(row['Close'])
                                    volume = 0 if pd.isna(row['Volume']) else int(row['Volume'])

                                    price_objects.append(StockPrice(
                                        stock=stock,
                                        date=row['Date'],
                                        open_price=open_price,
                                        high_price=high_price,
                                        low_price=low_price,
                                        close_price=close_price,
                                        volume=volume
                                    ))
                                
                                # Xóa dữ liệu cũ và thêm dữ liệu mới
                                StockPrice.objects.filter(stock=stock).delete()
                                StockPrice.objects.bulk_create(price_objects, ignore_conflicts=True)
                            
                        except Exception as e:
                            logger.error(f"Error processing {symbol}: {str(e)}")
                            continue

                # Đếm số lượng record sau khi cập nhật
                final_stock_count = Stock.objects.count()
                final_price_count = StockPrice.objects.count()
                
                self.stdout.write(f"""
                Update Summary:
                - Stocks: {final_stock_count} (Added: {final_stock_count - initial_stock_count})
                - Price Records: {final_price_count} (Added: {final_price_count - initial_price_count})
                """)
                
                # Log một vài mẫu dữ liệu để kiểm tra
                sample_stocks = Stock.objects.all()[:5]
                self.stdout.write("\nSample Stock Data:")
                for stock in sample_stocks:
                    self.stdout.write(f"""
                    Symbol: {stock.symbol}
                    Price: {stock.current_price}
                    Change: {stock.percent_change}%
                    Volume: {stock.volume}
                    """)
                    
                    # Log một vài giá lịch sử
                    recent_prices = StockPrice.objects.filter(stock=stock).order_by('-date')[:3]
                    self.stdout.write("Recent Prices:")
                    for price in recent_prices:
                        self.stdout.write(f"Date: {price.date}, Close: {price.close_price}")
                    self.stdout.write("-------------------")

                self.stdout.write(self.style.SUCCESS('Successfully updated all stock data'))

        except Exception as e:
            logger.error(f"Error during data update: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

    def update_market_indices(self):
        """Cập nhật các chỉ số thị trường"""
        # Tạm thời set giá trị mặc định
        indices = {
            'VNINDEX': '^VNINDEX',
            'VN30': '^VN30',
            'HNX': '^HNX',
            'UPCOM': '^UPCOM'
        }

        for name, symbol in indices.items():
            try:
                # Tạm thời tạo record với giá trị mặc định
                MarketIndex.objects.update_or_create(
                    name=name,
                    defaults={
                        'value': 0,
                        'change': '0.00%'
                    }
                )
                logger.info(f"Created/Updated market index {name}")
            except Exception as e:
                logger.error(f"Error updating market index {name}: {str(e)}")
