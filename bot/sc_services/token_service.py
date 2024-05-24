from decimal import Decimal
from coinbase.rest import RESTClient
from dacite import from_dict
from bot.sc_types import *
from bot.sc_services import *

class TokenService:
    def __init__(self, api_client: RESTClient) -> None:
        self.api_client: RESTClient = api_client

    def getTokenPrice(self, tokenPair: CurrencyPair) -> Decimal:
        product = from_dict(Product, self.api_client.get_product(tokenPair.value))
        return Decimal(product.price)


token_service_singleton = TokenService(rest_client_singleton)
