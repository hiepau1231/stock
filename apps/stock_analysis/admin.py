from django.contrib import admin
from .models import (
    MarketIndex, 
    Stock, 
    StockData, 
    WatchList, 
    StockPrice,
    UserPortfolio,
    UserStockHolding,
    Portfolio,
    PortfolioItem,
    HistoricalData,
    Industry,
    PriceAlert
)

@admin.register(MarketIndex)
class MarketIndexAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'change', 'timestamp')
    search_fields = ('name',)
    list_filter = ('timestamp',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'industry', 'current_price', 'change', 'percent_change')
    list_filter = ('industry',)
    search_fields = ('symbol', 'name')

@admin.register(StockData)
class StockDataAdmin(admin.ModelAdmin):
    list_display = ('stock', 'price', 'change', 'volume', 'timestamp')
    search_fields = ('stock__symbol',)
    list_filter = ('timestamp',)

@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    filter_horizontal = ('stocks',)
    search_fields = ('user__username',)

@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'open_price', 'close_price', 'volume')
    list_filter = ('date', 'stock')
    search_fields = ('stock__symbol',)
    date_hierarchy = 'date'

@admin.register(UserPortfolio)
class UserPortfolioAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(UserStockHolding)
class UserStockHoldingAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'stock', 'quantity', 'average_buy_price')
    search_fields = ('portfolio__user__username', 'stock__symbol')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'initial_value', 'current_value', 'created_at')
    list_filter = ('user',)
    search_fields = ('name', 'user__username')

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'stock', 'quantity', 'purchase_price', 'current_price', 'profit_loss')
    list_filter = ('portfolio', 'stock')
    search_fields = ('portfolio__name', 'stock__symbol')

@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'open_price', 'close_price', 'volume')
    search_fields = ('stock__symbol',)
    list_filter = ('date',)

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock', 'alert_type', 'price_threshold', 'is_active', 'last_triggered')
    list_filter = ('alert_type', 'is_active', 'stock')
    search_fields = ('user__username', 'stock__symbol')
