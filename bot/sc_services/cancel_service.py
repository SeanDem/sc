import json
import threading
import time
from coinbase.websocket import WSClient
from typing import Set
from dacite import from_dict
from bot.sc_types import *
from bot.sc_services import *
from bot.other import *
from bot.keys import api_key, api_secret


class CancelService(SingletonBase):
    def __init__(self):
        self.api_client = EnhancedRestClient.get_instance()
        self.orders_to_cancel: Set[str] = set()
        self.cancel_lock = threading.Lock()
        self.init_websocket()

    def init_websocket(self) -> None:
        self.ws_client = WSClient(
            api_key=api_key, api_secret=api_secret, on_message=self.on_message
        )
        self.ws_thread = threading.Thread(target=self.run_websocket)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def run_websocket(self) -> None:
        self.ws_client.open()
        self.ws_client.subscribe([], ["user", "heartbeats"])
        self.ws_client.run_forever_with_exception_check()

    def on_message(self, msg: str) -> None:
        data = json.loads(msg)
        message = from_dict(WS_Message, data)
        for event in message.events:
            for order in event.orders or []:
                if order.status == "CANCELLED":
                    with self.cancel_lock:
                        if order.order_id in self.orders_to_cancel:
                            self.orders_to_cancel.remove(order.order_id)
                            print(
                                f"Order {order.order_id} has been cancelled and removed from the set"
                            )

    def cancel_orders(self, order_ids: list[str]) -> None:
        LOGGER.info(f"Cancelling {len(order_ids)} orders...")
        with self.cancel_lock:
            self.orders_to_cancel.update(order_ids)
        for i in range(0, len(order_ids), 100):
            self.api_client.cancel_orders(order_ids[i : i + 100])
        self.wait_for_cancellation(order_ids)

    def wait_for_cancellation(self, order_ids) -> None:
        while any(order_id in self.orders_to_cancel for order_id in order_ids):
            time.sleep(0.05)
            LOGGER.info(f"{len(self.orders_to_cancel)} orders left to cancel...")

    def cancel_all_orders(self, pair: CurrencyPair | None = None) -> None:
        LOGGER.info("Cancelling all orders...")
        data = []
        if pair:
            data = self.api_client.list_orders(pair.value, ["OPEN"])
        else:
            data = self.api_client.list_orders(order_status=["OPEN"])
        orders = from_dict(AllOrdersList, data)
        order_ids = [order.order_id for order in orders.orders]
        self.cancel_orders(order_ids)
