from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockViewSet, mock_stock_data

router = DefaultRouter()
router.register(r'stocks', StockViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mock_stock_data/', mock_stock_data, name='mock_stock_data'),
]
