import json
import threading
from bot.keys import api_key, api_secret
from coinbase.rest import RESTClient
from coinbase.websocket import WSClient
from dacite import from_dict
from bot.config import sc_config
from bot.sc_types import *
from bot.sc_services import *
from bot.other import *


class Cancel_Service(SingletonBase, WSClient):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            on_message=self.on_message,
            api_key=api_key,
            api_secret=api_secret,
            on_open=self.on_open,
            on_close=self.on_close,
        )
        self.orderBook: OrderBook = OrderBook.get_instance()
        self.api_client: RESTClient = EnhancedRestClient.get_instance()
        self.config = sc_config
        self.orders_to_cancel = set[str]()

    def start(self) -> None:
        thread = threading.Thread(target=self.run_websocket)
        thread.daemon = True
        thread.start()

    def run_websocket(self):
        try:
            self.open()
            self.subscribe([], ["user", "heartbeats"])
            self.run_forever_with_exception_check()
        except Exception as e:
            LOGGER.info(f"ORDER_SERVICE error: {e}")
        finally:
            self.close()

    def on_message(self, msg: str) -> None:
        data = json.loads(msg)
        if (
            data["channel"] == "heartbeats"
            or data["channel"] == "subscriptions"
            or "type" in data
        ):
            return

        event = from_dict(WS_Message, data)
        if event.events[0].type == "snapshot":
            return

        for order_event in event.events[0].orders or []:
            if order_event.status == OrderStatus.CANCELLED.value:
                self.orders_to_cancel.discard(order_event.order_id)
                LOGGER.info(f"Order {order_event.order_id} has been cancelled")

    def cancel_orders(self, orderIds: list[str]):
        self.api_client.cancel_orders(orderIds)
        self.orders_to_cancel.update(orderIds)

    def cancel_all_orders(self) -> None:
        LOGGER.info("Cancelling all orders...")
        data = self.api_client.list_orders(order_status=["OPEN"])
        orders = from_dict(AllOrdersList, data)

        order_ids = [order.order_id for order in orders.orders]
        for i in range(0, len(order_ids), 100):
            self.cancel_orders(order_ids[i : i + 100])

    def cancel_orders_and_wait(self, orderIds: list[str]) -> None:
        self.cancel_orders(orderIds)
