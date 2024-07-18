import time
import uuid
from decimal import Decimal, ROUND_DOWN
from bot.other import *
from bot.sc_services import *
from bot.sc_types import *
from bot.config import sc_config


class OrderService(SingletonBase):
    def __init__(
        self,
    ) -> None:
        self.config: dict[CurrencyPair, CurrencyPairConfig] = sc_config
        self.api_client = EnhancedRestClient.get_instance()
        self.accountService = AccountService.get_instance()
        self.tokenService = TokenService.get_instance()
        self.orderBook = OrderBook.get_instance()
        self.max_order_qty = 10
        self.min_order_qty = 0.05

    def generate_order_id(self) -> str:
        return str(uuid.uuid4())

    def adjust_precision(self, size: str, decimals=4) -> str:
        return str(
            Decimal(size).quantize(Decimal("1." + "0" * decimals), rounding=ROUND_DOWN)
        )

    async def buy_order(
        self,
        pair: CurrencyPair,
        qty: str,
        price: str,
    ) -> str | None:
        if Decimal(price) > Decimal(self.config[pair].max_buy_price):
            LOGGER.info(f"Buy price too high for {pair.value} at {price}")
            return

        qty_float = float(qty)
        while qty_float > self.max_order_qty:
            time.sleep(0.15)
            order_id = await self._buy_order(pair, str(self.max_order_qty), price)
            qty_float -= self.max_order_qty
            if not order_id:
                return
        if qty_float > self.min_order_qty:
            await self._buy_order(pair, str(qty_float), price)

    async def _buy_order(self, pair: CurrencyPair, qty: str, price: str) -> str | None:
        if float(qty) < self.min_order_qty:
            return
        best_ask = Decimal(self.tokenService.ticker_data[pair.value].best_ask)
        if Decimal(price) >= best_ask:
            LOGGER.info(f"Buy price at or above above best ask {best_ask} at {price}")
            price = str(best_ask - Decimal("0.0001"))
            LOGGER.info(f"Adjusting price to {price}")

        adjusted_qty = self.adjust_precision(qty, self.config[pair].qty_precision)
        adjusted_price = self.adjust_precision(price)
        response_dict = self.api_client.limit_order_gtc_buy(
            client_order_id=self.generate_order_id(),
            product_id=pair.value,
            base_size=adjusted_qty,
            limit_price=adjusted_price,
        )
        if response_dict["success"]:
            LOGGER.info(
                f"Buy Limit Order {pair.value}: {adjusted_qty} at {adjusted_price}"
            )
            await self.orderBook.update_order(
                pair,
                OrderSide.BUY,
                adjusted_price,
                response_dict["order_id"],
                adjusted_qty,
            )
            return response_dict["order_id"]
        else:
            LOGGER.info(f"Failed to create buy order for {pair.value}")
            amt: Decimal = self.accountService.get_usdc_available_to_trade()
            LOGGER.info(f"Available to trade: {amt}")
            LOGGER.info(response_dict)
            return None

    async def sell_order(
        self,
        pair: CurrencyPair,
        qty: str,
        price: str,
    ) -> str | None:
        if Decimal(price) < Decimal(self.config[pair].min_sell_price):
            LOGGER.info(f"Sell price too low for {pair.value} at {price}")
            return

        qty_float = float(qty)
        while qty_float > self.max_order_qty:
            time.sleep(0.15)
            order_id = self._sell_order(pair, str(self.max_order_qty), price)
            qty_float -= self.max_order_qty
            if not order_id:
                return
        if qty_float > self.min_order_qty:
            await self._sell_order(pair, str(qty_float), price)

    async def _sell_order(self, pair: CurrencyPair, qty: str, price: str) -> str | None:
        if float(qty) < self.min_order_qty:
            return
        best_bid = Decimal(self.tokenService.ticker_data[pair.value].best_bid)

        if Decimal(price) <= best_bid:
            LOGGER.info(f"Sell price at or below best bid {best_bid} at {price}")
            price = str(best_bid + Decimal("0.0001"))
            LOGGER.info(f"Adjusting price to {price}")

        adjusted_qty = self.adjust_precision(qty, self.config[pair].qty_precision)
        adjusted_price = self.adjust_precision(price)
        response = self.api_client.limit_order_gtc_sell(
            client_order_id=self.generate_order_id(),
            product_id=pair.value,
            base_size=adjusted_qty,
            limit_price=adjusted_price,
        )
        if response["success"]:
            LOGGER.info(
                f"Sell Limit Order {pair.value}: {adjusted_qty} at {adjusted_price}"
            )
            await self.orderBook.update_order(
                pair, OrderSide.SELL, adjusted_price, response["order_id"], adjusted_qty
            )
            return response["order_id"]
        else:
            LOGGER.info(f"Failed to create sell order for {pair.value}")
            amt = self.accountService.get_token_available_to_trade(pair)
            LOGGER.info(f"Available to trade: {amt}")
            LOGGER.info(response)
            return None
