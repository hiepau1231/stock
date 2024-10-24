from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class Stock(models.Model):
    id = models.BigAutoField(primary_key=True)
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

class StockPrice(models.Model):
    id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('stock', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.stock.symbol} - {self.date}"

class UserPortfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_portfolio')
    stocks = models.ManyToManyField(Stock, through='UserStockHolding')

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

class StockData(models.Model):
    ticker = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.FloatField()
    close_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    volume = models.IntegerField()

    class Meta:
        unique_together = ('ticker', 'date')

class StockIndex(models.Model):
    name = models.CharField(max_length=50, unique=True)
    value = models.FloatField()
    change = models.FloatField()
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}: {self.value}"

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s portfolio: {self.name}"

class PortfolioItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()

    def __str__(self):
        return f"{self.portfolio.name} - {self.stock.symbol}: {self.quantity}"

class HistoricalData(models.Model):
    stock = models.ForeignKey('Stock', related_name='historical_data', on_delete=models.CASCADE)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()

    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.stock.symbol} - {self.date}"
