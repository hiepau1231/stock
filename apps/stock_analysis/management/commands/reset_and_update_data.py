from django.core.management.base import BaseCommand
from django.db import transaction
from apps.stock_analysis.models import Stock, StockPrice, Industry
from apps.stock_analysis.services.stock_service import StockService
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Reset and update all stock data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days of historical data to fetch'
        )

    def handle(self, *args, **options):
        days = options['days']
        
        # Danh sách các ngành
        INDUSTRIES = [
            'Bất động sản',
            'Ngân hàng',
            'Chứng khoán',
            'Bảo hiểm',
            'Dầu khí',
            'Xây dựng',
            'Thép',
            'Điện',
            'Công nghệ',
            'Bán lẻ',
            'Dược phẩm'
        ]

        # Danh sách mã cổ phiếu theo ngành
        STOCK_MAPPING = {
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
                # Xóa dữ liệu cũ
                self.stdout.write('Deleting old data...')
                StockPrice.objects.all().delete()
                Stock.objects.all().delete()
                Industry.objects.all().delete()

                # Tạo lại các ngành
                self.stdout.write('Creating industries...')
                industry_objects = {}
                for industry_name in INDUSTRIES:
                    industry = Industry.objects.create(name=industry_name)
                    industry_objects[industry_name] = industry

                # Tạo lại cổ phiếu và cập nhật dữ liệu
                service = StockService()
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')

                for industry_name, symbols in STOCK_MAPPING.items():
                    industry = industry_objects[industry_name]
                    
                    for symbol in symbols:
                        self.stdout.write(f'Processing {symbol}...')
                        
                        # Tạo cổ phiếu
                        stock = Stock.objects.create(
                            symbol=symbol,
                            industry=industry
                        )

                        # Lấy và lưu dữ liệu lịch sử
                        df = service.get_stock_data(symbol, start_date, end_date)
                        if df is not None:
                            price_objects = []
                            for _, row in df.iterrows():
                                price_objects.append(StockPrice(
                                    stock=stock,
                                    date=row['Date'],
                                    open_price=row['Open'],
                                    high_price=row['High'],
                                    low_price=row['Low'],
                                    close_price=row['Close'],
                                    volume=row['Volume']
                                ))
                            StockPrice.objects.bulk_create(price_objects)
                        else:
                            logger.warning(f"Could not fetch data for {symbol}")

                self.stdout.write(self.style.SUCCESS('Successfully reset and updated all stock data'))

        except Exception as e:
            logger.error(f"Error during data reset and update: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
