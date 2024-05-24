import uuid
from decimal import Decimal, ROUND_DOWN
from coinbase.rest import RESTClient
from bot.sc_services import *
from bot.sc_types import *
from bot.config import config


class OrderService:
    def __init__(
        self,
        api_client: RESTClient = rest_client_singleton,
        accountService: AccountService = account_service_singleton,
        ws_client: EnhancedWSClient = ws_client_singleton,
        config: dict[CurrencyPair, CurrencyPairConfig] = config,
    ) -> None:
        self.config = config
        self.api_client: RESTClient = api_client
        self.precision = 4
        self.accountService = accountService
        self.ws_client = ws_client

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
        if Decimal(price) > Decimal(config[pair].max_buy_price):
            print(f"Buy price too high for {pair.value} at {price}")
            return
        if Decimal(price) > Decimal(self.ws_client.ticker_data.best_bid):
            print(f"Buy price above best bid for {pair.value} at {price}")
            price = str(
                Decimal(self.ws_client.ticker_data.best_bid) - Decimal("0.0001")
            )
            print(f"Adjusting price to {price}")
        orderId = self.generate_order_id()
        adjusted_qty = self.adjust_precision(qty, config[pair].qty_precision)
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

    def sellOrder(
        self,
        pair: CurrencyPair,
        qty: str,
        price: str,
    ) -> str | None:
        if Decimal(price) < Decimal(config[pair].min_sell_price):
            print(f"Sell price too low for {pair.value} at {price}")
            return
        if Decimal(price) < Decimal(self.ws_client.ticker_data.best_ask):
            print(f"Sell price below best ask for {pair.value} at {price}")
            price = str(
                Decimal(self.ws_client.ticker_data.best_ask) + Decimal("0.0001")
            )
            print(f"Adjusting price to {price}")

        orderId = self.generate_order_id()
        adjusted_qty = self.adjust_precision(qty, config[pair].qty_precision)
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

    def attempt_sell(self, pair: CurrencyPair, qty: str, price: str) -> str | None:
        qty_decimal = Decimal(qty)
        return self.sellOrder(pair, price=price, qty=str(qty_decimal))


order_service_singleton = OrderService()
