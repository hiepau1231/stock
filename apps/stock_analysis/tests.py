from django.test import TestCase

from django.urls import reverse

from .models import Stock, HistoricalData

from .services.stock_service import StockService

from unittest.mock import patch, Mock, MagicMock

from django.contrib.auth.models import User

from django.test import Client

import unittest

import pandas as pd

import yfinance as yf



class StockModelTestCase(TestCase):

    def setUp(self):

        Stock.objects.create(symbol="AAPL", name="Apple Inc.", current_price=150.00)



    def test_stock_creation(self):

        stock = Stock.objects.get(symbol="AAPL")

        self.assertEqual(stock.name, "Apple Inc.")

        self.assertEqual(stock.current_price, 150.00)



    def test_stock_str_representation(self):

        stock = Stock.objects.get(symbol="AAPL")

        self.assertEqual(str(stock), "AAPL - Apple Inc.")



    def test_stock_price_update(self):

        stock = Stock.objects.get(symbol="AAPL")

        stock.current_price = 160.00

        stock.save()

        updated_stock = Stock.objects.get(symbol="AAPL")

        self.assertEqual(updated_stock.current_price, 160.00)



class StockServiceTestCase(TestCase):

    def setUp(self):
        self.service = StockService()

    @patch('yfinance.Ticker')
    def test_get_stock_data(self, mock_ticker):
        # Tạo mock data cho yfinance
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            'regularMarketPrice': 100,
            'regularMarketChange': 5,
            'regularMarketChangePercent': 0.05
        }
        mock_ticker.return_value = mock_ticker_instance
        
        result = self.service.get_stock_data('VNM')
        self.assertIsNotNone(result)
        self.assertEqual(result['symbol'], 'VNM')
        self.assertEqual(result['price'], 100)

    @patch('yfinance.Ticker')
    def test_get_market_overview(self, mock_ticker):
        # Tạo mock data cho yfinance
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            'regularMarketPrice': 1000,
            'regularMarketChange': 10,
            'regularMarketChangePercent': 0.01
        }
        mock_ticker.return_value = mock_ticker_instance
        
        market_overview = self.service.get_market_overview()
        self.assertEqual(len(market_overview), 4)  # Kiểm tra 4 chỉ số: VNINDEX, VN30, HNX, UPCOM

    @patch('yfinance.Ticker')
    def test_get_historical_data(self, mock_ticker):
        # Tạo mock data cho historical data
        mock_ticker_instance = MagicMock()
        mock_history = pd.DataFrame({
            'Open': [100, 101],
            'High': [102, 103],
            'Low': [98, 99],
            'Close': [101, 102],
            'Volume': [1000, 1100]
        })
        mock_ticker_instance.history.return_value = mock_history
        mock_ticker.return_value = mock_ticker_instance

        result = self.service.get_historical_data('VNM', '2024-01-01', '2024-01-02')
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)

    @patch('requests.get')
    def test_get_stock_list(self, mock_get):
        # Tạo mock data cho web scraping
        mock_response = MagicMock()
        mock_response.text = '''
        <table class="table">
            <tbody>
                <tr>
                    <td>VNM</td>
                    <td>Vinamilk</td>
                    <td>HOSE</td>
                </tr>
            </tbody>
        </table>
        '''
        mock_get.return_value = mock_response

        result = self.service.get_stock_list()
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0]['ticker'], 'VNM')





class ViewsTestCase(TestCase):

    def setUp(self):

        Stock.objects.create(symbol='VNM', name='Vinamilk', exchange='HOSE')

        self.user = User.objects.create_user(username='testuser', password='12345')

        self.client = Client()

        self.client.login(username='testuser', password='12345')



    def test_dashboard_view(self):

        response = self.client.get(reverse('stock_analysis:dashboard'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'stock_analysis/dashboard.html')



    def test_stock_list_view(self):

        response = self.client.get(reverse('stock_analysis:stock_list'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'stock_analysis/stock_list.html')



    def test_stock_detail_view(self):

        response = self.client.get(reverse('stock_analysis:stock_detail', args=['VNM']))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'stock_analysis/stock_detail.html')




# Thêm các test case khác nếu cần




