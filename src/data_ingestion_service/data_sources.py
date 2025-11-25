from abc import ABC, abstractmethod
from typing import List

from src.data_ingestion_service.market_data import MarketData

class DataSourceConnector(ABC):
    """
    Abstract base class for all data source connectors.
    Ensures standardized interface for fetching market data and providing integrity scores.
    """

    @abstractmethod
    async def fetch_market_data(self, market_id: str) -> List[MarketData]:
        """
        Fetches market data for a given market ID from the specific data source.
        Returns a list of MarketData objects, each potentially representing different aspects or timestamps.
        """
        pass

    @property
    @abstractmethod
    def integrity_score(self) -> float:
        """
        Returns a score (0.0 to 1.0) indicating the general integrity/reliability of this data source.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the data source.
        """
        pass
