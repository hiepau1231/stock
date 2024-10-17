from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'latest_price', 'last_updated']
        read_only_fields = ['id', 'last_updated']
