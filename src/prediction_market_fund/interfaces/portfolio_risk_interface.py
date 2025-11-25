from abc import ABC, abstractmethod
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
    """Represents the overall state of the fund's portfolio."""
    cash_balance: float
    positions: Dict[str, Position] = field(default_factory=dict) # market_id -> Position
    total_value: float = 0.0 # Derived, sum of cash and market value of positions

@dataclass
class TradeOrder:
    """Represents a proposed trade to be executed."""
    market_id: str
    asset: str # e.g., "YES" or "NO" share
    action: str # "BUY" or "SELL"
    quantity: float
    price_limit: Optional[float] # Optional limit price for the order
    timestamp: datetime = field(default_factory=datetime.utcnow)

class IPortfolioManager(ABC):
    """Defines the interface for managing the fund's portfolio."""

    @abstractmethod
    def get_portfolio_state(self) -> PortfolioState:
        """Retrieves the current state of the portfolio."""
        pass

    @abstractmethod
    def execute_trade(self, order: TradeOrder) -> Position:
        """
        Executes a trade order and updates the portfolio.
        Returns the updated or new position.
        """
        pass

class IRiskManager(ABC):
    """Defines the interface for assessing and managing trading risk."""

    @abstractmethod
    def assess_trade_risk(self, order: TradeOrder, portfolio: PortfolioState) -> bool:
        """
        Assesses the risk of a proposed trade order against the current portfolio state.
        Returns True if the trade is approved, False otherwise.
        """
        pass
