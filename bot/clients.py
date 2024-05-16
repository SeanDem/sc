from coinbase.rest import RESTClient
from .keys import api_key, api_secret

REST_CLIENT = RESTClient(api_key=api_key, api_secret=api_secret)
