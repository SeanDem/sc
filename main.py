import time
from bot.trading_bot import TradingBot
from bot.other.logger import LOGGER

if __name__ == "__main__":
    LOGGER.info("Bot version 1.0.4")
    bot = TradingBot()
    try:
        LOGGER.info("Starting bot instance...")
        bot.start()
    except Exception as e:
        LOGGER.error(f"Critical error: {e}")
        LOGGER.error("Restarting bot instance in 100 seconds...")
        time.sleep(5)
        bot.start()
