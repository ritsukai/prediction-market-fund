from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Any

from src.prediction_market_fund.interfaces.market_data_interface import MarketData
from src.prediction_market_fund.interfaces.portfolio_risk_interface import TradeOrder, PortfolioState

@dataclass
class InvestmentMemo:
    trade_order: TradeOrder
    justification: str
    data_sources: List[str]
    calculated_ev: float
    conviction_level: float
    polymarket_market_id: str

class IStrategyEngine(ABC):
    @abstractmethod
    def generate_trade_orders(self, market_data: MarketData, portfolio_state: PortfolioState) -> (List[TradeOrder], List[InvestmentMemo]):
        pass

    @abstractmethod
    def actively_manage_positions(self, market_data: MarketData, portfolio_state: PortfolioState) -> (List[TradeOrder], List[InvestmentMemo]):
        pass
