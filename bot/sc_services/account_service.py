from decimal import Decimal
from dacite import from_dict
from coinbase.rest import RESTClient
from bot.sc_types import *


class AccountService:
    def __init__(self, api_client: RESTClient) -> None:
        self.api_client = api_client
        self.uuid = "5218e553-84ec-54ec-a572-df8243f3d5ba"

    def getPortfolioBreakdown(self) -> PortfolioBreakdown:
        return from_dict(
            data_class=PortfolioBreakdown,
            data=self.api_client.get_portfolio_breakdown(self.uuid),
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
