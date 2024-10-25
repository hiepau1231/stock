import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError
from ..models import Stock, StockPrice, HistoricalData
from django.utils import timezone

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    def get_stock_data(self, symbol):
        """Lấy dữ liệu realtime của một mã cổ phiếu"""
        try:
            cache_key = f'stock_data_{symbol}'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            ticker = yf.Ticker(f"{symbol}.VN")
            info = ticker.info
            
            stock_data = {
                'symbol': symbol,
                'price': info.get('regularMarketPrice', 0),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('regularMarketVolume', 0)
            }
            
            cache.set(cache_key, stock_data, self.cache_timeout)
            return stock_data

        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return None

    def get_historical_data(self, symbol, start_date, end_date):
        """Lấy dữ liệu lịch sử của một mã cổ phiếu"""
        try:
            ticker = yf.Ticker(f"{symbol}.VN")
            df = ticker.history(start=start_date, end=end_date)
            return df.reset_index().to_dict('records')
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None

    def get_market_overview(self):
        """Lấy thông tin thị trường"""
        try:
            cache_key = 'market_overview'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            market_data = [
                {'symbol': 'VNINDEX', 'price': 1200, 'change': 5.2, 'change_percent': 0.43},
                {'symbol': 'VN30', 'price': 1180, 'change': 4.8, 'change_percent': 0.41},
                {'symbol': 'HNX', 'price': 230, 'change': 1.5, 'change_percent': 0.65},
                {'symbol': 'UPCOM', 'price': 85, 'change': 0.3, 'change_percent': 0.35}
            ]

            cache.set(cache_key, market_data, 300)  # Cache for 5 minutes
            return market_data

        except Exception as e:
            logger.error(f"Error fetching market overview: {str(e)}")
            return []

    def get_top_movers(self, limit=5):
        cache_key = f'top_movers_{limit}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info(f"Returning cached top movers data for {limit} stocks")
            return cached_data

        try:
            all_stocks = self.get_stock_list()
            
            stock_data = []
            for stock in all_stocks:
                data = self.get_stock_data(stock['ticker'])
                if data:
                    stock_data.append(data)
            
            sorted_stocks = sorted(stock_data, key=lambda x: x['change_percent'], reverse=True)
            
            top_gainers = sorted_stocks[:limit]
            top_losers = sorted_stocks[-limit:][::-1]
            
            result = {
                'top_gainers': top_gainers,
                'top_losers': top_losers
            }
            
            cache.set(cache_key, result, 300)
            
            logger.info(f"Successfully fetched top {limit} gainers and losers")
            return result
        except Exception as e:
            logger.error(f"Error fetching top movers: {str(e)}")
            return None

    def get_company_overview(self, symbol):
        """Lấy thông tin tổng quan về công ty"""
        try:
            cache_key = f'company_overview_{symbol}'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

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

            cache.set(cache_key, overview, 3600)  # Cache 1 giờ
            return overview
        except Exception as e:
            logger.error(f"Error fetching company overview for {symbol}: {str(e)}")
            return None

    def get_stock_list(self):
        """Lấy danh sách tất cả các mã cổ phiếu"""
        try:
            cache_key = 'stock_list'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            # Đây là một danh sách mẫu. Bạn cần thay thế bằng cách lấy danh sách thực tế.
            sample_stocks = [
                {'ticker': 'VNM', 'organName': 'Vinamilk', 'comGroupCode': 'HOSE'},
                {'ticker': 'VIC', 'organName': 'Vingroup', 'comGroupCode': 'HOSE'},
                {'ticker': 'FPT', 'organName': 'FPT Corp', 'comGroupCode': 'HOSE'},
                {'ticker': 'MWG', 'organName': 'Thế Giới Di Động', 'comGroupCode': 'HOSE'},
                {'ticker': 'HPG', 'organName': 'Hòa Phát', 'comGroupCode': 'HOSE'}
            ]
            
            cache.set(cache_key, sample_stocks, 3600)  # Cache 1 giờ
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

    def get_stock_historical_data(self, symbol, days=30):
        try:
            stock = Stock.objects.get(symbol=symbol)
            historical_data = HistoricalData.objects.filter(
                stock=stock
            ).order_by('-date')[:days]
            
            if not historical_data.exists():
                # Nếu không có dữ liệu trong database, thử lấy từ yfinance
                end_date = timezone.now().date()
                start_date = end_date - timedelta(days=days)
                
                ticker = yf.Ticker(f"{symbol}.VN")
                df = ticker.history(start=start_date, end=end_date)
                
                # Lưu dữ liệu vào database
                for index, row in df.iterrows():
                    historical_data = HistoricalData.objects.create(
                        stock=stock,
                        date=index.date(),
                        open_price=float(row['Open']),
                        high_price=float(row['High']),
                        low_price=float(row['Low']),
                        close_price=float(row['Close']),
                        volume=int(row['Volume'])
                    )
                
                # Lấy lại dữ liệu từ database
                historical_data = HistoricalData.objects.filter(
                    stock=stock
                ).order_by('-date')[:days]
            
            return [
                {
                    'date': data.date.strftime('%Y-%m-%d'),
                    'open': float(data.open_price),
                    'high': float(data.high_price),
                    'low': float(data.low_price),
                    'close': float(data.close_price),
                    'volume': int(data.volume),
                    'change': ((data.close_price - data.open_price) / data.open_price) * 100
                }
                for data in historical_data
            ]
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return []

    # Bạn có thể thêm các phương thức khác nếu cần
