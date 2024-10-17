from rest_framework import serializers
from .models import Prediction

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['id', 'stock', 'predicted_price', 'prediction_date', 'created_at']
        read_only_fields = ['id', 'created_at']
