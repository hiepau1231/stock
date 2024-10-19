from django.urls import path
from . import views

urlpatterns = [
    # Define your real_time_services URL patterns here
    path('example/', views.example_view, name='example'),
    path('test/', views.test_view, name='test'),
]
