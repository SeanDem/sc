import asyncio
from coinbase.websocket import WSClient
from bot.keys import api_key, api_secret
from bot.sc_types import *
from bot.sc_services import *
from bot.other import *


class UserOrdersService(SingletonBase):
    def __init__(self, on_message) -> None:
        self.ws_client = WSClient(
            on_message=on_message,
            api_key=api_key,
            api_secret=api_secret,
            on_open=self.on_open,
            on_close=self.on_close,
        )

    def start(self) -> None:
        task = asyncio.create_task(self.run_websocket())

    async def run_websocket(self) -> None:
        try:
            await self.ws_client.open_async()
            await self.ws_client.subscribe_async([], ["user", "heartbeats"])
            await self.ws_client.run_forever_with_exception_check_async()
        except Exception as e:
            LOGGER.info(f"ORDER_SERVICE error: {e}")

    def on_open(self) -> None:
        LOGGER.info("UserOrders WebSocket is now open!")

    def on_close(self) -> None:
        LOGGER.info("WebSocket closed")
