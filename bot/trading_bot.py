import time
from .keys import api_key, api_secret
from .services.events_service import EventService

from .clients import REST_CLIENT
from .services.token_service import TokenService
from .services.order_service import OrderService
from .services.account_service import AccountService
from .stypes.config import BotConfig


class TradingBot:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.api_client = REST_CLIENT
        self.accountService = AccountService(config)
        self.orderService = OrderService(config)
        self.tokenService = TokenService(config)
        self.eventService = EventService(api_key=api_key, api_secret=api_secret)

    def run(self) -> None:
        while True:
            try:
                self.trade_cycle()
            except Exception as e:
                print(f"Error: {e}")
                print("Restarting trading loop in 10 seconds...")
                time.sleep(10)

    def trade_cycle(self) -> None:
        current_price = self.fetch_current_price()
        self.attempt_buy(current_price)
        self.attempt_sell(current_price)
        time.sleep(5)

    def fetch_current_price(self) -> float:
        price = self.tokenService.getTokenPrice(self.config.pair)
        print(f"Current Price: {price}")
        return price

    def attempt_buy(self, price) -> None:
        if price < self.config.price_ceiling:
            usdc_available = self.accountService.get_usdc_available_to_trade()
            print(f"Available USDC: {usdc_available}\n")
            if usdc_available > 1:
                self.orderService.buyOrder(usdc_available)

    def attempt_sell(self, price) -> None:
        if price > self.config.price_floor:
            dai_available = self.accountService.get_token_available_to_trade()
            print(f"Available DAI: {dai_available}\n")
            if dai_available > 1:
                self.orderService.sellOrder(dai_available)
