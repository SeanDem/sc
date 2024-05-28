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

    def generate_order_id(self) -> str:
        return str(uuid.uuid4())

    def adjust_precision(self, size: str, decimals=4) -> str:
        return str(
            Decimal(size).quantize(Decimal("1." + "0" * decimals), rounding=ROUND_DOWN)
        )

    def buy_order(
        self,
        pair: CurrencyPair,
        qty: str,
        price: str,
    ) -> str | None:
        if Decimal(price) > Decimal(self.config[pair].max_buy_price):
            print(f"Buy price too high for {pair.value} at {price}")
            return

        best_bid = Decimal(self.tokenService.ticker_data[pair.value].best_bid)
        if Decimal(price) > best_bid:
            print(f"Buy price above {best_bid} at {price}")
            print(f"Adjusting price to {best_bid}")
            price = str(best_bid - Decimal("0.0001"))

        orderId = self.generate_order_id()
        adjusted_qty = self.adjust_precision(qty, self.config[pair].qty_precision)
        adjusted_price = self.adjust_precision(price)
        response = self.api_client.limit_order_gtc_buy(
            client_order_id=orderId,
            product_id=pair.value,
            base_size=adjusted_qty,
            limit_price=adjusted_price,
        )
        if not response["success"]:
            print(f"Failed to create buy order for {pair.value}")
            print(response)
        else:
            print(f"Buy Limit Order {pair.value}: {adjusted_qty} at {adjusted_price}")
            return orderId

    def sell_order(
        self,
        pair: CurrencyPair,
        qty: str,
        price: str,
    ) -> str | None:
        if Decimal(price) < Decimal(self.config[pair].min_sell_price):
            print(f"Sell price too low for {pair.value} at {price}")
            return

        best_ask = Decimal(self.tokenService.ticker_data[pair.value].best_ask)
        if Decimal(price) < best_ask:
            print(f"Sell price below {best_ask} at {price}")
            print(f"Adjusting price to {price}")
            price = str(best_ask + Decimal("0.0001"))

        orderId = self.generate_order_id()
        adjusted_qty = self.adjust_precision(qty, self.config[pair].qty_precision)
        adjusted_price = self.adjust_precision(price)
        response = self.api_client.limit_order_gtc_sell(
            client_order_id=orderId,
            product_id=pair.value,
            base_size=adjusted_qty,
            limit_price=adjusted_price,
        )
        if not response["success"]:
            print(f"Failed to create sell order for {pair.value}")
            print(response)
        else:
            print(f"Sell limit order {pair.value}: {adjusted_qty} at {adjusted_price}")
            return orderId
