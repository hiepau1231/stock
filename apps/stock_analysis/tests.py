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

import numpy as np

from django.utils import timezone  # Sửa lại import này

from datetime import timedelta  # Chỉ import timedelta từ datetime



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

class TechnicalIndicatorTestCase(TestCase):
    def setUp(self):
        # Tạo user test và login
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        self.client.login(username='testuser', password='12345')
        
        # Tạo dữ liệu mẫu cho test
        self.stock = Stock.objects.create(
            symbol="VNM",
            name="Vinamilk",
            current_price=100.0,
            change=1.0,
            percent_change=1.0
        )
        
        # Tạo dữ liệu lịch sử
        dates = pd.date_range(end='2024-01-01', periods=50)
        for i, date in enumerate(dates):
            HistoricalData.objects.create(
                stock=self.stock,
                date=date.date(),
                open_price=100 + i,
                high_price=105 + i,
                low_price=95 + i,
                close_price=102 + i,
                volume=1000000 + i * 1000
            )

    def test_rsi_calculation(self):
        response = self.client.get(
            reverse('stock_analysis:technical_indicators', args=['VNM']),
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        
        # Kiểm tra các trường trong response
        self.assertIn('rsi', data)
        self.assertIn('macd', data)
        self.assertIn('signal', data)
        self.assertIn('bb_upper', data)
        self.assertIn('bb_middle', data)
        self.assertIn('bb_lower', data)
        
        # Kiểm tra giá trị RSI nằm trong khoảng hợp lý
        self.assertTrue(0 <= data['rsi'] <= 100)

    def test_macd_calculation(self):
        response = self.client.get(
            reverse('stock_analysis:technical_indicators', args=['VNM']),
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        
        # MACD line nên khác signal line
        self.assertNotEqual(data['macd'], data['signal'])

    def test_bollinger_bands(self):
        response = self.client.get(
            reverse('stock_analysis:technical_indicators', args=['VNM']),
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        
        # Upper band phải lớn hơn middle band
        self.assertGreater(data['bb_upper'], data['bb_middle'])
        # Lower band phải nhỏ hơn middle band
        self.assertLess(data['bb_lower'], data['bb_middle'])

    def test_invalid_stock_symbol(self):
        response = self.client.get(
            reverse('stock_analysis:technical_indicators', args=['INVALID']),
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'application/json')

    @patch('pandas.DataFrame.rolling')
    def test_rsi_calculation_with_mock(self, mock_rolling):
        # Mock rolling window calculations
        mock_rolling.return_value.mean.return_value = pd.Series([0.5, 0.6, 0.7])
        
        response = self.client.get(
            reverse('stock_analysis:technical_indicators', args=['VNM']),
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

class StockDetailViewTest(TestCase):
    def setUp(self):
        # Tạo user test và login
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        self.client.login(username='testuser', password='12345')
        
        # Tạo dữ liệu mẫu với giá trị lớn để test intcomma
        self.stock = Stock.objects.create(
            symbol="VNM",
            name="Vinamilk",
            current_price=100000.0,  # Giá trị lớn để test intcomma
            change=1000.0,
            percent_change=1.0
        )
        
        # Tạo dữ liệu lịch sử
        current_date = timezone.now()  # Sử dụng django.utils.timezone
        for i in range(5):
            HistoricalData.objects.create(
                stock=self.stock,
                date=(current_date - timedelta(days=i)).date(),
                open_price=100000 + i * 1000,
                high_price=105000 + i * 1000,
                low_price=95000 + i * 1000,
                close_price=102000 + i * 1000,
                volume=1000000 + i * 10000
            )
        
        self.url = reverse('stock_analysis:stock_detail', args=['VNM'])

    def test_stock_detail_view_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stock_analysis/stock_detail.html')

    def test_stock_detail_context(self):
        response = self.client.get(self.url)
        self.assertIn('stock', response.context)
        self.assertIn('historical_data', response.context)
        
        # Test số được format đúng (thêm dấu phẩy ngăn cách hàng nghìn)
        content = response.content.decode()
        
        # Test giá hiện tại
        current_price = response.context['stock'].current_price
        formatted_price = "{:,.2f}".format(current_price)  # Format số theo định dạng Python chuẩn
        self.assertIn(formatted_price, content)
        
        # Test dữ liệu lịch sử
        historical_data = response.context['historical_data']
        if historical_data:
            first_record = historical_data[0]
            # Kiểm tra các giá trong dữ liệu lịch sử
            for price in [
                first_record.open_price,
                first_record.high_price,
                first_record.low_price,
                first_record.close_price
            ]:
                formatted_price = "{:,.2f}".format(price)
                self.assertIn(formatted_price, content)
            
            # Kiểm tra volume
            formatted_volume = "{:,}".format(first_record.volume)
            self.assertIn(formatted_volume, content)

    def test_stock_detail_technical_indicators_load(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'technical_indicators')
        self.assertContains(response, 'tradingview_chart')
        
    def test_historical_data_display(self):
        response = self.client.get(self.url)
        # Kiểm tra dữ liệu lịch sử được hiển thị
        self.assertContains(response, 'Lịch sử giao dịch')
        self.assertContains(response, '1,000,000')  # Test volume formatting

