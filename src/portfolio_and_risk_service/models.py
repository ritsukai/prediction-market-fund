from dataclasses import dataclass, field
from typing import List, Literal, Dict, Optional
from datetime import datetime

# Assuming MarketData exists in data_ingestion_service based on Historical Progress
@dataclass
class MarketData:
    asset_id: str
    timestamp: datetime
    price: float
    volume: float
    order_book_depth: Dict[str, float] = field(default_factory=dict) # e.g., {'bid_volume': 100, 'ask_volume': 120, 'bid_price': 99.5, 'ask_price': 100.5}
    current_probability: float = 0.0 # Placeholder for probability


@dataclass
class Position:
    asset_id: str
    quantity: float
    average_entry_price: float
    current_price: float
    probability: float = 0.0 # Probability associated with the position
    
@dataclass
class TradeOrder:
    asset_id: str
    order_type: Literal['buy', 'sell']
    quantity: float
    price: float # Desired price
    timestamp: datetime

@dataclass
class RiskAssessment:
    approved: bool
    rejection_reason: str = ""
    simulated_execution_price: float = 0.0
    simulated_fees: float = 0.0

@dataclass
class PortfolioState:
    nav: float = 0.0
    cash: float = 0.0
    positions: List[Position] = field(default_factory=list)
    trade_history: List[TradeOrder] = field(default_factory=list)