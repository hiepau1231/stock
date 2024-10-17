from rest_framework import viewsets
from .models import Prediction
from .serializers import PredictionSerializer
from rest_framework.permissions import IsAuthenticated

class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]
