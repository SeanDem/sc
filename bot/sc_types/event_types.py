from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class OrderStatus(Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP_LIMIT"


@dataclass
class OrderEvent:
    order_id: str
    client_order_id: str
    cumulative_quantity: str
    leaves_quantity: str
    avg_price: str
    total_fees: str
    status: str
    product_id: str
    creation_time: str
    order_side: str
    order_type: str
    limit_price: Optional[str] = "0"
    stop_price: Optional[str] = "0"


@dataclass
class Event:
    type: Optional[str]
    orders: Optional[List[OrderEvent]] = field(default_factory=list)


@dataclass
class CB_Message:
    channel: str
    client_id: str
    timestamp: str
    sequence_num: int
    events: List[Event]
