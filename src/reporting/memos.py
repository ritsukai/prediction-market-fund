from src.core.types import InvestmentMemo, Trade
from typing import List

class MemoGenerator:
    """Generates and stores Investment Memos."""

    def __init__(self, storage_path: str = "memos"):
        self.storage_path = storage_path
        # In a real implementation, you'd initialize a database or file storage system.
        self._memos: List[InvestmentMemo] = []

    def generate_memo(self, trade: Trade, thesis: str, sources: List[str], expected_value: float, conviction: float) -> InvestmentMemo:
        """
        Generates a new investment memo for a given trade.
        """
        memo = InvestmentMemo(
            memo_id=f"memo_{trade.trade_id}",
            trade_id=trade.trade_id,
            market_id=trade.market_id,
            thesis=thesis,
            sources=sources,
            expected_value=expected_value,
            conviction=conviction,
        )
        self.save_memo(memo)
        return memo

    def save_memo(self, memo: InvestmentMemo):
        """
        Saves the investment memo to storage.
        
        For now, we'll just keep it in memory. In a real system, this would
        write to a file or a database.
        """
        print(f"Saving memo: {memo.memo_id}")
        self._memos.append(memo)

    def get_memo_for_trade(self, trade_id: str) -> InvestmentMemo:
        """
        Retrieves the investment memo for a specific trade.
        """
        for memo in self._memos:
            if memo.trade_id == trade_id:
                return memo
        raise ValueError(f"No memo found for trade_id: {trade_id}")

