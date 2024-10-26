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

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    def get_stock_data(self, symbol, start_date=None, end_date=None):
        """Get stock data from yfinance"""
        try:
            logger.info(f"Getting data for {symbol}")
            ticker = yf.Ticker(f"{symbol}.VN")
            today_data = ticker.history(period='1d')
            logger.info(f"Today's data: {today_data}")
            
            if not today_data.empty:
                current_price = float(today_data['Close'].iloc[-1])
                logger.info(f"Current price from history: {current_price}")
            else:
                info = ticker.info
                logger.info(f"Info data: {info}")
                current_price = info.get('regularMarketPrice', 0)
                logger.info(f"Current price from info: {current_price}")
            
            # Xử lý NaN values
            current_price = 0 if pd.isna(current_price) else float(current_price)
            change = 0 if pd.isna(change) else float(change)
            percent_change = 0 if pd.isna(percent_change) else float(percent_change)
            volume = 0 if pd.isna(volume) else int(volume)

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
            return None

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
            # Lấy dữ liệu từ MarketIndex
            indices = MarketIndex.objects.all()
            market_data = []
            
            for index in indices:
                market_data.append({
                    'symbol': index.name,
                    'price': float(index.value),
                    'change': index.change,
                })
            
            # Thêm thống kê thị trường
            total_stocks = Stock.objects.count()
            up_stocks = Stock.objects.filter(percent_change__gt=0).count()
            down_stocks = Stock.objects.filter(percent_change__lt=0).count()
            
            market_stats = {
                'total_stocks': total_stocks,
                'up_stocks': up_stocks,
                'down_stocks': down_stocks,
                'unchanged_stocks': total_stocks - up_stocks - down_stocks,
                'total_value': Stock.objects.aggregate(
                    total=models.Sum('market_cap')
                )['total'] or 0
            }
            
            return {
                'indices': market_data,
                'stats': market_stats
            }
        except Exception as e:
            logger.error(f"Error getting market overview: {str(e)}")
            return None

    def get_top_movers(self, limit=5):
        """Lấy top cổ phiếu tăng/giảm mạnh nhất"""
        try:
            stocks = Stock.objects.all()
            
            # Lọc và sắp xếp theo phần trăm thay đổi
            gainers = sorted(
                [s for s in stocks if s.percent_change is not None and s.percent_change > 0],
                key=lambda x: x.percent_change,
                reverse=True
            )[:limit]
            
            losers = sorted(
                [s for s in stocks if s.percent_change is not None and s.percent_change < 0],
                key=lambda x: x.percent_change
            )[:limit]
            
            return {
                'top_gainers': [
                    {
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'price': stock.current_price,
                        'change': stock.change,
                        'change_percent': stock.percent_change,
                        'volume': stock.volume
                    } for stock in gainers
                ],
                'top_losers': [
                    {
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'price': stock.current_price,
                        'change': stock.change,
                        'change_percent': stock.percent_change,
                        'volume': stock.volume
                    } for stock in losers
                ]
            }
        except Exception as e:
            logger.error(f"Error getting top movers: {str(e)}")
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
        # Lấy dữ liệu benchmark
        benchmark_data = self.get_benchmark_data(
            symbol=portfolio.benchmark_symbol,
            start_date=portfolio.created_at
        )
        
        # Tính toán return của danh mục
        portfolio_return = (portfolio.current_value - portfolio.initial_value) / portfolio.initial_value
        
        # Tính toán return của benchmark
        if benchmark_data is not None and not benchmark_data.empty:
            benchmark_return = (benchmark_data['Close'][-1] - benchmark_data['Close'][0]) / benchmark_data['Close'][0]
        else:
            benchmark_return = 0
            
        return {
            'portfolio_return': portfolio_return,
            'benchmark_return': benchmark_return,
            'alpha': portfolio_return - benchmark_return
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

    # Bạn có thể thêm các phương thức khác nếu cần







