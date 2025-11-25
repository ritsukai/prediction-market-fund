from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

@dataclass
class MarketData:
    market_id: str
    timestamp: datetime
    price: float
    volume: float
    additional_info: Dict[str, Any]

class IDataIngestionService(ABC):
    @abstractmethod
    def fetch_market_data(self, market_id: str) -> MarketData:
        pass
