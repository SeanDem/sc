# Stablecoin Trading Bot

This trading bot is designed to automate the process of buying and selling stablecoins on the Coinbase Pro exchange. The bot focuses on executing buy and sell orders based on predefined price levels and adjusting prices to maintain a competitive edge in the market.

## Features

- **Automated Trading**: Executes trades automatically based on real-time market data.
- **Price Adjustment**: Dynamically adjusts order prices to stay competitive based on the current best ask and bid prices.
- **Order Management**: Places multiple buy orders within a specified price range and sells at predefined price points.
- **Performance Monitoring**: Tracks buy and sell orders to evaluate the bot's performance and efficiency.

## Requirements

- Python 3.8 or higher
- A Coinbase Pro Advanced API

## Setup

1. Clone the repository:
  git clone [https://github.com/your-username/stablecoin-trading-bot.git](https://github.com/SeanDem/sc/)
  cd sc
2. Install required Python packages:
  pip install -r requirements.txt
3. Set up your API credentials in a secure configuration file or environment variables:
  export API_KEY='your_api_key'
  export API_SECRET='your_api_secret'
  export API_PASSPHRASE='your_api_passphrase'


## Configuration

Modify the `config.json` file to set up your trading parameters, including:
- Target coin pair
!! List any additional configuration parameters you might have discussed or considered.

## Usage

To start the trading bot, run: python bot.py


Ensure that the bot is running in an environment where it can maintain a stable means of connectivity to the Coinbase Pro API.

## Caution

This bot makes real trades with potentially significant financial impact. Use it at your own risk. Ensure you thoroughly test any changes in a simulation environment before executing them on live markets.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome. Please fork the repository and submit a pull request with your suggested changes.

