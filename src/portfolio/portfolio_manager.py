from src.core.types import PortfolioState, Trade, Position, Market
from typing import Dict

class PortfolioManager:
    """
    Manages the state of the trading portfolio.
    """

    def __init__(self, initial_cash: float = 10000.0):
        self.state = PortfolioState(nav=initial_cash, cash=initial_cash)

    def update_portfolio_from_trade(self, trade: Trade, market: Market):
        """
        Updates the portfolio state based on a new trade.
        """
        if trade.action == 'buy':
            self._execute_buy(trade, market)
        elif trade.action == 'sell':
            self._execute_sell(trade)
        else:
            raise ValueError(f"Invalid trade action: {trade.action}")

        self._update_nav()
        self._update_sector_exposure(market)


    def _execute_buy(self, trade: Trade, market: Market):
        trade_cost = trade.shares * trade.price
        
        if self.state.cash < trade_cost:
            raise ValueError("Insufficient cash for trade.")

        self.state.cash -= trade_cost

        if trade.market_id in self.state.positions:
            position = self.state.positions[trade.market_id]
            
            # Update existing position
            new_total_cost = (position.shares * position.entry_price) + trade_cost
            position.shares += trade.shares
            position.entry_price = new_total_cost / position.shares
            
        else:
            # Create new position
            self.state.positions[trade.market_id] = Position(
                market_id=trade.market_id,
                outcome=trade.outcome,
                shares=trade.shares,
                entry_price=trade.price,
                current_value=trade_cost 
            )

    def _execute_sell(self, trade: Trade):
        if trade.market_id not in self.state.positions:
            raise ValueError("Attempting to sell a position that does not exist.")

        position = self.state.positions[trade.market_id]
        if trade.shares > position.shares:
            raise ValueError("Attempting to sell more shares than owned.")

        position.shares -= trade.shares
        self.state.cash += trade.shares * trade.price
        
        # If all shares are sold, remove the position
        if position.shares == 0:
            del self.state.positions[trade.market_id]

    def _update_nav(self):
        """
        Recalculates the Net Asset Value of the portfolio.
        """
        # For simplicity, we'll value positions at their entry price for now.
        # A real implementation would need to fetch the current market price
        # for each position.
        
        position_values = sum(pos.shares * pos.entry_price for pos in self.state.positions.values())
        self.state.nav = self.state.cash + position_values
        self.state.pnl = self.state.nav - 10000 # Assuming 10k initial capital
        
    def _update_sector_exposure(self, market: Market):
        """
        Recalculates the exposure to each market sector.
        """
        # This is a simplified implementation. A real system would need to
        # iterate through all positions and sum their values by sector.
        
        if market.id in self.state.positions:
            position_value = self.state.positions[market.id].current_value
            self.state.sector_exposure[market.category] = position_value / self.state.nav
        

    def get_state(self) -> PortfolioState:
        return self.state

