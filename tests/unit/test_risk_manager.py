import unittest
from unittest.mock import MagicMock
from src.risk_manager import RiskManager
from src.models import Position, MarketData
import datetime

class TestRiskManager(unittest.TestCase):

    def setUp(self):
        # Mock a get_nav function for the RiskManager
        self.mock_get_nav = MagicMock(return_value=10000.0) # Assume NAV of $10,000
        self.risk_manager = RiskManager(self.mock_get_nav)
        self.risk_manager.sector_mapping = {
            "market_A": "US Politics",
            "market_B": "Crypto Events",
            "market_C": "US Politics",
            "market_D": "Tech Stocks"
        }

    # Test RISK-001: Max position size
    def test_check_market_exposure_max_position_size(self):
        current_positions = [
            Position("market_A", 1000.0, 5.0, "long", datetime.datetime.now()) # $5000 position
        ] # 50% of NAV, already over 10% limit
        self.mock_get_nav.return_value = 10000.0

        # Proposed trade would make it even larger
        proposed_trade_amount = 500.0 # $500 more
        self.assertFalse(self.risk_manager.check_market_exposure("market_A", proposed_trade_amount, current_positions))

        # A smaller position, within limits, should pass initially
        current_positions_ok = [
            Position("market_D", 100.0, 5.0, "long", datetime.datetime.now()) # $500 position, 5% of NAV
        ]
        self.assertTrue(self.risk_manager.check_market_exposure("market_D", 100.0, current_positions_ok)) # Proposed $100, total $600, still 6% NAV

        # Proposed trade would exceed max position size
        current_positions_near_limit = [
            Position("market_D", 180.0, 5.0, "long", datetime.datetime.now()) # $900 position, 9% of NAV
        ]
        self.assertFalse(self.risk_manager.check_market_exposure("market_D", 101.0, current_positions_near_limit)) # Proposed $101, total $1001, 10.01% NAV


    # Test RISK-001: Max sector exposure
    def test_check_market_exposure_max_sector_exposure(self):
        current_positions = [
            Position("market_A", 1000.0, 2.0, "long", datetime.datetime.now()), # US Politics: $2000
            Position("market_C", 500.0, 2.0, "long", datetime.datetime.now())   # US Politics: $1000. Total $3000, 30% of NAV
        ]
        self.mock_get_nav.return_value = 10000.0

        # Proposed trade would exceed sector limit
        proposed_trade_amount = 100.0 # $100 more in US Politics
        self.assertFalse(self.risk_manager.check_market_exposure("market_A", proposed_trade_amount, current_positions))

        # A separate market in the same sector should also be rejected
        self.assertFalse(self.risk_manager.check_market_exposure("market_C", proposed_trade_amount, current_positions))

        # Proposed trade in a different sector should pass (if within its own limits)
        self.assertTrue(self.risk_manager.check_market_exposure("market_B", 1000.0, current_positions)) # Crypto Events, $1000, 10% NAV, well within limit.

    # Test assess_risk with various scenarios
    def test_assess_risk(self):
        self.mock_get_nav.return_value = 10000.0
        portfolio = [
            Position("market_A", 500.0, 5.0, "long", datetime.datetime.now()),   # $2500 (25% NAV)
            Position("market_B", 200.0, 10.0, "long", datetime.datetime.now()),  # $2000 (20% NAV)
            Position("market_C", 100.0, 10.0, "long", datetime.datetime.now())   # $1000 (10% NAV)
        ]

        risk_assessment = self.risk_manager.assess_risk(portfolio)

        self.assertAlmostEqual(risk_assessment["current_nav"], 10000.0)
        self.assertTrue(risk_assessment["risk_flags"]) # Should have flags due to market_A and market_B

        # Check individual position exposure
        self.assertGreater(risk_assessment["position_exposure"]["market_A"], self.risk_manager.MAX_POSITION_SIZE_RATIO)
        self.assertGreater(risk_assessment["position_exposure"]["market_B"], self.risk_manager.MAX_POSITION_SIZE_RATIO)
        self.assertAlmostEqual(risk_assessment["position_exposure"]["market_C"], 0.10) # At the limit

        # Check sector exposure
        # market_A and market_C are "US Politics": (2500 + 1000) / 10000 = 35%
        self.assertGreater(risk_assessment["sector_exposure"]["US Politics"], self.risk_manager.MAX_SECTOR_EXPOSURE_RATIO)
        self.assertAlmostEqual(risk_assessment["sector_exposure"]["Crypto Events"], 0.20) # 2000 / 10000 = 20%

        # Test with no risk flags
        portfolio_no_risk = [
            Position("market_A", 100.0, 5.0, "long", datetime.datetime.now()), # $500 (5% NAV)
            Position("market_B", 100.0, 5.0, "long", datetime.datetime.now()), # $500 (5% NAV)
        ]
        risk_assessment_no_risk = self.risk_manager.assess_risk(portfolio_no_risk)
        self.assertFalse(risk_assessment_no_risk["risk_flags"])

if __name__ == '__main__':
    unittest.main()
