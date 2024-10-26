import logging
from django.core.cache import cache
from .stock_service import StockService
import pandas as pd
import numpy as np
from ..models import Stock, StockPrice
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.stock_service = StockService()
        self.cache_timeout = 604800  # 1 tuần

    def get_top_recommendations(self, limit=5):
        """Lấy top cổ phiếu được khuyến nghị"""
        try:
            cache_key = 'top_recommendations'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            recommendations = []
            stocks = Stock.objects.select_related('industry').all()

            for stock in stocks:
                try:
                    score = 0
                    reasons = []

                    # Lấy dữ liệu giá 30 ngày gần nhất
                    prices = StockPrice.objects.filter(
                        stock=stock
                    ).order_by('-date')[:30]

                    if prices.exists():
                        prices_list = list(prices)
                        
                        # Tính MA20
                        close_prices = [float(p.close_price) for p in prices_list[:20]]
                        if len(close_prices) >= 20:
                            ma20 = sum(close_prices) / 20
                            current_price = float(prices_list[0].close_price)
                            
                            # Kiểm tra giá trên MA20
                            if current_price > ma20:
                                score += 10
                                reasons.append("Giá trên MA20")

                        # Kiểm tra volume
                        volumes = [p.volume for p in prices_list[:5]]
                        if len(volumes) >= 5:
                            avg_volume = sum(volumes) / 5
                            if prices_list[0].volume > avg_volume * 1.5:  # Volume tăng 50%
                                score += 5
                                reasons.append("Khối lượng giao dịch tăng mạnh")

                        # Kiểm tra xu hướng giá
                        if len(prices_list) >= 5:
                            price_5d_ago = float(prices_list[4].close_price)
                            price_change = ((current_price - price_5d_ago) / price_5d_ago) * 100
                            if price_change > 5:  # Tăng trên 5%
                                score += 5
                                reasons.append(f"Tăng {price_change:.1f}% trong 5 ngày")

                        # Kiểm tra RSI
                        if len(close_prices) >= 14:
                            delta = pd.Series(close_prices).diff()
                            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                            rs = gain / loss
                            rsi = 100 - (100 / (1 + rs.iloc[-1]))
                            
                            if 30 <= rsi <= 70:
                                score += 5
                                reasons.append(f"RSI = {rsi:.1f} (vùng an toàn)")

                    # Thêm điểm cho các cổ phiếu blue-chip
                    if stock.symbol in ['VIC', 'VHM', 'VCB', 'BID', 'CTG', 'HPG', 'MSN', 'VNM', 'FPT', 'MWG']:
                        score += 10
                        reasons.append("Blue-chip")

                    if score >= 15:  # Chỉ lấy các cổ phiếu có điểm cao
                        recommendations.append({
                            'symbol': stock.symbol,
                            'name': stock.name,
                            'industry': stock.industry.name if stock.industry else 'N/A',
                            'current_price': stock.current_price,
                            'change_percent': stock.percent_change,
                            'score': score,
                            'reasons': reasons
                        })

                except Exception as e:
                    logger.error(f"Error analyzing stock {stock.symbol}: {str(e)}")
                    continue

            # Sắp xếp theo điểm và lấy top N
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            result = recommendations[:limit]
            
            # Cache kết quả
            cache.set(cache_key, result, self.cache_timeout)
            return result

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []

    def get_recommendation_details(self, symbol):
        """Lấy chi tiết khuyến nghị cho một mã cổ phiếu"""
        try:
            stock = Stock.objects.get(symbol=symbol)
            prices = StockPrice.objects.filter(stock=stock).order_by('-date')[:60]
            
            if not prices.exists():
                return None

            prices_df = pd.DataFrame(list(prices.values()))
            
            # Tính các chỉ báo kỹ thuật
            close_prices = prices_df['close_price'].astype(float)
            
            # MA20
            ma20 = close_prices.rolling(window=20).mean().iloc[-1]
            current_price = float(close_prices.iloc[-1])
            
            # RSI
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # Bollinger Bands
            std = close_prices.rolling(window=20).std()
            upper_band = ma20 + (std.iloc[-1] * 2)
            lower_band = ma20 - (std.iloc[-1] * 2)
            
            # Đánh giá chi tiết
            analysis = {
                'technical': {
                    'trend': 'Tăng' if current_price > ma20 else 'Giảm',
                    'rsi': float(rsi),
                    'ma20': float(ma20),
                    'upper_band': float(upper_band),
                    'lower_band': float(lower_band)
                },
                'recommendation': {
                    'action': self._get_action(current_price, ma20, rsi, upper_band, lower_band),
                    'target_price': round(current_price * 1.1, 2),
                    'stop_loss': round(current_price * 0.95, 2),
                    'reasons': self._get_reasons(current_price, ma20, rsi, upper_band, lower_band)
                }
            }
            
            return analysis

        except Exception as e:
            logger.error(f"Error getting recommendation details for {symbol}: {str(e)}")
            return None

    def _get_action(self, price, ma20, rsi, upper_band, lower_band):
        """Xác định hành động dựa trên các chỉ báo"""
        if price > ma20 and rsi < 70:
            return 'Mua'
        elif price < ma20 and rsi > 30:
            return 'Bán'
        elif price > upper_band and rsi > 70:
            return 'Chốt lời'
        elif price < lower_band and rsi < 30:
            return 'Tích lũy'
        else:
            return 'Nắm giữ'

    def _get_reasons(self, price, ma20, rsi, upper_band, lower_band):
        """Phân tích lý do khuyến nghị"""
        reasons = []
        if price > ma20:
            reasons.append("Giá trên MA20, xu hướng tăng")
        else:
            reasons.append("Giá dưới MA20, xu hướng giảm")

        if rsi < 30:
            reasons.append("RSI dưới 30, cổ phiếu oversold")
        elif rsi > 70:
            reasons.append("RSI trên 70, cổ phiếu overbought")
        else:
            reasons.append(f"RSI = {rsi:.1f}, vùng an toàn")

        if price > upper_band:
            reasons.append("Giá trên Bollinger Band trên, có thể điều chỉnh")
        elif price < lower_band:
            reasons.append("Giá dưới Bollinger Band dưới, có thể phục hồi")

        return reasons
