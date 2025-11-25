import unittest
from src.prediction_market_fund.portfolio_and_risk_service.portfolio_manager import PortfolioManager
from src.prediction_market_fund.portfolio_and_risk_service.models import TradeOrder, Position


class TestPortfolioManager(unittest.TestCase):

    def setUp(self):
        self.manager = PortfolioManager(initial_cash=1000.0)

    def test_get_portfolio_state_initial(self):
        state = self.manager.get_portfolio_state()
        self.assertEqual(state.cash, 1000.0)
        self.assertEqual(len(state.positions), 0)

    def test_execute_buy_order_new_position(self):
        order = TradeOrder(market_id="ETH-USD", action="BUY", amount=1.0, price=100.0)
        self.manager.execute_trade(order)

        state = self.manager.get_portfolio_state()
        self.assertEqual(state.cash, 900.0)
        self.assertEqual(len(state.positions), 1)
        self.assertIn("ETH-USD", state.positions)
        position = state.positions["ETH-USD"]
        self.assertEqual(position.amount, 1.0)
        self.assertEqual(position.entry_price, 100.0)

    def test_execute_buy_order_existing_position(self):
        # First buy
        order1 = TradeOrder(market_id="ETH-USD", action="BUY", amount=1.0, price=100.0)
        self.manager.execute_trade(order1)

        # Second buy
        order2 = TradeOrder(market_id="ETH-USD", action="BUY", amount=0.5, price=120.0)
        self.manager.execute_trade(order2)

        state = self.manager.get_portfolio_state()
        self.assertEqual(state.cash, 1000.0 - 100.0 - 60.0)
        self.assertEqual(len(state.positions), 1)
        position = state.positions["ETH-USD"]
        self.assertEqual(position.amount, 1.5)
        self.assertAlmostEqual(position.entry_price, (1 * 100 + 0.5 * 120) / 1.5)

    def test_execute_buy_order_insufficient_funds(self):
        order = TradeOrder(market_id="BTC-USD", action="BUY", amount=1.0, price=10000.0)  # Too expensive
        self.manager.execute_trade(order)

        state = self.manager.get_portfolio_state()
        self.assertEqual(state.cash, 1000.0)  # Cash should not change
        self.assertEqual(len(state.positions), 0)

    def test_execute_sell_order_full_position(self):
        buy_order = TradeOrder(market_id="ETH-USD", action="BUY", amount=1.0, price=100.0)
        self.manager.execute_trade(buy_order)

        sell_order = TradeOrder(market_id="ETH-USD", action="SELL", amount=1.0, price=150.0)
        self.manager.execute_trade(sell_order)

        state = self.manager.get_portfolio_state()
        self.assertEqual(state.cash, 1000.0 - 100.0 + 150.0)
        self.assertEqual(len(state.positions), 0) # Position should be gone

    def test_execute_sell_order_partial_position(self):
        buy_order = TradeOrder(market_id="ETH-USD", action="BUY", amount=2.0, price=100.0)
        self.manager.execute_trade(buy_order)

        sell_order = TradeOrder(market_id="ETH-USD", action="SELL", amount=0.5, price=150.0)
        self.manager.execute_trade(sell_order)

        state = self.manager.get_portfolio_state()
        self.assertEqual(state.cash, 1000.0 - 200.0 + 75.0)
        self.assertEqual(len(state.positions), 1)
        position = state.positions["ETH-USD"]
        self.assertEqual(position.amount, 1.5)
        self.assertEqual(position.entry_price, 100.0) # Entry price remains the same

    def test_execute_sell_order_no_position(self):
        sell_order = TradeOrder(market_id="XYZ-USD", action="SELL", amount=1.0, price=100.0)
        self.manager.execute_trade(sell_order)

        state = self.manager.get_portfolio_state()
        self.assertEqual(state.cash, 1000.0)
        self.assertEqual(len(state.positions), 0)

    def test_execute_sell_order_insufficient_shares(self):
        buy_order = TradeOrder(market_id="ETH-USD", action="BUY", amount=1.0, price=100.0)
        self.manager.execute_trade(buy_order)

        sell_order = TradeOrder(market_id="ETH-USD", action="SELL", amount=2.0, price=150.0)
        self.manager.execute_trade(sell_order)

        state = self.manager.get_portfolio_state()
        self.assertEqual(state.cash, 900.0) # Cash should not change from failed sell
        self.assertEqual(len(state.positions), 1)
        position = state.positions["ETH-USD"]
        self.assertEqual(position.amount, 1.0)

if __name__ == '__main__':
    unittest.main()
