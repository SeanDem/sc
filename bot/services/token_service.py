from bot.stypes.config import BotConfig
from coinbase.rest import RESTClient
from dacite import from_dict
from ..stypes.token_types import CurrencyPair, Product
from ..clients import REST_CLIENT


class TokenService:
    api_client: RESTClient = REST_CLIENT

    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def getTokenPrice(self, tokenPair: CurrencyPair) -> float:
        product = from_dict(Product, self.api_client.get_product(tokenPair.value))
        return float(product.price)
