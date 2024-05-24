from coinbase.rest import RESTClient
from bot.keys import api_key, api_secret

rest_client_singleton = RESTClient(api_key=api_key, api_secret=api_secret)
