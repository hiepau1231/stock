from django.core.management.base import BaseCommand
from apps.stock_analysis.models import Portfolio
from apps.stock_analysis.services.stock_service import StockService

class Command(BaseCommand):
    help = 'Cập nhật dữ liệu benchmark cho tất cả portfolio'

    def handle(self, *args, **kwargs):
        stock_service = StockService()
        portfolios = Portfolio.objects.all()
        
        for portfolio in portfolios:
            try:
                benchmark_data = stock_service.get_benchmark_data(
                    symbol=portfolio.benchmark_symbol,
                    start_date=portfolio.created_at
                )
                
                if benchmark_data is not None and not benchmark_data.empty:
                    portfolio.benchmark_start_value = benchmark_data['Close'][0]
                    portfolio.benchmark_current_value = benchmark_data['Close'][-1]
                    portfolio.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully updated benchmark data for portfolio {portfolio.name}'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error updating benchmark data for portfolio {portfolio.name}: {str(e)}'
                    )
                )
