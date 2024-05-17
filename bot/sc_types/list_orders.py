from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


class OrderStatus(Enum):
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


@dataclass
class LimitGoodTillCancelled:
    base_size: str
    limit_price: str
    post_only: bool


@dataclass
class OrderConfiguration:
    limit_limit_gtc: Optional[LimitGoodTillCancelled]


@dataclass
class Order:
    order_id: str
    product_id: str
    user_id: str
    side: str
    client_order_id: str
    status: str
    time_in_force: str
    created_time: str
    completion_percentage: str
    filled_size: str
    average_filled_price: str
    fee: str
    number_of_fills: str
    filled_value: str
    pending_cancel: bool
    size_in_quote: bool
    total_fees: str
    size_inclusive_of_fees: bool
    total_value_after_fees: str
    trigger_status: str
    order_type: str
    reject_reason: str
    settled: bool
    product_type: str
    reject_message: str
    cancel_message: str
    order_placement_source: str
    outstanding_hold_amount: str
    is_liquidation: bool
    last_fill_time: Optional[str]
    leverage: str
    margin_type: str
    retail_portfolio_id: str
    order_configuration: OrderConfiguration
    edit_history: List[dict] = field(default_factory=list)


@dataclass
class AllOrdersList:
    orders: List[Order]
