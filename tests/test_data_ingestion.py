# Tests for the data ingestion module
import unittest
from unittest.mock import patch
import requests
from src.data_ingestion import get_polymarket_data

class TestDataIngestion(unittest.TestCase):
    @patch("src.data_ingestion.requests.get")
    def test_get_polymarket_data_success(self, mock_get):
        # Mock the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"id": "1", "name": "Test Market"}]

        # Call the function
        data = get_polymarket_data()

        # Assert the result
        self.assertEqual(data, [{"id": "1", "name": "Test Market"}])

    @patch("src.data_ingestion.requests.get")
    def test_get_polymarket_data_failure(self, mock_get):
        # Mock a failed API response
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.RequestException

        # Call the function
        data = get_polymarket_data()

        # Assert the result
        self.assertIsNone(data)

if __name__ == "__main__":
    unittest.main()
