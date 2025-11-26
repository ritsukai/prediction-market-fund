from src.core.types import PortfolioState, Trade
from typing import Dict

class RiskManager:
    """
    Enforces risk management constraints on the portfolio.
    """

    def __init__(self, max_position_size: float = 0.1, max_sector_exposure: float = 0.3):
        """
        Initializes the RiskManager with the defined constraints.

        :param max_position_size: Maximum size of a single position as a fraction of NAV.
        :param max_sector_exposure: Maximum exposure to a single sector as a fraction of NAV.
        """
        self.max_position_size = max_position_size
        self.max_sector_exposure = max_sector_exposure

    def _check_max_position_size(self, portfolio: PortfolioState, trade: Trade) -> bool:
        """
        Checks if a new trade would exceed the maximum position size.
        """
        # This is a simplified check. A real implementation would need to consider
        # the change in NAV and the value of the existing position.
        trade_value = trade.shares * trade.price
        if trade_value / portfolio.nav > self.max_position_size:
            print(f"Trade rejected: Exceeds max position size of {self.max_position_size * 100}%")
            return False
        return True

    def _check_sector_exposure(self, portfolio: PortfolioState, trade_market_category: str) -> bool:
        """
        Checks if a new trade would exceed the maximum sector exposure.
        """
        # This is a simplified check. A real implementation would need to
        # fetch the market category for the trade and calculate the total
        # exposure to that sector.
        
        current_exposure = portfolio.sector_exposure.get(trade_market_category, 0)
        
        # We can't calculate the new exposure without knowing the trade size,
        # so this check is incomplete. We'll refine this later.
        
        if current_exposure >= self.max_sector_exposure:
             print(f"Trade rejected: Exceeds max sector exposure to {trade_market_category} of {self.max_sector_exposure * 100}%")
             return False
        
        return True
        

    def approve_trade(self, portfolio: PortfolioState, trade: Trade, trade_market_category: str) -> bool:
        """
        Checks if a trade is compliant with all risk management rules.

        :param portfolio: The current portfolio state.
        :param trade: The proposed trade.
        :return: True if the trade is approved, False otherwise.
        """
        if not self._check_max_position_size(portfolio, trade):
            return False
        
        if not self._check_sector_exposure(portfolio, trade_market_category):
            return False

        # Add more risk checks here as the system evolves.

        return True

