import unittest
from datetime import datetime
from src.portfolio_and_risk_service.portfolio_manager import PortfolioManager
from src.portfolio_and_risk_service.models import PortfolioState, Position, TradeOrder

class TestPortfolioManager(unittest.TestCase):

    def setUp(self):
        self.initial_cash = 10000.0
        self.pm = PortfolioManager(initial_cash=self.initial_cash)

    def test_initial_portfolio_state(self):
        state = self.pm.get_portfolio_state()
        self.assertEqual(state.cash, self.initial_cash)
        self.assertEqual(state.nav, self.initial_cash)
        self.assertEqual(len(state.positions), 0)
        self.assertEqual(len(state.trade_history), 0)

    def test_buy_order(self):
        trade_order = TradeOrder("AAPL", 'buy', 10, 150.0, datetime.now())
        execution_price = 150.0
        fees = 1.5 # 1% of 10 * 150
        self.pm.process_trade_order(trade_order, execution_price, fees)

        state = self.pm.get_portfolio_state()
        self.assertEqual(state.cash, self.initial_cash - (10 * 150.0) - fees)
        self.assertAlmostEqual(state.nav, self.initial_cash - fees, places=2) # NAV should reflect market value of positions
        self.assertEqual(len(state.positions), 1)
        self.assertEqual(state.positions[0].asset_id, "AAPL")
        self.assertEqual(state.positions[0].quantity, 10)
        self.assertEqual(len(state.trade_history), 1)

    def test_sell_order(self):
        # First buy some shares
        buy_order = TradeOrder("AAPL", 'buy', 10, 150.0, datetime.now())
        self.pm.process_trade_order(buy_order, 150.0, 1.5)

        # Then sell some shares
        sell_order = TradeOrder("AAPL", 'sell', 5, 160.0, datetime.now())
        self.pm.process_trade_order(sell_order, 160.0, 0.8) # 1% of 5 * 160

        state = self.pm.get_portfolio_state()
        # Cash = initial - buy_cost + sell_revenue
        expected_cash = self.initial_cash - (10 * 150.0 + 1.5) + (5 * 160.0 - 0.8)
        self.assertAlmostEqual(state.cash, expected_cash, places=2)
        self.assertEqual(len(state.positions), 1)
        self.assertEqual(state.positions[0].asset_id, "AAPL")
        self.assertEqual(state.positions[0].quantity, 5)
        self.assertEqual(len(state.trade_history), 2)
    
    def test_buy_more_of_existing_position(self):
        # First buy some shares
        buy_order_1 = TradeOrder("AAPL", 'buy', 10, 150.0, datetime.now())
        self.pm.process_trade_order(buy_order_1, 150.0, 1.5)
        
        # Buy more
        buy_order_2 = TradeOrder("AAPL", 'buy', 5, 160.0, datetime.now())
        self.pm.process_trade_order(buy_order_2, 160.0, 0.8)

        state = self.pm.get_portfolio_state()
        self.assertEqual(len(state.positions), 1)
        self.assertEqual(state.positions[0].asset_id, "AAPL")
        self.assertEqual(state.positions[0].quantity, 15)
        # (10 * 150 + 5 * 160) / 15
        self.assertAlmostEqual(state.positions[0].average_entry_price, 153.33, places=2)

    def test_sell_all_position(self):
        buy_order = TradeOrder("MSFT", 'buy', 5, 200.0, datetime.now())
        self.pm.process_trade_order(buy_order, 200.0, 1.0)

        sell_order = TradeOrder("MSFT", 'sell', 5, 210.0, datetime.now())
        self.pm.process_trade_order(sell_order, 210.0, 1.05)

        state = self.pm.get_portfolio_state()
        self.assertEqual(len(state.positions), 0)
        expected_cash = self.initial_cash - (5 * 200.0 + 1.0) + (5 * 210.0 - 1.05)
        self.assertAlmostEqual(state.cash, expected_cash, places=2)

    def test_insufficient_cash_for_buy(self):
        trade_order = TradeOrder("GOOG", 'buy', 100, 1000.0, datetime.now())
        with self.assertRaisesRegex(ValueError, "Insufficient cash to execute buy order."):
            self.pm.process_trade_order(trade_order, 1000.0, 10.0)

    def test_insufficient_quantity_for_sell(self):
        buy_order = TradeOrder("AMZN", 'buy', 5, 100.0, datetime.now())
        self.pm.process_trade_order(buy_order, 100.0, 0.5)

        sell_order = TradeOrder("AMZN", 'sell', 10, 110.0, datetime.now())
        with self.assertRaisesRegex(ValueError, "Insufficient quantity to execute sell order."):
            self.pm.process_trade_order(sell_order, 110.0, 1.0)

    def test_recalculate_nav_with_market_price_change(self):
        buy_order = TradeOrder("AAPL", 'buy', 10, 150.0, datetime.now())
        self.pm.process_trade_order(buy_order, 150.0, 1.5)
        
        # Manually update current_price for NAV recalculation simulation
        for position in self.pm._portfolio_state.positions:
            if position.asset_id == "AAPL":
                position.current_price = 160.0
                break
        
        state = self.pm.get_portfolio_state()
        # NAV = cash + (10 * 160.0)
        expected_nav = (self.initial_cash - (10 * 150.0) - 1.5) + (10 * 160.0)
        self.assertAlmostEqual(state.nav, expected_nav, places=2)
