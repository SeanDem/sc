from collections import defaultdict
from decimal import Decimal
import random
from typing import Dict, List, Tuple
from bot.other import *
from bot.sc_services import *
from bot.sc_types import *
from typing import Dict


class OrderBook(SingletonBase):
    def __init__(self):
        # orders[pair][side][price][order_id] = amount
        self.orders: Dict[str, Dict[str, Dict[str, Dict[str, str]]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(dict))
        )
        self.order_lookup: Dict[str, Tuple[str, str, str]] = {}

    def get_random_order_id(self, side: OrderSide) -> str:
        if not self.order_lookup:
            LOGGER.warning("No orders in order book")
            return ""
        order = random.choice(list(self.order_lookup.keys()))
        if self.order_lookup[order][1] == side.value:
            return order
        else:
            return self.get_random_order_id(side)

    def get_and_delete_random_order(self, side: OrderSide) -> str:
        random_order_id = self.get_random_order_id(side)
        self.delete_order_by_id(random_order_id)
        return random_order_id

    def get_and_delete_random_orders(self, side: OrderSide, amount=2) -> List[str]:
        orders = []
        for _ in range(amount):
            random_order_id = self.get_and_delete_random_order(side)
            if random_order_id:
                orders.append(random_order_id)
        return orders

    def add_price(self, pair: CurrencyPair, side: OrderSide, price: str) -> None:
        self.orders[pair.value][side.value][price] = {}

    def add_prices(
        self, pair: CurrencyPair, side: OrderSide, prices: List[str]
    ) -> None:
        for price in prices:
            self.add_price(pair, side, price)

    def update_order(
        self,
        pair: CurrencyPair,
        side: OrderSide,
        price: str,
        order_id: str,
        amt: str,
    ) -> None:
        self.order_lookup.update({order_id: (pair.value, side.value, price)})
        self.orders[pair.value][side.value][price][order_id] = amt

    def delete_order(
        self, pair: CurrencyPair, side: OrderSide, price: str, order_id: str
    ) -> None:
        if order_id in self.orders[pair.value][side.value][price]:
            del self.orders[pair.value][side.value][price][order_id]

    def delete_order_by_id(self, order_id: str) -> bool:
        if order_id in self.order_lookup:
            pair, side, price = self.order_lookup[order_id]
            del self.orders[pair][side][price][order_id]
            del self.order_lookup[order_id]
            return True
        return False

    def get_prices_at_zero_amount(
        self, pair: CurrencyPair, side: OrderSide, maxSize=10
    ) -> List[str]:
        zero_amount_prices = []
        for price, orders in self.orders[pair.value][side.value].items():
            if not orders:
                numeric_price = Decimal(price)
                zero_amount_prices.append(numeric_price)
        zero_amount_prices.sort()
        if OrderSide.BUY == side:
            zero_amount_prices.reverse()
        return [str(price) for price in zero_amount_prices[:maxSize]]

    def get_prices_with_lowest_amount(
        self, pair: CurrencyPair, side: OrderSide, maxSize=10
    ) -> List[str]:
        min_amount = Decimal("Infinity")
        prices_with_min_amount = []

        for price, orders in self.orders[pair.value][side.value].items():
            for order_id, amount in orders.items():
                amount_decimal = Decimal(amount)
                price_decimal = Decimal(price)
                if amount_decimal < min_amount:
                    min_amount = amount_decimal
                    prices_with_min_amount = [price_decimal]
                elif amount_decimal == min_amount:
                    prices_with_min_amount.append(price_decimal)

        prices_with_min_amount.sort()
        if side == OrderSide.BUY:
            prices_with_min_amount.reverse()

        return [str(price) for price in prices_with_min_amount[:maxSize]]

    def get_top_orders(
        self,
        pair: CurrencyPair,
        side: OrderSide,
        num_ids: int,
        smallest_price: bool = True,
    ) -> List[Tuple[str, Decimal, Decimal]]:
        order_list = []

        for price, orders in self.orders[pair.value][side.value].items():
            for order_id, amount in orders.items():
                order_list.append((order_id, Decimal(amount), Decimal(price)))

        order_list.sort(key=lambda x: (-x[1], x[2] if smallest_price else -x[2]))

        return [
            (order_id, amount, price)
            for order_id, amount, price in order_list[:num_ids]
        ]
