import uuid
from decimal import Decimal, ROUND_DOWN
from coinbase.rest import RESTClient
from sc_types import CurrencyPair
from account_service import AccountService


class OrderService:
    def __init__(self, api_client: RESTClient, accountService: AccountService) -> None:
        self.api_client: RESTClient = api_client
        self.precision = 4
        self.accountService = accountService

    def generate_order_id(self) -> str:
        return str(uuid.uuid4())

    def adjust_precision(self, size: str) -> str:
        return str(Decimal(size).quantize(Decimal("1." + "0" * 4), rounding=ROUND_DOWN))

    def buyOrder(
        self,
        pair: CurrencyPair,
        qty: str,
        price: str,
    ):
        if float(price) > 0.9999:
            print("Buy price too high")
            return
        orderId = self.generate_order_id()
        adjusted_size = self.adjust_precision(qty)
        response = self.api_client.limit_order_gtc_buy(
            client_order_id=orderId,
            product_id=pair.value,
            base_size=adjusted_size,
            limit_price=price,
        )

    def sellOrder(
        self,
        pair: CurrencyPair,
        qty: str,
        price: str,
    ):
        if float(price) < 0.9994:
            print("Sale price price too low")
            return
        orderId = self.generate_order_id()
        adjusted_size = self.adjust_precision(qty)
        response = self.api_client.limit_order_gtc_sell(
            client_order_id=orderId,
            product_id=pair.value,
            base_size=adjusted_size,
            limit_price=price,
        )

    def attempt_buy(self, pair: CurrencyPair, qty: str, price: str) -> None:
        usdc_available = self.accountService.get_usdc_available_to_trade()
        qty_float = float(qty)
        usdc_available_float = float(usdc_available)
        qty_to_order: float = min(usdc_available_float, qty_float)
        if usdc_available > 1 and usdc_available > qty_to_order:
            self.buyOrder(pair, price=price, qty=str(qty_to_order))
            print(f"Created buy order for {pair.value}: {float(qty):.2f} at {price}")

    def attempt_sell(self, pair: CurrencyPair, qty: str, price: str) -> None:
        token_available = self.accountService.get_token_available_to_trade(pair)
        qty_float = float(qty)
        token_available_float = float(token_available)
        qty_to_order: float = min(token_available_float, qty_float)
        if token_available_float > 1 and token_available_float > qty_to_order:
            self.sellOrder(pair, price=price, qty=str(qty_to_order))
            print(f"Created sell order for {pair.value}: {float(qty):.2f} at {price}")
