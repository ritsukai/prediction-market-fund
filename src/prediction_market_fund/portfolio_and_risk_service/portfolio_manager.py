from src.prediction_market_fund.interfaces.portfolio_risk_interface import IPortfolioManager
from src.prediction_market_fund.portfolio_and_risk_service.models import PortfolioState, TradeOrder, Position
from typing import Dict


class PortfolioManager(IPortfolioManager):
    def __init__(self, initial_cash: float = 100000.0):
        self._portfolio_state = PortfolioState(cash=initial_cash, positions={})

    def get_portfolio_state(self) -> PortfolioState:
        return self._portfolio_state

    def execute_trade(self, order: TradeOrder) -> None:
        current_cash = self._portfolio_state.cash
        current_positions = self._portfolio_state.positions

        if order.action == "BUY":
            cost = order.amount * order.price
            if current_cash >= cost:
                self._portfolio_state.cash -= cost
                if order.market_id in current_positions:
                    position = current_positions[order.market_id]
                    total_amount = position.amount + order.amount
                    new_entry_price = ((position.amount * position.entry_price) + cost) / total_amount
                    position.amount = total_amount
                    position.entry_price = new_entry_price
                else:
                    current_positions[order.market_id] = Position(
                        market_id=order.market_id,
                        amount=order.amount,
                        entry_price=order.price
                    )
            else:
                print(f"Insufficient funds to buy {order.amount} of {order.market_id}")
        elif order.action == "SELL":
            if order.market_id in current_positions:
                position = current_positions[order.market_id]
                if position.amount >= order.amount:
                    self._portfolio_state.cash += order.amount * order.price
                    position.amount -= order.amount
                    if position.amount == 0:
                        del current_positions[order.market_id]
                else:
                    print(f"Insufficient shares to sell {order.amount} of {order.market_id}")
            else:
                print(f"No position in {order.market_id} to sell")
        else:
            print(f"Unknown trade action: {order.action}")
