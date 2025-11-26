# Tests for the EV calculator module
import unittest
from src.ev_calculator import calculate_expected_value

class TestEvCalculator(unittest.TestCase):
    def test_calculate_expected_value(self):
        # Test case 1: Positive EV
        self.assertAlmostEqual(calculate_expected_value(0.6, 2.0), 0.2)

        # Test case 2: Negative EV
        self.assertAlmostEqual(calculate_expected_value(0.4, 2.0), -0.2)

        # Test case 3: Zero EV
        self.assertAlmostEqual(calculate_expected_value(0.5, 2.0), 0.0)

if __name__ == "__main__":
    unittest.main()
