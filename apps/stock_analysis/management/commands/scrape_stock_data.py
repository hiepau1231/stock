from django.core.management.base import BaseCommand
from apps.stock_analysis.web_scraping_script import scrape_stock_data
from apps.stock_analysis.models import Stock

class Command(BaseCommand):
    help = 'Scrapes stock data and stores it in the database'

    def add_arguments(self, parser):
        parser.add_argument('symbols', nargs='*', type=str, help='Stock symbols to scrape')

    def handle(self, *args, **options):
        symbols = options['symbols']
        if not symbols:
            symbols = Stock.objects.values_list('symbol', flat=True)

        for symbol in symbols:
            self.stdout.write(f"Scraping data for {symbol}...")
            scrape_stock_data(symbol)
            self.stdout.write(self.style.SUCCESS(f'Successfully scraped and stored data for {symbol}'))
