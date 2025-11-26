from .data_sources import DataSource

class DataIngestionService:
    """
    A service for ingesting data from various sources.
    """

    def __init__(self, data_sources: list[DataSource]):
        """
        Initializes the DataIngestionService with a list of data sources.

        Args:
            data_sources: A list of DataSource objects.
        """
        self.data_sources = data_sources

    def fetch_data(self):
        """
        Fetches data from all registered data sources.

        Returns:
            A dictionary containing the data fetched from each data source.
        """
        data = {}
        for source in self.data_sources:
            data[source.get_name()] = source.get_data()
        return data
