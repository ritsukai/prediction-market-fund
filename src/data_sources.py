from abc import ABC, abstractmethod
from typing import Dict, List
from src.models import MarketData
import datetime

class DataSourceConnector(ABC):
    @abstractmethod
    def get_market_data(self, market_id: str) -> MarketData:
        pass

class MockDataSourceConnector(DataSourceConnector):
    def get_market_data(self, market_id: str) -> MarketData:
        # Simulate fetching market data with some basic order book depth
        # For simulation, we'll use a simplified order book
        if market_id == "market_A":
            return MarketData(
                market_id="market_A",
                current_price=0.60,
                timestamp=datetime.datetime.now(),
                order_book={
                    "bids": [[0.59, 100], [0.58, 200]],
                    "asks": [[0.61, 150], [0.62, 100]]
                }
            )
        elif market_id == "market_B":
            return MarketData(
                market_id="market_B",
                current_price=0.30,
                timestamp=datetime.datetime.now(),
                order_book={
                    "bids": [[0.29, 50], [0.28, 100]],
                    "asks": [[0.31, 75], [0.32, 50]]
                }
            )
        else:
            # Simulate a market with low liquidity for testing SIM-001
            return MarketData(
                market_id=market_id,
                current_price=0.50,
                timestamp=datetime.datetime.now(),
                order_book={
                    "bids": [[0.49, 10], [0.48, 20]], # Total $14.70 + $28.80 = $43.50 bid depth (very low)
                    "asks": [[0.51, 15], [0.52, 10]]  # Total $7.65 + $5.20 = $12.85 ask depth (very low)
                }
            )
