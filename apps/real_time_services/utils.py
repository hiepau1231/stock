import requests
from bs4 import BeautifulSoup
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.stock_analysis.models import Stock
from apps.stock_analysis.serializers import StockSerializer

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
            stock = await Stock.objects.aget(symbol=symbol)
            stock.latest_price = price
            await stock.asave()
            # Send update via WebSocket
            await dispatch_stock_update(stock)
        await asyncio.sleep(60)  # Update every 60 seconds

def dispatch_stock_update(stock_instance):
    channel_layer = get_channel_layer()
    serializer = StockSerializer(stock_instance)
    async_to_sync(channel_layer.group_send)(
        "stock_data",
        {
            'type': 'send_stock_data',
            'data': serializer.data,
        }
    )

async def start_background_tasks():
    asyncio.create_task(update_stock_prices())
