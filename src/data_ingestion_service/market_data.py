
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MarketData:
    market_id: str
    timestamp: datetime
    price: float
    volume: float
