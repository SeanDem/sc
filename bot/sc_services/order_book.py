from collections import defaultdict
from decimal import Decimal
import random
import threading
from typing import Dict, List, Tuple
from bot.other import *
from bot.sc_services import *
from bot.sc_types import *
from typing import Dict


class OrderBook(SingletonBase):
    def __init__(self):
        self.orders: Dict[str, Dict[str, Dict[str, Dict[str, str]]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(dict))
        )
        self.order_lookup: Dict[str, Tuple[str, str, str]] = {}
        self.thread_lock = threading.Lock()
        self.fileUtil = FileUtil.get_instance()

    def get_random_order_id(self, side: OrderSide) -> str:
        attempts = len(self.order_lookup)
        while attempts > 0:
            order = random.choice(list(self.order_lookup.keys()))
            if self.order_lookup[order][1] == side.value:
                return order
            attempts -= 1
        LOGGER.warning("No orders of the specified side in order book")
        return ""

    def get_and_delete_random_order(self, side: OrderSide) -> str:
        random_order_id = self.get_random_order_id(side)
        if random_order_id:
            self.delete_order_by_id(random_order_id)
        return random_order_id

    def get_and_delete_random_orders(self, side: OrderSide, amount=2) -> List[str]:
        # TODO maybe add token as parameter
        orders = []
        for _ in range(amount):
            random_order_id = self.get_and_delete_random_order(side)
            if random_order_id:
                orders.append(random_order_id)
            else:
                LOGGER.warning(f"No more {side.value} orders in order book")
                break
        return orders

    def add_price(self, pair: CurrencyPair, side: OrderSide, price: str) -> None:
        with self.thread_lock:
            self.orders[pair.value][side.value][price] = {}

    def add_prices(self, pair: CurrencyPair, side: OrderSide, prices: List[str]) -> None:
        for price in prices:
            self.add_price(pair, side, price)

    def update_order(self, pair: CurrencyPair,side: OrderSide,price: str,order_id: str,amt: str,) -> None:
        with self.thread_lock:
            self.order_lookup.update({order_id: (pair.value, side.value, price)})
            self.orders[pair.value][side.value][price][order_id] = amt

    def delete_order(self, pair: CurrencyPair, side: OrderSide, price: str, order_id: str) -> None:
        if order_id in self.orders[pair.value][side.value][price]:
            with self.thread_lock:
                del self.orders[pair.value][side.value][price][order_id]

    def delete_order_by_id(self, order_id: str) -> bool:
        with self.thread_lock:
            if order_id in self.order_lookup:
                pair, side, price = self.order_lookup[order_id]
                if order_id in self.orders.get(pair, {}).get(side, {}).get(price, {}):
                    del self.orders[pair][side][price][order_id]
                    del self.order_lookup[order_id]
                    return True
        return False

    def get_prices_with_lowest_amount(self, pair: CurrencyPair, side: OrderSide, maxSize=10) -> List[str]:
        prices_with_min_amount = []
        min_amount = Decimal("Infinity")

        for price, orders in self.orders[pair.value][side.value].items():
            price_decimal = Decimal(price)
            if not orders:
                if Decimal("0") < min_amount:
                    min_amount = Decimal("0")
                    prices_with_min_amount = [price_decimal]
                elif Decimal("0") == min_amount:
                    prices_with_min_amount.append(price_decimal)
            else:
                for order_id, amount in orders.items():
                    amount_decimal = Decimal(amount)
                    if amount_decimal < min_amount:
                        min_amount = amount_decimal
                        prices_with_min_amount = [price_decimal]
                    elif amount_decimal == min_amount:
                        prices_with_min_amount.append(price_decimal)

        prices_with_min_amount.sort()
        if side == OrderSide.BUY:
            prices_with_min_amount.reverse()

        return [str(price) for price in prices_with_min_amount[:maxSize]]

    def get_top_orders(self,pair: CurrencyPair,side: OrderSide,num_ids: int,smallest_price: bool = True,) -> List[Tuple[str, Decimal, Decimal]]:
        order_list = []

        for price, orders in self.orders[pair.value][side.value].items():
            for order_id, amount in orders.items():
                order_list.append((order_id, Decimal(amount), Decimal(price)))

        order_list.sort(key=lambda x: (-x[1], x[2] if smallest_price else -x[2]))

        return [
            (order_id, amount, price)
            for order_id, amount, price in order_list[:num_ids]
        ]

    def log_order_book_info(self):
        for token, sides in self.orders.items():
            LOGGER.info(f"Orders for {token}")

            total_token_amount = 0
            total_token_orders = 0

            for side, prices in sides.items():
                LOGGER.info(f"{side.capitalize()} side orders")

                total_side_amount = 0
                total_side_orders = 0

                for price, orders in prices.items():
                    total_price_amount = sum(
                        float(amount) for amount in orders.values()
                    )
                    number_of_orders = len(orders)

                    LOGGER.info(
                        f"{price}: Total Amount: {total_price_amount}, Orders: {number_of_orders}"
                    )

                    total_side_amount += total_price_amount
                    total_side_orders += number_of_orders

                LOGGER.info(
                    f"Total for {side.capitalize()} side: Amount: {total_side_amount}, Orders: {total_side_orders}"
                )

                total_token_amount += total_side_amount
                total_token_orders += total_side_orders

            LOGGER.info(
                f"Total for {token}: Amount: {total_token_amount}, Orders: {total_token_orders}"
            )
            LOGGER.info("")
