from abc import ABC, abstractmethod
from typing import Any, Dict

class DataSourceConnector(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def fetch_data(self, market_id: str) -> Dict[str, Any]:
        pass

class MockDataSourceConnector(DataSourceConnector):
    def connect(self) -> None:
        print("MockDataSourceConnector connected.")

    def fetch_data(self, market_id: str) -> Dict[str, Any]:
        # Simulate fetching data for a given market_id
        if market_id == "market_123":
            return {"market_id": market_id, "price": 100.50, "volume": 1000.0, "timestamp": "2023-10-27T10:00:00Z"}
        elif market_id == "market_456":
            return {"market_id": market_id, "price": 250.75, "volume": 500.0, "timestamp": "2023-10-27T10:01:00Z"}
        else:
            return {"market_id": market_id, "price": 0.0, "volume": 0.0, "timestamp": "2023-10-27T10:02:00Z"}
