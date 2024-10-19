import requests
from bs4 import BeautifulSoup
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio
from apps.stock_analysis.models import Stock
from apps.stock_analysis.serializers import StockSerializer
import logging

logger = logging.getLogger(__name__)

async def fetch_stock_data(symbol):
    url = f'https://finance.example.com/stock/{symbol}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find('span', {'class': 'price'})
        if price_element:
            return float(price_element.text)
        else:
            logger.error(f"Price element not found for symbol {symbol}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return None

async def update_stock_prices():
    channel_layer = get_channel_layer()
    symbols = ['AAPL', 'GOOGL', 'MSFT']  # Example symbols

    while True:
        for symbol in symbols:
            try:
                price = await fetch_stock_data(symbol)
                if price is not None:
                    # Update database
                    stock = await Stock.objects.aget(symbol=symbol)
                    stock.latest_price = price
                    await stock.asave()
                    # Send update via WebSocket
                    await dispatch_stock_update(stock)
                else:
                    logger.warning(f"Skipping update for {symbol} due to invalid price data")
            except Exception as e:
                logger.error(f"Error updating stock {symbol}: {e}")
        await asyncio.sleep(60)  # Update every 60 seconds

async def dispatch_stock_update(stock_instance):
    channel_layer = get_channel_layer()
    serializer = StockSerializer(stock_instance)
    try:
        await channel_layer.group_send(
            "stock_data",
            {
                'type': 'send_stock_data',
                'data': serializer.data,
            }
        )
    except Exception as e:
        logger.error(f"Error dispatching stock update: {e}")

async def start_background_tasks():
    asyncio.create_task(update_stock_prices())