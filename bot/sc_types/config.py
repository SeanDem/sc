from dataclasses import dataclass
from enum import Enum
from .event_types import OrderSide


class CurrencyPair(Enum):
    DAI_USDC = "DAI-USDC"
    GYEN_USDC = "GYEN-USDC"
    PAX_USDC = "PAX-USDC"
    GUSD_USDC = "GUSD-USDC"
    USDT_USDC = "USDT-USDC"
    EUROC_USDC = "EUROC-USDC"
    PYUSD_USDC = "PYUSD-USDC"


@dataclass
class QueueOrder:
    pair: CurrencyPair
    price: str
    qty: str
    type: OrderSide
