from coinbase.rest import RESTClient
from dacite import from_dict
from sc_types.token_types import Product
from sc_types.config import CurrencyPair


class TokenService:
    def __init__(self, api_client: RESTClient) -> None:
        self.api_client: RESTClient = api_client

    def getTokenPrice(self, tokenPair: CurrencyPair) -> float:
        product = from_dict(Product, self.api_client.get_product(tokenPair.value))
        return float(product.price)
