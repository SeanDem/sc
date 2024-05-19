from dataclasses import dataclass, field
from typing import List, Optional


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
class WS_Message:
    channel: str
    client_id: str
    timestamp: str
    sequence_num: int
    events: List[Event]
