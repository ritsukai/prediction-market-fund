from abc import ABC, abstractmethod
from typing import List

class MarketData:
    # Placeholder for MarketData structure
    pass

class IMarketDataService(ABC):
    @abstractmethod
    def get_market_data(self, market_id: str) -> MarketData:
        pass
