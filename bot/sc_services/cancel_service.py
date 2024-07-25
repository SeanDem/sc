import asyncio
import json
from coinbase.websocket import WSClient
from typing import Set
from dacite import from_dict
from bot.sc_types import *
from bot.sc_services import *
from bot.other import *
from bot.keys import api_key, api_secret


class CancelService(SingletonBase):
    def __init__(self) -> None:
        self.api_client = EnhancedRestClient.get_instance()
        self.orderBook = OrderBook.get_instance()
        self.orders_to_cancel: Set[str] = set()
        self.cancel_lock = asyncio.Lock()
        self.ws_client = WSClient(
            api_key=api_key,
            api_secret=api_secret,
            on_message=self.on_message_wrapper,
            on_open=self.on_open,
            on_close=self.on_close,
        )

    def start(self) -> None:
        LOGGER.info("Starting CancelService")
        task = asyncio.create_task(self.run_websocket())

    async def run_websocket(self) -> None:
        try:
            await self.ws_client.open_async()
            await self.ws_client.subscribe_async([], ["user", "heartbeats"])
            await self.ws_client.run_forever_with_exception_check_async()
        except Exception as e:
            LOGGER.info(f"CANCEL_SERVICE ERROR: {e}")

    def on_message_wrapper(self, msg: str) -> None:
        task = asyncio.create_task(self.on_message_async(msg))

    async def on_message_async(self, msg: str) -> None:
        data = json.loads(msg)
        if data["channel"] == "heartbeats":
            return
        message = from_dict(WS_Message, data)
        for event in message.events:
            for order in event.orders or []:
                if order.status == "CANCELLED":
                    async with self.cancel_lock:
                        if order.order_id in self.orders_to_cancel:
                            self.orders_to_cancel.remove(order.order_id)
                            await self.orderBook.delete_order_by_id(order.order_id)
                            LOGGER.info(
                                f"Order {order.order_id} has been cancelled and removed from the set"
                            )

    async def cancel_orders(self, order_ids: list[str]) -> None:
        if not order_ids:
            return
        LOGGER.info(f"Cancelling {len(order_ids)} orders")
        async with self.cancel_lock:
            self.orders_to_cancel.update(order_ids)
        for i in range(0, len(order_ids), 100):
            LOGGER.info(f"Attempting to cancel orders {order_ids[i:i+100]}")
            self.api_client.cancel_orders(order_ids[i : i + 100])
        await self.wait_for_cancellation(order_ids)

    async def wait_for_cancellation(self, order_ids) -> None:
        max_retries = 10
        retries = 0
        while (
            any(order_id in self.orders_to_cancel for order_id in order_ids)
            and retries < max_retries
        ):
            retries += 1
            await asyncio.sleep(1)
        if retries == max_retries:
            LOGGER.error(f"Failed to cancel all orders in {max_retries} retries")
            async with self.cancel_lock:
                self.orders_to_cancel.clear()
        else:
            LOGGER.info("All orders have been cancelled")

        LOGGER.info("Sleeping for 15 seconds")
        await asyncio.sleep(15)

    async def cancel_all_orders(self, pair: CurrencyPair | None = None) -> None:
        LOGGER.info("Cancelling all orders")
        data = []
        if pair:
            data = self.api_client.list_orders(pair.value, ["OPEN"])
        else:
            data = self.api_client.list_orders(order_status=["OPEN"])

        orders = from_dict(AllOrdersList, data)
        order_ids = [order.order_id for order in orders.orders]
        await self.cancel_orders(order_ids)

    def on_open(self) -> None:
        LOGGER.info("CancelService WebSocket is now open!")

    def on_close(self) -> None:
        LOGGER.info("CancelService WebSocket is closed")
