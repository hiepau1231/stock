from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.stock_analysis.models import Stock, WatchList

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho testing'

    def handle(self, *args, **kwargs):
        try:
            # Tạo một số cổ phiếu mẫu
            stocks = [
                {'symbol': 'VNM', 'name': 'Vinamilk', 'exchange': 'HOSE'},
                {'symbol': 'VIC', 'name': 'Vingroup', 'exchange': 'HOSE'},
                {'symbol': 'FPT', 'name': 'FPT Corp', 'exchange': 'HOSE'},
            ]
            
            for stock_data in stocks:
                Stock.objects.get_or_create(**stock_data)

            # Tạo watchlist cho user đầu tiên
            user = User.objects.first()
            if user:
                watchlist, created = WatchList.objects.get_or_create(user=user)
                for stock in Stock.objects.all():
                    watchlist.stocks.add(stock)

            self.stdout.write(
                self.style.SUCCESS('Successfully created sample data')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample data: {str(e)}')
            )
