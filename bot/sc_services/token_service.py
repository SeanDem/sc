import json
import threading

from dacite import from_dict
from bot.other import *
from bot.sc_types import *
from bot.sc_services import *
from coinbase.websocket import WSClient
from bot.keys import api_key, api_secret
from bot.config import sc_config


class TokenService(SingletonBase):
    def __init__(self) -> None:
        self.ws = WSClient(
            api_key=api_key,
            api_secret=api_secret,
            on_message=self.on_message,
            on_open=self.on_open,
            on_close=self.on_close,
        )
        self.config = sc_config
        self.ticker_data: dict[str, TickerEvent] = {}

    def start(self) -> None:
        thread = threading.Thread(target=self.run_websocket)
        thread.daemon = True
        thread.start()

    def run_websocket(self):
        try:
            self.ws.open()
            self.ws.subscribe(
                ["DAI-USD"],
                [
                    "ticker",
                    "heartbeats",
                ],
            )
            self.ws.run_forever_with_exception_check()
        except Exception as e:
            LOGGER.info(f"TOKEN_SERVICE ERROR: {e}")
        finally:
            self.ws.close()

    def on_message(self, msg: str) -> None:
        data = json.loads(msg)
        if data["channel"] == "heartbeats":
            return
        data = from_dict(WS_Message, data)
        for ticker in data.events[0].tickers or []:
            ticker.product_id = self.USDC_NORMALIZER(ticker.product_id)
            self.ticker_data[ticker.product_id] = ticker

    def on_open(self) -> None:
        LOGGER.info("WebSocket is now open!")

    def on_close(self) -> None:
        LOGGER.info("WebSocket closed")

    def USDC_NORMALIZER(self, usc: str) -> str:
        if not usc.endswith("USDC"):
            usc = usc.replace("USD", "USDC")
        return usc
