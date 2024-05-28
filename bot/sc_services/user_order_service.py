import threading
from coinbase.websocket import WSClient
from bot.keys import api_key, api_secret
from bot.sc_types import *
from bot.sc_services import *
from bot.other import *


class UserOrdersService(SingletonBase, WSClient):
    def __init__(self, on_message) -> None:
        super().__init__(
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
            self.open()
            self.subscribe([], ["user", "heartbeats"])
            self.run_forever_with_exception_check()
        except Exception as e:
            print(f"ORDER_SERVICE error: {e}")
        finally:
            self.close()

    def on_open(self) -> None:
        print("WebSocket is now open!")
        self.reconnect_attempts = 0

    def on_close(self) -> None:
        print("WebSocket closed")
