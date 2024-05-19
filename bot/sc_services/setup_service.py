import time
from dacite import from_dict

from limit_order_service import OrderService
from sc_types.event_types import OrderSide
from sc_types.list_orders import AllOrdersList
from services.order_queue import OrderBook
from services.limit_order_service import OrderService
from services.account_service import AccountService
from sc_types.config import CurrencyPair


class SetupService:
    def __init__(
        self,
        accountService: AccountService,
        orderService: OrderService,
        orderBook: OrderBook,
    ):
        self.accountService = accountService
        self.orderService = orderService
        self.orderBook = orderBook

        def setup_initial_orders(self) -> None:
            usdc_amt = self.accountService.get_usdc_available_to_trade()
            token_amt = self.accountService.get_token_available_to_trade(
                CurrencyPair.DAI_USDC
            )
            print(f"USDC: {usdc_amt}")
            print(f"{CurrencyPair.DAI_USDC.value}: {token_amt}")
            buy_prices = self.generate_order_distribution(0.9871, 0.9989, 8)
            buy_qty: str = "{:.4f}".format(usdc_amt / len(buy_prices))
            for price in buy_prices:
                time.sleep(1)
                self.orderService.attempt_buy(CurrencyPair.DAI_USDC, buy_qty, price)
                self.orderBook.update_order(
                    CurrencyPair.DAI_USDC, OrderSide.BUY, price, amount=buy_qty
                )

            sell_prices = [".9999", "1.0006"]
            sell_qty: str = "{:.4f}".format(token_amt / len(sell_prices))
            for price in sell_prices:
                time.sleep(1)
                self.orderService.attempt_sell(CurrencyPair.DAI_USDC, sell_qty, price)
                self.orderBook.update_order(
                    CurrencyPair.DAI_USDC, OrderSide.SELL, price, sell_qty
                )

        def cancel_all_orders(self) -> None:
            data = self.api_client.list_orders()
            orders = from_dict(AllOrdersList, data)
            orderIds = [
                order.order_id for order in orders.orders if order.status == "OPEN"
            ]
            if orderIds:
                self.api_client.cancel_orders(orderIds)
                while True:
                    time.sleep(3)
                    data = self.api_client.list_orders()
                    orders = from_dict(AllOrdersList, data)
                    if all(
                        order.status == "CANCELLED"
                        for order in orders.orders
                        if order.order_id in orderIds
                    ):
                        break
            print("All orders have been cancelled!")

        def generate_order_distribution(
            self, min_val: float, max_val: float, amount: int
        ) -> list:
            step = (max_val - min_val) / (amount - 1)
            distribution = [min_val + i * step for i in range(amount)]
            return [f"{num:.4f}" for num in distribution]