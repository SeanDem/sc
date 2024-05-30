from decimal import Decimal
import json
from threading import Timer

from dacite import from_dict
from .other.logger import LOGGER
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

    def start(self) -> None:
        self.tokenService.start()
        self.userOrdersService.start()
        self.setup()

    def setup(self) -> None:
        self.setupService.start()
        self.schedule_rebalance()
        self.schedule_available_funds_check()

    def schedule_available_funds_check(self) -> None:
        time = 60

        def check_for_available_funds() -> None:
            LOGGER.info(f"{time} seconds have passed, checking for available funds...")
            usdc = self.accountService.get_usdc_available_to_trade()
            dai = self.accountService.get_token_available_to_trade(
                CurrencyPair.DAI_USDC
            )

            if usdc > Decimal("1"):
                self.fill_buy_ladder(CurrencyPair.DAI_USDC, usdc)

            if dai > Decimal("1"):
                self.fill_sell_ladder(CurrencyPair.DAI_USDC, dai)

            Timer(time, check_for_available_funds).start()

        Timer(time, check_for_available_funds).start()

    def schedule_rebalance(self) -> None:
        time = 3600

        def rebalance():
            self.setupService.re_balance_All()
            LOGGER.info(f"{time} seconds have passed, re-balancing all pairs...")
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

    def fill_buy_ladder(self, pair: CurrencyPair, amount: Decimal) -> None:
        min_amount_buy_prices = self.orderBook.get_prices_with_lowest_amount(
            CurrencyPair(pair.value), OrderSide.BUY
        )
        order_amount = abs(Decimal(amount)) / len(min_amount_buy_prices)
        for price in min_amount_buy_prices:
            self.orderService.buy_order(
                CurrencyPair(pair.value),
                str(order_amount),
                price,
            )

    def fill_sell_ladder(self, pair: CurrencyPair, amount: Decimal) -> None:
        max_amount_buy_prices = self.orderBook.get_prices_with_lowest_amount(
            CurrencyPair(pair.value), OrderSide.BUY
        )
        order_amount = abs(Decimal(amount)) / len(max_amount_buy_prices)
        for price in max_amount_buy_prices:
            self.orderService.sell_order(
                CurrencyPair(pair.value),
                str(order_amount),
                price,
            )
