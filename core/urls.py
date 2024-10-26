# -*- encoding: utf-8 -*-







"""







Copyright (c) 2019 - present AppSeed.us







"""















from django.contrib import admin







from django.urls import path, include







from django.conf import settings







from django.conf.urls.static import static















urlpatterns = [







    path('admin/', admin.site.urls),          # Django admin route







    path("", include("apps.home.urls")),             # UI Kits Html files







    path("auth/", include("apps.authentication.urls")), # Auth routes with 'auth/' prefix







    path('stock/', include('apps.stock_analysis.urls', namespace='stock_analysis')),







]















if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
