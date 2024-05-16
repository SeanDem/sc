from dataclasses import dataclass
from enum import Enum
from typing import List


class CurrencyPair(Enum):
    DAI_USDC = "DAI-USDC"
    GYEN_USDC = "GYEN-USDC"
    PAX_USDC = "PAX-USDC"
    GUSD_USDC = "GUSD-USDC"
    USDT_USDC = "USDT-USDC"
    EUROC_USDC = "EUROC-USDC"
    PYUSD_USDC = "PYUSD-USDC"


@dataclass
class Product:
    product_id: str
    price: str
    price_percentage_change_24h: str
    volume_24h: str
    volume_percentage_change_24h: str
    base_increment: str
    quote_increment: str
    quote_min_size: str
    quote_max_size: str
    base_min_size: str
    base_max_size: str
    base_name: str
    quote_name: str
    watched: bool
    is_disabled: bool
    new: bool
    status: str
    cancel_only: bool
    limit_only: bool
    post_only: bool
    trading_disabled: bool
    auction_mode: bool
    product_type: str
    quote_currency_id: str
    base_currency_id: str
    mid_market_price: str
    alias: str
    alias_to: List[str]
    base_display_symbol: str
    quote_display_symbol: str
    view_only: bool
    price_increment: str
    display_name: str
    product_venue: str
    approximate_quote_24h_volume: str
