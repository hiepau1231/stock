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
    HistoricalData
)

@admin.register(MarketIndex)
class MarketIndexAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'change', 'timestamp')
    search_fields = ('name',)
    list_filter = ('timestamp',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name')
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
    list_display = ('stock', 'date', 'open', 'high', 'low', 'close', 'volume')
    list_filter = ('stock', 'date')
    search_fields = ('stock__symbol', 'stock__name')

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
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__username')
    list_filter = ('created_at',)

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'stock', 'quantity', 'purchase_price', 'purchase_date')
    search_fields = ('portfolio__name', 'stock__symbol')
    list_filter = ('purchase_date',)

@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'open_price', 'close_price', 'volume')
    search_fields = ('stock__symbol',)
    list_filter = ('date',)
