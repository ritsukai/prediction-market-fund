import unittest
from src.prediction_market_fund.portfolio_and_risk_service.risk_manager import RiskManager
from src.prediction_market_fund.portfolio_and_risk_service.models import PortfolioState, TradeOrder, Position


class TestRiskManager(unittest.TestCase):

    def setUp(self):
        self.risk_manager = RiskManager(max_market_exposure_percentage=0.20)
        self.initial_cash = 1000.0
        self.initial_portfolio_state = PortfolioState(cash=self.initial_cash, positions={})

    def test_assess_trade_risk_within_limits_buy_new_position(self):
        # Buy 100 at 10, total value 1000 + 100 = 1100. Exposure 100/1100 ~ 9% < 20%
        order = TradeOrder(market_id="ETH-USD", action="BUY", amount=10.0, price=10.0)
        is_risky = self.risk_manager.assess_trade_risk(order, self.initial_portfolio_state)
        self.assertTrue(is_risky)

    def test_assess_trade_risk_exceeds_limits_buy_new_position(self):
        # Buy 300 at 10, total value 1000 + 3000 = 4000. Exposure 3000/4000 = 75% > 20%
        order = TradeOrder(market_id="ETH-USD", action="BUY", amount=300.0, price=10.0)
        is_risky = self.risk_manager.assess_trade_risk(order, self.initial_portfolio_state)
        self.assertFalse(is_risky)

    def test_assess_trade_risk_within_limits_buy_existing_position(self):
        # Start with 100 cash, 900 in ETH (9 units @ 100)
        initial_positions = {"ETH-USD": Position(market_id="ETH-USD", amount=9.0, entry_price=100.0)}
        state_with_position = PortfolioState(cash=100.0, positions=initial_positions)
        # Current portfolio value = 100 (cash) + 900 (ETH) = 1000
        # Current ETH exposure = 900 (90%)

        # Try to buy more: 0.1 ETH @ 100. New exposure would be (900 + 10) / (1000 + 10) = 910/1010 ~ 90%
        # This should fail even if cash is available, due to initial high exposure
        order = TradeOrder(market_id="ETH-USD", action="BUY", amount=0.1, price=100.0)
        is_risky = self.risk_manager.assess_trade_risk(order, state_with_position)
        self.assertFalse(is_risky)

    def test_assess_trade_risk_within_limits_sell_reducing_exposure(self):
        # Start with 100 cash, 900 in ETH (9 units @ 100)
        initial_positions = {"ETH-USD": Position(market_id="ETH-USD", amount=9.0, entry_price=100.0)}
        state_with_position = PortfolioState(cash=100.0, positions=initial_positions)
        # Current portfolio value = 100 (cash) + 900 (ETH) = 1000
        # Current ETH exposure = 900 (90%)

        # Sell 7 ETH @ 100. New exposure would be (900 - 700) / (1000 - 700) = 200/300 ~ 66% (still too high, but less risky)
        order = TradeOrder(market_id="ETH-USD", action="SELL", amount=7.0, price=100.0)
        is_risky = self.risk_manager.assess_trade_risk(order, state_with_position)
        self.assertTrue(is_risky) # This should pass as the exposure decreases, even if still high according to the initial logic, the *trade itself* reduces risk.

    def test_assess_trade_risk_no_position_sell(self):
        order = TradeOrder(market_id="XYZ-USD", action="SELL", amount=1.0, price=100.0)
        is_risky = self.risk_manager.assess_trade_risk(order, self.initial_portfolio_state)
        self.assertTrue(is_risky) # Selling a non-existent position is not a risk from an exposure perspective

if __name__ == '__main__':
    unittest.main()
