import logging
from datetime import datetime, timedelta
import time
import pandas as pd
import requests
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError
from ..models import Stock, StockPrice
from django.utils import timezone
import random

logger = logging.getLogger(__name__)

class StockService:
    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = "GGO8XKMA3V6UUNV6"  # Thay thế bằng API key của bạn
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    def _make_api_call(self, function, symbol, **kwargs):
        params = {
            "function": function,
            "symbol": symbol,
            "apikey": self.API_KEY,
            **kwargs
        }
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                if "Error Message" in data:
                    raise ValueError(data["Error Message"])
                if "Note" in data:
                    logger.warning(f"API limit reached: {data['Note']}")
                    time.sleep(60)  # Wait for 60 seconds before next attempt
                    continue
                return data
            except requests.RequestException as e:
                logger.error(f"API call failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {str(e)}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
        return None

    def get_market_overview(self):
        """Lấy tổng quan thị trường"""
        data = [
            {
                'index_name': 'VN-Index',
                'value': round(random.uniform(900, 1100), 2),
                'change': round(random.uniform(-10, 10), 2),
                'change_percent': round(random.uniform(-2, 2), 2)
            },
            {
                'index_name': 'HNX-Index',
                'value': round(random.uniform(100, 200), 2),
                'change': round(random.uniform(-5, 5), 2),
                'change_percent': round(random.uniform(-2, 2), 2)
            },
            {
                'index_name': 'UPCOM-Index',
                'value': round(random.uniform(50, 100), 2),
                'change': round(random.uniform(-3, 3), 2),
                'change_percent': round(random.uniform(-2, 2), 2)
            }
        ]
        return pd.DataFrame(data)

    def get_stock_list(self):
        return [
            {'symbol': 'VNM', 'name': 'Vinamilk', 'exchange': 'HOSE'},
            {'symbol': 'VIC', 'name': 'Vingroup', 'exchange': 'HOSE'},
            {'symbol': 'FPT', 'name': 'FPT Corporation', 'exchange': 'HOSE'},
            {'symbol': 'MBB', 'name': 'MBBank', 'exchange': 'HOSE'},
            {'symbol': 'VCB', 'name': 'Vietcombank', 'exchange': 'HOSE'},
        ]

    def get_historical_data(self, symbol, start_date, end_date):
        date_range = pd.date_range(start=start_date, end=end_date)
        data = []
        last_close = random.uniform(10, 100)
        for date in date_range:
            open_price = last_close * (1 + random.uniform(-0.02, 0.02))
            close = open_price * (1 + random.uniform(-0.02, 0.02))
            high = max(open_price, close) * (1 + random.uniform(0, 0.01))
            low = min(open_price, close) * (1 - random.uniform(0, 0.01))
            volume = int(random.uniform(100000, 1000000))
            data.append({
                'date': date.date(),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
            last_close = close
        return data

    def get_stock_data(self, symbol):
        return {
            "symbol": symbol,
            "price": round(random.uniform(10, 100), 2),
            "change": round(random.uniform(-5, 5), 2),
            "change_percent": round(random.uniform(-5, 5), 2)
        }

    def get_top_gainers(self):
        stocks = self.get_stock_list()
        return [
            {'symbol': stock['symbol'], 'name': stock['name'], 'change_percent': round(random.uniform(1, 5), 2)}
            for stock in random.sample(stocks, min(3, len(stocks)))
        ]

    def get_top_losers(self):
        stocks = self.get_stock_list()
        return [
            {'symbol': stock['symbol'], 'name': stock['name'], 'change_percent': round(random.uniform(-5, -1), 2)}
            for stock in random.sample(stocks, min(3, len(stocks)))
        ]

    # Thêm các phương thức khác khi cần thiết
