from decimal import Decimal
from logging import config
import time
from typing import LiteralString
from coinbase.rest import RESTClient
from dacite import from_dict
from sc_types import *
from sc_services import *
from config import config


class SetupService:
    def __init__(
        self,
        accountService,
        orderService,
        orderBook,
        api_client,
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
        usdc_amt = self.accountService.get_usdc_available_to_trade()
        token_amt = self.accountService.get_token_available_to_trade(config.pair)

        account_balance = self.accountService.get_account_balance()
        funds_allocated = (
            float(account_balance) * float(config.percent_of_funds)
        ) - token_amt
        print(f"Total account balance: {float(account_balance):.2f} USD")
        print(
            f"Allocated for trading on {config.pair.value}: {funds_allocated:.2f} USD"
        )
        print(f"Available {config.pair.value.split('-')[0]} tokens: {token_amt:.4f}")
        print(f"USDC available for trading: {usdc_amt:.2f} USD")
        print(f"USDC allocated for buying: {funds_allocated:.2f} USD")

        buy_prices = self.generate_order_distribution(
            float(config.buy_range.start),
            min(float(config.buy_range.end), float(config.max_buy_price)),
            config.buy_range.num_steps,
        )
        buy_qty = "{:.4f}".format(funds_allocated / len(buy_prices))
        for price in buy_prices:
            time.sleep(0.1)
            self.orderService.attempt_buy(config.pair, buy_qty, price)
            self.orderBook.update_order(
                config.pair, OrderSide.BUY, price, amount=buy_qty
            )

        sell_prices = self.generate_order_distribution(
            max(float(config.sell_range.start), float(config.min_sell_price)),
            float(config.sell_range.end),
            config.sell_range.num_steps,
        )
        sell_qty = "{:.4f}".format(token_amt / len(sell_prices))
        for price in sell_prices:
            time.sleep(0.1)
            self.orderService.attempt_sell(config.pair, sell_qty, price)
            self.orderBook.update_order(config.pair, OrderSide.SELL, price, sell_qty)

    def cancel_and_verify_orders(self, orderIds, max_retries=3):
        if orderIds:
            self.api_client.cancel_orders(orderIds)

            retries = 0
            while retries < max_retries:
                time.sleep(3)
                print(
                    f"Checking if all orders have been cancelled... (Attempt {retries + 1})"
                )
                try:
                    data = self.api_client.list_orders()
                    orders = from_dict(AllOrdersList, data)
                    if all(
                        order.status == "CANCELLED"
                        for order in orders.orders
                        if order.order_id in orderIds
                    ):
                        print("All orders have been cancelled!")
                        break
                except Exception as e:
                    print(f"An error occurred: {e}")
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
        orderIds = [order.order_id for order in orders.orders if order.status == "OPEN"]
        self.cancel_and_verify_orders(orderIds, max_retries)

    def generate_order_distribution(
        self, min_val: float, max_val: float, amount: int
    ) -> list:
        if amount == 1:
            return [f"{min_val:.4f}"]
        step = (max_val - min_val) / (amount - 1)
        distribution = [min_val + i * step for i in range(amount)]
        return [f"{num:.4f}" for num in distribution]

    def validate_configs(self) -> LiteralString | None:
        errors = []
        total_percent = 0
        for pair, settings in self.config.items():
            try:
                percent_funds = Decimal(settings.percent_of_funds)
                total_percent += percent_funds
                if not (0 < percent_funds < 1):
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
            return "\n".join(errors)
        else:
            print("All configurations are logically sound.")
