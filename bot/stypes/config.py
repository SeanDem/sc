from dataclasses import dataclass
from bot.stypes.token_types import CurrencyPair


@dataclass
class BotConfig:
    percent_funds: float
    pair: CurrencyPair
    precision: int
    target_buy_price: str
    target_sell_price: str
    price_ceiling: float
    price_floor: float
