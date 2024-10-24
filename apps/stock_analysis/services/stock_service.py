from vnstock import *
from requests.exceptions import RequestException
import time

# Các import khác...









from datetime import datetime, timedelta







import logging







import pandas as pd















logger = logging.getLogger(__name__)















class StockService:







    @staticmethod







    def get_market_overview():







        """Lấy tổng quan thị trường"""







        try:







            return market_top_mover()







        except Exception as e:







            logger.error(f"Error getting market overview: {str(e)}")







            return None















    @staticmethod
    def get_stock_data(symbol, start_date, end_date):
        max_retries = 3
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                data = stock_historical_data(symbol=symbol, start_date=start_date, end_date=end_date)
                return data
            except RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Lỗi kết nối: {e}. Thử lại sau {retry_delay} giây...")
                    time.sleep(retry_delay)
                else:
                    print(f"Không thể lấy dữ liệu sau {max_retries} lần thử. Lỗi: {e}")
                    return None

    # Các phương thức khác...









    @staticmethod







    def get_stock_historical_data(symbol, start_date=None, end_date=None):







        """Lấy dữ liệu lịch sử của một mã cổ phiếu"""







        try:







            if not start_date:







                start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')







            if not end_date:







                end_date = datetime.now().strftime('%Y-%m-%d')







            







            return stock_historical_data(







                symbol=symbol,







                start_date=start_date,







                end_date=end_date







           