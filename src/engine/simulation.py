from src.portfolio.portfolio_manager import PortfolioManager
from src.portfolio.risk_manager import RiskManager
from src.data.sources import DataSource
from src.reporting.memos import MemoGenerator
from src.core.types import Trade, Market
from typing import List

class Simulation:
    """
    The main simulation engine for the prediction market fund.
    """

    def __init__(self, data_sources: List[DataSource], initial_cash: float = 10000.0):
        self.portfolio_manager = PortfolioManager(initial_cash=initial_cash)
        self.risk_manager = RiskManager()
        self.memo_generator = MemoGenerator()
        self.data_sources = data_sources
        self.active_markets: List[Market] = []

    def run_step(self):
        """
        Executes one step of the simulation.
        """
        print("Running simulation step...")
        
        self._fetch_market_data()
        
        # In a real system, the agent would analyze the market data and
        # decide to make trades. For now, we'll just simulate a single trade.
        
        if self.active_markets:
            self._simulate_trade(self.active_markets[0])
            
        self._print_portfolio_status()


    def _fetch_market_data(self):
        """
        Fetches market data from all available data sources.
        """
        print("Fetching market data...")
        for source in self.data_sources:
            self.active_markets.extend(source.fetch_markets())
        
        # Remove duplicates
        self.active_markets = list({market.id: market for market in self.active_markets}.values())


    def _simulate_trade(self, market: Market):
        """
        Simulates the execution of a single trade.
        """
        
        # This is a placeholder for the agent's decision-making logic.
        # Here, we'll just create a mock trade.
        
        mock_trade = Trade(
            trade_id="trade-001",
            market_id=market.id,
            outcome='yes',
            action='buy',
            shares=10,
            price=market.probability,
            fees=0.1,
            slippage=0.01
        )

        # 1. Check with the risk manager
        if self.risk_manager.approve_trade(self.portfolio_manager.get_state(), mock_trade, market.category):
            print("Trade approved by Risk Manager.")
            
            # 2. Update the portfolio
            self.portfolio_manager.update_portfolio_from_trade(mock_trade, market)
            print("Portfolio updated.")

            # 3. Generate an investment memo
            self.memo_generator.generate_memo(
                trade=mock_trade,
                thesis="Based on recent news, the probability of this event is underestimated.",
                sources=["NewsDataSource"],
                expected_value=0.65,
                conviction=0.8
            )
            print("Investment memo generated.")
            
        else:
            print("Trade rejected by Risk Manager.")


    def _print_portfolio_status(self):
        """
        Prints the current status of the portfolio.
        """
        print("\n--- Portfolio Status ---")
        print(self.portfolio_manager.get_state().model_dump_json(indent=2))
        print("------------------------\n")
