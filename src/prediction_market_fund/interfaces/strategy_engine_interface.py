from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

# Assuming these are defined elsewhere or will be defined
# from prediction_market_fund.portfolio_and_risk_service.models import PortfolioState, TradeOrder
# from data_ingestion_service.market_data import MarketData

@dataclass
class InvestmentMemo:
    """
    A justification for a trade decision, providing transparency and auditability.
    """
    timestamp: datetime
    market_id: str  # e.g., Polymarket market ID
    action: str     # "BUY", "SELL", "HOLD"
    asset: str      # Name of the asset being traded
    quantity: float # Amount of asset
    price: float    # Price at which the decision was made or trade executed
    calculated_ev: float # Expected Value (EV) calculation at decision time
    conviction: float    # A confidence score (0-1) in the EV calculation
    rationale: str  # Detailed explanation, citing data sources
    data_sources: list[str] # List of URLs or identifiers for data used

class IStrategyEngine(ABC):
    """
    Defines the interface for the Strategy Engine, responsible for
    generating investment decisions based on market data and portfolio state.
    """

    @abstractmethod
    def run_strategy(self, market_data: "MarketData", portfolio_state: "PortfolioState") -> tuple[list["TradeOrder"], list[InvestmentMemo]]:
        """
        Executes the trading strategy.

        Args:
            market_data: The latest market data.
            portfolio_state: The current state of the portfolio.

        Returns:
            A tuple containing:
            - A list of proposed TradeOrder objects.
            - A list of corresponding InvestmentMemo objects justifying each trade.
        """
        pass
