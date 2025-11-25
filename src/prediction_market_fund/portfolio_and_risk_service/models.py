from dataclasses import dataclass
from typing import Dict

@dataclass
class Position:
    market_id: str
    amount: float
    entry_price: float

@dataclass
class TradeOrder:
    market_id: str
    action: str  # e.g., "BUY", "SELL"
    amount: float
    price: float

@dataclass
class PortfolioState:
    cash: float
    positions: Dict[str, Position]  # market_id -> Position
