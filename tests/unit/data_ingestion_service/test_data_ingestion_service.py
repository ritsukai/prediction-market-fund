import unittest
from datetime import datetime
from src.data_ingestion_service.data_ingestion_service import DataIngestionService
from src.data_ingestion_service.data_sources import MockDataSourceConnector
from src.data_ingestion_service.market_data import MarketData


class TestDataIngestionService(unittest.TestCase):
    def setUp(self):
        self.mock_connector = MockDataSourceConnector()
        self.data_ingestion_service = DataIngestionService(self.mock_connector)

    def test_fetch_market_data_existing_market(self):
        market_id = "market_123"
        market_data = self.data_ingestion_service.fetch_market_data(market_id)

        self.assertIsInstance(market_data, MarketData)
        self.assertEqual(market_data.market_id, market_id)
        self.assertIsInstance(market_data.timestamp, datetime)
        self.assertAlmostEqual(market_data.price, 100.50)
        self.assertAlmostEqual(market_data.volume, 1000.0)

    def test_fetch_market_data_non_existing_market(self):
        market_id = "market_999"
        market_data = self.data_ingestion_service.fetch_market_data(market_id)

        self.assertIsInstance(market_data, MarketData)
        self.assertEqual(market_data.market_id, market_id)
        self.assertIsInstance(market_data.timestamp, datetime)
        self.assertAlmostEqual(market_data.price, 0.0)
        self.assertAlmostEqual(market_data.volume, 0.0)

    def test_get_historical_data_not_implemented(self):
        market_id = "market_123"
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        historical_data = self.data_ingestion_service.get_historical_data(market_id, start_date, end_date)

        self.assertEqual(historical_data, [])

    def test_mock_data_source_connector_connect(self):
        # The connect method just prints, so we check if it doesn't raise an error
        try:
            self.mock_connector.connect()
        except Exception as e:
            self.fail(f"connect() raised an unexpected exception: {e}")

    def test_mock_data_source_connector_fetch_data(self):
        market_id = "market_456"
        data = self.mock_connector.fetch_data(market_id)
        self.assertIn("market_id", data)
        self.assertIn("price", data)
        self.assertIn("volume", data)
        self.assertIn("timestamp", data)
        self.assertEqual(data["market_id"], market_id)


if __name__ == '__main__':
    unittest.main()
