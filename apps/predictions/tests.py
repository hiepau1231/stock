from django.test import TestCase
from django.utils import timezone
from datetime import datetime
from .models import StockPrediction, PredictionModel

class PredictionModelTest(TestCase):
    def setUp(self):
        self.model = PredictionModel.objects.create(
            name='LSTM Model',
            version='1.0',
            description='Long Short-Term Memory model for stock prediction',
            parameters={'layers': 3, 'units': 50},
            accuracy=0.85
        )
        
    def test_model_creation(self):
        self.assertEqual(self.model.name, 'LSTM Model')
        self.assertEqual(self.model.version, '1.0')
        self.assertEqual(self.model.accuracy, 0.85)

class StockPredictionTest(TestCase):
    def setUp(self):
        self.prediction = StockPrediction.objects.create(
            symbol='VNM',
            predicted_price=100.0,
            prediction_date=timezone.now(),
            confidence=0.85,
            model_version='v1.0'
        )
    
    def test_prediction_creation(self):
        self.assertEqual(self.prediction.symbol, 'VNM')
        self.assertEqual(self.prediction.predicted_price, 100.0)
        self.assertEqual(self.prediction.confidence, 0.85)
        self.assertEqual(self.prediction.model_version, 'v1.0')
