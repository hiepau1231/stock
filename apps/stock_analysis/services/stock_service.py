import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError
from ..models import Stock, StockPrice, HistoricalData, MarketIndex, Industry
from django.utils import timezone
import numpy as np
from django.db.models import Max, F

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    def get_stock_data(self, symbol, start_date=None, end_date=None):
        """Get stock data from yfinance"""
        try:
            cache_key = f'stock_data_{symbol}'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            ticker = yf.Ticker(f"{symbol}.VN")
            
            try:
                # Lấy dữ liệu gần nhất
                today_data = ticker.history(period='1d')
                if not today_data.empty:
                    current_price = float(today_data['Close'].iloc[-1])
                    open_price = float(today_data['Open'].iloc[-1])
                    change = current_price - open_price
                    percent_change = (change / open_price) * 100 if open_price != 0 else 0
                    volume = int(today_data['Volume'].iloc[-1])
                else:
                    raise ValueError("No data available")
                    
            except Exception as e:
                logger.warning(f"Error getting live data for {symbol}: {str(e)}")
                # Fallback to database
                latest_price = StockPrice.objects.filter(
                    stock__symbol=symbol
                ).order_by('-date').first()
                
                if latest_price:
                    current_price = float(latest_price.close_price)
                    open_price = float(latest_price.open_price)
                    change = current_price - open_price
                    percent_change = (change / open_price) * 100 if open_price != 0 else 0
                    volume = int(latest_price.volume)
                else:
                    current_price = 0
                    change = 0
                    percent_change = 0
                    volume = 0

            stock_data = {
                'symbol': symbol,
                'price': current_price,
                'change': change,
                'change_percent': percent_change,
                'volume': volume
            }

            # Cache data
            cache.set(cache_key, stock_data, self.cache_timeout)
            return stock_data

        except Exception as e:
            logger.error(f"Error in get_stock_data for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'price': 0,
                'change': 0,
                'change_percent': 0,
                'volume': 0
            }

    def get_historical_data(self, symbol, start_date=None, end_date=None):
        """Get historical stock data from yfinance"""
        try:
            ticker = yf.Ticker(f"{symbol}.VN")
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
                
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                # Thử lấy dữ liệu từ database
                historical_prices = StockPrice.objects.filter(
                    stock__symbol=symbol,
                    date__range=[start_date, end_date]
                ).order_by('date')
                
                if historical_prices.exists():
                    data = {
                        'Date': [],
                        'Open': [],
                        'High': [],
                        'Low': [],
                        'Close': [],
                        'Volume': []
                    }
                    
                    for price in historical_prices:
                        data['Date'].append(price.date)
                        data['Open'].append(float(price.open_price))
                        data['High'].append(float(price.high_price))
                        data['Low'].append(float(price.low_price))
                        data['Close'].append(float(price.close_price))
                        data['Volume'].append(int(price.volume))
                    
                    return pd.DataFrame(data)
                
                logger.warning(f"No historical data found for symbol {symbol}")
                return None
                
            # Định dạng lại dữ liệu
            df = df.reset_index()
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None

    def get_market_overview(self):
        """Lấy tổng quan thị trường"""
        try:
            cache_key = 'market_overview'
            data = cache.get(cache_key)
            
            if not data:
                # Dữ liệu mẫu
                data = {
                    'vnindex': 1153.40,
                    'vnindex_change': 1.37,
                    'volume': 543789123,
                    'chart_data': {
                        'labels': ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                        'values': [1050, 1100, 1150, 1200, 1180, 1220, 1240, 1260, 1280]
                    }
                }
                
                try:
                    # Thử lấy dữ liệu thật từ yfinance
                    vnindex = yf.Ticker("^VNINDEX")
                    current_data = vnindex.history(period="1d")
                    historical_data = vnindex.history(period="1y")
                    
                    if not current_data.empty and not historical_data.empty:
                        current_price = current_data['Close'].iloc[-1]
                        open_price = current_data['Open'].iloc[-1]
                        change_percent = ((current_price - open_price) / open_price) * 100
                        
                        data = {
                            'vnindex': round(current_price, 2),
                            'vnindex_change': round(change_percent, 2),
                            'volume': int(current_data['Volume'].iloc[-1]),
                            'chart_data': {
                                'labels': historical_data.index.strftime('%b').tolist(),
                                'values': historical_data['Close'].tolist()
                            }
                        }
                    else:
                        logger.warning("No data found for VN-Index, using default values")
                except Exception as e:
                    logger.error(f"Error getting live market data: {str(e)}")
                    
                # Cache trong 5 phút
                cache.set(cache_key, data, 300)
            
            return data

        except Exception as e:
            logger.error(f"Error getting market overview: {str(e)}")
            return {
                'vnindex': 1153.40,
                'vnindex_change': 1.37,
                'volume': 543789123,
                'chart_data': {
                    'labels': ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                    'values': [1050, 1100, 1150, 1200, 1180, 1220, 1240, 1260, 1280]
                }
            }

    def get_top_gainers(self, limit=5):
        """Lấy danh sách cổ phiếu tăng giá mạnh nhất"""
        cache_key = f'top_gainers_{limit}'
        data = cache.get(cache_key)
        
        if not data:
            # Implement logic to get top gainers
            # This is a simplified example
            data = self._get_stock_changes()
            data = sorted(data, key=lambda x: x['change_percent'], reverse=True)[:limit]
            
            cache.set(cache_key, data, 300)
            
        return data

    def get_top_losers(self, limit=5):
        """Lấy danh sách cổ phiếu giảm giá mạnh nhất"""
        cache_key = f'top_losers_{limit}'
        data = cache.get(cache_key)
        
        if not data:
            # Implement logic to get top losers
            data = self._get_stock_changes()
            data = sorted(data, key=lambda x: x['change_percent'])[:limit]
            
            cache.set(cache_key, data, 300)
            
        return data

    def _get_stock_changes(self):
        """Helper method to get stock price changes"""
        # Danh sách mã cổ phiếu VN30 (ví dụ)
        vn30_symbols = ['VNM.VN', 'VIC.VN', 'VHM.VN', 'HPG.VN', 'MSN.VN']
        results = []
        
        for symbol in vn30_symbols:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1d")  # Thay đổi từ "2d" thành "1d"
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    open_price = hist['Open'].iloc[-1]
                    change_percent = ((current_price - open_price) / open_price) * 100
                    
                    results.append({
                        'symbol': symbol.replace('.VN', ''),
                        'price': round(current_price, 2),
                        'change_percent': round(change_percent, 2)
                    })
                else:
                    logger.warning(f"No data found for {symbol}")
            except Exception as e:
                logger.error(f"Error getting data for {symbol}: {str(e)}")
                
        return results

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

    def get_benchmark_data(self, symbol='^VNINDEX', start_date=None, end_date=None):
        """Lấy dữ liệu benchmark (VN-Index)"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            return hist
        except Exception as e:
            logger.error(f"Error fetching benchmark data: {e}")
            return None
            
    def calculate_portfolio_performance(self, portfolio):
        """Tính toán hiệu suất danh mục so với benchmark"""
        try:
            # Kiểm tra initial_value
            if portfolio.initial_value == 0:
                return {
                    'portfolio_return': 0,
                    'benchmark_return': 0,
                    'alpha': 0,
                    'message': 'Portfolio has no initial value'
                }

            # Lấy dữ liệu benchmark
            try:
                benchmark_data = self.get_benchmark_data(
                    symbol=portfolio.benchmark_symbol,
                    start_date=portfolio.created_at
                )
                
                # Tính toán return của danh mục
                portfolio_return = float((portfolio.current_value - portfolio.initial_value) / portfolio.initial_value) * 100
                
                # Tính toán return của benchmark
                if benchmark_data is not None and not benchmark_data.empty:
                    first_price = float(benchmark_data['Close'].iloc[0])
                    last_price = float(benchmark_data['Close'].iloc[-1])
                    benchmark_return = ((last_price - first_price) / first_price) * 100
                else:
                    benchmark_return = 0
                    
                return {
                    'portfolio_return': round(portfolio_return, 2),
                    'benchmark_return': round(benchmark_return, 2),
                    'alpha': round(portfolio_return - benchmark_return, 2)
                }
                
            except Exception as e:
                logger.error(f"Error calculating benchmark return: {str(e)}")
                return {
                    'portfolio_return': round(portfolio_return, 2),
                    'benchmark_return': 0,
                    'alpha': round(portfolio_return, 2),
                    'error': str(e)
                }
                
        except Exception as e:
            logger.error(f"Error calculating portfolio performance: {str(e)}")
            return {
                'portfolio_return': 0,
                'benchmark_return': 0,
                'alpha': 0,
                'error': str(e)
            }

    def calculate_portfolio_risk(self, portfolio):
        """Tính toán các chỉ số rủi ro cho danh mục"""
        try:
            # Lấy dữ liệu lịch sử của tất cả cổ phiếu trong danh mục
            portfolio_items = portfolio.portfolioitem_set.all()
            stock_data = {}
            weights = {}
            total_value = sum(item.current_value for item in portfolio_items)
            
            for item in portfolio_items:
                # Lấy dữ liệu lịch sử
                hist_data = self.get_stock_historical_data(item.stock.symbol)
                if hist_data:
                    # Tính returns
                    prices = pd.DataFrame(hist_data)['close']
                    returns = prices.pct_change().dropna()
                    stock_data[item.stock.symbol] = returns
                    # Tính trọng số
                    weights[item.stock.symbol] = item.current_value / total_value
            
            if not stock_data:
                return None
            
            # Tạo DataFrame cho returns
            returns_df = pd.DataFrame(stock_data)
            
            # Tính các chỉ số rủi ro
            portfolio_return = sum(weights[symbol] * returns_df[symbol].mean() for symbol in weights)
            portfolio_std = np.sqrt(sum(sum(weights[symbol1] * weights[symbol2] * 
                                          returns_df[symbol1].cov(returns_df[symbol2])
                                          for symbol2 in weights)
                                      for symbol1 in weights))
            
            # Tính Sharpe Ratio (giả sử risk-free rate = 3%)
            risk_free_rate = 0.03
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
            
            # Tính Beta với VN-Index
            benchmark_data = self.get_benchmark_data(
                symbol=portfolio.benchmark_symbol,
                start_date=portfolio.created_at
            )
            if benchmark_data is not None:
                benchmark_returns = benchmark_data['Close'].pct_change().dropna()
                portfolio_returns = sum(weights[symbol] * returns_df[symbol] for symbol in weights)
                beta = portfolio_returns.cov(benchmark_returns) / benchmark_returns.var()
            else:
                beta = None
            
            return {
                'volatility': portfolio_std * np.sqrt(252),  # Annualized volatility
                'sharpe_ratio': sharpe_ratio * np.sqrt(252),  # Annualized Sharpe ratio
                'beta': beta,
                'weights': weights,
                'correlation_matrix': returns_df.corr().to_dict(),
                'var_95': self.calculate_var(returns_df, weights, confidence_level=0.95),
                'max_drawdown': self.calculate_max_drawdown(returns_df, weights)
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {str(e)}")
            return None

    def calculate_var(self, returns_df, weights, confidence_level=0.95):
        """Tính Value at Risk"""
        portfolio_returns = sum(weights[symbol] * returns_df[symbol] for symbol in weights)
        var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
        return abs(var)

    def calculate_max_drawdown(self, returns_df, weights):
        """Tính Maximum Drawdown"""
        portfolio_returns = sum(weights[symbol] * returns_df[symbol] for symbol in weights)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns / rolling_max - 1
        return abs(drawdowns.min())

    def get_industry_overview(self):
        """Lấy tổng quan theo ngành"""
        try:
            industries = Industry.objects.all()
            overview = []
            
            for industry in industries:
                stocks = Stock.objects.filter(industry=industry)
                if stocks.exists():
                    total_market_cap = sum(s.market_cap or 0 for s in stocks)
                    avg_pe = statistics.mean([s.pe_ratio for s in stocks if s.pe_ratio])
                    
                    overview.append({
                        'name': industry.name,
                        'stock_count': stocks.count(),
                        'total_market_cap': total_market_cap,
                        'average_pe': avg_pe,
                        'top_stocks': list(stocks.order_by('-market_cap')[:3].values('symbol', 'name', 'current_price', 'percent_change'))
                    })
            
            return overview
        except Exception as e:
            logger.error(f"Error getting industry overview: {str(e)}")
            return None

    def get_market_news(self, limit=3):
        # Đây là một phiên bản đơn giản với dữ liệu mẫu
        news = [
            {
                'title': 'Thị trường chứng khoán tăng mạnh',
                'summary': 'VN-Index tăng 15 điểm trong phiên giao dịch hôm nay.',
                'source': 'VnExpress',
                'date': timezone.now(),
                'url': 'https://vnexpress.net/kinh-doanh/chung-khoan',
                'image_url': 'https://i1-kinhdoanh.vnecdn.net/2023/09/20/VNI-7293-1695198154.png?w=380&h=228&q=100&dpr=1&fit=crop&s=Swd6JjpStebEzT6WARjLOA'
            },
            {
                'title': 'Cổ phiếu ngân hàng dẫn dắt thị trường',
                'summary': 'Nhóm cổ phiếu ngân hàng tăng mạnh, kéo theo sự tăng điểm của thị trường.',
                'source': 'CafeF',
                'date': timezone.now() - timezone.timedelta(hours=2),
                'url': 'https://cafef.vn/thi-truong-chung-khoan.chn',
                'image_url': 'https://cafefcdn.com/thumb_w/640/203337114487263232/2023/10/13/photo1697185693801-16971856940611735318003.jpg'
            },
            {
                'title': 'Nhà đầu tư nước ngoài mua ròng trở lại',
                'summary': 'Khối ngoại mua ròng hơn 500 tỷ đồng trong phiên giao dịch hôm nay.',
                'source': 'NDH',
                'date': timezone.now() - timezone.timedelta(hours=4),
                'url': 'https://ndh.vn/chung-khoan',
                'image_url': 'https://ndh.vn/wp-content/uploads/2021/03/chung-khoan-viet-nam.jpg'
            }
        ]
        return news[:limit]

    # Bạn có thể thêm các phương thức khác nếu cần


















