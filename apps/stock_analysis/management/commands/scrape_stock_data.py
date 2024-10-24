from django.core.management.base import BaseCommand
from stock_analysis.web_scraping_script import StockScraper
from stock_analysis.models import StockData, MarketIndex
import logging
from datetime import datetime

class Command(BaseCommand):
    help = 'Scrape dữ liệu chứng khoán từ website'

    def handle(self, *args, **kwargs):
        scraper = None
        try:
            scraper = StockScraper()
            
            # Scrape dữ liệu chỉ số
            self.stdout.write("Đang scrape dữ liệu chỉ số thị trường...")
            indices_data = scraper.scrape_stock_indices()
            if indices_data:
                for name, data in indices_data.items():
                    MarketIndex.objects.create(
                        name=name,
                        value=data['value'],
                        change=data['change'],
                        timestamp=datetime.now()
                    )
                self.stdout.write(self.style.SUCCESS(
                    f"Đã lưu {len(indices_data)} chỉ số thị trường"
                ))

            # Scrape dữ liệu các mã cổ phiếu
            stock_codes = ['VNM', 'VIC', 'FPT']  # Thêm các mã cần scrape
            for code in stock_codes:
                self.stdout.write(f"Đang scrape dữ liệu cổ phiếu {code}...")
                stock_data = scraper.scrape_stock_data(code)
                if stock_data:
                    StockData.objects.create(
                        code=stock_data['code'],
                        price=stock_data['price'],
                        change=stock_data['change'],
                        volume=stock_data['volume'],
                        timestamp=datetime.now()
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"Đã lưu dữ liệu cổ phiếu {code}"
                    ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Lỗi: {str(e)}"))
            logging.error(f"Lỗi trong quá trình scraping: {str(e)}")
        
        finally:
            if scraper:
                scraper.close()
