from rest_framework import viewsets
from .models import Stock
from .serializers import StockSerializer
from rest_framework.permissions import IsAuthenticated

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
