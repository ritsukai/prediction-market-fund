import unittest
from src.portfolio.portfolio_manager import PortfolioManager
from src.core.types import Trade, Market

class TestPortfolioManager(unittest.TestCase):

    def setUp(self):
        self.portfolio_manager = PortfolioManager(initial_cash=10000.0)
        self.market = Market(
            id="market-001",
            question="Will AI achieve AGI by 2030?",
            url="https://polymarket.com/market/market-001",
            probability=0.35,
            category="Technology",
            resolution_criteria="AGI is defined as..."
        )

    def test_execute_buy_trade(self):
        trade = Trade(
            trade_id="trade-001",
            market_id="market-001",
            outcome='yes',
            action='buy',
            shares=10,
            price=0.35,
            fees=0,
            slippage=0
        )
        self.portfolio_manager.update_portfolio_from_trade(trade, self.market)
        
        portfolio_state = self.portfolio_manager.get_state()
        self.assertEqual(portfolio_state.cash, 9996.5)
        self.assertIn("market-001", portfolio_state.positions)
        self.assertEqual(portfolio_state.positions["market-001"].shares, 10)
        self.assertEqual(portfolio_state.pnl, 0)
        self.assertEqual(portfolio_state.nav, 10000)


    def test_execute_sell_trade(self):
        # First, buy some shares
        buy_trade = Trade(
            trade_id="trade-001",
            market_id="market-001",
            outcome='yes',
            action='buy',
            shares=20,
            price=0.5,
            fees=0,
            slippage=0
        )
        self.portfolio_manager.update_portfolio_from_trade(buy_trade, self.market)

        # Now, sell some of them
        sell_trade = Trade(
            trade_id="trade-002",
            market_id="market-001",
            outcome='yes',
            action='sell',
            shares=10,
            price=0.6,
            fees=0,
            slippage=0
        )
        self.portfolio_manager.update_portfolio_from_trade(sell_trade, self.market)
        
        portfolio_state = self.portfolio_manager.get_state()
        self.assertEqual(portfolio_state.cash, 9996.0) # 10000 - (20*0.5) + (10*0.6) = 9996
        self.assertEqual(portfolio_state.positions["market-001"].shares, 10)
        self.assertEqual(portfolio_state.pnl, 1)


if __name__ == '__main__':
    unittest.main()