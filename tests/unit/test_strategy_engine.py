import unittest
from unittest.mock import MagicMock, call
from src.strategy_engine import StrategyEngine
from src.models import MarketData, Position, InvestmentMemo, TradeExecutionResult
import datetime

class TestStrategyEngine(unittest.TestCase):

    def setUp(self):
        self.mock_market_data_service = MagicMock()
        self.mock_portfolio_manager = MagicMock()
        self.mock_risk_manager = MagicMock()

        self.strategy_engine = StrategyEngine(
            market_data_service=self.mock_market_data_service,
            portfolio_manager=self.mock_portfolio_manager,
            risk_manager=self.mock_risk_manager
        )
        self.mock_portfolio_manager.cash = 10000.0
        self.mock_portfolio_manager.MAX_POSITION_SIZE_RATIO = 0.10

        # Common mock market data
        self.mock_market_data_A = MarketData(
            market_id="market_A", current_price=0.60, timestamp=datetime.datetime.now(),
            order_book={
                "bids": [[0.59, 1000], [0.58, 2000]],
                "asks": [[0.61, 1500], [0.62, 1000]]
            }
        )
        self.mock_market_data_B = MarketData(
            market_id="market_B", current_price=0.30, timestamp=datetime.datetime.now(),
            order_book={
                "bids": [[0.29, 500], [0.28, 1000]],
                "asks": [[0.31, 750], [0.32, 500]]
            }
        )

    # Test EXP-001: Investment Memo generation
    def test_generate_investment_memo(self):
        market_id = "test_market"
        decision = "BUY"
        rationale_detail = "Test buying decision."
        memo = self.strategy_engine.generate_investment_memo(market_id, decision, rationale_detail, self.mock_market_data_A)

        self.assertIsInstance(memo, InvestmentMemo)
        self.assertEqual(memo.market_id, market_id)
        self.assertEqual(memo.decision, decision)
        self.assertIn(rationale_detail, memo.rationale)
        self.assertIn("Calculated EV:", memo.rationale)
        self.assertIn("Polymarket URL:", memo.rationale)
        self.assertIsNotNone(memo.timestamp)
        self.assertIsInstance(memo.expected_value, float)
        self.assertIsInstance(memo.conviction_level, float)
        self.assertIsInstance(memo.data_sources, list)

    # Test STRAT-001: Profit-taking
    def test_run_strategy_profit_taking(self):
        # Setup a position with profit
        profitable_position = Position(
            market_id="market_A", quantity=100.0, cost_basis=0.50, 
            direction="long", open_timestamp=datetime.datetime.now()
        )
        self.mock_portfolio_manager.get_current_positions.return_value = [profitable_position]
        self.mock_market_data_service.get_market_data.return_value = self.mock_market_data_A # Current price 0.60
        self.strategy_engine.monitored_markets = ["market_A"]

        # Mock trade execution to be successful
        self.mock_portfolio_manager.execute_trade.return_value = TradeExecutionResult(
            market_id="market_A", executed_price=0.60, executed_quantity=100.0, fees=0.60, success=True, message=""
        )

        self.strategy_engine.run_strategy()

        # Expect a sell trade for profit-taking
        self.mock_portfolio_manager.execute_trade.assert_called_once_with(
            self.mock_market_data_A, profitable_position.quantity, "sell"
        )
        # Also verify that a memo was generated for the sell
        # The memo generation is called internally by _execute_and_log_trade, which is called by run_strategy

    # Test STRAT-001: Loss-cutting
    def test_run_strategy_loss_cutting(self):
        # Setup a position with loss
        losing_position = Position(
            market_id="market_B", quantity=100.0, cost_basis=0.40, 
            direction="long", open_timestamp=datetime.datetime.now()
        )
        self.mock_portfolio_manager.get_current_positions.return_value = [losing_position]
        self.mock_market_data_service.get_market_data.return_value = self.mock_market_data_B # Current price 0.30

        # Mock trade execution to be successful
        self.mock_portfolio_manager.execute_trade.return_value = TradeExecutionResult(
            market_id="market_B", executed_price=0.30, executed_quantity=100.0, fees=0.30, success=True, message=""
        )

        self.strategy_engine.run_strategy()

        # Expect a sell trade for loss-cutting
        self.mock_portfolio_manager.execute_trade.assert_called_once_with(
            self.mock_market_data_B, losing_position.quantity, "sell"
        )

    # Test STRAT-001: New trade opportunity (buy)
    def test_run_strategy_new_trade_opportunity(self):
        self.mock_portfolio_manager.get_current_positions.return_value = [] # No current positions
        self.strategy_engine.monitored_markets = ["market_A"]
        self.mock_market_data_service.get_market_data.return_value = self.mock_market_data_A # current_price=0.60

        # Mock risk manager to allow trade
        self.mock_risk_manager.check_market_exposure.return_value = True
        # Mock trade execution to be successful
        self.mock_portfolio_manager.execute_trade.return_value = TradeExecutionResult(
            market_id="market_A", executed_price=0.61, executed_quantity=100.0, fees=0.61, success=True, message=""
        )
        self.mock_portfolio_manager.cash = 10000.0 # Sufficient cash

        self.strategy_engine.run_strategy()
        
        # Expect a buy trade
        # The quantity calculated in strategy_engine is complex, so we check for call args rather than exact quantity
        self.assertTrue(self.mock_portfolio_manager.execute_trade.called)
        call_args, _ = self.mock_portfolio_manager.execute_trade.call_args
        self.assertEqual(call_args[0], self.mock_market_data_A) # MarketData
        self.assertIsInstance(call_args[1], float) # Amount (quantity)
        self.assertGreater(call_args[1], 0) # Should be a positive quantity
        self.assertEqual(call_args[2], "buy") # Direction

    # Test RISK-001 integration: New trade opportunity rejected by risk manager
    def test_run_strategy_new_trade_opportunity_rejected_by_risk(self):
        self.mock_portfolio_manager.get_current_positions.return_value = [] # No current positions
        self.strategy_engine.monitored_markets = ["market_A"]
        self.mock_market_data_service.get_market_data.return_value = self.mock_market_data_A

        # Mock risk manager to reject trade
        self.mock_risk_manager.check_market_exposure.return_value = False
        self.mock_portfolio_manager.cash = 10000.0 # Sufficient cash

        self.strategy_engine.run_strategy()
        
        # Expect no trade execution
        self.mock_portfolio_manager.execute_trade.assert_not_called()

if __name__ == '__main__':
    unittest.main()
