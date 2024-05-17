from ..sc_types.event_types import OrderSide
from ..sc_types.config import CurrencyPair
from ..sc_types import Order
from queue import Queue


class OrderQueue:
    def __init__(self) -> None:
        self.buyQueue = Queue()
        self.sellQueue = Queue()

    def addSalesConfig(self, pair: CurrencyPair, sell_prices: list) -> None:
        for price in sell_prices:
            self.sellQueue.put(Order(pair, price, OrderSide.SELL))

    def addBuysConfig(self, pair: CurrencyPair, buy_prices: list) -> None:
        for price in buy_prices:
            self.buyQueue.put(Order(pair, price, OrderSide.BUY))

    def addPairConfig(
        self, pair: CurrencyPair, buy_prices: list, sell_prices: list
    ) -> None:
        self.addBuysConfig(pair, buy_prices)
        self.addSalesConfig(pair, sell_prices)

    def getBuyOrder(self) -> Order:
        return self.buyQueue.get()

    def getSellOrder(self) -> Order:
        return self.sellQueue.get()

    def putBuyOrder(self, order: Order) -> None:
        self.buyQueue.put(order)

    def putSellOrder(self, order: Order) -> None:
        self.sellQueue.put(order)

    def getBuyQueueSize(self) -> int:
        return self.buyQueue.qsize()

    def getSellQueueSize(self) -> int:
        return self.sellQueue.qsize()
