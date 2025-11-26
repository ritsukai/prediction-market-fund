# Tests for the portfolio manager module
import unittest
from src.portfolio_manager import PortfolioManager

class TestPortfolioManager(unittest.TestCase):
    def test_update_portfolio_buy(self):
        portfolio = PortfolioManager(initial_capital=100000)
        trade = {"decision": "BUY", "market_id": "1", "size": 100, "net_trade_value": 50.0}
        portfolio.update_portfolio(trade)
        self.assertEqual(portfolio.cash, 99950.0)
        self.assertEqual(portfolio.positions["1"], 100)

    def test_update_portfolio_sell(self):
        portfolio = PortfolioManager(initial_capital=100000)
        portfolio.positions["1"] = 100
        trade = {"decision": "SELL", "market_id": "1", "size": 50, "net_trade_value": 25.0}
        portfolio.update_portfolio(trade)
        self.assertEqual(portfolio.cash, 100025.0)
        self.assertEqual(portfolio.positions["1"], 50)

if __name__ == "__main__":
    unittest.main()
