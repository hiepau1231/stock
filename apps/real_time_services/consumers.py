from channels.generic.websocket import AsyncWebsocketConsumer
import json

class StockDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("stock_data", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("stock_data", self.channel_name)

    async def send_stock_data(self, event):
        stock_data = event['data']
        await self.send(text_data=json.dumps(stock_data))
