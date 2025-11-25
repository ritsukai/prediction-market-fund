from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime

class Outcome(Enum):
    YES = "YES"
    NO = "NO"

@dataclass
class Position:
    """Represents a single position held in a prediction market."""
    market_id: str
    asset: str # e.g., "YES" share in a market
    quantity: float
    cost_basis: float # Average price at which the position was acquired

@dataclass
class PortfolioState:
    """
    Represents the overall state of the fund's portfolio.
    
    Attributes:
        cash_balance: The current cash available in the portfolio.
        positions: A dictionary mapping market_id to Position objects.
        total_value: The total value of the portfolio (cash + market value of positions).
    """
    cash_balance: float
    positions: Dict[str, Position] = field(default_factory=dict) # market_id -> Position
    total_value: float = 0.0 # Derived, sum of cash and market value of positions

@dataclass
class TradeOrder:
    """
    Represents a proposed trade to be executed.
    
    Attributes:
        market_id: The ID of the market to trade in.
        asset: The asset to trade (e.g., "YES" or "NO" shares).
        action: The action to perform ("BUY" or "SELL").
        quantity: The amount of the asset to trade.
        price_limit: Optional limit price for the order.
        timestamp: The time the trade order was created.
    """
    market_id: str
    asset: str # e.g., "YES" or "NO" share
    action: str # "BUY" or "SELL"
    quantity: float
    price_limit: Optional[float] # Optional limit price for the order
    timestamp: datetime = field(default_factory=datetime.utcnow)
