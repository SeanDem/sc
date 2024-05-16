import time

from bot.trading_bot import TradingBot
from bot.stypes.token_types import CurrencyPair
from bot.stypes.config import BotConfig

config = BotConfig(
    percent_funds=0.5,
    pair=CurrencyPair.DAI_USDC,
    precision=4,
    target_buy_price=".9951",
    target_sell_price=".9997",
    price_ceiling=1.0,
    price_floor=1.0,
)
if __name__ == "__main__":
    while True:
        try:
            bot = TradingBot(config)
            bot.run()
        except Exception as e:
            print(f"Critical error: {e}")
            print("Restarting bot instance in 5 seconds...")
            time.sleep(5)
