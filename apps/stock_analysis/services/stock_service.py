import logging
from datetime import datetime, timedelta
import time
import pandas as pd
from requests.exceptions import RequestException
from vnstock import *

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
            )
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return None

    @staticmethod
    def get_industry_analysis():
        """Lấy phân tích ngành"""
        try:
            # Thay thế bằng hàm thích hợp từ thư viện vnstock
            # Ví dụ: return industry_analysis()
            # Nếu không có hàm tương ứng, bạn có thể tạo một phân tích giả
            return pd.DataFrame({
                'industry': ['Technology', 'Finance', 'Healthcare'],
                'performance': [10.5, 8.2, 12.3]
            })
        except Exception as e:
            logger.error(f"Error getting industry analysis: {str(e)}")
            return None

    @staticmethod
    def get_stock_list():
        """Lấy danh sách cổ phiếu"""
        try:
            # Thay thế bằng hàm thích hợp từ thư viện vnstock
            # Ví dụ: return listing_companies()
            # Nếu không có hàm tương ứng, bạn có thể tạo một danh sách giả
            return pd.DataFrame({
                'ticker': ['VNM', 'VIC', 'VCB'],
                'companyName': ['Vinamilk', 'Vingroup', 'Vietcombank'],
                'exchange': ['HOSE', 'HOSE', 'HOSE'],
                'industryName': ['Food & Beverage', 'Real Estate', 'Banking']
            })
        except Exception as e:
            logger.error(f"Error getting stock list: {str(e)}")
            return None