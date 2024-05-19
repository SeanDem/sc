import time
from coinbase.rest import RESTClient
from dacite import from_dict
from bot.sc_types import *
from bot.sc_services.account_service import AccountService
from bot.sc_services.order_service import OrderService
from bot.sc_services.order_book import OrderBook


class SetupService:
    def __init__(self, accountService, orderService, orderBook, api_client) -> None:
        self.accountService: AccountService = accountService
        self.orderService: OrderService = orderService
        self.orderBook: OrderBook = orderBook
        self.api_client: RESTClient = api_client

    def start(self) -> None:
        self.cancel_all_orders()
        self.setup_initial_orders(CurrencyPair.DAI_USDC)

    def setup_initial_orders(self, currency_pair) -> None:
        print("Setting up initial orders...")
        usdc_amt = self.accountService.get_usdc_available_to_trade()
        token_amt = self.accountService.get_token_available_to_trade(
            CurrencyPair.DAI_USDC
        )
        print(f"USDC: {usdc_amt}")
        print(f"{CurrencyPair.DAI_USDC.value}: {token_amt}")
        buy_prices = self.generate_order_distribution(0.9871, 0.9995, 8)
        buy_qty: str = "{:.4f}".format(usdc_amt / len(buy_prices))
        for price in buy_prices:
            time.sleep(1)
            self.orderService.attempt_buy(CurrencyPair.DAI_USDC, buy_qty, price)
            self.orderBook.update_order(
                CurrencyPair.DAI_USDC, OrderSide.BUY, price, amount=buy_qty
            )

        sell_prices = [".9999", "1.0002"]
        sell_qty: str = "{:.4f}".format(token_amt / len(sell_prices))
        for price in sell_prices:
            time.sleep(1)
            self.orderService.attempt_sell(CurrencyPair.DAI_USDC, sell_qty, price)
            self.orderBook.update_order(
                CurrencyPair.DAI_USDC, OrderSide.SELL, price, sell_qty
            )

    def cancel_all_orders(self) -> None:
        print("Cancelling all orders...")
        data = self.api_client.list_orders()
        orders = from_dict(AllOrdersList, data)
        orderIds = [order.order_id for order in orders.orders if order.status == "OPEN"]
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
        if amount == 1:
            return [f"{min_val:.4f}"]
        step = (max_val - min_val) / (amount - 1)
        distribution = [min_val + i * step for i in range(amount)]
        return [f"{num:.4f}" for num in distribution]
