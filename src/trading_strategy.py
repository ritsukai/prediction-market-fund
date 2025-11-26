# Trading strategy module for the prediction market fund
from src.ev_calculator import calculate_expected_value

def generate_trading_signal(market_data):
    """
    Generates a trading signal based on market data.
    """
    # This is a placeholder for a more sophisticated trading strategy.
    # For now, we'll just generate a BUY signal if the EV is positive.
    for market in market_data:
        # Assuming the market data has 'probability' and 'odds' fields
        if "probability" in market and "odds" in market:
            ev = calculate_expected_value(market["probability"], market["odds"])
            if ev > 0:
                return {"market_id": market["id"], "decision": "BUY", "size": 100}
    return None
