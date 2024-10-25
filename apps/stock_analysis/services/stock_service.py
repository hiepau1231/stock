import logging

from datetime import datetime, timedelta

import pandas as pd

import yfinance as yf

from django.core.cache import cache

from django.conf import settings

from django.core.exceptions import ValidationError

from ..models import Stock, StockPrice, HistoricalData

from django.utils import timezone

import csv

import os

import requests

from bs4 import BeautifulSoup

import ssl



logger = logging.getLogger(__name__)



class StockService:

    def __init__(self):

        self.cache_timeout = 300  # 5 minutes

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        }

        self.base_url = "https://restv2.fireant.vn"

        self.ssl_context = ssl.create_default_context()

        self.ssl_context.check_hostname = False

        self.ssl_context.verify_mode = ssl.CERT_NONE



    def get_stock_data(self, symbol):
        """Lấy dữ liệu realtime của một mã cổ phiếu"""
        try:
            # Thử lấy từ cache trước
            cache_key = f'stock_data_{symbol}'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            # Lấy dữ liệu từ Fireant
            url = f"{self.base_url}/symbols/{symbol}/quote"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                stock_data = {
                    'symbol': symbol,
                    'price': float(data['price']),
                    'change': float(data['change']),
                    'change_percent': float(data['percentChange']),
                    'volume': int(data['volume'])
                }
                cache.set(cache_key, stock_data, self.cache_timeout)
                return stock_data

            return None

        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return None



    @staticmethod
    def get_historical_data(symbol, start_date, end_date):
        """Lấy dữ liệu lịch sử của một mã cổ phiếu"""
        try:
            ticker = yf.Ticker(f"{symbol}.VN")
            df = ticker.history(start=start_date, end=end_date)
            return df.reset_index()
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None



    def get_market_overview(self):
        """Lấy thông tin thị trường"""
        try:
            # Thử lấy từ cache
            cache_key = 'market_overview'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            # Lấy dữ liệu từ Fireant
            url = f"{self.base_url}/symbols/market-quotes"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                market_data = []
                
                # Parse dữ liệu chỉ số
                indices = {
                    'VNINDEX': 'VN-Index',
                    'VN30': 'VN30-Index',
                    'HNX': 'HNX-Index',
                    'UPCOM': 'UPCOM-Index'
                }
                
                for item in data:
                    if item['code'] in indices:
                        market_data.append({
                            'symbol': indices[item['code']],
                            'price': float(item['price']),
                            'change': float(item['change']),
                            'change_percent': float(item['percentChange'])
                        })
                
                if market_data:
                    cache.set(cache_key, market_data, 300)  # Cache for 5 minutes
                    return market_data

            # Nếu không lấy được dữ liệu, trả về dữ liệu mẫu
            sample_data = [
                {'symbol': 'VN-Index', 'price': 1200, 'change': 5.2, 'change_percent': 0.43},
                {'symbol': 'VN30-Index', 'price': 1180, 'change': 4.8, 'change_percent': 0.41},
                {'symbol': 'HNX-Index', 'price': 230, 'change': 1.5, 'change_percent': 0.65},
                {'symbol': 'UPCOM-Index', 'price': 85, 'change': 0.3, 'change_percent': 0.35}
            ]
            cache.set(cache_key, sample_data, 300)
            return sample_data

        except Exception as e:
            logger.error(f"Error fetching market overview: {str(e)}")
            return []

    def get_top_movers(self, top_type='gainers', limit=10):

        try:

            all_stocks = self.get_stock_list()

            stock_data = []

            for stock in all_stocks[:100]:  # Lấy 100 cổ phiếu đầu tiên để tránh quá nhiều requests

                data = self.get_stock_data(stock['ticker'])

                if data:

                    stock_data.append(data)

            

            sorted_stocks = sorted(stock_data, key=lambda x: x['change_percent'], reverse=(top_type == 'gainers'))

            return sorted_stocks[:limit]

        except Exception as e:

            logger.error(f"Error fetching top {top_type}: {str(e)}")

            return []



    def get_top_gainers(self):

        return self.get_top_movers('gainers')



    def get_top_losers(self):

        return self.get_top_movers('losers')



    def get_company_overview(self, symbol):
        """Lấy thông tin tổng quan về công ty"""
        try:
            # Thử lấy từ cache trước
            cache_key = f'company_overview_{symbol}'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            # Nếu không có trong cache, lấy dữ liệu mới từ yfinance
            ticker = yf.Ticker(f"{symbol}.VN")
            info = ticker.info
            
            overview = {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'description': info.get('longBusinessSummary', 'N/A'),
                'website': info.get('website', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'employees': info.get('fullTimeEmployees', 'N/A')
            }

            # Lưu vào cache
            cache.set(cache_key, overview, 3600)  # Cache 1 giờ
            return overview
        except Exception as e:
            logger.error(f"Error fetching company overview for {symbol}: {str(e)}")
            return None



    def get_stock_intraday(self, symbol):

        try:

            intraday_data = get_realtime_price(symbol)

            return intraday_data.to_dict('records')

        except Exception as e:

            logger.error(f"Error fetching intraday data for {symbol}: {str(e)}")

            return None



    def get_stock_list(self):
        """Lấy danh sách tất cả các mã cổ phiếu"""
        try:
            # Thử lấy từ cache
            cache_key = 'stock_list'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            # Lấy dữ liệu từ Fireant
            url = f"{self.base_url}/symbols"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                stocks = []
                for stock in data:
                    if stock['exchange'] in ['HOSE', 'HNX', 'UPCOM']:
                        stocks.append({
                            'ticker': stock['code'],
                            'organName': stock['companyName'],
                            'comGroupCode': stock['exchange']
                        })
                
                if stocks:
                    cache.set(cache_key, stocks, 3600)  # Cache 1 giờ
                    return stocks

            # Nếu không lấy được dữ liệu, trả về danh sách mẫu
            sample_stocks = [
                {'ticker': 'VNM', 'organName': 'Vinamilk', 'comGroupCode': 'HOSE'},
                {'ticker': 'VIC', 'organName': 'Vingroup', 'comGroupCode': 'HOSE'},
                {'ticker': 'FPT', 'organName': 'FPT Corp', 'comGroupCode': 'HOSE'},
                {'ticker': 'MWG', 'organName': 'Thế Giới Di Động', 'comGroupCode': 'HOSE'},
                {'ticker': 'HPG', 'organName': 'Hòa Phát', 'comGroupCode': 'HOSE'}
            ]
            cache.set(cache_key, sample_stocks, 3600)
            return sample_stocks

        except Exception as e:
            logger.error(f"Error fetching stock list: {str(e)}")
            return []

    def update_stock_data(self):

        stocks = self.get_stock_list()

        updated_count = 0

        for stock_info in stocks:

            symbol = stock_info['ticker']

            data = self.get_stock_data(symbol)

            if data:

                stock, created = Stock.objects.update_or_create(

                    symbol=symbol,

                    defaults={

                        'name': stock_info['organName'],

                        'exchange': stock_info['comGroupCode'],

                        'current_price': data['price'],

                        'change': data['change'],

                        'percent_change': data['change_percent'],

                    }

                )

                updated_count += 1

            else:

                logger.warning(f"Failed to update data for {symbol}")

        

        logger.info(f"Updated {updated_count} out of {len(stocks)} stocks")

        return updated_count



    # You can add more methods as needed





