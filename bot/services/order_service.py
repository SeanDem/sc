import uuid
from dacite import from_dict
from decimal import Decimal, ROUND_DOWN
from coinbase.rest import RESTClient
from ..stypes.config import BotConfig
from ..stypes.order_types import OrderResponse
from ..clients import REST_CLIENT


class OrderService:
    api_client: RESTClient = REST_CLIENT

    def __init__(self, config: BotConfig):
        self.config = config

    def generate_order_id(self) -> str:
        return str(uuid.uuid4())

    def adjust_precision(self, size: float) -> str:
        return str(
            Decimal(size).quantize(
                Decimal("1." + "0" * self.config.precision), rounding=ROUND_DOWN
            )
        )

    def buyOrder(self, size: float):
        orderId = self.generate_order_id()
        adjusted_size = self.adjust_precision(size)
        response = self.api_client.limit_order_gtc_buy(
            client_order_id=orderId,
            product_id=self.config.pair.value,
            base_size=adjusted_size,
            limit_price=self.config.target_buy_price,
        )
        res: OrderResponse = from_dict(data_class=OrderResponse, data=response)
        self.print_order_status(res)
        return res

    def sellOrder(self, size: float):
        orderId = self.generate_order_id()
        adjusted_size = self.adjust_precision(size)
        response = self.api_client.limit_order_gtc_sell(
            client_order_id=orderId,
            product_id=self.config.pair.value,
            base_size=adjusted_size,
            limit_price=self.config.target_sell_price,
        )
        res: OrderResponse = from_dict(data_class=OrderResponse, data=response)
        self.print_order_status(res)
        return res

    def print_order_status(self, response: OrderResponse) -> None:
        if response.success and response.success_response:
            print(f"{response.success_response.side} Limit Order: Successful")
            print(f"Order ID: {response.success_response.order_id}")
            print(f"Product ID: {response.success_response.product_id}")
            print(f"Side: {response.success_response.side}")
            print(f"Client Order ID: {response.success_response.client_order_id}")
            print(
                f"Base Size: {response.order_configuration.limit_limit_gtc.base_size}"
            )
            print(
                f"Limit Price: {response.order_configuration.limit_limit_gtc.limit_price}"
            )
            print(
                f"Post Only: {response.order_configuration.limit_limit_gtc.post_only}"
            )
        else:
            # Assumes the error_response is properly populated for failed cases
            print(
                f"{response.success_response.side if response.success_response else 'UNKNOWN'} Order Failed:"
            )
            print(f"Failure Reason: {response.failure_reason}")
            print(
                f"Error Message: {response.error_response.message if response.error_response else 'No error message provided'}"
            )
