from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class Market(BaseModel):
    """Represents a prediction market."""
    id: str
    question: str
    url: str
    
    # The current probability of the 'yes' outcome
    probability: float = Field(..., ge=0, le=1) 
    
    # Order book data for liquidity simulation
    order_book: Dict[str, List[Dict[str, float]]] = Field(default_factory=dict)
    
    # Market metadata
    category: str
    resolution_criteria: str
    
class Position(BaseModel):
    """Represents a position in a single market."""
    market_id: str
    
    # 'yes' or 'no'
    outcome: str
    
    # Number of shares
    shares: float
    
    # Average price paid per share
    entry_price: float
    
    # Current estimated value of the position
    current_value: float

class Trade(BaseModel):
    """Represents a single trade execution."""
    trade_id: str
    market_id: str
    outcome: str # 'yes' or 'no'
    action: str # 'buy' or 'sell'
    shares: float
    price: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Simulated fees and slippage
    fees: float
    slippage: float

class InvestmentMemo(BaseModel):
    """Justification for a trade."""
    memo_id: str
    trade_id: str
    market_id: str
    
    thesis: str
    sources: List[str]
    
    # Calculated expected value
    expected_value: float
    
    # Confidence level of the agent
    conviction: float
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PortfolioState(BaseModel):
    """Snapshot of the entire portfolio."""
    nav: float # Net Asset Value
    cash: float
    positions: Dict[str, Position] = Field(default_factory=dict)
    
    # Performance metrics
    pnl: float = 0.0
    sharpe_ratio: Optional[float] = None
    
    # Risk metrics
    max_drawdown: Optional[float] = None
    sector_exposure: Dict[str, float] = Field(default_factory=dict)
    
    # Timestamp of the snapshot
    timestamp: datetime = Field(default_factory=datetime.utcnow)
