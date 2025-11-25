import datetime
from typing import List, Dict, Optional
from src.portfolio_risk_interface import IPortfolioManager
from src.models import Position, TradeExecutionResult, MarketData

class PortfolioManager(IPortfolioManager):
    INITIAL_CAPITAL = 10000.0
    TRANSACTION_FEE_RATE = 0.01 # 1% simulated platform/gas fees
    MIN_LIQUIDITY_REQUIRED = 5000.0 # $5k depth for SIM-001

    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.cash: float = self.INITIAL_CAPITAL
        self.nav_history: List[float] = [self.INITIAL_CAPITAL]

    def get_current_positions(self) -> List[Position]:
        return list(self.positions.values())

    def _calculate_execution_price_and_fees(self, market_data: MarketData, amount: float, direction: str) -> Optional[tuple[float, float, float]]:
        # SIM-001: Calculate execution price based on actual order book depth for the trade size
        # SIM-001: Deduct 1% simulated platform/gas fees from every trade
        # SIM-001: Reject trades if insufficient liquidity exists (<$5k depth)

        if not market_data.order_book:
            return None # No order book data

        total_cost = 0.0
        remaining_amount_to_fill = abs(amount)
        executed_quantity = 0.0
        order_book_side = market_data.order_book["asks"] if direction == "buy" else market_data.order_book["bids"]

        if not order_book_side:
            return None # No liquidity

        current_liquidity_depth = sum(price * size for price, size in order_book_side)
        if current_liquidity_depth < self.MIN_LIQUIDITY_REQUIRED:
            return None # Insufficient liquidity

        for price, size in order_book_side:
            if remaining_amount_to_fill <= 0:
                break

            fill_quantity = min(remaining_amount_to_fill, size)
            total_cost += fill_quantity * price
            executed_quantity += fill_quantity
            remaining_amount_to_fill -= fill_quantity

        if remaining_amount_to_fill > 0:
            # Could not fill the entire order with available liquidity
            return None # Or handle partial fills, for now, fail.

        avg_execution_price = total_cost / executed_quantity if executed_quantity > 0 else 0.0
        fees = total_cost * self.TRANSACTION_FEE_RATE

        return avg_execution_price, fees, executed_quantity


    def execute_trade(self, market_data: MarketData, amount: float, direction: str) -> TradeExecutionResult:
        market_id = market_data.market_id

        if not market_data.order_book:
            return TradeExecutionResult(
                market_id=market_id, executed_price=0.0, executed_quantity=0.0, fees=0.0,
                success=False, message="Trade failed: No order book data available."
            )

        execution_details = self._calculate_execution_price_and_fees(market_data, amount, direction)
        if not execution_details:
            # If execution_details is None here, it means _calculate_execution_price_and_fees
            # determined there was insufficient liquidity or could not fill the entire order.
            return TradeExecutionResult(
                market_id=market_id, executed_price=0.0, executed_quantity=0.0, fees=0.0,
                success=False, message="Trade failed: Insufficient liquidity."
            )

        executed_price, fees, executed_quantity = execution_details

        total_transaction_value = executed_quantity * executed_price

        if direction == "buy":
            if self.cash < (total_transaction_value + fees):
                return TradeExecutionResult(
                    market_id=market_id, executed_price=0.0, executed_quantity=0.0, fees=0.0,
                    success=False, message="Trade failed: Insufficient cash."
                )
            self.cash -= (total_transaction_value + fees)
            if market_id in self.positions:
                # Update existing position
                position = self.positions[market_id]
                new_total_quantity = position.quantity + executed_quantity
                position.cost_basis = ((position.cost_basis * position.quantity) + total_transaction_value) / new_total_quantity
                position.quantity = new_total_quantity
            else:
                self.positions[market_id] = Position(
                    market_id=market_id, quantity=executed_quantity, cost_basis=executed_price,
                    direction="long", open_timestamp=datetime.datetime.now()
                )
        elif direction == "sell":
            if market_id not in self.positions or self.positions[market_id].quantity < executed_quantity:
                return TradeExecutionResult(
                    market_id=market_id, executed_price=0.0, executed_quantity=0.0, fees=0.0,
                    success=False, message="Trade failed: Insufficient position to sell."
                )
            position = self.positions[market_id]
            self.cash += (total_transaction_value - fees) # Cash increases, minus fees
            position.quantity -= executed_quantity
            if position.quantity <= 0:
                del self.positions[market_id]

        self.nav_history.append(self.calculate_nav())
        return TradeExecutionResult(
            market_id=market_id, executed_price=executed_price, executed_quantity=executed_quantity, fees=fees,
            success=True, message="Trade executed successfully."
        )

    def calculate_nav(self, current_market_data: Optional[Dict[str, MarketData]] = None) -> float:
        total_holdings_value = 0.0
        for market_id, position in self.positions.items():
            if current_market_data and market_id in current_market_data:
                total_holdings_value += position.quantity * current_market_data[market_id].current_price
            else:
                # Fallback or error if market data not provided for active positions
                # For now, we'll use cost basis if market data isn't available
                total_holdings_value += position.quantity * position.cost_basis
        return self.cash + total_holdings_value
