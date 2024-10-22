from django.db import models
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio')
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
