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
        LOGGER.info("Scheduling available funds check")

        def check_for_available_funds() -> None:
            LOGGER.info(f"{time} seconds have passed, checking for available funds...")
            usdc = self.accountService.get_usdc_available_to_trade()
            dai = self.accountService.get_token_available_to_trade(
                CurrencyPair.DAI_USDC
            )

            if usdc > Decimal("1") or dai > Decimal("1"):
                LOGGER.info("Adding orders for DAI-USDC...")
                self.setupService.setup_initial_orders(
                    self.config[CurrencyPair.DAI_USDC]
                )
            Timer(time, check_for_available_funds).start()

        Timer(time, check_for_available_funds).start()

    def schedule_rebalance(self) -> None:
        time = 3600
        LOGGER.info("Scheduling re-balancer")

        def rebalance():
            self.setupService.re_balance_All()
            LOGGER.info(f"{time} seconds have passed, re-balancing all pairs...")
            Timer(time, rebalance).start()

        Timer(time, rebalance).start()

    def handle_order(self, order: OrderEvent) -> None:
        self.seen_order_ids.add(order.order_id)
        if order.status == OrderStatus.FILLED.value:
            self.orderBook.delete_order_by_id(order.order_id)
            if order.order_side == OrderSide.BUY.value:
                self.handle_buy_order(order)
            elif order.order_side == OrderSide.SELL.value:
                self.handle_sell_order(order)

    def handle_buy_order(self, order: OrderEvent) -> None:
        LOGGER.info(
            f"Buy order event filled for {order.product_id}: {order.cumulative_quantity} at {order.avg_price} USDC"
        )
        min_amount_sell_prices = self.orderBook.get_prices_with_lowest_amount(
            CurrencyPair(order.product_id), OrderSide.SELL
        )
        order_amount = abs(Decimal(order.cumulative_quantity)) / len(
            min_amount_sell_prices
        )
        for price in min_amount_sell_prices:
            self.orderService.sell_order(
                CurrencyPair(order.product_id),
                str(order_amount),
                price,
            )

        # max_amount_buy_orders = self.orderBook.get_top_orders(
        #     CurrencyPair(order.product_id), OrderSide.BUY, 3, True
        # )
        # max_amount_buy_ids, max_amount_buy_amounts, max_amount_buy_prices = zip(
        #     *max_amount_buy_orders
        # )

        # self.setupService.cancel_and_verify_orders(max_amount_buy_ids)
        # total_qty = sum(max_amount_buy_amounts)
        # new_orders = list(max_amount_buy_prices) + [order.avg_price]
        # qty = total_qty / len(new_orders)
        # for price in new_orders:
        #     self.orderService.buy_order(
        #         pair=CurrencyPair(order.product_id),
        #         qty=str(qty),
        #         price=str(price),
        #     )

    def handle_sell_order(self, order: OrderEvent) -> None:
        LOGGER.info(
            f"Sell order event filled for {order.product_id}: {order.cumulative_quantity} at {order.avg_price} USDC"
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

        # min_amount_sell_orders = self.orderBook.get_top_orders(
        #     CurrencyPair(order.product_id), OrderSide.SELL, 3, False
        # )
        # min_amount_sell_ids, min_amount_sell_amounts, min_amount_sell_prices = zip(
        #     *min_amount_sell_orders
        # )

        # self.setupService.cancel_and_verify_orders(min_amount_sell_ids)

        # total_qty = sum(min_amount_sell_amounts)
        # new_orders = list(min_amount_sell_prices) + [order.avg_price]
        # qty = total_qty / len(new_orders)
        # for price in new_orders:
        #     self.orderService.sell_order(
        #         pair=CurrencyPair(order.product_id),
        #         qty=str(qty),
        #         price=str(price),
        #     )

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
