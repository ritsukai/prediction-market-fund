# Dashboard module for the prediction market fund
from flask import Flask, render_template
from src.portfolio_manager import PortfolioManager

app = Flask(__name__)

# Dummy portfolio for demonstration purposes
portfolio = PortfolioManager(initial_capital=100000)

@app.route("/")
def dashboard():
    """
    Renders the dashboard.
    """
    return render_template("dashboard.html", nav=portfolio.get_nav())

if __name__ == "__main__":
    app.run(debug=True)
