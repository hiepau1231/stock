# apps/mock_api/views.py
from django.http import JsonResponse

def mock_stock_data(request):
    """
    Returns mock stock data.
    """
    data = {
        "stocks": [
            {"id": 1, "symbol": "AAPL", "name": "Apple Inc.", "latest_price": 150.00, "last_updated": "2023-10-01T12:00:00Z"},
            {"id": 2, "symbol": "GOOGL", "name": "Alphabet Inc.", "latest_price": 2750.00, "last_updated": "2023-10-01T12:05:00Z"},
            {"id": 3, "symbol": "AMZN", "name": "Amazon.com, Inc.", "latest_price": 3400.00, "last_updated": "2023-10-01T12:10:00Z"},
        ]
    }
    return JsonResponse(data)
