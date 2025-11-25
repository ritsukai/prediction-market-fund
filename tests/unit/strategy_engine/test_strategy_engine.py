import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import importlib

from src.prediction_market_fund.strategy_engine.strategy_engine import StrategyEngine
from src.prediction_market_fund.interfaces.market_data_interface import IMarketDataService, MarketData, MarketPriceData
from src.prediction_market_fund.interfaces.portfolio_risk_interface import IPortfolioManager, IRiskManager
from src.prediction_market_fund.portfolio_and_risk_service import models # Import the module
from src.prediction_market_fund.interfaces.strategy_engine_interface import InvestmentMemo

class TestStrategyEngine(unittest.TestCase):

    def setUp(self):
        # Reload the models module to ensure latest dataclass definitions are used
        importlib.reload(models)
        from src.prediction_market_fund.interfaces.portfolio_risk_interface import PortfolioState, Position, TradeOrder

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

        # Mock initial portfolio state for _manage_existing_positions
        self.initial_portfolio_state_with_position = PortfolioState(
            cash_balance=1000.0,
            positions={
                "market-old": Position(market_id="market-old", asset="yes", quantity=50.0, cost_basis=0.4, entry_price=0.4, current_price=0.4, unrealized_pnl=0.0)
            }
        )

        self.initial_portfolio_state_empty = PortfolioState(cash_balance=1000.0, positions={})


    @patch('src.prediction_market_fund.strategy_engine.strategy_engine.datetime')
    def test_run_strategy_buy_opportunity(self, mock_datetime):
        """Test strategy engine identifies a BUY opportunity and generates trade/memo."""
        mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0)

        mock_market_data_list = [
            MarketData(
                market_id="market-123",
                question="Test Question",
                current_price=0.5,
                volume_24h=100.0,
                total_liquidity=1000.0
            )
        ]
        mock_market_price_data = MarketPriceData(market_id="market-123", asset="yes", price=0.5, timestamp=datetime.now())

        self.mock_market_data_service.get_all_market_data.return_value = mock_market_data_list
        self.mock_market_data_service.get_market_price.return_value = mock_market_price_data
        self.mock_portfolio_manager.get_portfolio_state.return_value = self.initial_portfolio_state_empty
        self.mock_risk_manager.assess_trade_risk.return_value = True # Assume risk manager approves

        # Mock _calculate_ev_and_conviction to force a BUY signal
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.75, 0.8)) # EV > price, high conviction

        trades, memos = self.strategy_engine.run_strategy(Mock(), Mock()) # market_data and portfolio_state params are now ignored

        self.assertEqual(len(trades), 1)
        self.assertEqual(len(memos), 1)

        trade = trades[0]
        memo = memos[0]

        self.assertEqual(trade.action, "BUY")
        self.assertAlmostEqual(trade.quantity, self.strategy_engine.trade_amount_per_decision / mock_market_price_data.price)
        self.assertEqual(trade.market_id, "market-123")

        self.assertEqual(memo.action, "BUY")
        self.assertIn("New opportunity", memo.rationale)
        self.assertEqual(memo.market_id, "market-123")
        self.mock_risk_manager.assess_trade_risk.assert_called_once()
        self.mock_market_data_service.get_all_market_data.assert_called_once()
        self.mock_portfolio_manager.get_portfolio_state.assert_called_once()

    @patch('src.prediction_market_fund.strategy_engine.strategy_engine.datetime')
    def test_run_strategy_sell_opportunity(self, mock_datetime):
        """Test strategy engine identifies a SELL opportunity (profit-taking or stop-loss) and generates trade/memo."""
        mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0)

        profitable_market_id = "market-old"
        profitable_position = Position(
            market_id=profitable_market_id, asset="yes", quantity=50.0, cost_basis=0.4, entry_price=0.4, current_price=0.4, unrealized_pnl=0.0
        )
        profit_portfolio_state = PortfolioState(
            cash_balance=1000.0,
            positions={profitable_market_id: profitable_position}
        )

        mock_market_price_data = MarketPriceData(market_id=profitable_market_id, asset="yes", price=0.8, timestamp=datetime.now())
        mock_market_data_list = [MarketData(market_id=profitable_market_id, question="q", current_price=0.8, volume_24h=100, total_liquidity=1000)]

        self.mock_market_data_service.get_all_market_data.return_value = mock_market_data_list
        self.mock_market_data_service.get_market_price.return_value = mock_market_price_data
        self.mock_portfolio_manager.get_portfolio_state.return_value = profit_portfolio_state
        self.mock_risk_manager.assess_trade_risk.return_value = True

        # Mock _calculate_ev_and_conviction to avoid new buy opportunities
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.5, 0.8))

        trades, memos = self.strategy_engine.run_strategy(Mock(), Mock())

        self.assertEqual(len(trades), 1)
        self.assertEqual(len(memos), 1)

        trade = trades[0]
        memo = memos[0]

        self.assertEqual(trade.action, "SELL")
        self.assertAlmostEqual(trade.quantity, profitable_position.quantity)
        self.assertEqual(trade.market_id, profitable_market_id)

        self.assertEqual(memo.action, "SELL")
        self.assertIn("Profit-taking", memo.rationale)
        self.assertEqual(memo.market_id, profitable_market_id)
        self.mock_risk_manager.assess_trade_risk.assert_called_once()

    @patch('src.prediction_market_fund.strategy_engine.strategy_engine.datetime')
    def test_run_strategy_no_trade_low_conviction(self, mock_datetime):
        """Test strategy engine does not trade with low conviction for new opportunities."""
        mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0)

        mock_market_data_list = [
            MarketData(
                market_id="market-456",
                question="Another Question",
                current_price=0.5,
                volume_24h=50.0,
                total_liquidity=500.0
            )
        ]
        mock_market_price_data = MarketPriceData(market_id="market-456", asset="yes", price=0.5, timestamp=datetime.now())

        self.mock_market_data_service.get_all_market_data.return_value = mock_market_data_list
        self.mock_market_data_service.get_market_price.return_value = mock_market_price_data
        self.mock_portfolio_manager.get_portfolio_state.return_value = self.initial_portfolio_state_empty
        self.mock_risk_manager.assess_trade_risk.return_value = True

        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.8, 0.5)) # High EV, but low conviction

        trades, memos = self.strategy_engine.run_strategy(Mock(), Mock())

        self.assertEqual(len(trades), 0)
        self.assertEqual(len(memos), 0)
        self.mock_risk_manager.assess_trade_risk.assert_not_called()

    @patch('src.prediction_market_fund.strategy_engine.strategy_engine.datetime')
    def test_run_strategy_no_trade_no_opportunity(self, mock_datetime):
        """Test strategy engine does not trade when EV is close to current price or no new opportunities."""
        mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0)

        mock_market_data_list = [
            MarketData(
                market_id="market-789",
                question="Neutral Question",
                current_price=0.5,
                volume_24h=50.0,
                total_liquidity=500.0
            )
        ]
        mock_market_price_data = MarketPriceData(market_id="market-789", asset="yes", price=0.5, timestamp=datetime.now())

        self.mock_market_data_service.get_all_market_data.return_value = mock_market_data_list
        self.mock_market_data_service.get_market_price.return_value = mock_market_price_data
        self.mock_portfolio_manager.get_portfolio_state.return_value = self.initial_portfolio_state_empty
        self.mock_risk_manager.assess_trade_risk.return_value = True

        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.51, 0.8)) # EV close to price, high conviction

        trades, memos = self.strategy_engine.run_strategy(Mock(), Mock())

        self.assertEqual(len(trades), 0)
        self.assertEqual(len(memos), 0)
        self.mock_risk_manager.assess_trade_risk.assert_not_called()

    @patch('src.prediction_market_fund.strategy_engine.strategy_engine.datetime')
    def test_run_strategy_risk_manager_rejects(self, mock_datetime):
        """Test trade is not executed if Risk Manager rejects it."""
        mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0)

        mock_market_data_list = [
            MarketData(
                market_id="market-rejected",
                question="Question Rejected",
                current_price=0.5,
                volume_24h=100.0,
                total_liquidity=1000.0
            )
        ]
        mock_market_price_data = MarketPriceData(market_id="market-rejected", asset="yes", price=0.5, timestamp=datetime.now())

        self.mock_market_data_service.get_all_market_data.return_value = mock_market_data_list
        self.mock_market_data_service.get_market_price.return_value = mock_market_price_data
        self.mock_portfolio_manager.get_portfolio_state.return_value = self.initial_portfolio_state_empty

        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.75, 0.8))
        self.mock_risk_manager.assess_trade_risk.return_value = False # Risk manager rejects

        trades, memos = self.strategy_engine.run_strategy(Mock(), Mock())

        self.assertEqual(len(trades), 0)
        self.assertEqual(len(memos), 0)
        self.mock_risk_manager.assess_trade_risk.assert_called_once()

    @patch('src.prediction_market_fund.strategy_engine.strategy_engine.datetime')
    def test_run_strategy_insufficient_cash_to_buy(self, mock_datetime):
        """Test BUY trade is not attempted if cash balance is too low (checked by risk manager)."""
        mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0)

        mock_market_data_list = [
            MarketData(
                market_id="market-nocash",
                question="No Cash Question",
                current_price=100.0,
                volume_24h=10.0,
                total_liquidity=100.0
            )
        ]
        mock_market_price_data = MarketPriceData(market_id="market-nocash", asset="yes", price=100.0, timestamp=datetime.now())

        low_cash_portfolio = PortfolioState(cash_balance=5.0, positions={})

        self.mock_market_data_service.get_all_market_data.return_value = mock_market_data_list
        self.mock_market_data_service.get_market_price.return_value = mock_market_price_data
        self.mock_portfolio_manager.get_portfolio_state.return_value = low_cash_portfolio

        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.9, 0.8)) # Strong buy signal
        self.mock_risk_manager.assess_trade_risk.return_value = False # Simulate risk manager rejecting due to insufficient cash

        trades, memos = self.strategy_engine.run_strategy(Mock(), Mock())

        self.assertEqual(len(trades), 0)
        self.assertEqual(len(memos), 0)
        self.mock_risk_manager.assess_trade_risk.assert_called_once()

    @patch('src.prediction_market_fund.strategy_engine.strategy_engine.datetime')
    def test_run_strategy_insufficient_shares_to_sell(self, mock_datetime):
        """Test SELL trade is not attempted if no shares or insufficient shares are held (checked by risk manager)."""
        mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0)

        mock_market_data_list = [
            MarketData(
                market_id="market-noshares",
                question="No Shares Question",
                current_price=0.5,
                volume_24h=100.0,
                total_liquidity=1000.0
            )
        ]
        mock_market_price_data = MarketPriceData(market_id="market-noshares", asset="yes", price=0.5, timestamp=datetime.now())

        self.mock_market_data_service.get_all_market_data.return_value = mock_market_data_list
        self.mock_market_data_service.get_market_price.return_value = mock_market_price_data
        self.mock_portfolio_manager.get_portfolio_state.return_value = self.initial_portfolio_state_empty # No shares in any market

        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.1, 0.8)) # Strong sell signal
        self.mock_risk_manager.assess_trade_risk.return_value = False # Simulate risk manager rejecting due to no shares

        trades, memos = self.strategy_engine.run_strategy(Mock(), Mock())

        self.assertEqual(len(trades), 0)
        self.assertEqual(len(memos), 0)
        # Note: _manage_existing_positions won't propose a trade if there's no position,
        # so risk_manager won't be called for that path. But if _identify_new_opportunities
        # were to propose a sell on a market we don't have, risk_manager would be called.
        # For this specific test, we're testing the _manage_existing_positions path primarily.
        self.mock_risk_manager.assess_trade_risk.assert_not_called() # No existing positions to manage

    @patch('src.prediction_market_fund.strategy_engine.strategy_engine.datetime')
    def test_run_strategy_profit_taking(self, mock_datetime):
        """Test strategy engine identifies a profit-taking opportunity and generates a SELL trade/memo."""
        mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0)

        # Setup a market where we have a profitable position
        profitable_market_id = "market-profitable"
        profitable_position = Position(
            market_id=profitable_market_id, asset="yes", quantity=100.0, cost_basis=0.3, entry_price=0.3, current_price=0.3, unrealized_pnl=0.0
        )
        profit_portfolio_state = PortfolioState(
            cash_balance=1000.0,
            positions={profitable_market_id: profitable_position}
        )
        mock_market_price_data = MarketPriceData(market_id=profitable_market_id, asset="yes", price=0.6, timestamp=datetime.now())
        mock_market_data_list = [MarketData(market_id=profitable_market_id, question="q", current_price=0.6, volume_24h=100, total_liquidity=1000)]

        self.mock_market_data_service.get_all_market_data.return_value = mock_market_data_list
        self.mock_market_data_service.get_market_price.return_value = mock_market_price_data
        self.mock_portfolio_manager.get_portfolio_state.return_value = profit_portfolio_state
        self.mock_risk_manager.assess_trade_risk.return_value = True

        # Mock EV to be neutral to avoid conflicting with profit-taking logic
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.6, 0.8))

        trades, memos = self.strategy_engine.run_strategy(Mock(), Mock())

        self.assertEqual(len(trades), 1)
        self.assertEqual(len(memos), 1)

        trade = trades[0]
        memo = memos[0]

        self.assertEqual(trade.action, "SELL")
        self.assertAlmostEqual(trade.quantity, profitable_position.quantity) # Should sell entire position
        self.assertEqual(trade.market_id, profitable_market_id)

        self.assertEqual(memo.action, "SELL")
        self.assertIn("Profit-taking", memo.rationale)
        self.assertEqual(memo.market_id, profitable_market_id)
        self.mock_risk_manager.assess_trade_risk.assert_called_once()

    @patch('src.prediction_market_fund.strategy_engine.strategy_engine.datetime')
    def test_run_strategy_loss_cutting(self, mock_datetime):
        """Test strategy engine identifies a loss-cutting opportunity and generates a SELL trade/memo."""
        mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0)

        # Setup a market where we have a losing position
        losing_market_id = "market-losing"
        losing_position = Position(
            market_id=losing_market_id, asset="yes", quantity=100.0, cost_basis=0.8, entry_price=0.8, current_price=0.8, unrealized_pnl=0.0
        )
        loss_portfolio_state = PortfolioState(
            cash_balance=1000.0,
            positions={losing_market_id: losing_position}
        )
        mock_market_price_data = MarketPriceData(market_id=losing_market_id, asset="yes", price=0.4, timestamp=datetime.now())
        mock_market_data_list = [MarketData(market_id=losing_market_id, question="q", current_price=0.4, volume_24h=100, total_liquidity=1000)]

        self.mock_market_data_service.get_all_market_data.return_value = mock_market_data_list
        self.mock_market_data_service.get_market_price.return_value = mock_market_price_data
        self.mock_portfolio_manager.get_portfolio_state.return_value = loss_portfolio_state
        self.mock_risk_manager.assess_trade_risk.return_value = True

        # Mock EV to be neutral to avoid conflicting with loss-cutting logic
        self.strategy_engine._calculate_ev_and_conviction = Mock(return_value=(0.4, 0.8))

        trades, memos = self.strategy_engine.run_strategy(Mock(), Mock())

        self.assertEqual(len(trades), 1)
        self.assertEqual(len(memos), 1)

        trade = trades[0]
        memo = memos[0]

        self.assertEqual(trade.action, "SELL")
        self.assertAlmostEqual(trade.quantity, losing_position.quantity) # Should sell entire position
        self.assertEqual(trade.market_id, losing_market_id)

        self.assertEqual(memo.action, "SELL")
        self.assertIn("Stop-loss", memo.rationale)
        self.assertEqual(memo.market_id, losing_market_id)
        self.mock_risk_manager.assess_trade_risk.assert_called_once()

if __name__ == '__main__':
    unittest.main()

