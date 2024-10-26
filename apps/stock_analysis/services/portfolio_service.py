from decimal import Decimal

from django.utils import timezone

from ..models import Portfolio, PortfolioItem, Stock

from .stock_service import StockService

import logging

from django.db.models import Sum



logger = logging.getLogger(__name__)



class PortfolioService:

    def __init__(self):

        self.stock_service = StockService()



    def create_portfolio(self, user, name, description=""):

        """Tạo danh mục đầu tư mới"""

        try:

            portfolio = Portfolio.objects.create(

                user=user,

                name=name,

                description=description,

                initial_value=0,

                current_value=0

            )

            logger.info(f"Created new portfolio: {name} for user {user.username}")

            return portfolio

        except Exception as e:

            logger.error(f"Error creating portfolio: {str(e)}")

            return None



    def add_stock_to_portfolio(self, portfolio, symbol, quantity, purchase_price, purchase_date):

        """Thêm cổ phiếu vào danh mục"""

        try:

            stock = Stock.objects.get(symbol=symbol)

            

            # Tính giá trị hiện tại

            current_price = float(stock.current_price or 0)

            current_value = current_price * quantity

            initial_value = float(purchase_price) * quantity

            profit_loss = current_value - initial_value

            

            # Tạo hoặc cập nhật portfolio item

            portfolio_item, created = PortfolioItem.objects.update_or_create(

                portfolio=portfolio,

                stock=stock,

                defaults={

                    'quantity': quantity,

                    'purchase_price': purchase_price,

                    'purchase_date': purchase_date,

                    'current_price': current_price,

                    'current_value': current_value,

                    'profit_loss': profit_loss

                }

            )

            

            # Cập nhật giá trị danh mục

            self.update_portfolio_value(portfolio)

            

            logger.info(f"Added/Updated {symbol} to portfolio {portfolio.name}")

            return portfolio_item

            

        except Stock.DoesNotExist:

            logger.error(f"Stock {symbol} not found")

            return None

        except Exception as e:

            logger.error(f"Error adding stock to portfolio: {str(e)}")

            return None



    def update_portfolio_value(self, portfolio):

        """Cập nhật giá trị danh mục"""

        try:

            items = PortfolioItem.objects.filter(portfolio=portfolio)

            

            # Tính tổng giá trị ban đầu và hiện tại

            initial_value = sum(float(item.purchase_price * item.quantity) for item in items)

            current_value = sum(float(item.current_price * item.quantity) for item in items)

            

            # Cập nhật portfolio

            portfolio.initial_value = initial_value

            portfolio.current_value = current_value

            portfolio.updated_at = timezone.now()

            portfolio.save()

            

            logger.info(f"Updated portfolio {portfolio.name} values: initial={initial_value}, current={current_value}")

            

        except Exception as e:

            logger.error(f"Error updating portfolio value: {str(e)}")



    def update_portfolio_prices(self, portfolio):

        """Cập nhật giá hiện tại của tất cả cổ phiếu trong danh mục"""

        try:

            items = PortfolioItem.objects.filter(portfolio=portfolio)

            for item in items:

                stock_data = self.stock_service.get_stock_data(item.stock.symbol)

                if stock_data:

                    item.current_price = stock_data['price']

                    item.current_value = item.current_price * item.quantity

                    item.profit_loss = item.current_value - (item.purchase_price * item.quantity)

                    item.save()

            

            # Cập nhật tổng giá trị danh mục

            self.update_portfolio_value(portfolio)

            logger.info(f"Updated all stock prices in portfolio {portfolio.name}")

            

        except Exception as e:

            logger.error(f"Error updating portfolio prices: {str(e)}")



    def get_portfolio_summary(self, portfolio):

        """Lấy tổng quan về danh mục"""

        try:

            items = PortfolioItem.objects.filter(portfolio=portfolio)

            total_value = sum(item.current_value for item in items)

            

            # Tính phân bổ theo ngành

            industry_allocation = {}

            for item in items:

                industry = item.stock.industry.name if item.stock.industry else 'Khác'

                value = float(item.current_value)

                if industry in industry_allocation:

                    industry_allocation[industry] += value

                else:

                    industry_allocation[industry] = value

            

            # Chuyển đổi giá trị thành phần trăm

            for industry in industry_allocation:

                industry_allocation[industry] = (industry_allocation[industry] / total_value) * 100

            

            return {

                'total_value': total_value,

                'total_profit_loss': sum(item.profit_loss for item in items),

                'stock_count': items.count(),

                'industry_allocation': industry_allocation,

                'performance': self.stock_service.calculate_portfolio_performance(portfolio),

                'risk_metrics': self.stock_service.calculate_portfolio_risk(portfolio)

            }

            

        except Exception as e:

            logger.error(f"Error getting portfolio summary: {str(e)}")

            return None



    def get_user_portfolios(self, user):

        """Lấy danh sách danh mục của user"""

        return Portfolio.objects.filter(user=user)



    def get_portfolio_performance(self, user):

        """Lấy dữ liệu hiệu suất danh mục"""

        # Implement logic to calculate portfolio performance over time

        # This is a simplified example

        return {

            'dates': ['2024-01', '2024-02', '2024-03'],

            'values': [1000, 1100, 1150]

        }



