# Tests for the investment memo module
import unittest
from src.investment_memo import generate_investment_memo

class TestInvestmentMemo(unittest.TestCase):
    def test_generate_investment_memo(self):
        memo = generate_investment_memo(
            market_id="1",
            decision="BUY",
            ev=0.2,
            conviction="High",
            sources=["Source A", "Source B"],
        )
        self.assertIn("<h1>Investment Memo</h1>", memo)
        self.assertIn("<strong>Market ID:</strong> 1", memo)
        self.assertIn("<strong>Decision:</strong> BUY", memo)
        self.assertIn("<strong>Expected Value:</strong> 0.2", memo)
        self.assertIn("<strong>Conviction:</strong> High", memo)
        self.assertIn("<li>Source A</li>", memo)
        self.assertIn("<li>Source B</li>", memo)

if __name__ == "__main__":
    unittest.main()
