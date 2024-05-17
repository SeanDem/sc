from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from .event_types import OrderSide


class CurrencyPair(Enum):
    DAI_USDC = "DAI-USDC"
    GYEN_USDC = "GYEN-USDC"
    PAX_USDC = "PAX-USDC"
    GUSD_USDC = "GUSD-USDC"
    USDT_USDC = "USDT-USDC"
    EUROC_USDC = "EUROC-USDC"
    PYUSD_USDC = "PYUSD-USDC"


class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    token: CurrencyPair
    price: float
    type: OrderSide
