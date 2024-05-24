from turtle import setup
import numpy as np
from decimal import ROUND_DOWN, Decimal
from logging import config
from os import error
import time
from typing import LiteralString
from coinbase.rest import RESTClient
from dacite import from_dict
from bot.sc_types import *
from bot.sc_services import *
from bot.config import config


class SetupService:
    def __init__(
        self,
        accountService = account_service_singleton,
        orderService = order_service_singleton,
        orderBook = order_book_singleton,
        api_client = rest_client_singleton,
        config: dict[CurrencyPair, CurrencyPairConfig] = config,
    ) -> None:
        self.accountService: AccountService = accountService
        self.orderService: OrderService = orderService
        self.orderBook: OrderBook = orderBook
        self.api_client: RESTClient = api_client
        self.config = config

    def start(self) -> None:
        self.validate_configs()
        self.cancel_all_orders()
        for pair, config in self.config.items():
            self.setup_initial_orders(config)

    def re_balance_All(self) -> None:
        for pair, config in self.config.items():
            self.re_balance_pair(pair)

    def re_balance_pair(self, pair: CurrencyPair) -> None:
        self.cancel_orders(pair)
        self.setup_initial_orders(config[pair])

    def setup_initial_orders(self, config: CurrencyPairConfig) -> None:
        print(f"Setting up initial orders for {config.pair.value}...")
        token_amt = Decimal(
            self.accountService.get_token_available_to_trade(config.pair)
        )

        account_balance = self.accountService.get_account_balance()
        funds_allocated = Decimal(account_balance) * Decimal(config.percent_of_funds)
        usdc_available: Decimal = funds_allocated - Decimal(token_amt)
        print(f"Account balance: {float(account_balance):.2f} USD")
        print(f"Allocated {config.pair.value}: {funds_allocated:.2f} USD")
        print(f"Available {config.pair.value.split('-')[0]}: {token_amt:.4f}")
        print(f"Available USDC: {usdc_available:.4f} USD")

        buy_prices = self.generate_order_distribution(
            float(config.buy_range.start),
            float(config.buy_range.end),
            config.buy_range.num_steps,
            config.buy_range.skew,
        )

        buy_qty: Decimal = usdc_available / config.buy_range.num_steps
        buy_qty = self.adjust_precision(buy_qty)
        if Decimal(buy_qty) > Decimal(0.05):
            for price in buy_prices:
                time.sleep(0.15)
                order_id = self.orderService.buy_order(config.pair, str(buy_qty), price)
                if order_id:
                    self.orderBook.update_order(
                        config.pair,
                        OrderSide.BUY,
                        price,
                        order_id,
                        str(buy_qty),
                    )

        sell_prices = self.generate_order_distribution(
            float(config.sell_range.start),
            float(config.sell_range.end),
            config.sell_range.num_steps,
            config.sell_range.skew,
        )
        sell_qty = token_amt / config.sell_range.num_steps
        sell_qty = self.adjust_precision(sell_qty)
        print(f"Token amount: {token_amt}")
        print(f"Sell quantity: {sell_qty}")
        if Decimal(sell_qty) > Decimal(0.05):
            for price in sell_prices:
                time.sleep(0.15)
                order_id = self.orderService.attempt_sell(
                    config.pair, str(buy_qty), price
                )
                if order_id:
                    self.orderBook.update_order(
                        config.pair,
                        OrderSide.SELL,
                        price,
                        order_id,
                        str(buy_qty),
                    )

    def cancel_and_verify_orders(self, orderIds, max_retries=15):
        if orderIds:
            self.api_client.cancel_orders(orderIds)
            retries = 0
            while retries < max_retries:
                time.sleep(0.1)
                data = self.api_client.list_orders()
                orders = from_dict(AllOrdersList, data)
                if all(
                    order.status == OrderStatus.CANCELLED.value
                    for order in orders.orders
                    if order.order_id in orderIds
                ):
                    print("All orders have been cancelled!")
                    break
                retries += 1
            else:
                print(f"All orders could not be cancelled after {max_retries} retries.")

    def cancel_orders(self, pair: CurrencyPair) -> None:
        print(f"Cancelling orders for {pair.value}...")
        data = self.api_client.list_orders()
        orders = from_dict(AllOrdersList, data)
        orderIds = [
            order.order_id
            for order in orders.orders
            if order.product_id == pair.value and order.status == "OPEN"
        ]
        self.cancel_and_verify_orders(orderIds)

    def cancel_all_orders(self, max_retries: int = 3) -> None:
        print("Cancelling all orders...")
        data = self.api_client.list_orders()
        orders = from_dict(AllOrdersList, data)
        orderIds = [
            order.order_id
            for order in orders.orders
            if order.status == "OPEN" or order.status == "PENDING"
        ]
        self.cancel_and_verify_orders(orderIds, max_retries)

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
        print(f"Generated distribution: {distribution}")
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

                if not (buy_start < buy_end):
                    errors.append(
                        f"{pair}: Buy range start {settings.buy_range.start} should be less than end {settings.buy_range.end}."
                    )
                if not (sell_start < sell_end):
                    errors.append(
                        f"{pair}: Sell range start {settings.sell_range.start} should be less than end {settings.sell_range.end}."
                    )
            except:
                errors.append(f"{pair}: Invalid range values.")
        if total_percent != 1:
            errors.append(
                f"Total percent_of_funds should add up to 1. Currently at {total_percent}."
            )
        if errors:
            print("Errors found in configurations:")
            raise error("\n".join(errors))
        else:
            print("All configurations are logically sound.")

    def adjust_precision(self, size: Decimal, decimals=4) -> Decimal:
        return size.quantize(Decimal("1." + "0" * decimals), rounding=ROUND_DOWN)

setup_service_singleton = SetupService()