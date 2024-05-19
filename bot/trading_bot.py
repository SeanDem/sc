from bot.sc_types import *
from bot.sc_services import *
from coinbase.rest import RESTClient
from keys import api_key, api_secret


class TradingBot:
    def __init__(self) -> None:
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

    def start(self) -> None:
        self.eventService.start()

    def handle_order(self, order: OrderEvent) -> None:
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
