# Paper trader module for the prediction market fund
from src.config import SLIPPAGE, FEES

def execute_trade(market_id, decision, size, price):
    """
    Simulates the execution of a trade, accounting for slippage and fees.
    """
    # Simulate slippage
    execution_price = price * (1 + SLIPPAGE) if decision == "BUY" else price * (1 - SLIPPAGE)

    # Calculate fees
    trade_value = size * execution_price
    fee_amount = trade_value * FEES

    # Calculate net trade value
    net_trade_value = trade_value - fee_amount

    return {
        "market_id": market_id,
        "decision": decision,
        "size": size,
        "execution_price": execution_price,
        "fee_amount": fee_amount,
        "net_trade_value": net_trade_value,
    }
