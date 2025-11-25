from src.portfolio_and_risk_service.models import PortfolioState, Position, TradeOrder, Optional
from typing import List
from datetime import datetime

class PortfolioManager:
    def __init__(self, initial_cash: float):
        self._portfolio_state = PortfolioState(cash=initial_cash, nav=initial_cash)

    def get_portfolio_state(self) -> PortfolioState:
        # Recalculate NAV before returning the state
        self._recalculate_nav()
        return self._portfolio_state

    def process_trade_order(self, trade_order: TradeOrder, execution_price: float, fees: float):
        cost = (execution_price * trade_order.quantity) + fees

        if trade_order.order_type == 'buy':
            if self._portfolio_state.cash < cost:
                raise ValueError("Insufficient cash to execute buy order.")

            self._portfolio_state.cash -= cost
            self._add_or_update_position(trade_order.asset_id, trade_order.quantity, execution_price)

        elif trade_order.order_type == 'sell':
            position = self._get_position(trade_order.asset_id)
            if not position or position.quantity < trade_order.quantity:
                raise ValueError("Insufficient quantity to execute sell order.")
            
            self._portfolio_state.cash += (execution_price * trade_order.quantity) - fees
            self._remove_or_update_position(trade_order.asset_id, trade_order.quantity)

        self._portfolio_state.trade_history.append(trade_order)
        self._recalculate_nav()

    def get_positions(self) -> List[Position]:
        return self._portfolio_state.positions

    def _add_or_update_position(self, asset_id: str, quantity: float, price: float):
        for position in self._portfolio_state.positions:
            if position.asset_id == asset_id:
                total_quantity = position.quantity + quantity
                position.average_entry_price = ((position.average_entry_price * position.quantity) + (price * quantity)) / total_quantity
                position.quantity = total_quantity
                position.current_price = price
                return
        self._portfolio_state.positions.append(Position(asset_id=asset_id, quantity=quantity, average_entry_price=price, current_price=price))

    def _remove_or_update_position(self, asset_id: str, quantity: float):
        for i, position in enumerate(self._portfolio_state.positions):
            if position.asset_id == asset_id:
                position.quantity -= quantity
                if position.quantity <= 0:
                    del self._portfolio_state.positions[i]
                return

    def _get_position(self, asset_id: str) -> Optional[Position]:
        for position in self._portfolio_state.positions:
            if position.asset_id == asset_id:
                return position
        return None

    def _recalculate_nav(self):
        current_assets_value = 0.0
        # For simplicity, using current_price from Position, which should be updated externally by a market data feed
        for position in self._portfolio_state.positions:
            current_assets_value += position.quantity * position.current_price
        self._portfolio_state.nav = self._portfolio_state.cash + current_assets_value
