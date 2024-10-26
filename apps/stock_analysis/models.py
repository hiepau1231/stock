from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class MarketIndex(models.Model):
    name = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    change = models.CharField(max_length=20)  # Ví dụ: "+1.2%" hoặc "-0.5%"
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.name} - {self.value}"

class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Industries"

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    change = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    percent_change = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    volume = models.BigIntegerField(null=True, default=0)
    market_cap = models.BigIntegerField(null=True, default=0)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    eps = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.symbol} - {self.name or 'N/A'}"

    def get_absolute_url(self):
        return reverse('stock_analysis:stock_detail', kwargs={'symbol': self.symbol})

    def update_price(self, price, change, percent_change):
        self.current_price = price
        self.change = change
        self.percent_change = percent_change
        self.save()

class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('stock', 'date')
        indexes = [
            models.Index(fields=['stock', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.stock.symbol} - {self.date}"

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stocks = models.ManyToManyField(Stock)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Watchlist của {self.user.username}"

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
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    benchmark_symbol = models.CharField(max_length=10, default='^VNINDEX')
    initial_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']

class PortfolioItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.portfolio.name} - {self.stock.symbol}"

    class Meta:
        unique_together = ('portfolio', 'stock')

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
    ALERT_TYPES = [
        ('above', 'Price Above'),
        ('below', 'Price Below'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES)
    price_threshold = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock.symbol} - {self.alert_type} {self.price_threshold}"

class StockFundamental(models.Model):
    stock = models.OneToOneField(Stock, on_delete=models.CASCADE)
    eps = models.FloatField(null=True)
    eps_diluted = models.FloatField(null=True)
    roe = models.FloatField(null=True)
    roa = models.FloatField(null=True)
    pb_ratio = models.FloatField(null=True)
    beta = models.FloatField(null=True)

class PortfolioTransaction(models.Model):
    """Model lưu lịch sử giao dịch"""
    TRANSACTION_TYPES = [
        ('BUY', 'Mua vào'),
        ('SELL', 'Bán ra')
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Thêm max_digits và decimal_places
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.stock.symbol} at {self.price}"
    
    @property
    def total_value(self):
        return self.quantity * self.price
