from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class MarketIndex(models.Model):
    name = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    change = models.CharField(max_length=20)  # Ví dụ: "+1.2%" hoặc "-0.5%"
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.name} - {self.value}"

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    exchange = models.CharField(max_length=10)
    current_price = models.FloatField(null=True)
    change = models.FloatField(null=True)
    percent_change = models.FloatField(null=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['symbol', 'exchange']),
            models.Index(fields=['updated_at', 'exchange'])
        ]

    def __str__(self):
        return f"{self.symbol} - {self.name}"

    def get_absolute_url(self):
        return reverse('stock_analysis:stock_detail', kwargs={'symbol': self.symbol})

    def update_price(self, price, change, percent_change):
        self.current_price = price
        self.change = change
        self.percent_change = percent_change
        self.save()

class StockData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    change = models.CharField(max_length=20)
    volume = models.BigIntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.stock.code} - {self.price} ({self.timestamp})"

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stocks = models.ManyToManyField(Stock)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Watchlist của {self.user.username}"

class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField()
    open = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    
    class Meta:
        unique_together = ('stock', 'date')
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.stock.symbol} - {self.date}"

class UserPortfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_portfolio')
    stocks = models.ManyToManyField(Stock, through='UserStockHolding')
    # Add default value for company_name
    def __str__(self):
        return f"Portfolio of {self.user.username}"

class UserStockHolding(models.Model):
    portfolio = models.ForeignKey(UserPortfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    average_buy_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('portfolio', 'stock')

    def __str__(self):
        return f"{self.portfolio.user.username} - {self.stock.symbol} ({self.quantity})"

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class PortfolioItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    
    @property
    def current_value(self):
        return self.quantity * self.stock.current_price
    
    @property
    def purchase_value(self):
        return self.quantity * self.purchase_price
    
    @property
    def profit_loss(self):
        return self.current_value - self.purchase_value
    
    @property
    def profit_loss_percentage(self):
        if self.purchase_value == 0:
            return 0
        return (self.profit_loss / self.purchase_value) * 100
    
    class Meta:
        ordering = ['-purchase_date']

class HistoricalData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='historical_data')
    date = models.DateField(db_index=True)
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.IntegerField()

    class Meta:
        unique_together = ('stock', 'date')
        indexes = [
            models.Index(fields=['stock', 'date']),
            models.Index(fields=['date', 'close_price'])
        ]

    def __str__(self):
        return f"{self.stock.symbol} - {self.date}"

class PriceAlert(models.Model):
    ALERT_TYPES = (
        ('above', 'Giá vượt trên'),
        ('below', 'Giá xuống dưới'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES)
    price_threshold = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.get_alert_type_display()} {self.price_threshold}"
