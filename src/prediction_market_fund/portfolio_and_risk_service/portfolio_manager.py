from src.prediction_market_fund.interfaces.portfolio_risk_interface import IPortfolioManager
from src.prediction_market_fund.portfolio_and_risk_service.models import Position, PortfolioState, TradeOrder
from typing import Dict

class PortfolioManager(IPortfolioManager):
    """
    Manages the fund's portfolio, including positions and cash balance.
    """
    def __init__(self, initial_cash_balance: float = 100000.0):
        self._portfolio_state = PortfolioState(cash_balance=initial_cash_balance)

    def get_portfolio_state(self) -> PortfolioState:
        """
        Retrieves the current state of the portfolio.
        """
        # In a real system, total_value would be dynamically calculated based on current market prices.
        # For this mock, we'll keep it simple or assume it's updated externally.
        self._portfolio_state.total_value = self._portfolio_state.cash_balance + \
                                            sum(pos.quantity * pos.cost_basis for pos in self._portfolio_state.positions.values())
        return self._portfolio_state

    def execute_trade(self, order: TradeOrder) -> Position:
        """
        Executes a trade order and updates the portfolio state.
        This is a simplified mock execution.
        """
        market_id = order.market_id
        asset = order.asset
        quantity = order.quantity
        price = order.price_limit if order.price_limit is not None else 1.0 # Assume 1.0 if no limit for simplicity
        trade_cost = quantity * price

        if order.action == "BUY":
            if self._portfolio_state.cash_balance < trade_cost:
                raise ValueError(f"Insufficient cash to execute BUY order for {trade_cost}")
            self._portfolio_state.cash_balance -= trade_cost

            if market_id in self._portfolio_state.positions:
                existing_pos = self._portfolio_state.positions[market_id]
                new_quantity = existing_pos.quantity + quantity
                new_cost_basis = ((existing_pos.quantity * existing_pos.cost_basis) + trade_cost) / new_quantity
                existing_pos.quantity = new_quantity
                existing_pos.cost_basis = new_cost_basis
                position = existing_pos
            else:
                position = Position(market_id=market_id, asset=asset, quantity=quantity, cost_basis=price)
                self._portfolio_state.positions[market_id] = position

        elif order.action == "SELL":
            if market_id not in self._portfolio_state.positions or self._portfolio_state.positions[market_id].quantity < quantity:
                raise ValueError(f"Insufficient shares to execute SELL order for {quantity} in {market_id}")
            
            existing_pos = self._portfolio_state.positions[market_id]
            self._portfolio_state.cash_balance += trade_cost
            existing_pos.quantity -= quantity
            
            if existing_pos.quantity == 0:
                del self._portfolio_state.positions[market_id]
            position = existing_pos

        else:
            raise ValueError(f"Unknown trade action: {order.action}")
        
        return position
