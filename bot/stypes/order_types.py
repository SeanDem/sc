from dataclasses import dataclass
from typing import Optional


@dataclass
class SuccessResponse:
    order_id: str
    product_id: str
    side: str
    client_order_id: str


@dataclass
class LimitLimitGtc:
    base_size: str
    limit_price: str
    post_only: bool


@dataclass
class OrderConfiguration:
    limit_limit_gtc: LimitLimitGtc


@dataclass
class ErrorResponse:
    error: str
    message: str
    error_details: str
    preview_failure_reason: str


@dataclass
class OrderResponse:
    success: bool
    failure_reason: str
    order_id: str
    order_configuration: OrderConfiguration
    success_response: Optional[SuccessResponse] = None
    error_response: Optional[ErrorResponse] = None
