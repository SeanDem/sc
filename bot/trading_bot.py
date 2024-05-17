from .services.order_queue import OrderQueue
from .keys import api_key, api_secret
from .services.events_service import EventService
from .clients import REST_CLIENT
from .services.token_service import TokenService
from .services.order_service import OrderService
from .services.account_service import AccountService
from .sc_types.config import CurrencyPair


class TradingBot:
    def __init__(self) -> None:
        self.api_client = REST_CLIENT
        self.accountService = AccountService()
        self.orderService = OrderService()
        self.tokenService = TokenService()
        self.eventService = EventService(api_key=api_key, api_secret=api_secret)
        self.orderQueue = OrderQueue()

    def run(self) -> None:
        print("Starting bot...")
        self.setupQueue()
        self.setupInitialOrders()

    def attempt_buy(self, pair: CurrencyPair, size: float, price: str) -> None:
        usdc_available = self.accountService.get_usdc_available_to_trade()
        qty = min(usdc_available, size)
        print(f"Available USDC: {usdc_available}\n")
        if usdc_available > 1 and usdc_available > size:
            self.orderService.buyOrder(pair, price=price, size=qty)
            print(f"Created buy order for {pair.value} at {price} for {qty}")

    def attempt_sell(self, pair: CurrencyPair, size: float, price: str) -> None:
        token_available = self.accountService.get_token_available_to_trade(pair)
        qty = min(token_available, size)
        print(f"Available {pair.value}: {token_available}\n")
        if token_available > 1 and token_available > size:
            self.orderService.sellOrder(pair, price=price, size=qty)
            print(f"Created sell order for {pair.value} at {price} for {qty}")

    def setupQueue(self) -> None:
        self.orderQueue.addPairConfig(
            CurrencyPair.DAI_USDC,
            ["0.9921", " 0.9941", " 0.9961"],
            ["1.0014", "1.004", "0.9994"],
        )

    def setupInitialOrders(self) -> None:
        buy_order_size_per = (
            self.accountService.get_usdc_available_to_trade()
            / self.orderQueue.getBuyQueueSize()
        )
        for _ in range(self.orderQueue.getBuyQueueSize()):
            order = self.orderQueue.getBuyOrder()
            self.attempt_buy(order.pair, buy_order_size_per, order.price)

        sell_order_size_per = (
            self.accountService.get_token_available_to_trade(CurrencyPair.DAI_USDC)
            / self.orderQueue.getSellQueueSize()
        )
        for _ in range(self.orderQueue.getSellQueueSize()):
            order = self.orderQueue.getSellOrder()
            self.attempt_sell(order.pair, sell_order_size_per, order.price)
