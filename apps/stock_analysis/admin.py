from django.contrib import admin
from .models import Stock, StockPrice, StockIndex, UserPortfolio, UserStockHolding

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'sector', 'industry')
    search_fields = ('symbol', 'name')

@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'open_price', 'close_price', 'volume')
    list_filter = ('stock', 'date')
    date_hierarchy = 'date'

@admin.register(StockIndex)
class StockIndexAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'change', 'last_updated')
    list_filter = ('name',)

admin.site.register(UserPortfolio)
admin.site.register(UserStockHolding)
