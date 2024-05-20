from threading import Thread
import time
from sc_types import *
from sc_services import *
from coinbase.rest import RESTClient
from keys import api_key, api_secret
from config import config


class TradingBot:
    def __init__(self) -> None:
        self.config = config
        self.api_client = RESTClient(api_key=api_key, api_secret=api_secret)
        self.accountService = AccountService(self.api_client)
        self.orderService = OrderService(self.api_client, self.accountService)
        self.orderBook = OrderBook()
        self.setupService = SetupService(
            accountService=self.accountService,
            orderService=self.orderService,
            orderBook=self.orderBook,
            api_client=self.api_client,
        )
        self.tokenService = TokenService(self.api_client)
        self.eventService = EnhancedWSClient(self.setupService, self.handle_order)
        self.orderNumber = 0

    def start(self) -> None:
        periodic_thread = Thread(target=self.periodic)
        periodic_thread.start()
        self.accountService.getPortfolioBreakdown()
        self.eventService.start()

    def periodic(self) -> None:
        print("Starting periodic thread")
        while True:
            hour: int = 60 * 60
            time.sleep(hour)
            print("Rebalancing all pairs...")
            self.setupService.re_balance_All()

    def handle_order(self, order: OrderEvent) -> None:
        self.orderNumber += 1
        time.sleep(60)  # Sleep for 60 seconds to ensure order is filled
        if self.orderNumber % 25 == 0:
            self.setupService.re_balance_pair(CurrencyPair(order.product_id))
        elif order.order_side == OrderSide.BUY.value:
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
        min_amount_and_price = self.orderBook.get_lowest_qty_price(
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
        min_amount_and_price = self.orderBook.get_lowest_qty_price(
            CurrencyPair(order.product_id), OrderSide.BUY
        )
        self.orderService.attempt_buy(
            CurrencyPair(order.product_id),
            str(order_amount),
            min_amount_and_price,
        )
