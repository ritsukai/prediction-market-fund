# Prediction Market Fund Architecture

This document outlines the high-level architecture of the Prediction Market Fund system, detailing its core components, their responsibilities, and the interfaces through which they interact.

## 1. System Overview

The Prediction Market Fund is designed to autonomously participate in prediction markets. It comprises several key services that handle data ingestion, strategy execution, portfolio management, and risk assessment.

## 2. Core Services

### 2.1. Data Ingestion Service
- **Responsibility:** Connects to external data sources (e.g., Polymarket APIs, news feeds, on-chain data) to fetch real-time and historical market data. It normalizes data into a consistent format (`MarketData`).
- **Interface:** `IMarketDataService` (defined in `src/prediction_market_fund/interfaces/market_data_interface.py`)
- **Key Outputs:** `MarketData` objects.

### 2.2. Strategy Engine
- **Responsibility:** Consumes `MarketData` and `PortfolioState` to identify trading opportunities. It calculates expected values (EVs), determines conviction levels, generates `InvestmentMemo`s to justify trades, and proposes `TradeOrder`s.
- **Interface:** `IStrategyEngine` (defined in `src/prediction_market_fund/interfaces/strategy_engine_interface.py`)
- **Key Inputs:** `MarketData`, `PortfolioState`.
- **Key Outputs:** `InvestmentMemo`, `TradeOrder`.

### 2.3. Portfolio and Risk Service
This service is composed of two main components:

#### 2.3.1. Portfolio Manager
- **Responsibility:** Manages the fund's positions, executes trades, and maintains the current `PortfolioState`.
- **Interface:** `IPortfolioManager` (defined in `src/prediction_market_fund/interfaces/portfolio_risk_interface.py`)
- **Key Inputs:** `TradeOrder`.
- **Key Outputs:** Updated `PortfolioState`, `Position` objects.

#### 2.3.2. Risk Manager
- **Responsibility:** Evaluates proposed `TradeOrder`s against predefined risk parameters. Approves or rejects trades to prevent excessive exposure or loss.
- **Interface:** `IRiskManager` (defined in `src/prediction_market_fund/interfaces/portfolio_risk_interface.py`)
- **Key Inputs:** `TradeOrder`, `PortfolioState`.
- **Key Outputs:** Boolean (trade approval/rejection).

## 3. Data Models and Interfaces

All core data structures and service contracts are defined using Python dataclasses and ABCs (Abstract Base Classes) for clarity and enforceability.

### Interfaces
- `src/prediction_market_fund/interfaces/market_data_interface.py`: Defines `IMarketDataService`.
- `src/prediction_market_fund/interfaces/portfolio_risk_interface.py`: Defines `IPortfolioManager`, `IRiskManager`.
- `src/prediction_market_fund/interfaces/strategy_engine_interface.py`: Defines `IStrategyEngine`.

### Core Data Models
- `MarketData`: Represents market information.
- `Position`: Represents an open position in a market.
- `PortfolioState`: Aggregates all current positions and fund balance.
- `TradeOrder`: Represents a proposed buy or sell action.
- `InvestmentMemo`: Justification for a trade decision.
