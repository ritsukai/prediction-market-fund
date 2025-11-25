from dataclasses import dataclass
from datetime import datetime

@dataclass
class MarketData:
    """
    Represents standardized market data for a given prediction market.
    """
    market_id: str
    question: str
    current_price: float # Current price of the 'YES' outcome
    volume_24h: float
    total_liquidity: float
    # Add other relevant market data fields as needed, e.g., closing_time, outcomes
