from src.prediction_market_fund.interfaces.strategy_engine_interface import IStrategyEngine, InvestmentMemo
from src.prediction_market_fund.interfaces.market_data_interface import IMarketDataService, MarketData
from src.prediction_market_fund.interfaces.portfolio_risk_interface import IPortfolioManager, IRiskManager, PortfolioState, TradeOrder
from datetime import datetime
from typing import List, Tuple
import random # For mock EV calculation

class StrategyEngine(IStrategyEngine):
    """
    A concrete implementation of the IStrategyEngine interface. Responsible for
    analyzing market data, portfolio state, calculating expected values, and
    generating justified trade orders.
    """

    def __init__(self, 
                 market_data_service: IMarketDataService,
                 portfolio_manager: IPortfolioManager,
                 risk_manager: IRiskManager,
                 min_conviction_for_trade: float = 0.6,
                 trade_amount_per_decision: float = 10.0):
        self.market_data_service = market_data_service
        self.portfolio_manager = portfolio_manager
        self.risk_manager = risk_manager
        self.min_conviction_for_trade = min_conviction_for_trade
        self.trade_amount_per_decision = trade_amount_per_decision

    def _calculate_ev_and_conviction(self, market_data: MarketData) -> Tuple[float, float]:
        """
        Mock function to calculate Expected Value (EV) and conviction for a market.
        In a real scenario, this would involve sophisticated models.
        """
        # Simulate EV and conviction based on current price, with some randomness
        ev = market_data.current_price + (random.random() - 0.5) * 0.2 # EV can swing +/- 10%
        conviction = random.uniform(0.4, 0.9) # Conviction between 40% and 90%
        
        # Ensure EV stays within [0, 1] for probability markets
        ev = max(0.01, min(0.99, ev))

        return ev, conviction

    def run_strategy(self, market_data: MarketData, portfolio_state: PortfolioState) -> Tuple[List[TradeOrder], List[InvestmentMemo]]:
        """
        Executes the trading strategy for a single market.
        """
        proposed_trades: List[TradeOrder] = []
        investment_memos: List[InvestmentMemo] = []

        market_id = market_data.market_id
        current_price = market_data.current_price

        # STRAT-001: Actively manage positions based on dynamic EV changes
        ev, conviction = self._calculate_ev_and_conviction(market_data)
        
        # Determine desired position based on EV and conviction
        # Simplified logic: If EV > current_price and high conviction, consider buying.
        # If EV < current_price and high conviction, consider selling.
        # If conviction is low, do nothing.

        action = "HOLD"
        trade_quantity = 0.0
        rationale_suffix = "" # Initialize rationale_suffix

        if conviction >= self.min_conviction_for_trade:
            if ev > current_price * 1.05: # 5% arbitrage opportunity to buy
                action = "BUY"
                trade_quantity = self.trade_amount_per_decision / current_price # Amount in shares
            elif ev < current_price * 0.95: # 5% arbitrage opportunity to sell
                action = "SELL"
                trade_quantity = self.trade_amount_per_decision / current_price # Amount in shares

        # Get current position for this market
        current_position = portfolio_state.positions.get(market_id)
        
        # STRAT-001: Active Position Management - Profit Taking / Loss Cutting
        if current_position:
            profit_threshold = 1.10 # 10% profit margin
            loss_threshold = 0.90   # 10% loss cut
            
            # Calculate current value of held position
            current_position_value = current_position.quantity * current_price
            cost_basis_value = current_position.quantity * current_position.cost_basis

            if current_position_value > cost_basis_value * profit_threshold:
                # Take profit: sell a portion or all of the position
                action = "SELL"
                trade_quantity = current_position.quantity # Sell all for simplicity, could be partial
                rationale_suffix = " Identified profit-taking opportunity."
            elif current_position_value < cost_basis_value * loss_threshold:
                # Cut loss: sell a portion or all of the position
                action = "SELL"
                trade_quantity = current_position.quantity # Sell all for simplicity, could be partial
                rationale_suffix = " Identified loss-cutting opportunity."
            else:
                rationale_suffix = "" # No specific profit/loss action
        
        # Modify trade quantity based on current position to actively manage (existing logic)
        if action == "BUY" and current_position:
            # If we already hold, maybe buy less aggressively or hold
            pass
        elif action == "SELL" and current_position:
            # Ensure we don't try to sell more than we own
            if trade_quantity > current_position.quantity:
                trade_quantity = current_position.quantity
            if trade_quantity == 0: # If we have no shares to sell, change action to HOLD
                action = "HOLD"
        elif action == "SELL" and not current_position: # Cannot sell if no position
            action = "HOLD"
            trade_quantity = 0.0
        elif action == "BUY" and portfolio_state.cash_balance < self.trade_amount_per_decision: # Cannot buy if no cash
             action = "HOLD"
             trade_quantity = 0.0


        if action != "HOLD" and trade_quantity > 0:
            # Create TradeOrder
            trade_order = TradeOrder(
                market_id=market_id,
                asset="YES", # Assuming trading 'YES' shares for simplicity
                action=action,
                quantity=trade_quantity,
                price_limit=current_price, # Use current price as limit
                timestamp=datetime.utcnow()
            )
            
            # ARCH-001-REFERENCE: Risk Manager interaction
            if self.risk_manager.assess_trade_risk(trade_order, portfolio_state):
                proposed_trades.append(trade_order)

                # EXP-001: Generate Investment Memo for every trade execution
                memo = InvestmentMemo(
                    timestamp=datetime.utcnow(),
                    market_id=market_id,
                    action=action,
                    asset="YES",
                    quantity=trade_quantity,
                    price=current_price,
                    calculated_ev=ev,
                    conviction=conviction,
                    rationale=f"Calculated EV {ev:.2f} with conviction {conviction:.2f}. "
                              f"Current price {current_price:.2f}. Identified {action} opportunity.{rationale_suffix}",
                    data_sources=["Mock Market Data", f"Polymarket link for {market_id}"]
                )
                investment_memos.append(memo)
            else:
                print(f"StrategyEngine: Trade {action} {trade_quantity} for {market_id} rejected by Risk Manager.")

        return proposed_trades, investment_memos
