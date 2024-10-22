from django.contrib import admin
from .models import Stock, StockPrice, UserPortfolio, UserStockHolding

admin.site.register(Stock)
admin.site.register(StockPrice)
admin.site.register(UserPortfolio)
admin.site.register(UserStockHolding)
