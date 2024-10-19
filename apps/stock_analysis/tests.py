from django.test import TestCase
from .models import Stock

class StockModelTestCase(TestCase):
    def setUp(self):
        Stock.objects.create(symbol="AAPL", name="Apple Inc.", latest_price=150.00)

    def test_stock_creation(self):
        stock = Stock.objects.get(symbol="AAPL")
        self.assertEqual(stock.name, "Apple Inc.")
        self.assertEqual(stock.latest_price, 150.00)

    def test_stock_str_representation(self):
        stock = Stock.objects.get(symbol="AAPL")
        self.assertEqual(str(stock), "AAPL - Apple Inc.")

    def test_stock_price_update(self):
        stock = Stock.objects.get(symbol="AAPL")
        stock.latest_price = 160.00
        stock.save()
        updated_stock = Stock.objects.get(symbol="AAPL")
        self.assertEqual(updated_stock.latest_price, 160.00)