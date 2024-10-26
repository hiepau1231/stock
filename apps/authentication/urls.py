# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    path('logout/', views.logout_view, name='logout'),
]
