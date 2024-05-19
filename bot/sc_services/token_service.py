from coinbase.rest import RESTClient
from dacite import from_dict
from sc_types import *


class TokenService:
    def __init__(self, api_client: RESTClient) -> None:
        self.api_client: RESTClient = api_client

    def getTokenPrice(self, tokenPair: CurrencyPair) -> float:
        product = from_dict(Product, self.api_client.get_product(tokenPair.value))
        return float(product.price)
