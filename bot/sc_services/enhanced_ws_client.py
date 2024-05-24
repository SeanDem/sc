import time
from coinbase.websocket import WSClient
from bot.keys import api_key, api_secret
from bot.sc_types import *
from bot.sc_services import *
from bot.other.singleton_base import SingletonBase


class EnhancedWSClient(SingletonBase, WSClient):
    def __init__(self, on_message) -> None:
        super().__init__(
            on_message=on_message,
            api_key=api_key,
            api_secret=api_secret,
            on_open=self.on_open,
            on_close=self.on_close,
        )
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    def start(self) -> None:
        try:
            self.open()
            self.subscribe([CurrencyPair.DAI_USDC.value], ["user", "ticker_batch"])
            self.run_forever_with_exception_check()
        except Exception as e:
            print(f"Error in event service: {e}")
        finally:
            self.close()

    def on_open(self) -> None:
        print("WebSocket is now open!")
        self.reconnect_attempts = 0

    def on_close(self) -> None:
        print("WebSocket closed")
        if self.should_reconnect():
            self.attempt_reconnect()
        else:
            print("Maximum reconnect attempts reached, stopping client.")

    def should_reconnect(self) -> bool:
        return self.reconnect_attempts < self.max_reconnect_attempts

    def attempt_reconnect(self) -> None:
        self.reconnect_attempts += 1
        wait_time = min(2**self.reconnect_attempts, 2)
        print(f"Attempting to reconnect in {wait_time} seconds...")
        time.sleep(wait_time)
        try:
            self.open()
        except Exception as e:
            print(f"Failed to reconnect: {str(e)}")
            self.on_close()

    def on_error(self, error):
        print(f"WebSocket encountered an error: {error}")
        self.on_close()
