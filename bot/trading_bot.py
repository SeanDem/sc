from decimal import Decimal
from threading import Thread
import time
from bot.sc_types import *
from bot.sc_services import *
from bot.config import config
from coinbase.rest import RESTClient
from bot.keys import api_key, api_secret


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
        self.seen_order_ids = set[str]()

    def start(self) -> None:
        periodic_thread = Thread(target=self.periodic)
        periodic_thread.start()
        self.accountService.getPortfolioBreakdown()
        self.eventService.start()

    def periodic(self) -> None:
        print("Starting periodic thread")
        while True:
            hour: int = 60 * 60
            time.sleep(3 * hour)
            print(f"{3} hours has passed, re-balancing all pairs...")
            self.setupService.re_balance_All()

    def handle_order(self, order: OrderEvent) -> None:
        if order.status != OrderStatus.FILLED.value:
            print(f"Order event not filled type: {order}")
            return
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
        order_amount = Decimal(order.cumulative_quantity)
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
            f"Sell order event filled for {order.product_id}: {order.cumulative_quantity} at {order.avg_price} USDC"
        )
        order_amount = abs(Decimal(order.cumulative_quantity))
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
