from dacite import from_dict
from main import CLIENT
from stypes import PortfolioBreakdown
from coinbase.rest import RESTClient

class AccountService:
    api_client: RESTClient = CLIENT
    uuid = "5218e553-84ec-54ec-a572-df8243f3d5ba"
        
    def getPortfolioBreakdown(self) -> PortfolioBreakdown:
        return from_dict(data_class=PortfolioBreakdown, data= self.api_client.get_portfolio_breakdown(self.uuid))
    
    def get_usdc_available_to_trade(self) -> float:
        portfolio = self.getPortfolioBreakdown()
        usdc_available = 0.0
        for position in portfolio.breakdown.spot_positions:
            if position.asset == 'USDC' and position.is_cash:
                usdc_available += position.available_to_trade_fiat
        return usdc_available