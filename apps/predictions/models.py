from django.db import models
from django.utils import timezone

class StockPrediction(models.Model):
    symbol = models.CharField(max_length=10)
    predicted_price = models.FloatField()
    prediction_date = models.DateTimeField()
    confidence = models.FloatField()
    model_version = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-prediction_date']
        
    def __str__(self):
        return f"{self.symbol} - {self.prediction_date}"

class PredictionModel(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    description = models.TextField()
    parameters = models.JSONField()
    accuracy = models.FloatField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - v{self.version}"
