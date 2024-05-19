from collections import defaultdict
from typing import Dict
from bot.sc_types.config import CurrencyPair
from bot.sc_types import *


class OrderBook:
    def __init__(self) -> None:
        self.orders: Dict[CurrencyPair, Dict[OrderSide, Dict[str, str]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: "0"))
        )

    def get_order_amount(self, pair: CurrencyPair, side: OrderSide, price: str) -> str:
        """Get the order quantity for a given pair, side, and price."""
        return self.orders[pair][side][price]

    def update_order(
        self, pair: CurrencyPair, side: OrderSide, price: str, amount: str
    ) -> None:
        """Update the order quantity for a given pair, side, and price."""
        self.orders[pair][side][price] = amount

    def get_lowest_price(self, pair: CurrencyPair, side: OrderSide) -> str:
        """Get the price for the given pair and side that has the smallest quantity."""
        if self.orders[pair][side]:
            return min(self.orders[pair][side], key=lambda k: abs(float(k) - 1))
        return "1.001"

    def display_orders(self) -> None:
        """Helper function to display the order book nicely formatted."""
        for pair, sides in self.orders.items():
            print(f"{pair}:")
            for side, prices in sides.items():
                print(f"  {side}:")
                for price, qty in sorted(prices.items(), key=lambda x: float(x[0])):
                    print(f"    Price: {price}, Quantity: {qty}")
