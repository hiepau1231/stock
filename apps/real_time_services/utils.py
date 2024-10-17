import requests
from bs4 import BeautifulSoup
from .consumers import StockDataConsumer
from channels.layers import get_channel_layer
import asyncio
from apps.stock_analysis.models import Stock

async def fetch_stock_data(symbol):
    url = f'https://finance.example.com/stock/{symbol}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    price = soup.find('span', {'class': 'price'}).text
    return float(price)

async def update_stock_prices():
    channel_layer = get_channel_layer()
    symbols = ['AAPL', 'GOOGL', 'MSFT']  # Example symbols

    while True:
        for symbol in symbols:
            price = await fetch_stock_data(symbol)
            # Update database
            # Assuming Stock model is imported and available
            stock = await Stock.objects.aget(symbol=symbol)
            stock.latest_price = price
            await stock.asave()
            # Send update via WebSocket
            await channel_layer.group_send(
                "stock_data",
                {
                    'type': 'send_stock_data',
                    'data': {
                        'symbol': symbol,
                        'latest_price': price
                    }
                }
            )
        await asyncio.sleep(60)  # Update every 60 seconds
# Existing utils...
import asyncio

async def start_background_tasks():
    asyncio.create_task(update_stock_prices())
