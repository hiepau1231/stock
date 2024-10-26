import logging
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from .stock_service import StockService

logger = logging.getLogger(__name__)

class PortfolioOptimizationService:
    def __init__(self):
        self.stock_service = StockService()

    def get_portfolio_optimization(self, portfolio):
        """Phân tích và đưa ra gợi ý cân bằng danh mục"""
        try:
            # Lấy dữ liệu hiện tại của danh mục
            current_holdings = {}
            returns_data = {}
            
            for item in portfolio.portfolioitem_set.all():
                current_holdings[item.stock.symbol] = {
                    'weight': item.current_value / portfolio.current_value,
                    'quantity': item.quantity
                }
                
                # Lấy dữ liệu lịch sử để tính returns
                hist_data = self.stock_service.get_stock_historical_data(item.stock.symbol)
                if hist_data:
                    prices = pd.DataFrame(hist_data)['close']
                    returns_data[item.stock.symbol] = prices.pct_change().dropna()

            if not returns_data:
                return None

            # Tạo DataFrame cho returns
            returns_df = pd.DataFrame(returns_data)
            
            # Tính toán optimal weights
            optimal_weights = self._calculate_optimal_weights(returns_df)
            
            # Tạo gợi ý điều chỉnh
            recommendations = []
            for symbol in optimal_weights:
                current_weight = current_holdings[symbol]['weight']
                optimal_weight = optimal_weights[symbol]
                diff = optimal_weight - current_weight
                
                if abs(diff) > 0.05:  # Chỉ gợi ý khi chênh lệch > 5%
                    action = 'tăng' if diff > 0 else 'giảm'
                    recommendations.append({
                        'symbol': symbol,
                        'current_weight': current_weight,
                        'optimal_weight': optimal_weight,
                        'action': action,
                        'adjustment': abs(diff),
                        'reason': self._get_adjustment_reason(symbol, diff, returns_df)
                    })

            return {
                'current_weights': current_holdings,
                'optimal_weights': optimal_weights,
                'recommendations': recommendations
            }

        except Exception as e:
            logger.error(f"Error optimizing portfolio: {str(e)}")
            return None

    def _calculate_optimal_weights(self, returns_df):
        """Tính toán trọng số tối ưu sử dụng Modern Portfolio Theory"""
        try:
            # Tính expected returns và covariance matrix
            mu = returns_df.mean()
            cov = returns_df.cov()
            
            # Số lượng cổ phiếu
            n = len(returns_df.columns)
            
            # Hàm mục tiêu: Maximize Sharpe Ratio
            def objective(weights):
                portfolio_return = np.sum(mu * weights)
                portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
                return -portfolio_return/portfolio_std  # Negative vì minimize
            
            # Constraints
            constraints = (
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
            )
            bounds = tuple((0, 1) for _ in range(n))  # 0 <= weight <= 1
            
            # Initial guess: equal weights
            initial_weights = np.array([1/n] * n)
            
            # Optimize
            result = minimize(objective, initial_weights,
                            method='SLSQP',
                            bounds=bounds,
                            constraints=constraints)
            
            # Return as dictionary
            return dict(zip(returns_df.columns, result.x))
            
        except Exception as e:
            logger.error(f"Error calculating optimal weights: {str(e)}")
            return None

    def _get_adjustment_reason(self, symbol, weight_diff, returns_df):
        """Tạo lý do cho gợi ý điều chỉnh"""
        try:
            returns = returns_df[symbol]
            
            if weight_diff > 0:
                if returns.mean() > returns_df.mean().mean():
                    return f"Cổ phiếu {symbol} có hiệu suất tốt hơn trung bình danh mục"
                else:
                    return f"Tăng {symbol} để cân bằng rủi ro danh mục"
            else:
                if returns.std() > returns_df.std().mean():
                    return f"Giảm {symbol} để giảm rủi ro danh mục"
                else:
                    return f"Điều chỉnh {symbol} để tối ưu hiệu suất"
                    
        except Exception as e:
            logger.error(f"Error getting adjustment reason: {str(e)}")
            return "Điều chỉnh để tối ưu danh mục"
