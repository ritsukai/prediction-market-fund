from datetime import datetime
from typing import List
from src.data_ingestion_service.market_data import MarketData
from src.data_ingestion_service.data_sources import DataSourceConnector, MockDataSourceConnector
from src.prediction_market_fund.interfaces.market_data_interface import IMarketDataService


class DataIngestionService(IMarketDataService):
    def __init__(self, data_source_connector: DataSourceConnector):
        self.data_source_connector = data_source_connector
        self.data_source_connector.connect()

    def fetch_market_data(self, market_id: str) -> MarketData:
        raw_data = self.data_source_connector.fetch_data(market_id)
        return MarketData(
            market_id=raw_data["market_id"],
            timestamp=datetime.fromisoformat(raw_data["timestamp"].replace("Z", "+00:00")),
            price=raw_data["price"],
            volume=raw_data["volume"]
        )

    def get_historical_data(self, market_id: str, start_date: datetime, end_date: datetime) -> List[MarketData]:
        # For now, we'll return an empty list as historical data fetching is not yet implemented
        return []
