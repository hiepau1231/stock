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

    symbol = models.CharField(max_length=10, unique=True)

    company_name = models.CharField(max_length=255, default='')  # Thêm default=''

    exchange = models.CharField(max_length=50, default='HOSE')  # Thêm default='HOSE' hoặc giá trị phù hợp khác

    industry = models.CharField(max_length=255, null=True, blank=True)

    market_cap = models.BigIntegerField(null=True, blank=True)

    volume = models.BigIntegerField(null=True, blank=True)

    

    def __str__(self):

        return f"{self.symbol} - {self.company_name}"



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

    open_price = models.FloatField()

    high_price = models.FloatField()

    low_price = models.FloatField()

    close_price = models.FloatField()

    volume = models.BigIntegerField()

    

    class Meta:

        unique_together = ('stock', 'date')

        

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

    # Add default value for company_name

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

    purchase_price = models.FloatField()

    purchase_date = models.DateField()

    

    def __str__(self):

        return f"{self.portfolio.name} - {self.stock.symbol}"



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



