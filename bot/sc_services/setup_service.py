import asyncio
from decimal import ROUND_DOWN, Decimal
from typing import LiteralString
from coinbase.rest import RESTClient
import numpy as np

from bot.other.logger import LOGGER
from bot.other.singleton_base import SingletonBase
from bot.sc_types import *
from bot.sc_services import *
from bot.config import sc_config


class SetupService(SingletonBase):
    def __init__(
        self,
    ) -> None:
        self.accountService: AccountService = AccountService.get_instance()
        self.orderService: OrderService = OrderService.get_instance()
        self.orderBook: OrderBook = OrderBook.get_instance()
        self.api_client: RESTClient = EnhancedRestClient.get_instance()
        self.cancelService: CancelService = CancelService.get_instance()
        self.config = sc_config  # TODO convert to service

    async def start(self) -> None:
        try:
            self.validate_configs()
            await self.cancelService.cancel_all_orders()
            for pair, config in self.config.items():
                await self.setup_initial_orders(config)
        except Exception as e:
            LOGGER.error(f"Error in start: {e}")

    async def re_balance_All(self) -> None:
        for pair, config in self.config.items():
            await self.re_balance_pair(pair)

    async def re_balance_pair(self, pair: CurrencyPair) -> None:
        try:
            await self.cancelService.cancel_all_orders(pair)
            await self.setup_initial_orders(self.config[pair])
        except Exception as e:
            LOGGER.error(f"Error in re_balance_pair: {e}")

    async def setup_initial_orders(self, config: CurrencyPairConfig) -> None:
        LOGGER.info(f"Setting up initial orders for {config.pair.value}...")
        token_amt = Decimal(
            self.accountService.get_token_available_to_trade(config.pair)
        )
        usdc_available = self.accountService.get_usdc_available_to_trade()
        LOGGER.info(f"Available {config.pair.value.split('-')[0]}: {token_amt:.4f}")
        LOGGER.info(f"Available USDC: {usdc_available:.4f} USD")

        buy_prices = self.generate_order_distribution(
            float(config.buy_range.start),
            float(config.buy_range.end),
            config.buy_range.num_steps,
            config.buy_range.skew,
        )
        await self.orderBook.add_prices(
            config.pair, OrderSide.BUY, self.npy_to_list(buy_prices)
        )

        buy_qty: Decimal = (
            usdc_available / config.buy_range.num_steps
            if config.buy_range.num_steps != 0
            else Decimal(1)
        )
        buy_qty = self.adjust_precision(buy_qty)
        if Decimal(buy_qty) > Decimal(0.05):
            print(buy_qty)
            for price in buy_prices:
                await asyncio.sleep(0.2)
                order_id = await self.orderService.buy_order(
                    config.pair, str(buy_qty), price
                )
                print(order_id)
                if order_id:
                    await self.orderBook.update_order(
                        config.pair,
                        OrderSide.BUY,
                        price,
                        order_id,
                        str(buy_qty),
                    )
        if config.sell_range.start == config.sell_range.end:
            sell_prices = [config.sell_range.start]
            config.sell_range.num_steps = 1
        else:
            sell_prices = self.generate_order_distribution(
                float(config.sell_range.start),
                float(config.sell_range.end),
                config.sell_range.num_steps,
                config.sell_range.skew,
            )
            sell_prices = self.npy_to_list(sell_prices)

        await self.orderBook.add_prices(config.pair, OrderSide.SELL, sell_prices)

        sell_qty = (
            token_amt / config.sell_range.num_steps
            if config.sell_range.num_steps != 0
            else Decimal(1)
        )

        sell_qty = self.adjust_precision(sell_qty)
        if Decimal(sell_qty) > Decimal(0.05):
            for price in sell_prices:
                await asyncio.sleep(0.2)
                order_id = await self.orderService.sell_order(
                    config.pair, str(sell_qty), price
                )
                if order_id:
                    await self.orderBook.update_order(
                        config.pair,
                        OrderSide.SELL,
                        price,
                        order_id,
                        str(sell_qty),
                    )

    def generate_order_distribution(
        self, min_val: float, max_val: float, amount: int, skew=None
    ):
        x = np.linspace(0, 1, amount)
        if skew is not None:
            factor = skew.factor
            if skew.direction == SkewDirection.END:
                x = x ** (1 / factor)
            elif skew.direction == SkewDirection.START:
                x = 1 - (1 - x) ** (1 / factor)
            elif skew.direction == SkewDirection.MID:
                x = np.sin(x * np.pi - np.pi / 2 + np.pi * factor / 2) / 2 + 0.5
            distribution = min_val + (max_val - min_val) * x
        else:
            distribution = np.linspace(min_val, max_val, amount)
        LOGGER.info(f"Generated distribution: {distribution}")
        return distribution

    def validate_configs(self) -> LiteralString | None:
        errors = []
        total_percent = 0
        for pair, settings in self.config.items():
            try:
                percent_funds = Decimal(settings.percent_of_funds)
                total_percent += percent_funds
                if not (0 <= percent_funds <= 1):
                    errors.append(
                        f"{pair}: percent_of_funds {settings.percent_of_funds} should be between 0 and 1."
                    )
            except:
                errors.append(
                    f"{pair}: Invalid percent_of_funds value {settings.percent_of_funds}."
                )
            try:
                buy_start = Decimal(settings.buy_range.start)
                buy_end = Decimal(settings.buy_range.end)
                sell_start = Decimal(settings.sell_range.start)
                sell_end = Decimal(settings.sell_range.end)

                if not (buy_start <= buy_end):
                    errors.append(
                        f"{pair}: Buy range start {settings.buy_range.start} should be less then or equal to end {settings.buy_range.end}."
                    )
                if not (sell_start <= sell_end):
                    errors.append(
                        f"{pair}: Sell range start {settings.sell_range.start} should be then or equal to end {settings.sell_range.end}."
                    )
            except:
                errors.append(f"{pair}: Invalid range values.")
        if total_percent != 1:
            errors.append(
                f"Total percent_of_funds should add up to 1. Currently at {total_percent}."
            )
        if errors:
            LOGGER.info("Errors found in configurations:")
            raise ValueError("\n".join(errors))
        else:
            LOGGER.info("All configurations are logically sound.")

    def adjust_precision(self, size: Decimal, decimals=4) -> Decimal:
        return size.quantize(Decimal("1." + "0" * decimals), rounding=ROUND_DOWN)

    def npy_to_list(self, array: np.ndarray) -> list[str]:
        return [
            str(self.adjust_precision(Decimal(str(price)))) for price in array.tolist()
        ]
