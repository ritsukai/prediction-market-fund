# Prediction Market Fund Architecture

## Core Services

### Data Ingestion Service
- **Purpose**: Aggregates market data from various sources.
- **Key Data Structures**: `MarketData`
- **Interfaces**:
    - `DataSourceConnector` (abstract base class)
    - `DataIngestionService` (provides aggregated market data)

### Portfolio Manager
- **Purpose**: Manages the fund's portfolio state, including current positions, net asset value (NAV), and trade history.
- **Key Data Structures**: `PortfolioState`, `Position`, `TradeOrder`
- **Interfaces**:
    - `get_portfolio_state()`: Returns the current `PortfolioState`.
    - `process_trade_order(trade_order: TradeOrder)`: Updates the portfolio based on an approved `TradeOrder`.
    - `get_positions()`: Returns current holdings.

### Risk Manager
- **Purpose**: Enforces risk management constraints and simulates real-world trade execution conditions.
- **Key Data Structures**: `PortfolioState`, `TradeOrder`, `RiskAssessment`
- **Interfaces**:
    - `assess_trade(trade_order: TradeOrder, portfolio_state: PortfolioState) -> RiskAssessment`: Evaluates a proposed `TradeOrder` against risk constraints.
    - `approve_trade(trade_order: TradeOrder, portfolio_state: PortfolioState) -> bool`: Determines if a trade can proceed based on risk parameters and simulated market conditions.
    - `monitor_portfolio(portfolio_state: PortfolioState)`: Continuously checks the portfolio against predefined risk limits and triggers alerts/actions if thresholds are breached.

### Strategy Engine
- **Purpose**: Generates `TradeOrder` proposals based on market data and predefined strategies.
- **Interfaces**:
    - `generate_trade_orders(market_data: MarketData, portfolio_state: PortfolioState) -> list[TradeOrder]`

### Execution Service
- **Purpose**: Executes approved `TradeOrder` objects in the simulated market.
- **Interfaces**:
    - `execute_trade(trade_order: TradeOrder)`: Places the trade and handles simulated market interactions.

## Data Structures

### MarketData
- **Description**: Standardized structure for market data.
- **Attributes**: `asset_id`, `timestamp`, `price`, `volume`, `order_book_depth` (for simulation)

### PortfolioState
- **Description**: Represents the current state of the investment portfolio.
- **Attributes**: `nav`, `cash`, `positions` (list of `Position` objects), `trade_history`

### Position
- **Description**: Represents a single holding in the portfolio.
- **Attributes**: `asset_id`, `quantity`, `average_entry_price`, `current_price`

### TradeOrder
- **Description**: A proposed trade to be executed.
- **Attributes**: `asset_id`, `order_type` (buy/sell), `quantity`, `price` (desired), `timestamp`

### RiskAssessment
- **Description**: The outcome of a risk evaluation for a `TradeOrder`.
- **Attributes**: `approved` (boolean), `rejection_reason` (if not approved), `simulated_execution_price`, `simulated_fees`
