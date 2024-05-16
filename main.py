import random
import time
from coinbase.rest import RESTClient
from coinbase.websocket import WSClient
from accountService import AccountService
from keys import api_key, api_secret

pairsList = ["DAI-USDC", "GYEN-USDC", "PAX-USDC", "GUSD-USDC", "USDT-USDC", "EUROC-USDC", "PYUSD-USDC"]
pair = "DAI-USDC"
CLIENT = RESTClient(api_key=api_key, api_secret=api_secret)
def on_message(msg):
    print(msg)
WS_CLIENT = WSClient(api_key=api_key, api_secret=api_secret, on_message=on_message)


class TradingBot:
    def __init__(self):
        self.stablecoin = pair
        self.api_client: RESTClient = CLIENT
        self.target_buy_price:str = "0.995"
        self.target_sell_price:str = "1.000"
        self.base_size:str = '1'
        self.accountService = AccountService()

    def buyOrder(self):
        orderId = str(random.randint(0, 999999999))
        res = self.api_client.limit_order_gtc_buy(
            client_order_id=orderId,
            product_id=self.stablecoin,
            base_size=self.base_size,
            limit_price=self.target_buy_price)
        print(res)    
        
    def sellOrder(self):
        orderId = str(random.randint(0, 999999999))
        res = self.api_client.limit_order_gtc_sell(
            client_order_id=orderId,
            product_id=self.stablecoin,
            base_size="3",
            limit_price=self.target_sell_price)
        print(res)

    def run(self):
        self.getPortfolioBalance()
        while True:
            current_price =  self.api_client.get_product(self.stablecoin)
            print(f"Current Price Report for {current_price['product_id']}")
            print("--------------------------------------------------")
            print(f"Current Price: {current_price['price']} USDC")
            print(f"24h Volume: {current_price['volume_24h']} DAI")
            print(f"24h Price Change: {float(current_price['price_percentage_change_24h'])*100:.2f}%")
            print(f"24h Volume Change: {current_price['volume_percentage_change_24h']}%")
            time.sleep(30)

    
     

bot = TradingBot(client)
bot.run()