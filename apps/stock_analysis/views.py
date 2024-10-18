from rest_framework import viewsets
from .models import Stock
from .serializers import StockSerializer
from rest_framework.permissions import IsAuthenticated

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def mock_stock_data(request):
    mock_data = [
        {
            'id': 1,
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'latest_price': 150,
            'last_updated': '2023-10-01'
        },
        # Add more mock stock data as needed
    ]
    return Response(mock_data)
