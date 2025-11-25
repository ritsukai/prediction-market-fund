import datetime
from typing import List, Optional
from src.strategy_engine_interface import IStrategyEngine
from src.market_data_interface import IMarketDataService
from src.portfolio_risk_interface import IPortfolioManager, IRiskManager
from src.models import InvestmentMemo, MarketData, Position, TradeExecutionResult

class StrategyEngine(IStrategyEngine):
    PROFIT_TAKE_THRESHOLD = 0.15 # 15% profit
    LOSS_CUT_THRESHOLD = -0.10 # 10% loss
    EVALUATION_INTERVAL_SECONDS = 60 # How often to run strategy
    CONVICTION_THRESHOLD = 0.6 # Example conviction level for a trade
    MIN_EV_FOR_TRADE = 0.05 # Minimum Expected Value to consider a trade

    def __init__(
        self,
        market_data_service: IMarketDataService,
        portfolio_manager: IPortfolioManager,
        risk_manager: IRiskManager
    ):
        self.market_data_service = market_data_service
        self.portfolio_manager = portfolio_manager
        self.risk_manager = risk_manager
        self.monitored_markets: List[str] = ["market_A", "market_B", "market_C"] # Example markets

    def run_strategy(self):
        # STRAT-001: Positions must be actively managed and traded based on dynamic EV changes
        # This is a simplified loop. In reality, it would be event-driven or a continuous process.
        print("Running strategy...")
        current_positions = self.portfolio_manager.get_current_positions()
        current_market_data = {mid: self.market_data_service.get_market_data(mid) for mid in self.monitored_markets}

        # Active position management (STRAT-001)
        for position in current_positions:
            market_id = position.market_id
            if market_id not in current_market_data:
                print(f"Warning: No market data for active position {market_id}. Skipping active management.")
                continue

            data = current_market_data[market_id]
            current_price = data.current_price
            
            # Calculate PnL percentage
            pnl_percentage = (current_price - position.cost_basis) / position.cost_basis if position.cost_basis != 0 else 0

            # Profit-taking
            if pnl_percentage >= self.PROFIT_TAKE_THRESHOLD:
                print(f"Profit-taking on {market_id}. PnL: {pnl_percentage:.2%}")
                memo = self.generate_investment_memo(market_id, "SELL", f"Profit-taking at {pnl_percentage:.2%}.", data)
                trade_amount = position.quantity # Sell entire position
                self._execute_and_log_trade(data, trade_amount, "sell", memo)
                
            # Loss-cutting
            elif pnl_percentage <= self.LOSS_CUT_THRESHOLD:
                print(f"Loss-cutting on {market_id}. PnL: {pnl_percentage:.2%}")
                memo = self.generate_investment_memo(market_id, "SELL", f"Loss-cutting at {pnl_percentage:.2%}.", data)
                trade_amount = position.quantity # Sell entire position
                self._execute_and_log_trade(data, trade_amount, "sell", memo)

        # New trade opportunities
        for market_id, data in current_market_data.items():
            if market_id not in [p.market_id for p in current_positions]: # Only consider new positions
                # Simplified EV calculation for demonstration
                # In a real scenario, this would involve complex models
                expected_value = (data.current_price - 0.5) # Example: Bet on price divergence from 0.5
                
                if expected_value > self.MIN_EV_FOR_TRADE and data.current_price < 0.8: # Example: Only buy if price is reasonable
                    # Check risk constraints before proposing trade (RISK-001)
                    # We need a proposed trade *value* for risk manager, let's assume a fixed amount for now
                    proposed_trade_value = self.portfolio_manager.cash * self.portfolio_manager.MAX_POSITION_SIZE_RATIO * 0.5 # Half of max position
                    if self.risk_manager.check_market_exposure(market_id, proposed_trade_value, self.portfolio_manager.get_current_positions()):
                        print(f"Opportunity found for {market_id}. EV: {expected_value:.2f}")
                        memo = self.generate_investment_memo(market_id, "BUY", f"Calculated EV: {expected_value:.2f}.", data)
                        trade_amount_quantity = proposed_trade_value / data.current_price # Convert value to quantity
                        self._execute_and_log_trade(data, trade_amount_quantity, "buy", memo)
                    else:
                        print(f"Trade for {market_id} rejected by risk manager.")

    def _execute_and_log_trade(self, market_data: MarketData, amount: float, direction: str, memo: InvestmentMemo):
        trade_result = self.portfolio_manager.execute_trade(market_data, amount, direction)
        if trade_result.success:
            print(f"Trade executed: {direction} {trade_result.executed_quantity} of {market_data.market_id} @ {trade_result.executed_price:.2f}")
            print(f"Investment Memo for {market_data.market_id}:\n{memo.rationale}")
            # In a real system, you'd save the memo to a persistent store and potentially trigger a dashboard update.
        else:
            print(f"Trade failed for {market_data.market_id}: {trade_result.message}")

    def generate_investment_memo(self, market_id: str, decision: str, rationale_detail: str, market_data: MarketData) -> InvestmentMemo:
        # EXP-001: Every trade execution must be justified by a generated 'Investment Memo'
        # Investment Memo enhanced to include decision rationales (historical context)

        # Simplified EV calculation for memo, should align with run_strategy logic
        expected_value = (market_data.current_price - 0.5) # Consistent with run_strategy example

        return InvestmentMemo(
            market_id=market_id,
            decision=decision,
            rationale=f"Decision: {decision} on {market_id}. {rationale_detail} "
                      f"Current Price: {market_data.current_price:.2f}. "
                      f"Calculated EV: {expected_value:.2f}. Conviction: {self.CONVICTION_THRESHOLD:.2f}.\n" 
                      "Data Sources: MockDataSourceConnector, internal EV model.\n" 
                      "Polymarket URL: https://polymarket.com/market/{market_id}", # Example URL
            timestamp=datetime.datetime.now(),
            expected_value=expected_value,
            conviction_level=self.CONVICTION_THRESHOLD,
            data_sources=["MockDataSourceConnector", "Internal EV Model"],
            polymarket_market_url=f"https://polymarket.com/market/{market_id}"
        )
