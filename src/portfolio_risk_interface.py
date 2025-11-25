from abc import ABC, abstractmethod
from typing import List

class Position:
    # Placeholder for Position structure
    pass

class TradeExecutionResult:
    # Placeholder for TradeExecutionResult structure
    pass

class IPortfolioManager(ABC):
    @abstractmethod
    def get_current_positions(self) -> List[Position]:
        pass

    @abstractmethod
    def execute_trade(self, market_id: str, amount: float, direction: str) -> TradeExecutionResult:
        pass

class IRiskManager(ABC):
    @abstractmethod
    def assess_risk(self, portfolio: List[Position]) -> dict:
        pass

    @abstractmethod
    def check_market_exposure(self, market_id: str, proposed_trade_amount: float) -> bool:
        pass
