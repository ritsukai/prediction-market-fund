# Tests for the paper trader module
import unittest
from src.paper_trader import execute_trade

class TestPaperTrader(unittest.TestCase):
    def test_execute_trade_buy(self):
        trade = execute_trade(market_id="1", decision="BUY", size=100, price=0.5)
        self.assertEqual(trade["execution_price"], 0.505)
        self.assertAlmostEqual(trade["fee_amount"], 0.505)
        self.assertAlmostEqual(trade["net_trade_value"], 49.995)

    def test_execute_trade_sell(self):
        trade = execute_trade(market_id="1", decision="SELL", size=100, price=0.5)
        self.assertEqual(trade["execution_price"], 0.495)
        self.assertAlmostEqual(trade["fee_amount"], 0.495)
        self.assertAlmostEqual(trade["net_trade_value"], 49.005)

if __name__ == "__main__":
    unittest.main()
