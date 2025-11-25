import asyncio
from typing import Dict, List

from src.data_ingestion_service.market_data import MarketData
from src.data_ingestion_service.data_sources import DataSourceConnector

class DataIngestionService:
    """
    Gathers, cleans, and standardizes data from multiple independent sources.
    Adheres to ARCH-001-REFERENCE and implements DATA-001 principles.
    """

    def __init__(self, data_source_connectors: List[DataSourceConnector]):
        self.data_source_connectors: Dict[str, DataSourceConnector] = {
            connector.name: connector for connector in data_source_connectors
        }

    async def get_market_data(self, market_id: str) -> List[MarketData]:
        """
        Fetches market data from all configured sources for a given market_id.
        Applies multi-source verification as per DATA-001.
        """
        all_market_data: List[MarketData] = []
        tasks = [
            connector.fetch_market_data(market_id)
            for connector in self.data_source_connectors.values()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                # Log the error, but continue processing other sources
                print(f"Error fetching data: {res}") # Placeholder for actual logging
            else:
                all_market_data.extend(res)

        # DATA-001: Implement multi-source verification logic here.
        # For now, this is a placeholder. A full implementation would involve:
        # 1. Grouping market data by timestamp and market_id.
        # 2. Comparing probabilities/information from different sources.
        # 3. Applying a consensus mechanism or flagging discrepancies.
        # 4. Requiring a minimum number of high-integrity sources for 'high-conviction' data.
        print(f"DEBUG: Collected {len(all_market_data)} data points for {market_id}")
        return all_market_data
