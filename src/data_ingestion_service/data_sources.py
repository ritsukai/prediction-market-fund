
from abc import ABC, abstractmethod

class DataSourceConnector(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def fetch_data(self, market_id: str):
        pass
