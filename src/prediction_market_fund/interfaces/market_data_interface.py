from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

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

class IMarketDataService(ABC):
    """
    Defines the interface for a service that ingests and provides market data.
    """

    @abstractmethod
    def get_market_data(self, market_id: str) -> MarketData:
        """
        Retrieves current market data for a specific market ID.
        """
        pass

    @abstractmethod
    def get_all_market_data(self) -> Dict[str, MarketData]:
        """
        Retrieves current market data for all tracked markets.
        """
        pass
