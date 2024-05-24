from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Tuple
from ..other.singleton_base import SingletonBase
from bot.sc_types import *
from typing import Dict


class OrderBook(SingletonBase):
    def __init__(self):
        self.orders: Dict[str, Dict[str, Dict[str, Dict[str, str]]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(dict))
        )

    def update_order(
        self,
        pair: CurrencyPair,
        side: OrderSide,
        price: str,
        order_id: str,
        amt: str,
    ) -> None:
        self.orders[pair.value][side.value][price][order_id] = amt

    def clear_order(
        self, pair: CurrencyPair, side: OrderSide, price: str, order_id: str
    ) -> None:
        if order_id in self.orders[pair.value][side.value][price]:
            self.orders[pair.value][side.value][price][order_id] = "0"

    def get_prices_with_lowest_amount(
        self, pair: CurrencyPair, side: OrderSide
    ) -> List[str]:
        min_amount = Decimal("Infinity")
        prices_with_min_amount = []

        for price, orders in self.orders[pair.value][side.value].items():
            for order_id, amount in orders.items():
                amount_decimal = Decimal(amount)
                if amount_decimal < min_amount:
                    min_amount = amount_decimal
                    prices_with_min_amount = [price]
                elif amount_decimal == min_amount:
                    prices_with_min_amount.append(price)

        return prices_with_min_amount

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
