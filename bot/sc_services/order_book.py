from collections import defaultdict
from decimal import Decimal
from typing import Dict
from sc_types import *


class OrderBook:
    def __init__(self) -> None:
        self.orders: Dict[CurrencyPair, Dict[OrderSide, Dict[str, str]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: "0"))
        )

    def get_order_amount(self, pair: CurrencyPair, side: OrderSide, price: str) -> str:
        return self.orders[pair][side][price]

    def update_order(
        self, pair: CurrencyPair, side: OrderSide, price: str, amount: str
    ) -> None:
        self.orders[pair][side][price] = amount

    def get_lowest_qty_price(self, pair: CurrencyPair, side: OrderSide) -> str:
        if self.orders[pair][side]:
            return min(self.orders[pair][side], key=lambda k: abs(Decimal(k) - 1))
        return "1.00"
