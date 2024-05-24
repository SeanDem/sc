from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import json
from threading import Thread
import time

from dacite import from_dict
from bot.sc_types import *
from bot.sc_services import *
from bot.config import sc_config


class TradingBot:
    def __init__(self) -> None:

        self.config = sc_config
        self.seen_order_ids = set[str]()
        self.executor = ThreadPoolExecutor(20)
        self.api_client = EnhancedRestClient.get_instance()
        self.accountService = AccountService.get_instance()
        self.setupService = SetupService.get_instance()
        self.ws = EnhancedWSClient.get_instance(on_message=self.on_message)
        self.orderService = OrderService.get_instance()
        self.orderBook = OrderBook.get_instance()

    def start(self) -> None:
        periodic_thread = Thread(target=self.setup)
        periodic_thread.start()
        self.accountService.getPortfolioBreakdown()
        self.ws.start()

    def setup(self) -> None:
        print("Starting setup thread")
        self.setupService.start()
        while True:
            hour: int = 60 * 60
            hours_sleep = 1
            time.sleep(hours_sleep * hour)
            print(f"{hours_sleep} hours has passed, re-balancing all pairs...")
            self.setupService.re_balance_All()

    def handle_order(self, order: OrderEvent) -> None:
        if order.order_id in self.seen_order_ids:
            print(f"Skipping order event seen before: {order}")
            print(f"Seen order ids: {self.seen_order_ids}")
            return
        self.seen_order_ids.add(order.order_id)
        if order.status == OrderStatus.FILLED.value:
            print(f"Order event filled: {order}")
            if order.order_side == OrderSide.BUY.value:
                self.handle_buy_order(order)
            elif order.order_side == OrderSide.SELL.value:
                self.handle_sell_order(order)

    def handle_buy_order(self, order: OrderEvent) -> None:
        print(
            f"Buy order event filled for {order.product_id}: {order.cumulative_quantity} at {order.avg_price} USDC"
        )
        self.orderBook.clear_order(
            CurrencyPair(order.product_id),
            OrderSide.BUY,
            order.avg_price,
            order.order_id,
        )

        min_amount_sell_prices = self.orderBook.get_prices_with_lowest_amount(
            CurrencyPair(order.product_id), OrderSide.SELL
        )
        order_amount = abs(Decimal(order.cumulative_quantity)) / len(
            min_amount_sell_prices
        )
        for price in min_amount_sell_prices:
            self.orderService.attempt_sell(
                CurrencyPair(order.product_id),
                str(order_amount),
                price,
            )

        max_amount_buy_orders = self.orderBook.get_top_orders(
            CurrencyPair(order.product_id), OrderSide.BUY, 3, False
        )
        max_amount_buy_ids, max_amount_buy_amounts, max_amount_buy_prices = zip(
            *max_amount_buy_orders
        )
        self.setupService.cancel_and_verify_orders(max_amount_buy_ids)

        for id, qty, price in max_amount_buy_orders:
            self.orderService.buy_order(
                pair=CurrencyPair(order.product_id),
                qty=str(qty),
                price=str(price),
            )

    def handle_sell_order(self, order: OrderEvent) -> None:
        print(
            f"Sell order event filled for {order.product_id}: {order.cumulative_quantity} at {order.avg_price} USDC"
        )
        self.orderBook.clear_order(
            CurrencyPair(order.product_id),
            OrderSide.SELL,
            order.avg_price,
            order.order_id,
        )

        max_amount_buy_prices = self.orderBook.get_prices_with_lowest_amount(
            CurrencyPair(order.product_id), OrderSide.BUY
        )
        order_amount = abs(Decimal(order.cumulative_quantity)) / len(
            max_amount_buy_prices
        )
        for price in max_amount_buy_prices:
            self.orderService.buy_order(
                CurrencyPair(order.product_id),
                str(order_amount),
                price,
            )

        min_amount_sell_orders = self.orderBook.get_top_orders(
            CurrencyPair(order.product_id), OrderSide.SELL, 1, False
        )
        min_amount_sell_ids, min_amount_sell_amounts, min_amount_sell_prices = zip(
            *min_amount_sell_orders
        )
        self.setupService.cancel_and_verify_orders(min_amount_sell_ids)

        for id, qty, price in min_amount_sell_orders:
            self.orderService.sellOrder(
                pair=CurrencyPair(order.product_id),
                qty=str(qty),
                price=str(price),
            )

    def on_message(self, msg: str) -> None:
        data = json.loads(msg)
        if "type" in data:
            return

        message = from_dict(WS_Message, data)
        if message.channel == "ticker_batch":
            if message.events[0].tickers:
                self.ticker_data = message.events[0].tickers[0]
            return

        event = message.events[0]
        for order in event.orders or []:
            if order.status != OrderStatus.FILLED.value:
                return
            self.executor.submit(self.handle_order, order)
