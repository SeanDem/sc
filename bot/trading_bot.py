from decimal import Decimal
import json
from threading import Timer

from dacite import from_dict
from bot.other.logger import LOGGER
from bot.sc_services.rest_client import EnhancedRestClient
from bot.sc_types import *
from bot.sc_services import *
from bot.config import sc_config


class TradingBot:
    def __init__(self) -> None:
        self.tokenService = TokenService.get_instance()
        self.config = sc_config
        self.seen_order_ids = set[str]()
        self.api_client: EnhancedRestClient = EnhancedRestClient.get_instance()
        self.accountService = AccountService.get_instance()
        self.setupService = SetupService.get_instance()
        self.userOrdersService = UserOrdersService.get_instance(
            on_message=self.on_message
        )
        self.cancelled_orders = set[str]()
        self.orderService = OrderService.get_instance()
        self.orderBook = OrderBook.get_instance()
        self.cancelService = CancelService.get_instance()
        self.orders_to_refresh = 2
        self.refresh_interval = 60

    def start(self) -> None:
        self.tokenService.start()
        self.userOrdersService.start()
        self.setup()

    def setup(self) -> None:
        self.setupService.start()
        self.start_order_cancel_scheduler()
        self.start_available_funds_scheduler()
        self.start_rebalance_scheduler()
        self.start_info_scheduler()

    def start_info_scheduler(self) -> None:
        LOGGER.info("Starting info scheduler")

        def print_info():
            LOGGER.info("Checking info")
            total_orders_dict = self.api_client.list_orders(None, ["OPEN"])
            total_orders = from_dict(AllOrdersList, total_orders_dict).orders
            buy_orders = [order for order in total_orders if order.side == "BUY"]
            sell_orders = [order for order in total_orders if order.side == "SELL"]

            LOGGER.info(
                f"Total Orders: {len(total_orders)}\nBuy Orders: {len(buy_orders)}\nSell Orders: {len(sell_orders)}"
            )

            Timer(self.refresh_interval, print_info).start()

        Timer(self.refresh_interval, print_info).start()

    def start_order_cancel_scheduler(self) -> None:
        LOGGER.info("Starting order cancel scheduler")
        time = self.orders_to_refresh * self.refresh_interval

        def cancel_random_order() -> None:
            LOGGER.info(
                f"{time} seconds have passed, cancelling {self.orders_to_refresh} random order(s)..."
            )
            order_ids = self.orderBook.get_and_delete_random_orders(
                OrderSide.BUY,
                self.orders_to_refresh - 1,
            )
            self.cancelService.cancel_orders(order_ids)

            Timer(time, cancel_random_order).start()

        Timer(time, cancel_random_order).start()

    def start_available_funds_scheduler(self) -> None:
        LOGGER.info("Starting available funds scheduler")

        def check_for_available_funds() -> None:
            LOGGER.info(
                f"{self.refresh_interval} seconds have passed, checking for available funds"
            )
            usdc = self.accountService.get_usdc_available_to_trade()
            dai = self.accountService.get_token_available_to_trade(
                CurrencyPair.DAI_USDC
            )
            LOGGER.info(f"USDC: {usdc:.4f}\nDAI: {dai:.4f}")

            if usdc > Decimal(self.orders_to_refresh):
                self.fill_buy_ladder(CurrencyPair.DAI_USDC, usdc)

            if dai > Decimal(self.orders_to_refresh):
                self.fill_sell_ladder(CurrencyPair.DAI_USDC, dai)

            Timer(self.refresh_interval, check_for_available_funds).start()

        Timer(self.refresh_interval, check_for_available_funds).start()

    def start_rebalance_scheduler(self) -> None:
        LOGGER.info("Starting re-balance scheduler")
        time = 3600 * 6

        def rebalance():
            self.setupService.re_balance_All()
            LOGGER.info(f"{time/60} minutes have passed, re-balancing all pairs")
            Timer(time, rebalance).start()

        Timer(time, rebalance).start()

    def handle_order(self, order: OrderEvent) -> None:
        self.seen_order_ids.add(order.order_id)
        if order.status in (
            OrderStatus.FILLED.value,
            OrderStatus.CANCELLED.value,
            OrderStatus.EXPIRED.value,
            OrderStatus.FAILED.value,
        ):
            self.orderBook.delete_order_by_id(order.order_id)

    def on_message(self, msg: str) -> None:
        data = json.loads(msg)
        if (
            data["channel"] == "heartbeats"
            or "type" in data
            or data["channel"] == "subscriptions"
        ):
            return

        event = from_dict(WS_Message, data)
        if event.events[0].type == "snapshot":
            return

        for order_event in event.events[0].orders or []:
            self.handle_order(order_event)

    def fill_ladder(self, pair: CurrencyPair, amount: Decimal, side: OrderSide) -> None:
        LOGGER.info(f"Filling {side.value} ladder for {pair.value} with {amount:.4f}")
        prices = self.orderBook.get_prices_with_lowest_amount(
            pair, side, self.orders_to_refresh
        )

        if prices:
            order_amount = abs(Decimal(amount)) / len(prices)
            for price in prices:
                if side == OrderSide.BUY:
                    self.orderService.buy_order(pair, str(order_amount), price)
                else:
                    self.orderService.sell_order(pair, str(order_amount), price)
        else:
            LOGGER.info(f"No {side.value} prices available for {pair.value}")

    def fill_buy_ladder(self, pair: CurrencyPair, amount: Decimal) -> None:
        self.fill_ladder(pair, amount, OrderSide.BUY)

    def fill_sell_ladder(self, pair: CurrencyPair, amount: Decimal) -> None:
        self.fill_ladder(pair, amount, OrderSide.SELL)
