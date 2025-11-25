from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime

class Outcome(Enum):
    YES = "YES"
    NO = "NO"

@dataclass
class Position:
    """
    Represents a single position held in a prediction market.
    
    Attributes:
        market_id: The ID of the market.
        asset: The asset held (e.g., "YES" share).
        quantity: The amount of the asset held.
        cost_basis: The average price at which the position was acquired.
        entry_price: The price at which the position was initially entered.
        current_price: The most recent market price of the asset.
        unrealized_pnl: Unrealized Profit and Loss for the position.
    """
    market_id: str
    asset: str # e.g., "YES" share in a market
    quantity: float
    cost_basis: float # Average price at which the position was acquired
    entry_price: float = 0.0 # Price at which the position was initially entered
    current_price: float = 0.0 # Most recent market price of the asset
    unrealized_pnl: float = 0.0 # Unrealized PnL

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

    def has_position(self, market_id: str, asset: str) -> bool:
        """
        Checks if the portfolio has an active position for a given market_id and asset.
        """
        return any(p.market_id == market_id and p.asset == asset for p in self.positions.values())

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

