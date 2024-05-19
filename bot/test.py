from sc_types import *
from sc_services import *
from coinbase.rest import RESTClient
from keys import api_key, api_secret


class Test:

    def __init__(self):
        self.api_client = RESTClient(api_key=api_key, api_secret=api_secret)

    def getData(self):
        self.api_client.get_product_book
