from main import CLIENT
from coinbase.rest import RESTClient

class OrderService: 
    api_client: RESTClient = CLIENT