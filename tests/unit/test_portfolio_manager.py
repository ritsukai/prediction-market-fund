import unittest
from unittest.mock import MagicMock
import datetime
from src.portfolio_manager import PortfolioManager
from src.models import MarketData, Position, TradeExecutionResult

class TestPortfolioManager(unittest.TestCase):

    def setUp(self):
        self.portfolio_manager = PortfolioManager()
        self.mock_market_data_high_liquidity = MarketData(
            market_id="market_A",
            current_price=0.60,
            timestamp=datetime.datetime.now(),
            order_book={
                "bids": [[0.59, 10000], [0.58, 20000]], # Total $5900 + $11600 = $17500 bid depth
                "asks": [[0.61, 15000], [0.62, 10000]]  # Total $9150 + $6200 = $15350 ask depth
            }
        )
        self.mock_market_data_low_liquidity = MarketData(
            market_id="market_B",
            current_price=0.50,
            timestamp=datetime.datetime.now(),
            order_book={
                "bids": [[0.49, 10], [0.48, 20]], # Total $4.90 + $9.60 = $14.50 bid depth (very low)
                "asks": [[0.51, 15], [0.52, 10]]  # Total $7.65 + $5.20 = $12.85 ask depth (very low)
            }
        )
        self.mock_market_data_no_order_book = MarketData(
            market_id="market_C",
            current_price=0.70,
            timestamp=datetime.datetime.now(),
            order_book=None
        )

    # Test for SIM-001: Insufficient liquidity
    def test_execute_trade_insufficient_liquidity(self):
        # Try to buy for an amount that exceeds low liquidity
        result = self.portfolio_manager.execute_trade(self.mock_market_data_low_liquidity, 100.0, "buy")
        self.assertFalse(result.success)
        self.assertIn("Insufficient liquidity", result.message)

        # Even a small trade should fail if total depth is below MIN_LIQUIDITY_REQUIRED
        result_small_trade = self.portfolio_manager.execute_trade(self.mock_market_data_low_liquidity, 1.0, "buy")
        self.assertFalse(result_small_trade.success)
        self.assertIn("Insufficient liquidity", result_small_trade.message)

    # Test for SIM-001: No order book data
    def test_execute_trade_no_order_book_data(self):
        result = self.portfolio_manager.execute_trade(self.mock_market_data_no_order_book, 10.0, "buy")
        self.assertFalse(result.success)
        self.assertIn("No order book data", result.message)

    # Test for SIM-001: Fees deduction and price calculation
    def test_execute_trade_with_fees_and_slippage(self):
        initial_cash = self.portfolio_manager.cash
        buy_amount_quantity = 1000.0 / self.mock_market_data_high_liquidity.order_book["asks"][0][0] # Buy for ~1000 value
        result = self.portfolio_manager.execute_trade(self.mock_market_data_high_liquidity, buy_amount_quantity, "buy")
        
        self.assertTrue(result.success)
        self.assertGreater(result.executed_price, self.mock_market_data_high_liquidity.current_price) # Expect slippage
        self.assertGreater(result.fees, 0) # Expect fees
        self.assertLess(self.portfolio_manager.cash, initial_cash) # Cash should decrease
        self.assertIn(self.mock_market_data_high_liquidity.market_id, self.portfolio_manager.positions)

        position = self.portfolio_manager.positions[self.mock_market_data_high_liquidity.market_id]
        self.assertAlmostEqual(position.quantity, result.executed_quantity)
        self.assertAlmostEqual(position.cost_basis, result.executed_price)
        
        # Test selling
        sell_amount_quantity = position.quantity / 2
        initial_cash_after_buy = self.portfolio_manager.cash
        result_sell = self.portfolio_manager.execute_trade(self.mock_market_data_high_liquidity, sell_amount_quantity, "sell")

        self.assertTrue(result_sell.success)
        self.assertGreater(result_sell.fees, 0)
        self.assertGreater(self.portfolio_manager.cash, initial_cash_after_buy) # Cash should increase after selling (minus fees)
        expected_remaining_quantity = result.executed_quantity / 2 # Expected to be half of the initial buy
        self.assertAlmostEqual(self.portfolio_manager.positions[self.mock_market_data_high_liquidity.market_id].quantity, expected_remaining_quantity)

    def test_execute_trade_insufficient_cash(self):
        # Drain cash
        self.portfolio_manager.cash = 10.0
        result = self.portfolio_manager.execute_trade(self.mock_market_data_high_liquidity, 100.0, "buy")
        self.assertFalse(result.success)
        self.assertIn("Insufficient cash", result.message)

    def test_execute_trade_insufficient_position_to_sell(self):
        result = self.portfolio_manager.execute_trade(self.mock_market_data_high_liquidity, 10.0, "sell")
        self.assertFalse(result.success)
        self.assertIn("Insufficient position to sell", result.message)

    def test_calculate_nav(self):
        self.portfolio_manager.cash = 5000.0
        self.portfolio_manager.positions["market_A"] = Position(
            market_id="market_A", quantity=100.0, cost_basis=0.50, 
            direction="long", open_timestamp=datetime.datetime.now()
        )
        self.portfolio_manager.positions["market_B"] = Position(
            market_id="market_B", quantity=200.0, cost_basis=0.30, 
            direction="long", open_timestamp=datetime.datetime.now()
        )
        
        # Without current_market_data, uses cost_basis
        nav_without_market_data = self.portfolio_manager.calculate_nav()
        self.assertAlmostEqual(nav_without_market_data, 5000 + (100*0.50) + (200*0.30))

        # With current_market_data
        mock_current_market_data = {
            "market_A": MarketData("market_A", 0.60, datetime.datetime.now()),
            "market_B": MarketData("market_B", 0.40, datetime.datetime.now())
        }
        nav_with_market_data = self.portfolio_manager.calculate_nav(mock_current_market_data)
        self.assertAlmostEqual(nav_with_market_data, 5000 + (100*0.60) + (200*0.40))

    def test_partial_sell_updates_quantity_correctly(self):
        market_id = "test_market_partial_sell"
        initial_quantity = 100.0
        initial_cost_basis = 0.50
        sell_quantity = 30.0 # Sell a portion

        # Manually set up a position
        self.portfolio_manager.positions[market_id] = Position(
            market_id=market_id, quantity=initial_quantity, cost_basis=initial_cost_basis,
            direction="long", open_timestamp=datetime.datetime.now()
        )
        self.portfolio_manager.cash = 10000.0 # Ensure enough cash for initial setup if needed

        mock_market_data = MarketData(
            market_id=market_id,
            current_price=0.60,
            timestamp=datetime.datetime.now(),
            order_book={
                "bids": [[0.59, 10000], [0.58, 20000]], # Sufficient liquidity
                "asks": [[0.61, 15000], [0.62, 10000]]  # Sufficient liquidity
            }
        )

        result = self.portfolio_manager.execute_trade(mock_market_data, sell_quantity, "sell")

        self.assertTrue(result.success)
        self.assertIn(market_id, self.portfolio_manager.positions) # Position should still exist
        self.assertAlmostEqual(self.portfolio_manager.positions[market_id].quantity, initial_quantity - sell_quantity)
        self.assertGreater(self.portfolio_manager.cash, 10000.0) # Cash should have increased (minus fees)

if __name__ == '__main__':
    unittest.main()
