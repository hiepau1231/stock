from django.contrib import admin
from .models import StockPrediction, PredictionModel

@admin.register(StockPrediction)
class StockPredictionAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'predicted_price', 'prediction_date', 'confidence', 'model_version')
    list_filter = ('symbol', 'model_version', 'prediction_date')
    search_fields = ('symbol',)
    ordering = ('-prediction_date',)

@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'accuracy', 'created_at')
    list_filter = ('name', 'version')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
