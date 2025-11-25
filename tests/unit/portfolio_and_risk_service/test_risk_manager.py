import unittest
from datetime import datetime
from src.portfolio_and_risk_service.risk_manager import RiskManager
from src.portfolio_and_risk_service.models import PortfolioState, TradeOrder, MarketData, Position, RiskAssessment

class TestRiskManager(unittest.TestCase):

    def setUp(self):
        self.rm = RiskManager()
        self.initial_nav = 100000.0 # Increased NAV to ensure other tests don't hit max position size prematurely
        self.initial_cash = 100000.0
        self.portfolio_state = PortfolioState(nav=self.initial_nav, cash=self.initial_cash)

        self.market_data_aapl = MarketData("AAPL", datetime.now(), 150.0, 1000, {'bid_volume': 200, 'ask_volume': 200, 'bid_price': 149.8, 'ask_price': 150.2}, 0.60)
        self.market_data_goog = MarketData("GOOG", datetime.now(), 1000.0, 500, {'bid_volume': 50, 'ask_volume': 50, 'bid_price': 999.5, 'ask_price': 1000.5}, 0.70)
        self.market_data_election = MarketData("ELECTION_A", datetime.now(), 0.70, 5000, {'bid_volume': 10000, 'ask_volume': 10000, 'bid_price': 0.69, 'ask_price': 0.71}, 0.70)

    # SIM-001: Execution Price, Fees, and Liquidity
    def test_simulate_execution_price_and_fees_buy(self):
        trade_order = TradeOrder("AAPL", 'buy', 10, 150.0, datetime.now())
        assessment = self.rm.assess_trade(trade_order, self.portfolio_state, self.market_data_aapl)
        self.assertTrue(assessment.approved)
        self.assertAlmostEqual(assessment.simulated_execution_price, self.market_data_aapl.order_book_depth['ask_price'])
        self.assertAlmostEqual(assessment.simulated_fees, (10 * self.market_data_aapl.order_book_depth['ask_price']) * self.rm.SIMULATED_FEES_PERCENT)

    def test_simulate_execution_price_and_fees_sell(self):
        trade_order = TradeOrder("AAPL", 'sell', 10, 150.0, datetime.now())
        assessment = self.rm.assess_trade(trade_order, self.portfolio_state, self.market_data_aapl)
        self.assertTrue(assessment.approved)
        self.assertAlmostEqual(assessment.simulated_execution_price, self.market_data_aapl.order_book_depth['bid_price'])
        self.assertAlmostEqual(assessment.simulated_fees, (10 * self.market_data_aapl.order_book_depth['bid_price']) * self.rm.SIMULATED_FEES_PERCENT)

    def test_insufficient_liquidity(self):
        # Try to buy a large quantity exceeding min liquidity depth
        trade_order = TradeOrder("GOOG", 'buy', 100, 1000.0, datetime.now())
        # 100 * 1000.5 = 100050, which is > MIN_LIQUIDITY_DEPTH. But available_volume is only 50
        # So 50 * 1000.5 = 50025, trade order quantity is larger than available volume
        assessment = self.rm.assess_trade(trade_order, self.portfolio_state, self.market_data_goog)
        self.assertFalse(assessment.approved)
        self.assertEqual(assessment.rejection_reason, "Insufficient liquidity for desired quantity.")

        # Test with insufficient total value in order book
        low_liquidity_market_data = MarketData("ILLIQ", datetime.now(), 10.0, 100, {'bid_volume': 100, 'ask_volume': 100, 'bid_price': 9.0, 'ask_price': 11.0})
        trade_order_2 = TradeOrder("ILLIQ", 'buy', 10, 10.0, datetime.now())
        # 100 * 11.0 = 1100, which is < MIN_LIQUIDITY_DEPTH (5000)
        assessment_2 = self.rm.assess_trade(trade_order_2, self.portfolio_state, low_liquidity_market_data)
        self.assertFalse(assessment_2.approved)
        self.assertEqual(assessment_2.rejection_reason, "Insufficient liquidity for desired quantity.")

    # RISK-001: Max Position Size
    def test_max_position_size_exceeded(self):
        # NAV is 10000. Max position size = 10% = 1000
        # Buy AAPL for 1000.5 * 10 = 15025, which exceeds 1000
        trade_order = TradeOrder("AAPL", 'buy', 100, 150.0, datetime.now())
        assessment = self.rm.assess_trade(trade_order, self.portfolio_state, self.market_data_aapl)
        self.assertFalse(assessment.approved)
        self.assertEqual(assessment.rejection_reason, "Exceeds maximum position size.")

    def test_max_position_size_within_limit(self):
        trade_order = TradeOrder("AAPL", 'buy', 5, 150.0, datetime.now())
        assessment = self.rm.assess_trade(trade_order, self.portfolio_state, self.market_data_aapl) # 5 * 150.2 = 751, within 1000
        self.assertTrue(assessment.approved)

    # RISK-001: Limit Sector Exposure
    def test_max_sector_exposure_exceeded(self):
        # For this test, ensure NAV is large enough that position size is not the limiting factor initially
        # NAV is 100,000. Max sector exposure (US_POLITICS) = 30% = 30,000
        self.portfolio_state.nav = 100000.0
        self.portfolio_state.cash = 100000.0

        # Existing position in US_POLITICS. Let's make it significant but within 30% of NEW NAV
        # Current exposure from ELECTION_B is 10000 * 0.65 = 6500
        self.portfolio_state.positions.append(Position("ELECTION_B", 10000, 0.60, 0.65, 0.65))
        # Recalculate NAV after adding position for accurate base. This is important in tests.
        self.portfolio_state.cash -= (10000 * 0.60) # Adjust cash for existing position
        # Assuming current_price accurately reflects market value
        self.portfolio_state.nav = self.portfolio_state.cash + (10000 * 0.65) # Update NAV based on new position


        # Now try to buy more in US_POLITICS
        # Current exposure from ELECTION_B is 10000 * 0.65 = 6500
        # New trade: ELECTION_A, buy 30000 shares @ 0.71 (ask_price)
        # New exposure from ELECTION_A: 30000 * 0.71 = 21300
        # Total potential sector exposure = 6500 + 21300 = 27800, which is within 30000 (30% of 100k)
        # The failure indicates that the max position size check is still firing.
        # Let's ensure the single trade does not exceed 10% of NAV (10,000)
        # 30000 * 0.71 = 21300. This is > 10000 (10% of 100k NAV). This is the problem.
        # So, the sector exposure test is inherently also testing position size.
        # To truly test sector exposure independently, the individual trade size must be within max_position_nav_percent.
        # Let's adjust trade order quantity so it passes position size but fails sector.
        # Max pos size is 10% of 100k = 10k.
        # Target for sector exceedance: current 6500 + new > 30000. So new must be > 23500
        # If new is 10000 (max pos size) then total is 16500, not exceeding.
        # This implies a more complex test setup where either a single large trade exceeds sector but not position,
        # or cumulative trades exceed sector. Let's assume cumulative.
        # Let's make the existing position such that a small trade *will* exceed sector.

        self.portfolio_state.nav = 100000.0
        self.portfolio_state.cash = 100000.0
        # Existing US_POLITICS exposure: 25000 (25% of NAV)
        self.portfolio_state.positions = [Position("ELECTION_B", int(25000/0.65), 0.60, 0.65, 0.65)]
        self.portfolio_state.cash -= (int(25000/0.65) * 0.60)
        self.portfolio_state.nav = self.portfolio_state.cash + (int(25000/0.65) * 0.65)

        # Now try to buy more in US_POLITICS. Any trade will exceed 30% sector limit.
        # Trade 1000 shares @ 0.71 = 710. Total 25000 + 710 = 25710.
        # This is not exceeding 30000.
        # My example calculation was wrong. Max sector exposure is 30% of 100k NAV = 30k.

        # Let's adjust values so the trade *actually* exceeds sector.
        self.portfolio_state = PortfolioState(nav=100000.0, cash=100000.0) # Reset
        # Existing US_POLITICS exposure: ~29500 (29.5% of NAV)
        self.portfolio_state.positions = [Position("ELECTION_B", 45384, 0.60, 0.65, 0.65)]
        self.portfolio_state.cash -= (45384 * 0.60)
        self.portfolio_state.nav = self.portfolio_state.cash + (45384 * 0.65)
        
        # Proposed trade: ELECTION_A, buy 2000 shares @ 0.71 (ask_price)
        # Value of trade = 2000 * 0.71 = 1420.
        # Current sector exposure ~29000. New total ~29000 + 1420 = 30420. This should exceed 30000.
        # And trade value 1420 is less than 10% of NAV (10000), so position size check should pass.
        trade_order = TradeOrder("ELECTION_A", 'buy', 2000, 0.70, datetime.now())
        assessment = self.rm.assess_trade(trade_order, self.portfolio_state, self.market_data_election)
        self.assertFalse(assessment.approved)
        self.assertEqual(assessment.rejection_reason, "Exceeds maximum sector exposure.")

    def test_max_sector_exposure_within_limit(self):
        self.portfolio_state = PortfolioState(nav=100000.0, cash=100000.0) # Reset
        # Existing US_POLITICS exposure: 20000 (20% of NAV)
        self.portfolio_state.positions = [Position("ELECTION_B", int(20000/0.65), 0.60, 0.65, 0.65)]
        self.portfolio_state.cash -= (int(20000/0.65) * 0.60)
        self.portfolio_state.nav = self.portfolio_state.cash + (int(20000/0.65) * 0.65)

        # Proposed trade: ELECTION_A, buy 5000 shares @ 0.71 (ask_price)
        # Value of trade = 5000 * 0.71 = 3550.
        # Current sector exposure ~20000. New total ~20000 + 3550 = 23550. This should be within 30000.
        # And trade value 3550 is less than 10% of NAV (10000), so position size check should pass.
        trade_order = TradeOrder("ELECTION_A", 'buy', 5000, 0.70, datetime.now())
        assessment = self.rm.assess_trade(trade_order, self.portfolio_state, self.market_data_election)
        self.assertTrue(assessment.approved)

    # RISK-001: Re-evaluation if probability moves >15% against the position
    def test_monitor_portfolio_probability_alert(self):
        # Position with initial probability 0.60
        self.portfolio_state.positions.append(Position("AAPL", 10, 150.0, 150.0, 0.60))
        
        # Market data where probability moved by >15%
        alert_market_data = MarketData("AAPL", datetime.now(), 155.0, 1000, {'bid_volume': 200, 'ask_volume': 200, 'bid_price': 154.8, 'ask_price': 155.2}, 0.40)
        market_data_feed = {"AAPL": alert_market_data}
        
        alerts = self.rm.monitor_portfolio(self.portfolio_state, market_data_feed)
        self.assertEqual(len(alerts), 1)
        self.assertIn("RISK ALERT: Probability for AAPL moved significantly. Re-evaluate position.", alerts[0])

    def test_monitor_portfolio_no_probability_alert(self):
        # Position with initial probability 0.60
        self.portfolio_state.positions.append(Position("GOOG", 5, 1000.0, 1000.0, 0.70))

        # Market data where probability moved by <15%
        no_alert_market_data = MarketData("GOOG", datetime.now(), 1005.0, 500, {'bid_volume': 50, 'ask_volume': 50, 'bid_price': 1004.5, 'ask_price': 1005.5}, 0.65)
        market_data_feed = {"GOOG": no_alert_market_data}

        alerts = self.rm.monitor_portfolio(self.portfolio_state, market_data_feed)
        self.assertEqual(len(alerts), 0)

    def test_approve_trade(self):
        trade_order = TradeOrder("AAPL", 'buy', 5, 150.0, datetime.now())
        self.assertTrue(self.rm.approve_trade(trade_order, self.portfolio_state, self.market_data_aapl))

    def test_reject_trade(self):
        trade_order = TradeOrder("GOOG", 'buy', 100, 1000.0, datetime.now())
        self.assertFalse(self.rm.approve_trade(trade_order, self.portfolio_state, self.market_data_goog))
