from abc import ABC, abstractmethod
from typing import Dict
from src.data_ingestion_service.market_data import MarketData

class DataSourceConnector(ABC):
    """
    Abstract base class for all data source connectors. Defines the interface
    for fetching market data from various sources.
    """

    @abstractmethod
    def fetch_market_data(self, market_id: str) -> MarketData:
        """
        Fetches market data for a specific market ID.
        """
        pass

    @abstractmethod
    def fetch_all_market_data(self) -> Dict[str, MarketData]:
        """
        Fetches market data for all available markets.
        """
        pass

class MockDataSourceConnector(DataSourceConnector):
    """
    A mock implementation of DataSourceConnector for testing and development.
    Provides dummy market data.
    """

    def __init__(self):
        self._mock_data = {
            "market-123": MarketData(
                market_id="market-123",
                question="Will BTC reach $100k by 2024?",
                current_price=0.65,
                volume_24h=100000.0,
                total_liquidity=500000.0,
            ),
            "market-456": MarketData(
                market_id="market-456",
                question="Will ETH surpass BTC in market cap by 2025?",
                current_price=0.30,
                volume_24h=50000.0,
                total_liquidity=200000.0,
            ),
        }

    def fetch_market_data(self, market_id: str) -> MarketData:
        return self._mock_data.get(market_id)

    def fetch_all_market_data(self) -> Dict[str, MarketData]:
        return self._mock_data
