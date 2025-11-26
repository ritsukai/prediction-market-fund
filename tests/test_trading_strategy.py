# Tests for the trading strategy module
import unittest
from src.trading_strategy import generate_trading_signal

class TestTradingStrategy(unittest.TestCase):
    def test_generate_trading_signal_positive_ev(self):
        market_data = [{"id": "1", "probability": 0.6, "odds": 2.0}]
        signal = generate_trading_signal(market_data)
        self.assertEqual(signal, {"market_id": "1", "decision": "BUY", "size": 100})

    def test_generate_trading_signal_negative_ev(self):
        market_data = [{"id": "1", "probability": 0.4, "odds": 2.0}]
        signal = generate_trading_signal(market_data)
        self.assertIsNone(signal)

if __name__ == "__main__":
    unittest.main()
