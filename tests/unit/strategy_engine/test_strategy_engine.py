import unittest
from unittest.mock import Mock
from datetime import datetime

from src.prediction_market_fund.strategy_engine.strategy_engine import StrategyEngine
from src.prediction_market_fund.interfaces.market_data_interface import MarketData, IMarketDataService
from src.prediction_market_fund.interfaces.portfolio_risk_interface import PortfolioState, Position, TradeOrder, IPortfolioManager, IRiskManager
from src.prediction_market_fund.interfaces.strategy_engine_interface import InvestmentMemo

class TestStrategyEngine(unittest.TestCase):

    def setUp(self):
        self.mock_market_data_service = Mock(spec=IMarketDataService)
        self.mock_portfolio_manager = Mock(spec=IPortfolioManager)
        self.mock_risk_manager = Mock(spec=IRiskManager)

        self.strategy_engine = StrategyEngine(
            market_data_service=self.mock_market_data_service,
            portfolio_manager=self.mock_portfolio_manager,
            risk_manager=self.mock_risk_manager,
            min_conviction_for_trade=0.7,
            trade_amount_per_decision=100.0
        )

        # Mock initial portfolio state
        self.initial_portfolio_state = PortfolioState(
            cash_balance=1000.0,
            positions={
                "market-old": Position(market_id="market-old", asset="YES", quantity=50.0, cost_basis=0.4)
            }
        )
        self.mock_portfolio_manager.get_portfolio_state.return_value = self.initial_portfolio_state

    def test_run_strategy_buy_opportunity(self):
        """Test strategy engine identifies a BUY opportunity and generates trade/memo."""
        mock_market_data = MarketData(
            market_id="market-123",
            question="Test Question",
            current_price=0.5,
            volume_24h=100.0,
            total_liquidity=1000.0
        )

        # Mock _calculate_ev_and_conviction to force a BUY signal
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.7, 0.8)) # EV > price, high conviction
        self.mock_risk_manager.assess_trade_risk.return_value = True # Assume risk manager approves

        trades, memos = self.strategy_engine.run_strategy(mock_market_data, self.initial_portfolio_state)

        self.assertEqual(len(trades), 1)
        self.assertEqual(len(memos), 1)

        trade = trades[0]
        memo = memos[0]

        self.assertEqual(trade.action, "BUY")
        self.assertAlmostEqual(trade.quantity, self.strategy_engine.trade_amount_per_decision / mock_market_data.current_price)
        self.assertEqual(trade.market_id, "market-123")

        self.assertEqual(memo.action, "BUY")
        self.assertIn("Identified BUY opportunity", memo.rationale)
        self.assertEqual(memo.market_id, "market-123")
        self.mock_risk_manager.assess_trade_risk.assert_called_once() # ARCH-001-REFERENCE

    def test_run_strategy_sell_opportunity(self):
        """Test strategy engine identifies a SELL opportunity and generates trade/memo."""
        mock_market_data = MarketData(
            market_id="market-old", # Use a market where we have a position
            question="Old Market Question",
            current_price=0.8,
            volume_24h=200.0,
            total_liquidity=2000.0
        )

        # Mock _calculate_ev_and_conviction to force a SELL signal
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.6, 0.8)) # EV < price, high conviction
        self.mock_risk_manager.assess_trade_risk.return_value = True

        trades, memos = self.strategy_engine.run_strategy(mock_market_data, self.initial_portfolio_state)

        self.assertEqual(len(trades), 1)
        self.assertEqual(len(memos), 1)

        trade = trades[0]
        memo = memos[0]

        # For a SELL, the quantity should be capped at the available position quantity if the calculated trade amount is higher.
        expected_sell_quantity = min(self.strategy_engine.trade_amount_per_decision / mock_market_data.current_price, self.initial_portfolio_state.positions["market-old"].quantity)
        self.assertAlmostEqual(trade.quantity, expected_sell_quantity)
        self.assertEqual(trade.market_id, "market-old")
        self.assertEqual(memo.action, "SELL")
        self.assertIn("Identified SELL opportunity", memo.rationale)
        self.mock_risk_manager.assess_trade_risk.assert_called_once()

    def test_run_strategy_no_trade_low_conviction(self):
        """Test strategy engine does not trade with low conviction."""
        mock_market_data = MarketData(
            market_id="market-456",
            question="Another Question",
            current_price=0.5,
            volume_24h=50.0,
            total_liquidity=500.0
        )
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.8, 0.5)) # High EV, but low conviction

        trades, memos = self.strategy_engine.run_strategy(mock_market_data, self.initial_portfolio_state)

        self.assertEqual(len(trades), 0)
        self.assertEqual(len(memos), 0)
        self.mock_risk_manager.assess_trade_risk.assert_not_called()

    def test_run_strategy_no_trade_no_opportunity(self):
        """Test strategy engine does not trade when EV is close to current price."""
        mock_market_data = MarketData(
            market_id="market-789",
            question="Neutral Question",
            current_price=0.5,
            volume_24h=50.0,
            total_liquidity=500.0
        )
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.51, 0.8)) # EV close to price, high conviction

        trades, memos = self.strategy_engine.run_strategy(mock_market_data, self.initial_portfolio_state)

        self.assertEqual(len(trades), 0)
        self.assertEqual(len(memos), 0)
        self.mock_risk_manager.assess_trade_risk.assert_not_called()

    def test_run_strategy_risk_manager_rejects(self):
        """Test trade is not executed if Risk Manager rejects it."""
        mock_market_data = MarketData(
            market_id="market-rejected",
            question="Question Rejected",
            current_price=0.5,
            volume_24h=100.0,
            total_liquidity=1000.0
        )

        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.7, 0.8))
        self.mock_risk_manager.assess_trade_risk.return_value = False # Risk manager rejects

        trades, memos = self.strategy_engine.run_strategy(mock_market_data, self.initial_portfolio_state)

        self.assertEqual(len(trades), 0)
        self.assertEqual(len(memos), 0)
        self.mock_risk_manager.assess_trade_risk.assert_called_once()
    
    def test_run_strategy_insufficient_cash_to_buy(self):
        """Test BUY trade is not attempted if cash balance is too low."""
        mock_market_data = MarketData(
            market_id="market-nocash",
            question="No Cash Question",
            current_price=100.0,
            volume_24h=10.0,
            total_liquidity=100.0
        )

        # Set a very low cash balance that can't cover a trade
        low_cash_portfolio = PortfolioState(cash_balance=5.0)

        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.9, 0.8)) # Strong buy signal

        trades, memos = self.strategy_engine.run_strategy(mock_market_data, low_cash_portfolio)

        self.assertEqual(len(trades), 0)
        self.assertEqual(len(memos), 0)
        self.mock_risk_manager.assess_trade_risk.assert_not_called()

    def test_run_strategy_insufficient_shares_to_sell(self):
        """Test SELL trade is not attempted if no shares or insufficient shares are held."""
        mock_market_data = MarketData(
            market_id="market-noshares",
            question="No Shares Question",
            current_price=0.5,
            volume_24h=100.0,
            total_liquidity=1000.0
        )
        # Portfolio with no position in market-noshares
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.1, 0.8)) # Strong sell signal

        trades, memos = self.strategy_engine.run_strategy(mock_market_data, self.initial_portfolio_state)

        self.assertEqual(len(trades), 0)
        self.assertEqual(len(memos), 0)
        self.mock_risk_manager.assess_trade_risk.assert_not_called()

    def test_run_strategy_profit_taking(self):
        """Test strategy engine identifies a profit-taking opportunity and generates a SELL trade/memo."""
        # Setup a market where we have a profitable position
        profitable_market_id = "market-profitable"
        profitable_position = Position(
            market_id=profitable_market_id, asset="YES", quantity=100.0, cost_basis=0.3
        )
        profit_portfolio_state = PortfolioState(
            cash_balance=1000.0,
            positions={profitable_market_id: profitable_position}
        )
        mock_market_data = MarketData(
            market_id=profitable_market_id,
            question="Profitable Question",
            current_price=0.6, # Significantly higher than cost_basis (0.3)
            volume_24h=100.0,
            total_liquidity=1000.0
        )

        # Mock EV to be neutral to avoid conflicting with profit-taking logic
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.6, 0.8))
        self.mock_risk_manager.assess_trade_risk.return_value = True

        trades, memos = self.strategy_engine.run_strategy(mock_market_data, profit_portfolio_state)

        self.assertEqual(len(trades), 1)
        self.assertEqual(len(memos), 1)

        trade = trades[0]
        memo = memos[0]

        self.assertEqual(trade.action, "SELL")
        self.assertAlmostEqual(trade.quantity, profitable_position.quantity) # Should sell entire position
        self.assertEqual(trade.market_id, profitable_market_id)

        self.assertEqual(memo.action, "SELL")
        self.assertIn("Identified profit-taking opportunity.", memo.rationale)
        self.assertEqual(memo.market_id, profitable_market_id)
        self.mock_risk_manager.assess_trade_risk.assert_called_once()

    def test_run_strategy_loss_cutting(self):
        """Test strategy engine identifies a loss-cutting opportunity and generates a SELL trade/memo."""
        # Setup a market where we have a losing position
        losing_market_id = "market-losing"
        losing_position = Position(
            market_id=losing_market_id, asset="YES", quantity=100.0, cost_basis=0.8
        )
        loss_portfolio_state = PortfolioState(
            cash_balance=1000.0,
            positions={losing_market_id: losing_position}
        )
        mock_market_data = MarketData(
            market_id=losing_market_id,
            question="Losing Question",
            current_price=0.4, # Significantly lower than cost_basis (0.8)
            volume_24h=100.0,
            total_liquidity=1000.0
        )

        # Mock EV to be neutral to avoid conflicting with loss-cutting logic
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.4, 0.8))
        self.mock_risk_manager.assess_trade_risk.return_value = True

        trades, memos = self.strategy_engine.run_strategy(mock_market_data, loss_portfolio_state)

        self.assertEqual(len(trades), 1)
        self.assertEqual(len(memos), 1)

        trade = trades[0]
        memo = memos[0]

        self.assertEqual(trade.action, "SELL")
        self.assertAlmostEqual(trade.quantity, losing_position.quantity) # Should sell entire position
        self.assertEqual(trade.market_id, losing_market_id)

        self.assertEqual(memo.action, "SELL")
        self.assertIn("Identified loss-cutting opportunity.", memo.rationale)
        self.assertEqual(memo.market_id, losing_market_id)
        self.mock_risk_manager.assess_trade_risk.assert_called_once()

if __name__ == '__main__':
    unittest.main()
