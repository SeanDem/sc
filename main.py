import time
from bot.trading_bot import TradingBot

if __name__ == "__main__":
    bot = TradingBot()
    try:
        bot.start()
    except Exception as e:
        print(f"Critical error: {e}")
        print("Restarting bot instance in 100 seconds...")
        time.sleep(5)
        bot.start()
