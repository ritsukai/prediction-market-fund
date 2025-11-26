# Tests for the risk management module
import unittest
from src.portfolio_manager import PortfolioManager
from src.risk_management import check_risk_limits

class TestRiskManagement(unittest.TestCase):
    def test_check_risk_limits_pass(self):
        portfolio = PortfolioManager(initial_capital=100000)
        trade = {"size": 100, "execution_price": 0.5}
        passed, message = check_risk_limits(portfolio, trade)
        self.assertTrue(passed)
        self.assertEqual(message, "Risk limits passed")

    def test_check_risk_limits_fail(self):
        portfolio = PortfolioManager(initial_capital=1000)
        trade = {"size": 200, "execution_price": 0.6}
        passed, message = check_risk_limits(portfolio, trade)
        self.assertFalse(passed)
        self.assertEqual(message, "Max position size exceeded")

if __name__ == "__main__":
    unittest.main()
