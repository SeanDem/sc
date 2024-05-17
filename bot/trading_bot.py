from ast import Or
from re import S
import time
from .keys import api_key, api_secret
from .services.events_service import EventService
from .clients import REST_CLIENT
from .services.token_service import TokenService
from .services.order_service import OrderService
from .services.account_service import AccountService
from .sc_types.config import CurrencyPair
from .services.order_service import OrderQueue

class TradingBot:
    def __init__(self) -> None:
        self.api_client = REST_CLIENT
        self.accountService = AccountService()
        self.orderService = OrderService()
        self.tokenService = TokenService()
        self.eventService = EventService(
            api_key=api_key, api_secret=api_secret
        )
        self.orderQueue =  OrderQueue()
        

    # def run(self) -> None:
    #     self.eventService.testSub()
    #     while True:
    #         try:
    #             for pair in self.config.get_all_pairs():
    #                 self.trade_cycle(pair)
    #         except Exception as e:
    #             print(f"Error: {e}")
    #             print("Restarting trading loop in 10 seconds...")
    #             time.sleep(10)

    
    # def trade_cycle(self, pair: CurrencyPair) -> None:
        
    #     for self.config.get_all_buy_prices(pair):
    #         current_price = self.tokenService.getTokenPrice(pair)
    #         self.attempt_buy(current_price)
            
    #     self.attempt_buy(current_price)

    #     self.attempt_sell(current_price)
    #     time.sleep(5)


    # def attempt_buy(self, price) -> None:
    #     if price < 1.0:
    #         usdc_available = self.accountService.get_usdc_available_to_trade()
    #         print(f"Available USDC: {usdc_available}\n")
    #         if usdc_available > 1:
    #             self.orderService.buyOrder(usdc_available)

    # def attempt_sell(self, price) -> None:
    #     if price > 1.0:
    #         dai_available = self.accountService.get_token_available_to_trade()
    #         print(f"Available DAI: {dai_available}\n")
    #         if dai_available > 1:
    #             self.orderService.sellOrder(dai_available)

    
    def setupQueue(self) -> None:
        