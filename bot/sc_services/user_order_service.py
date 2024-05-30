import threading
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
        thread = threading.Thread(target=self.run_websocket)
        thread.daemon = True
        thread.start()

    def run_websocket(self):
        try:
            self.ws_client.open()
            self.ws_client.subscribe([], ["user", "heartbeats"])
            self.ws_client.run_forever_with_exception_check()
        except Exception as e:
            LOGGER.info(f"ORDER_SERVICE error: {e}")
        finally:
            self.ws_client.close()

    def on_open(self) -> None:
        LOGGER.info("WebSocket is now open!")
        self.reconnect_attempts = 0

    def on_close(self) -> None:
        LOGGER.info("WebSocket closed")
