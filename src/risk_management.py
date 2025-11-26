# Risk management module for the prediction market fund
from src.config import MAX_POSITION_SIZE, MAX_SECTOR_EXPOSURE

def check_risk_limits(portfolio, trade):
    """
    Checks if a trade violates any risk limits.
    """
    # Check max position size
    nav = portfolio.get_nav()
    if (trade["size"] * trade["execution_price"]) / nav > MAX_POSITION_SIZE:
        return False, "Max position size exceeded"

    # In a real scenario, we would also check sector exposure.
    # This would require market data that includes sector information.

    return True, "Risk limits passed"
