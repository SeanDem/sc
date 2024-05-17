from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum, auto


class OrderStatus(Enum):
    PENDING = auto()
    OPEN = auto()
    FILLED = auto()
    CANCELLED = auto()
    EXPIRED = auto()
    FAILED = auto()


class OrderSide(Enum):
    BUY = auto()
    SELL = auto()


class OrderType(Enum):
    LIMIT = auto()
    MARKET = auto()
    STOP_LIMIT = auto()


@dataclass
class OrderEvent:
    order_id: str  # Unique identifier of the order
    client_order_id: str  # Unique identifier specified by the client
    cumulative_quantity: float  # Amount the order is filled, in base currency
    leaves_quantity: float  # Amount remaining in the currency the order was placed
    avg_price: float  # Average filled price of the order so far
    total_fees: float  # Commission paid for the order
    status: OrderStatus  # Current status of the order
    product_id: str  # The product ID for which this order was placed
    creation_time: datetime  # When the order was placed
    order_side: OrderSide  # Side of the order: BUY or SELL
    order_type: OrderType  # Type of order: Limit, Market, Stop Limit
    limit_price: Optional[float] = 0  # Limit price, if applicable
    stop_price: Optional[float] = 0  # Stop price, if applicable
