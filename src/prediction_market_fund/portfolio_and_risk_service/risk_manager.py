from src.prediction_market_fund.interfaces.portfolio_risk_interface import IRiskManager
from src.prediction_market_fund.portfolio_and_risk_service.models import PortfolioState, TradeOrder


class RiskManager(IRiskManager):
    def __init__(self, max_market_exposure_percentage: float = 0.20):
        self.max_market_exposure_percentage = max_market_exposure_percentage

    def assess_trade_risk(self, order: TradeOrder, portfolio_state: PortfolioState) -> bool:
        # Simple risk assessment: check if a trade would exceed max market exposure

        current_portfolio_value = portfolio_state.cash
        for position in portfolio_state.positions.values():
            current_portfolio_value += position.amount * position.entry_price # Using entry_price as a proxy for current market price

        # Calculate potential portfolio value after trade for risk assessment
        # This is a simplified calculation and might need more sophistication in a real system
        potential_portfolio_value = current_portfolio_value

        # Calculate potential market exposure for the specific market
        potential_market_exposure = 0.0
        if order.market_id in portfolio_state.positions:
            potential_market_exposure = portfolio_state.positions[order.market_id].amount * portfolio_state.positions[order.market_id].entry_price

        if order.action == "BUY":
            potential_market_exposure += order.amount * order.price
        elif order.action == "SELL":
            potential_market_exposure -= order.amount * order.price
            if potential_market_exposure < 0: # Cannot have negative exposure
                potential_market_exposure = 0

        if current_portfolio_value > 0 and (potential_market_exposure / current_portfolio_value) > self.max_market_exposure_percentage:
            print(f"Trade for {order.market_id} exceeds maximum market exposure of {self.max_market_exposure_percentage * 100}%")
            return False
        
        return True
