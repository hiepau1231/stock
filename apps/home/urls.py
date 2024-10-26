# -*- encoding: utf-8 -*-

"""

Copyright (c) 2019 - present AppSeed.us

"""



from django.urls import path

from . import views



urlpatterns = [

    path('', views.index, name='home'),

    path('introduction/', views.introduction, name='introduction'),

    path('<str:template_name>', views.pages, name='pages'),

    path('map/', views.map_view, name='map'),

    path('profile/', views.profile, name='profile'),

]


