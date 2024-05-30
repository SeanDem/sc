from collections import defaultdict
from decimal import Decimal
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
