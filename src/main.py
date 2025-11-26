from src.data_ingestion import get_polymarket_data
from src.trading_strategy import generate_trading_signal
from src.paper_trader import execute_trade
from src.portfolio_manager import PortfolioManager
from src.risk_management import check_risk_limits
from src.investment_memo import generate_investment_memo
from src.config import INITIAL_CAPITAL

def main():
    """
    Main function to run the trading simulation.
    """
    # Initialize the portfolio manager
    portfolio = PortfolioManager(INITIAL_CAPITAL)

    # Fetch market data
    market_data = get_polymarket_data()

    if market_data:
        # Generate a trading signal
        signal = generate_trading_signal(market_data)

        if signal:
            # Check risk limits
            passed, message = check_risk_limits(portfolio, signal)

            if passed:
                # Execute the trade
                trade = execute_trade(
                    market_id=signal["market_id"],
                    decision=signal["decision"],
                    size=signal["size"],
                    price=0.5,  # Placeholder price
                )

                # Update the portfolio
                portfolio.update_portfolio(trade)

                # Generate an investment memo
                memo = generate_investment_memo(
                    market_id=trade["market_id"],
                    decision=trade["decision"],
                    ev=0.2,  # Placeholder EV
                    conviction="High",  # Placeholder conviction
                    sources=["Source A", "Source B"],  # Placeholder sources
                )

                # Print the memo
                print(memo)
            else:
                print(f"Trade rejected: {message}")

if __name__ == "__main__":
    main()
