from abc import ABC, abstractmethod
from typing import List
from src.core.types import Market

class DataSource(ABC):
    """
    Abstract base class for all data sources.
    """

    @abstractmethod
    def fetch_markets(self) -> List[Market]:
        """
        Fetches a list of active prediction markets.
        
        :return: A list of Market objects.
        """
        pass

class MockDataSource(DataSource):
    """
    A mock data source for testing purposes.
    """

    def fetch_markets(self) -> List[Market]:
        # In a real implementation, this would make an API call to a provider
        # like Polymarket's API. For now, we'll return some mock data.
        
        market1 = Market(
            id="market-001",
            question="Will AI achieve AGI by 2030?",
            url="https://polymarket.com/market/market-001",
            probability=0.35,
            category="Technology",
            resolution_criteria="AGI is defined as..."
        )
        
        market2 = Market(
            id="market-002",
            question="Will the next US President be from the Democratic party?",
            url="https://polymarket.com/market/market-002",
            probability=0.55,
            category="US Politics",
            resolution_criteria="..."
        )
        
        return [market1, market2]

class NewsDataSource(DataSource):
    """
    A mock data source that "fetches" news articles.
    """

    def fetch_markets(self) -> List[Market]:
        # This is a placeholder. A real implementation would use a news API
        # to fetch articles related to active markets.
        return []
        
    def get_news_for_market(self, market_id: str) -> List[str]:
        """
        Fetches news articles related to a specific market.
        """
        # In a real system, this would query a news API.
        print(f"Fetching news for market: {market_id}")
        return [
            "'AI Researchers Announce Major Breakthrough in Neural Network Efficiency'",
            "'Geopolitical Tensions Rise Ahead of US Election'"
        ]
