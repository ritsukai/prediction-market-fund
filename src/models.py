import datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class MarketData:
    market_id: str
    current_price: float
    timestamp: datetime.datetime
    # Add other relevant market data fields like order book depth, etc.
    order_book: Optional[Dict[str, List[Dict[str, float]]]] = None # "bids": [[price, size]], "asks": [[price, size]]

@dataclass
class Position:
    market_id: str
    quantity: float
    cost_basis: float
    direction: str # "long" or "short"
    open_timestamp: datetime.datetime

@dataclass
class TradeExecutionResult:
    market_id: str
    executed_price: float
    executed_quantity: float
    fees: float
    success: bool
    message: str

@dataclass
class InvestmentMemo:
    market_id: str
    decision: str # e.g., "BUY", "SELL", "HOLD"
    rationale: str
    timestamp: datetime.datetime
    expected_value: float
    conviction_level: float
    data_sources: List[str]
    polymarket_market_url: Optional[str] = None
