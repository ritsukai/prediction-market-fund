from typing import Dict
from src.data_ingestion_service.market_data import MarketData
from src.data_ingestion_service.data_sources import DataSourceConnector, MockDataSourceConnector
from src.prediction_market_fund.interfaces.market_data_interface import IMarketDataService

class DataIngestionService(IMarketDataService):
    """
    Implementation of the IMarketDataService using a DataSourceConnector.
    """
    def __init__(self, connector: DataSourceConnector):
        self._connector = connector

    def get_market_data(self, market_id: str) -> MarketData:
        """
        Retrieves current market data for a specific market ID using the connector.
        """
        return self._connector.fetch_market_data(market_id)

    def get_all_market_data(self) -> Dict[str, MarketData]:
        """
        Retrieves current market data for all tracked markets using the connector.
        """
        return self._connector.fetch_all_market_data()
