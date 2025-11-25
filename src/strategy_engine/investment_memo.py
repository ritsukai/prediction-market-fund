
from typing import List
from dataclasses import dataclass
from src.portfolio_and_risk_service.models import TradeOrder

@dataclass
class InvestmentMemo:
    trade_order: TradeOrder
    justification: str
    data_sources: List[str]
    calculated_ev: float
    conviction_level: float
    polymarket_market_id: str
