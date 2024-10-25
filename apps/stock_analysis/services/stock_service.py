import logging
from datetime import datetime, timedelta
import time
import pandas as pd
from requests.exceptions import RequestException
from vnstock import *  # Import tất cả các hàm từ vnstock
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class StockService:
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    def _make_api_call_with_retry(self, func, *args, **kwargs):
        for attempt in range(self.MAX_RETRIES):
            try:
                result = func(*args, **kwargs)
                if result is None or (isinstance(result, pd.DataFrame) and result.empty):
                    raise ValueError("API returned empty result")
                return result
            except RequestException as e:
                logger.warning(f"API request failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {str(e)}")
            except ValueError as e:
                logger.warning(f"API returned invalid data (attempt {attempt + 1}/{self.MAX_RETRIES}): {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error in API call (attempt {attempt + 1}/{self.MAX_RETRIES}): {str(e)}")
            
            if attempt < self.MAX_RETRIES - 1:
                time.sleep(self.RETRY_DELAY)
        
        logger.error(f"All {self.MAX_RETRIES} attempts failed for API call")
        return None

    def get_market_overview(self):
        """Lấy tổng quan thị trường"""
        cache_key = 'market_overview'
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        try:
            data = self._make_api_call_with_retry(market_top_mover)
            if data is not None and not data.empty:
                cache.set(cache_key, data, self.cache_timeout)
                return data
        except Exception as e:
            logger.error(f"Error fetching market overview: {str(e)}")

        # Trả về dữ liệu mặc định nếu không lấy được dữ liệu
        return pd.DataFrame({
            'index_name': ['VN-Index', 'HNX-Index', 'UPCOM-Index'],
            'value': [1000, 200, 100],
            'change': [10, 5, 2],
            'change_percent': [1.0, 0.5, 0.2]
        })

    def get_stock_data(self, symbol):
        cache_key = f'stock_data_{symbol}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            # Lấy dữ liệu từ API hoặc database
            data = self._fetch_stock_data(symbol)
            if data:
                cache.set(cache_key, data, timeout=settings.STOCK_DATA_CACHE_TIMEOUT)
            return data
        except ValidationError as e:
            logger.error(f"Validation error for stock {symbol}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching data for stock {symbol}: {str(e)}")
            return None

    def _fetch_stock_data(self, symbol):
        # Implement logic to fetch stock data from API or database
        # This is just a placeholder
        return {
            'symbol': symbol,
            'current_price': 100.0,
            'change': 1.5,
            'volume': 1000000,
            'pe_ratio': 15.5,
            'eps': 6.5,
        }

    def get_stock_historical_data(self, symbol, start_date=None, end_date=None):
        """Lấy dữ liệu lịch sử của một mã cổ phiếu"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            data = stock_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            if data is not None and not data.empty:
                data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
            return data
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return None

    def get_industry_analysis(self):
        """Lấy phân tích ngành"""
        cache_key = 'industry_analysis'
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        try:
            # Thử lấy dữ liệu từ API
            data = self._make_api_call_with_retry(industry_analysis, symbol='VNINDEX')
            if data is not None and not data.empty:
                cache.set(cache_key, data, self.cache_timeout)
                return data
        except Exception as e:
            logger.error(f"Error fetching industry analysis: {str(e)}")

        # Trả về dữ liệu mặc định nếu không lấy được dữ liệu từ API
        default_data = pd.DataFrame({
            'industry_name': ['Công nghệ', 'Tài chính', 'Bất động sản', 'Năng lượng', 'Y tế'],
            'market_cap': [1000000, 2000000, 1500000, 1200000, 800000],
            'change_percent': [1.5, -0.5, 0.8, -1.2, 2.0]
        })
        return default_data

    def get_stock_list(self):
        """Lấy danh sách cổ phiếu"""
        cache_key = 'stock_list'
        cached_data = cache.get(cache_key)
        if cached_data is not None:  # Thay đổi ở đây
            return cached_data

        try:
            data = self._make_api_call_with_retry(listing_companies)
            if data is not None and not data.empty:  # Thêm kiểm tra này
                cache.set(cache_key, data, self.cache_timeout)
            return data
        except RequestException:
            return None

    def get_stock_intraday(self, symbol):
        cache_key = f'stock_intraday_{symbol}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            data = self._make_api_call_with_retry(stock_intraday_data, symbol=symbol)
            cache.set(cache_key, data, self.cache_timeout)
            return data
        except RequestException:
            return None

    def get_all_industries(self):
        stock_list = self.get_stock_list()
        if stock_list is not None and not stock_list.empty:
            return sorted(stock_list['industry'].unique())
        return []

    def get_top_gainers(self, limit=10):
        """Lấy danh sách cổ phiếu tăng giá mạnh nhất"""
        cache_key = f'top_gainers_{limit}'
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        try:
            data = self._make_api_call_with_retry(listing_companies)
            if data is not None and not data.empty:
                if 'priceChange' not in data.columns:
                    data['priceChange'] = 0  # Giả sử không có thay đổi nếu không có dữ liệu
                if 'price' not in data.columns:
                    data['price'] = 0  # Giả sử giá bằng 0 nếu không có dữ liệu
                data['priceChangePercent'] = (data['priceChange'] / data['price']) * 100 if 'price' in data.columns else 0
                data = data.sort_values(by='priceChangePercent', ascending=False).head(limit)
                cache.set(cache_key, data, self.cache_timeout)
                return data
        except Exception as e:
            logger.error(f"Error fetching top gainers: {str(e)}")

        # Trả về dữ liệu mặc định nếu không lấy được dữ liệu
        return pd.DataFrame({
            'symbol': [f'STOCK{i}' for i in range(1, limit+1)],
            'price': [100 + i for i in range(limit)],
            'priceChangePercent': [5.0 - i*0.1 for i in range(limit)]
        })

    def get_top_losers(self, limit=10):
        """Lấy danh sách cổ phiếu giảm giá mạnh nhất"""
        cache_key = f'top_losers_{limit}'
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        try:
            data = self._make_api_call_with_retry(listing_companies)
            if data is not None and not data.empty:
                if 'priceChange' not in data.columns:
                    data['priceChange'] = 0  # Giả sử không có thay đổi nếu không có dữ liệu
                if 'price' not in data.columns:
                    data['price'] = 0  # Giả sử giá bằng 0 nếu không có dữ liệu
                data['priceChangePercent'] = (data['priceChange'] / data['price']) * 100 if 'price' in data.columns else 0
                data = data.sort_values(by='priceChangePercent', ascending=True).head(limit)
                cache.set(cache_key, data, self.cache_timeout)
                return data
        except Exception as e:
            logger.error(f"Error fetching top losers: {str(e)}")

        # Trả về dữ liệu mặc định nếu không lấy được dữ liệu
        return pd.DataFrame({
            'symbol': [f'STOCK{i}' for i in range(1, limit+1)],
            'price': [100 - i for i in range(limit)],
            'priceChangePercent': [-5.0 + i*0.1 for i in range(limit)]
        })

    def get_technical_indicators(self, symbol):
        cache_key = f'technical_indicators_{symbol}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # Calculate technical indicators
        indicators = self._calculate_technical_indicators(symbol)
        if indicators:
            cache.set(cache_key, indicators, timeout=settings.TECHNICAL_INDICATORS_CACHE_TIMEOUT)
        return indicators

    def _calculate_technical_indicators(self, symbol):
        # Implement logic to calculate technical indicators
        # This is just a placeholder
        return {
            'symbol': symbol,
            'rsi': 65.5,
            'macd': 0.75,
            'bollinger_bands': {
                'upper': 105.0,
                'middle': 100.0,
                'lower': 95.0
            }
        }
