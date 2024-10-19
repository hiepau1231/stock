from django.shortcuts import render
from django.http import JsonResponse

def example_view(request):
    return JsonResponse({'message': 'Real-Time Service is working!'})

# Add a new view for testing
def test_view(request):
    return JsonResponse({'message': 'Test view is working!'})
