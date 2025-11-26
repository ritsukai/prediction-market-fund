# Configuration for the prediction market fund

# Polymarket API details
POLYMARKET_API_URL = "https://strapi-matic.polymarket.com/markets"

# Simulation parameters
INITIAL_CAPITAL = 100000  # in USD
SLIPPAGE = 0.01  # 1%
FEES = 0.01  # 1%
MAX_POSITION_SIZE = 0.1  # 10% of NAV
MAX_SECTOR_EXPOSURE = 0.3  # 30% of NAV
PROBABILITY_REVALUATION_TRIGGER = 0.15  # 15% change
