from django.core.management.base import BaseCommand
from django.core.management import call_command
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Tự động cập nhật dữ liệu theo định kỳ'

    def handle(self, *args, **options):
        while True:
            try:
                self.stdout.write('Bắt đầu cập nhật dữ liệu...')
                call_command('load_historical_data')
                self.stdout.write(self.style.SUCCESS('Cập nhật dữ liệu thành công'))
                
                # Đợi 1 giờ trước khi cập nhật lại
                time.sleep(3600)
            except Exception as e:
                logger.error(f"Lỗi khi cập nhật dữ liệu: {str(e)}")
                time.sleep(300)  # Đợi 5 phút nếu có lỗi
