from abc import ABC, abstractmethod
from typing import List

class InvestmentMemo:
    # Placeholder for InvestmentMemo structure
    pass

class IStrategyEngine(ABC):
    @abstractmethod
    def run_strategy(self):
        pass

    @abstractmethod
    def generate_investment_memo(self, market_id: str, decision: str) -> InvestmentMemo:
        pass
