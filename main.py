import time

from bot.trading_bot import TradingBot
from bot.sc_types.token_types import CurrencyPair
from bot.sc_types.config import BotConfig

config = BotConfig(
    percent_funds=0.5,
    pair=CurrencyPair.DAI_USDC,
    precision=4,
    target_buy_price=".9951",
    target_sell_price=".9997",
)

if __name__ == "__main__":
    while True:
        bot = TradingBot(config)
        try:
            bot.run()
        except Exception as e:
            print(f"Critical error: {e}")
            print("Restarting bot instance in 5 seconds...")
            time.sleep(5)
            continue
