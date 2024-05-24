from bot.keys import api_key, api_secret
from bot.other.singleton_base import SingletonBase
from coinbase.rest import RESTClient


class EnhancedRestClient(RESTClient, SingletonBase):
    def __init__(self, api_key: str = api_key, api_secret: str = api_secret):
        super().__init__(api_key, api_secret)
