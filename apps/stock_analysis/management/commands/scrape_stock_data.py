from django.core.management.base import BaseCommand
from apps.stock_analysis.web_scraping_script import scrape_stock_data

class Command(BaseCommand):
    help = 'Scrapes stock data and stores it in the database'

    def handle(self, *args, **options):
        scrape_stock_data()
        self.stdout.write(self.style.SUCCESS('Successfully scraped and stored stock data'))
