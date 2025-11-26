# Data ingestion module for the prediction market fund
import requests
from src.config import POLYMARKET_API_URL

def get_polymarket_data():
    """
    Fetches data from the Polymarket API.
    """
    try:
        response = requests.get(POLYMARKET_API_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Polymarket API: {e}")
        return None
