import asyncio
import json

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
            on_message=self.on_message_wrapper,
            on_open=self.on_open,
            on_close=self.on_close,
        )
        self.config = sc_config
        self.ticker_data: dict[str, TickerEvent] = {}

    async def run_websocket(self) -> None:
        try:
            await self.ws.open_async()
            await self.ws.subscribe_async(
                ["DAI-USD"],  # TODO pair input
                [
                    "ticker",
                    "heartbeats",
                ],
            )
            await self.ws.run_forever_with_exception_check_async()
        except Exception as e:
            LOGGER.info(f"TOKEN_SERVICE ERROR: {e}")
        finally:
            await self.ws.close_async()

    def start(self) -> None:
        LOGGER.info("Starting TokenService")
        asyncio.create_task(self.run_websocket())

    def on_message_wrapper(self, msg: str) -> None:
        asyncio.create_task(self.on_message_async(msg))

    async def on_message_async(self, msg: str) -> None:
        data = json.loads(msg)
        if data["channel"] == "heartbeats":
            return
        data = from_dict(WS_Message, data)
        for ticker in data.events[0].tickers or []:
            ticker.product_id = self.USDC_NORMALIZER(ticker.product_id)
            self.ticker_data[ticker.product_id] = ticker

    def on_open(self) -> None:
        LOGGER.info("TokenService Websocket is now open!")

    def on_close(self) -> None:
        LOGGER.info("WebSocket closed")

    def USDC_NORMALIZER(self, usc: str) -> str:
        if not usc.endswith("USDC"):
            usc = usc.replace("USD", "USDC")
        return usc
