from django.contrib import admin
from .models import Stock, HistoricalStockData, UserPortfolio, UserStockHolding

admin.site.register(Stock)
admin.site.register(HistoricalStockData)
admin.site.register(UserPortfolio)
admin.site.register(UserStockHolding)