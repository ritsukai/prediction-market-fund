import asyncio
import unittest
from datetime import datetime
from typing import List

from src.data_ingestion_service.data_ingestion_service import DataIngestionService
from src.data_ingestion_service.data_sources import DataSourceConnector
from src.data_ingestion_service.market_data import MarketData

class MockDataSourceConnector(DataSourceConnector):
    def __init__(self, name: str, integrity_score: float, data: List[MarketData]):
        self._name = name
        self._integrity_score = integrity_score
        self._data = data

    @property
    def name(self) -> str:
        return self._name

    @property
    def integrity_score(self) -> float:
        return self._integrity_score

    async def fetch_market_data(self, market_id: str) -> List[MarketData]:
        # Simulate async operation
        await asyncio.sleep(0.01)
        return [d for d in self._data if d.market_id == market_id]

class TestDataIngestionService(unittest.IsolatedAsyncioTestCase):

    async def test_get_market_data_aggregation(self):
        # Mock data for two sources
        data_source1_data = [
            MarketData("market_A", datetime.now(), 0.7, "Source1", 0.9),
            MarketData("market_B", datetime.now(), 0.5, "Source1", 0.9),
        ]
        data_source2_data = [
            MarketData("market_A", datetime.now(), 0.75, "Source2", 0.8),
            MarketData("market_C", datetime.now(), 0.6, "Source2", 0.8),
        ]

        mock_source1 = MockDataSourceConnector("Source1", 0.9, data_source1_data)
        mock_source2 = MockDataSourceConnector("Source2", 0.8, data_source2_data)

        service = DataIngestionService([mock_source1, mock_source2])

        # Test aggregation for market_A
        market_a_data = await service.get_market_data("market_A")
        self.assertEqual(len(market_a_data), 2)
        self.assertIn(data_source1_data[0], market_a_data)
        self.assertIn(data_source2_data[0], market_a_data)

        # Test aggregation for market_B
        market_b_data = await service.get_market_data("market_B")
        self.assertEqual(len(market_b_data), 1)
        self.assertIn(data_source1_data[1], market_b_data)

        # Test aggregation for market_C
        market_c_data = await service.get_market_data("market_C")
        self.assertEqual(len(market_c_data), 1)
        self.assertIn(data_source2_data[1], market_c_data)

        # Test for a market with no data
        no_data_market = await service.get_market_data("market_D")
        self.assertEqual(len(no_data_market), 0)
