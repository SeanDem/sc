import uuid
from decimal import Decimal, ROUND_DOWN
from coinbase.rest import RESTClient
from sc_services.account_service import AccountService
from sc_types import *
from config import config


class OrderService:
    def __init__(
        self,
        api_client: RESTClient,
        accountService: AccountService,
        config: dict[CurrencyPair, CurrencyPairConfig] = config,
    ) -> None:
        self.config = config
        self.api_client: RESTClient = api_client
        self.precision = 4
        self.accountService = accountService

    def generate_order_id(self) -> str:
        return str(uuid.uuid4())

    def adjust_precision(self, size: str, decimals=4) -> str:
        return str(
            Decimal(size).quantize(Decimal("1." + "0" * decimals), rounding=ROUND_DOWN)
        )

    def buyOrder(
        self,
        pair: CurrencyPair,
        qty: str,
        price: str,
    ):
        if float(price) > float(config[pair].max_buy_price):
            print(f"Buy price too high for {pair.value} at {price}")
            return
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
            print(f"Failed to create buy order for {pair.value}: {response}")
        else:
            print(
                f"Created buy order for {pair.value}: {adjusted_qty} at {adjusted_price}"
            )

    def sellOrder(
        self,
        pair: CurrencyPair,
        qty: str,
        price: str,
    ):
        if float(price) < float(config[pair].min_sell_price):
            print(f"Sell price too low for {pair.value} at {price}")
            return
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
            print(f"Failed to create buy order for {pair.value}: {response}")
        else:
            print(
                f"Created sell order for {pair.value}: {adjusted_qty} at {adjusted_price}"
            )

    def attempt_buy(self, pair: CurrencyPair, qty: str, price: str) -> None:
        usdc_available = self.accountService.get_usdc_available_to_trade()
        qty_float = float(qty)
        usdc_available_float = float(usdc_available)
        qty_to_order: float = min(
            usdc_available_float, qty_float
        )  # should be fine but may cause issues
        if usdc_available > 1 and usdc_available > qty_to_order:
            self.buyOrder(pair, price=price, qty=str(qty_to_order))

    def attempt_sell(self, pair: CurrencyPair, qty: str, price: str) -> None:
        token_available = self.accountService.get_token_available_to_trade(pair)
        qty_float = float(qty)
        token_available_float = float(token_available)
        qty_to_order: float = min(
            token_available_float, qty_float
        )  # should be fine but may cause issues
        if token_available_float > 1 and token_available_float > qty_to_order:
            self.sellOrder(pair, price=price, qty=str(qty_to_order))
