# Prediction Market Fund Architecture

## Introduction
This document outlines the high-level architecture for the Prediction Market Fund. It details the main components, their responsibilities, and key interfaces.

## Components

### 1. Data Ingestion Service
Responsible for fetching and processing market data from various sources.

### 2. Strategy Engine
Responsible for generating trade signals based on market data and portfolio state.

### 3. Portfolio and Risk Service
Responsible for managing the fund's portfolio and assessing trading risks.

### Data Ingestion Service Interfaces
The `IDataIngestionService` provides methods for fetching market data.

**`IDataIngestionService`**
- `fetch_market_data(market_id: str) -> MarketData`: Fetches current market data for a given market ID.

**`MarketData` Dataclass**
- `market_id: str`: Unique identifier for the market.
- `timestamp: datetime`: Timestamp of the data.
- `price: float`: Current price of the market.
- `volume: float`: Trading volume of the market.
- `additional_info: Dict[str, Any]`: Any additional market-specific information.

### Strategy Engine Interfaces
The `IStrategyEngine` defines methods for generating and managing trade orders.

**`IStrategyEngine`**
- `generate_trade_orders(market_data: MarketData, portfolio_state: PortfolioState) -> (List[TradeOrder], List[InvestmentMemo])`: Generates a list of trade orders and corresponding investment memos based on current market data and portfolio state.
- `actively_manage_positions(market_data: MarketData, portfolio_state: PortfolioState) -> (List[TradeOrder], List[InvestmentMemo])`: Actively manages existing positions, generating trade orders and investment memos for adjustments.

**`InvestmentMemo` Dataclass**
- `trade_order: TradeOrder`: The trade order associated with the memo.
- `justification: str`: Detailed justification for the trade.
- `data_sources: List[str]`: List of data sources used for the decision.
- `calculated_ev: float`: Calculated expected value of the trade.
- `conviction_level: float`: Level of conviction in the trade decision.
- `polymarket_market_id: str`: Corresponding Polymarket market ID.

### Portfolio and Risk Service Interfaces
The `IPortfolioManager` and `IRiskManager` provide methods for managing the portfolio and assessing trade risks.

**`IPortfolioManager`**
- `get_portfolio_state() -> PortfolioState`: Retrieves the current state of the portfolio.
- `execute_trade(trade_order: TradeOrder) -> bool`: Executes a given trade order.

**`IRiskManager`**
- `assess_trade_risk(trade_order: TradeOrder) -> bool`: Assesses the risk of a potential trade order.

**`Position` Dataclass**
- `market_id: str`: Unique identifier for the market.
- `asset_id: str`: Unique identifier for the asset.
- `amount: float`: Quantity of the asset held.
- `entry_price: float`: Price at which the position was entered.
- `current_price: float`: Current market price of the asset.
- `unrealized_pnl: float`: Unrealized Profit and Loss.

**`TradeOrder` Dataclass**
- `order_id: str`: Unique identifier for the trade order.
- `market_id: str`: Identifier for the market the order belongs to.
- `asset_id: str`: Identifier for the asset being traded.
- `quantity: float`: Amount of asset to trade.
- `order_type: str`: Type of order (e.g., 'buy', 'sell').
- `price: float (optional)`: Limit price for the order.
- `timestamp: Any (optional)`: Time of order creation.
- `status: str`: Current status of the order (e.g., 'pending', 'executed', 'cancelled').
- `additional_info: Dict[str, Any] (optional)`: Any additional trade-specific information.

**`PortfolioState` Dataclass**
- `positions: List[Position]`: List of current positions.
- `cash_balance: float`: Current cash available.
- `total_value: float`: Total value of the portfolio.
- `leverage: float`: Current leverage ratio.
- `performance_metrics: Dict[str, Any]`: Various performance metrics of the portfolio.
