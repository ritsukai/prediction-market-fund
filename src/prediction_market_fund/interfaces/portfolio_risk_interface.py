from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Any, Dict

@dataclass
class Position:
    market_id: str
    asset_id: str
    amount: float
    entry_price: float
    current_price: float
    unrealized_pnl: float

@dataclass
class TradeOrder:
    order_id: str
    market_id: str
    asset_id: str
    quantity: float
    order_type: str  # e.g., 'buy', 'sell'
    price: float = None  # Optional: Limit price for the order
    timestamp: Any = None # Optional: time of order creation
    status: str = 'pending'  # e.g., 'pending', 'executed', 'cancelled'
    additional_info: Dict[str, Any] = None

@dataclass
class PortfolioState:
    positions: List[Position]
    cash_balance: float
    total_value: float
    leverage: float
    performance_metrics: Dict[str, Any]

class IPortfolioManager(ABC):
    @abstractmethod
    def get_portfolio_state(self) -> PortfolioState:
        pass

    @abstractmethod
    def execute_trade(self, trade_order: TradeOrder) -> bool:
        pass

class IRiskManager(ABC):
    @abstractmethod
    def assess_trade_risk(self, trade_order: TradeOrder) -> bool:
        pass