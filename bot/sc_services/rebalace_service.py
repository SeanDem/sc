from typing import Set
from bot.sc_types import *
from bot.sc_services import *
from bot.other import *


class RebalanceService(SingletonBase):
    def __init__(self):
        self.api_client = EnhancedRestClient.get_instance()
        self.orderBook = OrderBook.get_instance()
        self.orders_to_cancel: Set[str] = set()
