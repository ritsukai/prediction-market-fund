from src.portfolio_and_risk_service.models import PortfolioState, TradeOrder, RiskAssessment, MarketData, Position
from typing import Dict, Optional, List

class RiskManager:
    MAX_POSITION_NAV_PERCENT = 0.10 # 10% of NAV
    MAX_SECTOR_NAV_PERCENT = 0.30 # 30% of NAV
    PROBABILITY_RE_EVAL_THRESHOLD = 0.15 # 15% probability move against position
    SIMULATED_FEES_PERCENT = 0.01 # 1% simulated platform/gas fees
    MIN_LIQUIDITY_DEPTH = 5000 # $5k depth

    def __init__(self, sector_mapping: Optional[Dict[str, str]] = None):
        # Placeholder for asset_id to sector mapping
        self._sector_mapping = sector_mapping if sector_mapping is not None else {
            "GOOG": "TECH", "AAPL": "TECH", "MSFT": "TECH",
            "TSLA": "AUTO", "GM": "AUTO",
            "ETH": "CRYPTO", "BTC": "CRYPTO",
            "ELECTION_A": "US_POLITICS", "ELECTION_B": "US_POLITICS"
        }

    def _get_sector(self, asset_id: str) -> str:
        return self._sector_mapping.get(asset_id, "OTHER")

    def assess_trade(self, trade_order: TradeOrder, portfolio_state: PortfolioState, market_data: MarketData) -> RiskAssessment:
        # SIM-001: Simulate execution price based on order book depth
        simulated_execution_price = self._simulate_execution_price(trade_order, market_data)
        if simulated_execution_price is None:
            return RiskAssessment(approved=False, rejection_reason="Insufficient liquidity for desired quantity.")

        # SIM-001: Deduct simulated fees
        simulated_fees = (simulated_execution_price * trade_order.quantity) * self.SIMULATED_FEES_PERCENT
        trade_cost = (simulated_execution_price * trade_order.quantity) + simulated_fees

        # RISK-001: Max Position Size
        if not self._check_max_position_size(trade_order, portfolio_state, simulated_execution_price):
            return RiskAssessment(approved=False, rejection_reason="Exceeds maximum position size.")

        # RISK-001: Limit Sector Exposure
        if not self._check_sector_exposure(trade_order, portfolio_state, simulated_execution_price):
            return RiskAssessment(approved=False, rejection_reason="Exceeds maximum sector exposure.")

        return RiskAssessment(
            approved=True,
            simulated_execution_price=simulated_execution_price,
            simulated_fees=simulated_fees
        )

    def approve_trade(self, trade_order: TradeOrder, portfolio_state: PortfolioState, market_data: MarketData) -> bool:
        assessment = self.assess_trade(trade_order, portfolio_state, market_data)
        return assessment.approved

    def monitor_portfolio(self, portfolio_state: PortfolioState, market_data_feed: Dict[str, MarketData]) -> List[str]:
        alerts = []
        for position in portfolio_state.positions:
            if position.asset_id in market_data_feed:
                current_market_data = market_data_feed[position.asset_id]
                # RISK-001: Re-evaluation if probability moves >15% against the position
                if abs(position.probability - current_market_data.current_probability) > self.PROBABILITY_RE_EVAL_THRESHOLD:
                    alerts.append(f"RISK ALERT: Probability for {position.asset_id} moved significantly. Re-evaluate position.")

        return alerts

    def _simulate_execution_price(self, trade_order: TradeOrder, market_data: MarketData) -> Optional[float]:
        # SIM-001: Calculate execution price based on actual order book depth
        order_book = market_data.order_book_depth
        if trade_order.order_type == 'buy':
            available_volume = order_book.get('ask_volume', 0.0)
            ask_price = order_book.get('ask_price', 0.0)
            if available_volume * ask_price < self.MIN_LIQUIDITY_DEPTH or trade_order.quantity > available_volume:
                return None # Insufficient liquidity
            return ask_price
        elif trade_order.order_type == 'sell':
            available_volume = order_book.get('bid_volume', 0.0)
            bid_price = order_book.get('bid_price', 0.0)
            if available_volume * bid_price < self.MIN_LIQUIDITY_DEPTH or trade_order.quantity > available_volume:
                return None # Insufficient liquidity
            return bid_price
        return None

    def _check_max_position_size(self, trade_order: TradeOrder, portfolio_state: PortfolioState, simulated_execution_price: float) -> bool:
        # RISK-001: Cap max position size at 10% of NAV
        if portfolio_state.nav == 0:
            return True # No NAV, no positions yet, so any initial trade is fine within other constraints.

        current_position_value = 0.0
        for position in portfolio_state.positions:
            if position.asset_id == trade_order.asset_id:
                current_position_value = position.quantity * position.current_price # Using current_price for existing position
                break
        
        # Calculate potential new position value
        if trade_order.order_type == 'buy':
            new_position_value = current_position_value + (trade_order.quantity * simulated_execution_price)
        else: # Sell
            new_position_value = current_position_value - (trade_order.quantity * simulated_execution_price)
            if new_position_value < 0: new_position_value = 0 # Cannot have negative position value

        return new_position_value <= (portfolio_state.nav * self.MAX_POSITION_NAV_PERCENT)

    def _check_sector_exposure(self, trade_order: TradeOrder, portfolio_state: PortfolioState, simulated_execution_price: float) -> bool:
        # RISK-001: Limit sector exposure (e.g., US Politics) to 30% of NAV
        if portfolio_state.nav == 0:
            return True

        trade_sector = self._get_sector(trade_order.asset_id)
        current_sector_exposure = 0.0

        for position in portfolio_state.positions:
            if self._get_sector(position.asset_id) == trade_sector:
                current_sector_exposure += (position.quantity * position.current_price)
        
        # Calculate potential new sector exposure
        if trade_order.order_type == 'buy':
            new_sector_exposure = current_sector_exposure + (trade_order.quantity * simulated_execution_price)
        else: # Sell
            new_sector_exposure = current_sector_exposure - (trade_order.quantity * simulated_execution_price)
            if new_sector_exposure < 0: new_sector_exposure = 0

        return new_sector_exposure <= (portfolio_state.nav * self.MAX_SECTOR_NAV_PERCENT)
