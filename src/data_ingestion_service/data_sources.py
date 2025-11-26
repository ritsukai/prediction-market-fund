from abc import ABC, abstractmethod

class DataSource(ABC):
    """
    An abstract base class for data sources.
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of the data source.
        """
        pass

    @abstractmethod
    def get_data(self) -> dict:
        """
        Fetches data from the data source.
        """
        pass
