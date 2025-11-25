from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from dataclasses import dataclass

@dataclass
class MarketData:
    market_id: str
    timestamp: datetime
    price: float
    volume: float

class IMarketDataService(ABC):
    @abstractmethod
    def fetch_market_data(self, market_id: str) -> MarketData:
        pass

    @abstractmethod
    def get_historical_data(self, market_id: str, start_date: datetime, end_date: datetime) -> List[MarketData]:
        pass
