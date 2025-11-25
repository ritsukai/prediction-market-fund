from src.prediction_market_fund.interfaces.portfolio_risk_interface import IRiskManager
from src.prediction_market_fund.portfolio_and_risk_service.models import PortfolioState, TradeOrder

class RiskManager(IRiskManager):
    """
    Assesses the risk of proposed trades and enforces risk policies.
    This is a simplified mock implementation.
    """
    def __init__(self, max_exposure_per_market: float = 0.1, max_total_fund_exposure: float = 0.5):
        self.max_exposure_per_market = max_exposure_per_market
        self.max_total_fund_exposure = max_total_fund_exposure

    def assess_trade_risk(self, order: TradeOrder, portfolio: PortfolioState) -> bool:
        """
        Evaluates a trade order against predefined risk parameters.
        Returns True if the trade is approved, False otherwise.
        """
        # Calculate potential new state after trade (simplified)
        hypothetical_cash = portfolio.cash_balance
        hypothetical_positions = {k: v for k, v in portfolio.positions.items()} # shallow copy

        market_id = order.market_id
        quantity = order.quantity
        price = order.price_limit if order.price_limit is not None else 1.0 # Assume 1.0 if no limit for simplicity
        trade_cost = quantity * price

        if order.action == "BUY":
            if hypothetical_cash < trade_cost:
                return False # Not enough cash
            hypothetical_cash -= trade_cost
            
            if market_id in hypothetical_positions:
                existing_pos = hypothetical_positions[market_id]
                new_quantity = existing_pos.quantity + quantity
                new_cost_basis = ((existing_pos.quantity * existing_pos.cost_basis) + trade_cost) / new_quantity
                hypothetical_positions[market_id] = Position(market_id=market_id, asset=existing_pos.asset, quantity=new_quantity, cost_basis=new_cost_basis)
            else:
                hypothetical_positions[market_id] = Position(market_id=market_id, asset=order.asset, quantity=quantity, cost_basis=price)

        elif order.action == "SELL":
            if market_id not in hypothetical_positions or hypothetical_positions[market_id].quantity < quantity:
                return False # Not enough shares to sell
            
            existing_pos = hypothetical_positions[market_id]
            hypothetical_cash += trade_cost
            existing_pos.quantity -= quantity
            
            if existing_pos.quantity == 0:
                del hypothetical_positions[market_id]

        # --- Risk Checks ---
        # 1. Check total fund exposure (simplified: sum of all position values relative to total hypothetical value)
        hypothetical_total_value = hypothetical_cash + sum(pos.quantity * pos.cost_basis for pos in hypothetical_positions.values())
        if hypothetical_total_value == 0: # Avoid division by zero
            return True 

        total_positions_value = sum(pos.quantity * pos.cost_basis for pos in hypothetical_positions.values())
        if total_positions_value / hypothetical_total_value > self.max_total_fund_exposure:
            print(f"RiskManager: Rejecting trade due to exceeding total fund exposure limit. Current: {total_positions_value / hypothetical_total_value:.2f}, Max: {self.max_total_fund_exposure}")
            return False

        # 2. Check individual market exposure (simplified: value of position in one market relative to total hypothetical value)
        if market_id in hypothetical_positions:
            market_exposure = (hypothetical_positions[market_id].quantity * hypothetical_positions[market_id].cost_basis) / hypothetical_total_value
            if market_exposure > self.max_exposure_per_market:
                print(f"RiskManager: Rejecting trade due to exceeding per-market exposure limit for {market_id}. Current: {market_exposure:.2f}, Max: {self.max_exposure_per_market}")
                return False
        
        print(f"RiskManager: Approving trade for {order.market_id}")
        return True
