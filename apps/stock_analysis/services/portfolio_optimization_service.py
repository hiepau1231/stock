import logging
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from .stock_service import StockService
from ..models import StockPrice

logger = logging.getLogger(__name__)

class PortfolioOptimizationService:
    def __init__(self):
        self.stock_service = StockService()

    def optimize_portfolio(self, portfolio, risk_tolerance='moderate'):
        """Tối ưu hóa danh mục dựa trên Modern Portfolio Theory"""
        try:
            # Lấy danh sách cổ phiếu trong danh mục
            portfolio_items = portfolio.portfolioitem_set.all()
            symbols = [item.stock.symbol for item in portfolio_items]
            
            if not symbols:
                return {
                    'error': 'Portfolio is empty',
                    'message': 'Không có cổ phiếu trong danh mục'
                }

            # Lấy dữ liệu lịch sử
            returns_data = self._get_historical_returns(symbols)
            if returns_data is None:
                return {
                    'error': 'Insufficient data',
                    'message': 'Không đủ dữ liệu lịch sử để tối ưu hóa'
                }

            # Tính toán ma trận hiệp phương sai và vector kỳ vọng lợi nhuận
            returns_mean = returns_data.mean()
            returns_cov = returns_data.cov()

            # Thiết lập tham số tối ưu hóa dựa trên mức chấp nhận rủi ro
            risk_params = {
                'conservative': {'target_return': 0.10, 'max_weight': 0.3},
                'moderate': {'target_return': 0.15, 'max_weight': 0.4},
                'aggressive': {'target_return': 0.20, 'max_weight': 0.5}
            }
            params = risk_params.get(risk_tolerance, risk_params['moderate'])

            # Tối ưu hóa
            num_assets = len(symbols)
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Tổng trọng số = 1
                {'type': 'ineq', 'fun': lambda x: x - 0.05},     # Trọng số tối thiểu 5%
                {'type': 'ineq', 'fun': lambda x: params['max_weight'] - x}  # Trọng số tối đa
            ]
            
            bounds = tuple((0.05, params['max_weight']) for _ in range(num_assets))
            
            # Hàm mục tiêu: Minimize risk (variance)
            def objective(weights):
                portfolio_std = np.sqrt(np.dot(weights.T, np.dot(returns_cov, weights)))
                return portfolio_std

            # Initial guess: equal weights
            initial_weights = np.array([1/num_assets] * num_assets)
            
            # Tối ưu hóa
            result = minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )

            if not result.success:
                return {
                    'error': 'Optimization failed',
                    'message': 'Không thể tìm được giải pháp tối ưu'
                }

            # Tính toán các chỉ số của danh mục tối ưu
            optimized_weights = result.x
            portfolio_return = np.sum(returns_mean * optimized_weights)
            portfolio_risk = np.sqrt(np.dot(optimized_weights.T, np.dot(returns_cov, optimized_weights)))
            
            # Tạo kết quả
            recommendations = []
            current_weights = self._get_current_weights(portfolio_items)
            
            for i, symbol in enumerate(symbols):
                current_weight = current_weights.get(symbol, 0)
                target_weight = optimized_weights[i]
                
                if abs(target_weight - current_weight) > 0.05:  # Chỉ đề xuất khi chênh lệch > 5%
                    action = 'Tăng' if target_weight > current_weight else 'Giảm'
                    change = abs(target_weight - current_weight) * 100
                    
                    recommendations.append({
                        'symbol': symbol,
                        'current_weight': current_weight * 100,
                        'target_weight': target_weight * 100,
                        'action': action,
                        'change': change
                    })

            return {
                'success': True,
                'portfolio_return': portfolio_return * 100,
                'portfolio_risk': portfolio_risk * 100,
                'sharpe_ratio': (portfolio_return - 0.05) / portfolio_risk,  # Assuming risk-free rate = 5%
                'recommendations': recommendations
            }

        except Exception as e:
            logger.error(f"Error optimizing portfolio: {str(e)}")
            return {
                'error': 'Optimization error',
                'message': str(e)
            }

    def _get_historical_returns(self, symbols, days=252):
        """Lấy dữ liệu lợi nhuận lịch sử"""
        try:
            returns_data = {}
            
            for symbol in symbols:
                prices = StockPrice.objects.filter(
                    stock__symbol=symbol
                ).order_by('-date')[:days]
                
                if prices.count() < days/2:  # Yêu cầu ít nhất 50% số ngày
                    return None
                
                # Tính lợi nhuận hàng ngày
                prices_list = list(prices.values_list('close_price', flat=True))
                prices_list.reverse()
                returns = pd.Series(prices_list).pct_change().dropna()
                returns_data[symbol] = returns
            
            return pd.DataFrame(returns_data)
            
        except Exception as e:
            logger.error(f"Error getting historical returns: {str(e)}")
            return None

    def _get_current_weights(self, portfolio_items):
        """Tính trọng số hiện tại của danh mục"""
        total_value = sum(item.current_value for item in portfolio_items)
        if total_value == 0:
            return {}
            
        weights = {}
        for item in portfolio_items:
            weights[item.stock.symbol] = float(item.current_value) / total_value
            
        return weights
