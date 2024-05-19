import json
import threading
import time
from dacite import from_dict
from sc_types import *
from sc_services import *
from coinbase.websocket import WSClient
from coinbase.rest import RESTClient
from keys import api_key, api_secret


class TradingBot:
    def __init__(self) -> None:
        self.api_client = RESTClient(api_key=api_key, api_secret=api_secret)
        self.accountService = AccountService(self.api_client)
        self.orderService = OrderService(self.api_client, self.accountService)
        self.tokenService = TokenService(self.api_client)
        self.eventService = WSClient(
            api_key=api_key,
            api_secret=api_secret,
            on_close=self.on_close,
            on_message=self.on_message,
            on_open=self.on_open,
        )
        self.orderBook = OrderBook()

    def run(self) -> None:
        event_thread = threading.Thread(target=self.setup)
        event_thread.start()
        self.start_event_service()

    def setup(self) -> None:
        self.cancel_all_orders()
        self.setup_initial_orders()

    def start_event_service(self) -> None:
        try:
            self.eventService.open()
            self.eventService.subscribe([], ["user"])
            self.eventService.run_forever_with_exception_check()
        except Exception as e:
            print(f"Error in event service: {e}")
        finally:
            self.eventService.close()

    def setup_initial_orders(self) -> None:
        usdc_amt = self.accountService.get_usdc_available_to_trade()
        token_amt = self.accountService.get_token_available_to_trade(
            CurrencyPair.DAI_USDC
        )
        print(f"USDC: {usdc_amt}")
        print(f"{CurrencyPair.DAI_USDC.value}: {token_amt}")
        buy_prices = self.generate_order_distribution(0.9871, 0.9989, 8)
        buy_qty: str = "{:.4f}".format(usdc_amt / len(buy_prices))
        for price in buy_prices:
            time.sleep(1)
            self.orderService.attempt_buy(CurrencyPair.DAI_USDC, buy_qty, price)
            self.orderBook.update_order(
                CurrencyPair.DAI_USDC, OrderSide.BUY, price, amount=buy_qty
            )

        sell_prices = [".9999", "1.0006"]
        sell_qty: str = "{:.4f}".format(token_amt / len(sell_prices))
        for price in sell_prices:
            time.sleep(1)
            self.orderService.attempt_sell(CurrencyPair.DAI_USDC, sell_qty, price)
            self.orderBook.update_order(
                CurrencyPair.DAI_USDC, OrderSide.SELL, price, sell_qty
            )

    def on_open(self) -> None:
        print("WebSocket is now open!")

    def on_message(self, msg: str) -> None:
        message = from_dict(CB_Message, json.loads(msg))
        event = message.events[0]
        if event.type == "snapshot":
            return
        for order in event.orders or []:
            if order.cumulative_quantity == "0":
                continue
            if order.order_side == OrderSide.BUY.value:
                self.handle_buy_order(order)
            elif order.order_side == OrderSide.SELL.value:
                self.handle_sell_order(order)

    def handle_buy_order(self, order: OrderEvent) -> None:
        print(
            f"Buy order event filled or partially filled: {order.cumulative_quantity} at {order.avg_price}"
        )
        prev_amount = self.orderBook.get_order_amount(
            CurrencyPair(order.product_id), OrderSide.BUY, order.avg_price
        )
        order_amount = float(order.cumulative_quantity) - float(prev_amount)
        self.orderBook.update_order(
            CurrencyPair(order.product_id),
            OrderSide.BUY,
            order.avg_price,
            order.cumulative_quantity,
        )
        min_amount_and_price = self.orderBook.get_lowest_price(
            CurrencyPair(order.product_id), OrderSide.SELL
        )
        self.orderService.attempt_sell(
            CurrencyPair(order.product_id),
            str(order_amount),
            min_amount_and_price,
        )

    def handle_sell_order(self, order: OrderEvent) -> None:
        print(
            f"Sell order event filled or partially filled: {order.cumulative_quantity} at {order.avg_price}"
        )
        prev_amount = self.orderBook.get_order_amount(
            CurrencyPair(order.product_id), OrderSide.SELL, order.avg_price
        )
        order_amount = float(order.cumulative_quantity) - float(prev_amount)
        self.orderBook.update_order(
            CurrencyPair(order.product_id),
            OrderSide.SELL,
            order.avg_price,
            order.cumulative_quantity,
        )
        min_amount_and_price = self.orderBook.get_lowest_price(
            CurrencyPair(order.product_id), OrderSide.BUY
        )
        print(f"Min amount and price: {min_amount_and_price}")
        print(f"Order amount: {order_amount}")
        self.orderService.attempt_buy(
            CurrencyPair(order.product_id),
            str(order_amount),
            min_amount_and_price,
        )

    def on_close(self) -> None:
        print("WebSocket closed")

    def cancel_all_orders(self) -> None:
        data = self.api_client.list_orders()
        orders = from_dict(AllOrdersList, data)
        orderIds = [order.order_id for order in orders.orders if order.status == "OPEN"]
        if orderIds:
            self.api_client.cancel_orders(orderIds)
            while True:
                time.sleep(3)
                data = self.api_client.list_orders()
                orders = from_dict(AllOrdersList, data)
                if all(
                    order.status == "CANCELLED"
                    for order in orders.orders
                    if order.order_id in orderIds
                ):
                    break
        print("All orders have been cancelled!")

    def generate_order_distribution(
        self, min_val: float, max_val: float, amount: int
    ) -> list:
        step = (max_val - min_val) / (amount - 1)
        distribution = [min_val + i * step for i in range(amount)]
        return [f"{num:.4f}" for num in distribution]
