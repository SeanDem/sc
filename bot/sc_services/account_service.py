from decimal import Decimal
from dacite import from_dict
from bot.other.singleton_base import SingletonBase
from bot.sc_types import *
from bot.sc_services import *
from dacite import from_dict


class AccountService(SingletonBase):
    def __init__(self) -> None:
        self.api_client = EnhancedRestClient.get_instance()
        self.uuid = "5218e553-84ec-54ec-a572-df8243f3d5ba"

    def getPortfolioBreakdown(self) -> PortfolioBreakdown:
        return from_dict(
            data_class=PortfolioBreakdown,
            data=self.api_client.get_portfolio_breakdown(self.uuid),
        )

    def get_pending_orders(self, product_id: CurrencyPair, side: OrderSide) -> Decimal:
        try:
            orders_res = self.api_client.list_orders(
                product_id=product_id.value,
                order_side=side.value,
                order_status=["OPEN"],
            )
        except Exception as e:
            print(f"Error getting pending orders: {e}")
            return Decimal(0)

        orders = from_dict(AllOrdersList, orders_res)
        sum = Decimal(0)
        for order in orders.orders:
            print(order.filled_size)
            print(order.filled_value)
            sum += Decimal(order.filled_size)
        return sum

    def get_open_orders(self, product_id: CurrencyPair) -> AllOrdersList:
        return from_dict(
            AllOrdersList,
            self.api_client.list_orders(product_id=product_id.value, status="OPEN"),
        )

    def get_available_to_trade(self, asset: str) -> float:
        portfolio = self.getPortfolioBreakdown()
        available_to_trade = 0.0
        for position in portfolio.breakdown.spot_positions:
            if position.asset == asset:
                available_to_trade += position.available_to_trade_fiat
        return available_to_trade

    def get_token_available_to_trade(
        self,
        pair: CurrencyPair,
    ) -> Decimal:
        currency = pair.value.split("-")[0]
        return Decimal(self.get_available_to_trade(currency))

    def get_usdc_available_to_trade(self) -> float:
        return self.get_available_to_trade("USDC")

    def get_account_balance(self) -> str:
        portfolio = self.getPortfolioBreakdown()
        return portfolio.breakdown.portfolio_balances.total_balance.value
