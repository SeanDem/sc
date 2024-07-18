import asyncio
from decimal import Decimal
import json

from dacite import from_dict
from bot.other.logger import LOGGER
from bot.sc_services.rest_client import EnhancedRestClient
from bot.sc_types import *
from bot.sc_services import *
from bot.config import sc_config


class TradingBot:
    def __init__(self) -> None:
        self.config = sc_config
        self.tokenService = TokenService.get_instance()
        self.api_client: EnhancedRestClient = EnhancedRestClient.get_instance()
        self.accountService = AccountService.get_instance()
        self.setupService = SetupService.get_instance()
        self.userOrdersService = UserOrdersService.get_instance(
            on_message=self.on_message_wrapper
        )
        self.cancelled_orders = set[str]()
        self.orderService = OrderService.get_instance()
        self.orderBook = OrderBook.get_instance()
        self.cancelService = CancelService.get_instance()
        self.orders_to_refresh = 4
        self.refresh_interval = 600

    async def start(self) -> None:
        try:
            self.userOrdersService.start()
            self.tokenService.start()
            self.userOrdersService.start()
            self.cancelService.start()
            await self.setup()
        except Exception as e:
            LOGGER.error(f"Error in start: {e}")

    async def setup(self) -> None:
        try:
            await self.setupService.start()
            await self.start_order_cancel_scheduler()
            await self.start_available_funds_scheduler()
            await self.start_rebalance_scheduler()
            await self.start_info_scheduler()
        except Exception as e:
            LOGGER.error(f"Error in setup: {e}")

    async def start_info_scheduler(self) -> None:
        LOGGER.info("Starting info scheduler")
        interval_seconds = self.refresh_interval * 6

        async def print_info() -> None:
            try:
                LOGGER.info("Checking info")
                # TODO move this to service
                total_orders_dict = self.api_client.list_orders(None, ["OPEN"])
                total_orders = from_dict(AllOrdersList, total_orders_dict).orders
                buy_orders = [order for order in total_orders if order.side == "BUY"]
                sell_orders = [order for order in total_orders if order.side == "SELL"]

                LOGGER.info(
                    f"Total Orders: {len(total_orders)}\nBuy Orders: {len(buy_orders)}\nSell Orders: {len(sell_orders)}"
                )
                self.orderBook.log_order_book_info()
            except Exception as e:
                LOGGER.error(f"Error in print_info: {e}")
            finally:
                await self.delayed_execution(interval_seconds, print_info)

        await self.delayed_execution(interval_seconds, print_info)

    async def start_order_cancel_scheduler(self) -> None:
        LOGGER.info("Starting order cancel scheduler")
        interval_seconds = int(self.refresh_interval * 1.33)
        orders_to_refresh = self.orders_to_refresh // 2

        async def cancel_random_order() -> None:
            try:
                LOGGER.info(
                    f"{interval_seconds} seconds have passed, cancelling {self.orders_to_refresh -1} random order(s)"
                )
                buy_order_ids = self.orderBook.get_and_delete_random_orders(
                    OrderSide.BUY,
                    orders_to_refresh,
                )
                if buy_order_ids:
                    await self.cancelService.cancel_orders(buy_order_ids)

                sell_order_ids = self.orderBook.get_and_delete_random_orders(
                    OrderSide.SELL,
                    orders_to_refresh,
                )
                if sell_order_ids:
                    await self.cancelService.cancel_orders(sell_order_ids)
            except Exception as e:
                LOGGER.error(f"Error in cancel_random_order: {e}")
            finally:
                await self.delayed_execution(interval_seconds, cancel_random_order)

        await self.delayed_execution(interval_seconds, cancel_random_order)

    async def start_available_funds_scheduler(self) -> None:
        LOGGER.info("Starting available funds scheduler")
        interval_seconds = self.refresh_interval

        async def check_for_available_funds() -> None:
            try:
                LOGGER.info(
                    f"{interval_seconds} seconds have passed, checking for available funds"
                )
                usdc = self.accountService.get_usdc_available_to_trade()
                dai = self.accountService.get_token_available_to_trade(
                    CurrencyPair.DAI_USDC
                )  # TODO change to generic token
                LOGGER.info(f"USDC: {usdc:.4f}\nDAI: {dai:.4f}")

                if usdc > Decimal(self.orders_to_refresh):
                    await self.fill_buy_ladder(CurrencyPair.DAI_USDC, usdc)

                if dai > Decimal(self.orders_to_refresh):
                    await self.fill_sell_ladder(CurrencyPair.DAI_USDC, dai)
            except Exception as e:
                LOGGER.error(f"Error in check_for_available_funds: {e}")
            finally:
                await self.delayed_execution(
                    interval_seconds, check_for_available_funds
                )

        await self.delayed_execution(interval_seconds, check_for_available_funds)

    async def start_rebalance_scheduler(self) -> None:
        LOGGER.info("Starting re-balance scheduler")
        time = 3600 * 6  # 6 hours

        async def rebalance():
            try:
                LOGGER.info(f"{time/60/60} hours have passed, re-balancing all pairs")
                await self.setupService.re_balance_All()
            except Exception as e:
                LOGGER.error(f"Error in rebalance: {e}")
            finally:
                await self.delayed_execution(time, rebalance)

        await self.delayed_execution(time, rebalance)

    async def handle_order(self, order: OrderEvent) -> None:
        if order.status in (
            OrderStatus.FILLED.value,
            OrderStatus.CANCELLED.value,
            OrderStatus.EXPIRED.value,
            OrderStatus.FAILED.value,
        ):
            await self.orderBook.delete_order_by_id(order.order_id)

    def on_message_wrapper(self, msg: str) -> None:
        asyncio.create_task(self.on_message_async(msg))

    async def on_message_async(self, msg: str) -> None:
        try:
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
                await self.handle_order(order_event)
        except Exception as e:
            LOGGER.error(f"Error in on_message: {e}")

    async def fill_ladder(
        self, pair: CurrencyPair, amount: Decimal, side: OrderSide
    ) -> None:
        try:
            LOGGER.info(
                f"Filling {side.value} ladder for {pair.value} with {amount:.4f}"
            )
            orders_to_refresh = self.orders_to_refresh
            prices = self.orderBook.get_prices_with_lowest_amount(
                pair, side, orders_to_refresh
            )
            LOGGER.info(f"Adding {side.value} orders {prices}")
            if prices:
                order_amount = abs(Decimal(amount)) / len(prices)
                for price in prices:
                    if side == OrderSide.BUY:
                        await self.orderService.buy_order(
                            pair, str(order_amount), price
                        )
                    else:
                        await self.orderService.sell_order(
                            pair, str(order_amount), price
                        )

            else:
                LOGGER.info(f"No {side.value} prices available for {pair.value}")
                LOGGER.info(self.orderBook.orders[pair.value][side.value])
        except Exception as e:
            LOGGER.error(f"Error in fill_ladder: {e}")

    async def fill_buy_ladder(self, pair: CurrencyPair, amount: Decimal) -> None:
        await self.fill_ladder(pair, amount, OrderSide.BUY)

    async def fill_sell_ladder(self, pair: CurrencyPair, amount: Decimal) -> None:
        await self.fill_ladder(pair, amount, OrderSide.SELL)

    async def delayed_execution(self, interval_seconds, coro, *args, **kwargs):
        await asyncio.sleep(delay=interval_seconds)
        return asyncio.create_task(coro(*args, **kwargs))
