from coinbase.rest import RESTClient
from dacite import from_dict
from ..sc_types.token_types import Product
from ..sc_types.config import CurrencyPair
from ..clients import REST_CLIENT


class TokenService:
    api_client: RESTClient = REST_CLIENT

    def getTokenPrice(self, tokenPair: CurrencyPair) -> float:
        product = from_dict(Product, self.api_client.get_product(tokenPair.value))
        return float(product.price)
