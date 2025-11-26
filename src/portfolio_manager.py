# Portfolio manager module for the prediction market fund

class PortfolioManager:
    def __init__(self, initial_capital):
        self.cash = initial_capital
        self.positions = {}

    def update_portfolio(self, trade):
        """
        Updates the portfolio with a new trade.
        """
        if trade["decision"] == "BUY":
            self.cash -= trade["net_trade_value"]
            self.positions[trade["market_id"]] = self.positions.get(trade["market_id"], 0) + trade["size"]
        else:  # SELL
            self.cash += trade["net_trade_value"]
            self.positions[trade["market_id"]] = self.positions.get(trade["market_id"], 0) - trade["size"]

    def get_nav(self):
        """
        Calculates the Net Asset Value (NAV) of the portfolio.
        """
        # This is a simplified NAV calculation. In a real scenario, we would need to
        # get the current market prices of the positions.
        return self.cash + sum(self.positions.values())
