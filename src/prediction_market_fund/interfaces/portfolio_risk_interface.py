from abc import ABC, abstractmethod
from typing import Dict
from src.prediction_market_fund.portfolio_and_risk_service.models import PortfolioState, TradeOrder, Position


class IPortfolioManager(ABC):
    @abstractmethod
    def get_portfolio_state(self) -> PortfolioState:
        pass

    @abstractmethod
    def execute_trade(self, order: TradeOrder) -> None:
        pass


class IRiskManager(ABC):
    @abstractmethod
    def assess_trade_risk(self, order: TradeOrder, portfolio_state: PortfolioState) -> bool:
        pass
