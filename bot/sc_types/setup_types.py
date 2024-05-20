from dataclasses import dataclass
from enum import Enum
from sc_types import *


class CurrencyPair(Enum):
    DAI_USDC = "DAI-USDC"
    GYEN_USDC = "GYEN-USDC"
    PAX_USDC = "PAX-USDC"
    GUSD_USDC = "GUSD-USDC"
    USDT_USDC = "USDT-USDC"
    EUROC_USDC = "EUROC-USDC"
    PYUSD_USDC = "PYUSD-USDC"


@dataclass
class RangeConfig:
    start: str
    end: str
    num_steps: int


@dataclass
class CurrencyPairConfig:
    pair: CurrencyPair
    percent_of_funds: str
    max_buy_price: str
    min_sell_price: str
    buy_range: RangeConfig
    sell_range: RangeConfig
