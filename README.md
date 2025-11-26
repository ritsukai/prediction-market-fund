# Autonomous Prediction Market Trading System

This project is an autonomous trading system that uses probabilistic models to trade on prediction markets like Polymarket. The system is designed to be a fully autonomous, self-improving hedge fund that demonstrates superior decision-making through transparent reasoning and rigorous benchmarking.

## Getting Started

To get started with the project, you will need to have Docker installed. Once you have Docker installed, you can build and run the application using the following commands:

```
docker build -t prediction-market-fund .
docker run prediction-market-fund
```

## Project Structure

The project is organized into the following directories:

- `src`: The core source code for the autonomous trading agent.
- `docs`: Documentation for the project, including architectural diagrams and operational procedures.
- `tests`: Automated tests for the project.
- `notebooks`: Jupyter notebooks for data analysis and experimentation.
- `research`: Research papers and other materials related to the project.

## System Architecture

The system is designed as a modular, service-oriented architecture to ensure separation of concerns, testability, and maintainability. The core components of the system are:

- **Data Ingestion Service**: Responsible for sourcing and normalizing data from various external sources.
- **Strategy Engine**: The core logic unit that analyzes data, formulates trading hypotheses, and calculates expected value (EV) for potential trades.
- **Execution Service**: Connects to the Polymarket API (simulated for paper trading) to place, manage, and exit trades.
- **Portfolio and Risk Service**: Manages the overall portfolio, tracks positions, calculates Net Asset Value (NAV), and enforces risk management rules.
- **Learning Service**: Conducts post-mortems on trades, compares outcomes to initial theses, and updates the strategy engine's models.
- **Dashboard Service**: A web-based UI that provides real-time visibility into the fund's operations.