from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.stock_analysis.models import Portfolio, Stock, PortfolioItem
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Tạo portfolio mẫu cho testing'

    def handle(self, *args, **kwargs):
        try:
            # Lấy user đầu tiên hoặc superuser
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
                return

            # Tạo portfolio
            portfolio = Portfolio.objects.create(
                user=user,
                name='Danh mục mẫu'
            )

            # Lấy một số cổ phiếu mẫu
            stocks = Stock.objects.all()[:3]
            
            # Thêm cổ phiếu vào portfolio
            for stock in stocks:
                PortfolioItem.objects.create(
                    portfolio=portfolio,
                    stock=stock,
                    quantity=100,
                    purchase_price=stock.current_price or 10000,
                    purchase_date=datetime.now().date()
                )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created sample portfolio for user {user.username}')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample portfolio: {str(e)}')
            )
