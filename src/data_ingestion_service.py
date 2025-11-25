from src.market_data_interface import IMarketDataService
from src.data_sources import DataSourceConnector
from src.models import MarketData

class DataIngestionService(IMarketDataService):
    def __init__(self, connector: DataSourceConnector):
        self.connector = connector

    def get_market_data(self, market_id: str) -> MarketData:
        return self.connector.get_market_data(market_id)
