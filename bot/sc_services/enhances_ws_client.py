from concurrent.futures import ThreadPoolExecutor
import time
import json

from dacite import from_dict
from coinbase.websocket import WSClient
from bot.keys import api_key, api_secret
from bot.sc_types import *
from bot.config import config
from ..sc_types.event_types import TickerEvent


class EnhancedWSClient(WSClient):
    def __init__(
        self,
        config: dict[CurrencyPair, CurrencyPairConfig] = config,
    ):
        super().__init__(
            api_key,
            api_secret,
            on_open=self.on_open,
            on_message=self.on_message,
            on_close=self.on_close,
        )
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.config = config
        self.executor = ThreadPoolExecutor(20)
        self.ticker_data: TickerEvent

    def start(self) -> None:
        try:
            self.open()
            self.subscribe([CurrencyPair.DAI_USDC.value], ["user", "ticker_batch"])
            self.run_forever_with_exception_check()
        except Exception as e:
            print(f"Error in event service: {e}")
        finally:
            self.close()

    def on_message(self, msg: str) -> None:
        data = json.loads(msg)
        if "type" in data:
            return

        message = from_dict(WS_Message, data)
        if message.channel == "ticker_batch":
            if message.events[0].tickers:
                self.ticker_data = message.events[0].tickers[0]
            return

        event = message.events[0]
        for order in event.orders or []:
            if order.status != OrderStatus.FILLED.value:
                return
            self.executor.submit(self.handle_order, order)

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


ws_client_singleton = EnhancedWSClient()
