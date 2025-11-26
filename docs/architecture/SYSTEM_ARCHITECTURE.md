# System Architecture

This document outlines the high-level architecture of the Prediction Market Fund autonomous agent. The system is designed as a set of modular, independent services that communicate with each other through well-defined interfaces. This approach adheres to assertion `ARCH-001` and promotes maintainability, testability, and parallel development.

## Core Components

The system is composed of the following core services:

1.  **Data Ingestion Service**: Responsible for sourcing and normalizing data from various external sources, including the Polymarket API, news APIs, and other relevant on-chain or off-chain data providers. (Corresponds to `DATA-001`)
2.  **Strategy Engine**: The core decision-making unit. It consumes data from the Data Ingestion Service, generates trading ideas, calculates Expected Value (EV), and produces "Investment Memos". (Corresponds to `STRAT-001`, `EXP-001`)
3.  **Portfolio and Risk Service**: Maintains the state of the fund's portfolio, enforces risk management rules (e.g., position sizing, sector exposure), and calculates performance metrics. (Corresponds to `RISK-001`, `CAPITAL-PRESERVATION`, `BENCH-001`)
4.  **Execution Service**: Simulates the execution of trades against a realistic model of the Polymarket order books, accounting for liquidity, slippage, and fees. (Corresponds to `SIM-001`)
5.  **Learning & Post-Mortem Service**: Analyzes the outcomes of closed positions to generate insights and update the Strategy Engine's models. (Corresponds to `LEARN-001`)
6.  **Dashboard Service**: A web-based interface that provides real-time visualization of the fund's activities, portfolio, and the reasoning behind its trades. (Corresponds to `VIS-001`)

## Data Flow

The typical data flow for a single trading decision is as follows:

1.  The **Data Ingestion Service** continuously monitors markets and news sources, publishing cleaned, structured data.
2.  The **Strategy Engine** consumes this data, identifies a potential opportunity, and calculates the EV.
3.  If the EV is positive, the **Strategy Engine** generates an Investment Memo and proposes a trade (e.g., "BUY 100 shares of 'Market X' at $0.50").
4.  The proposed trade is sent to the **Portfolio and Risk Service**.
5.  The **Portfolio and Risk Service** checks the proposed trade against all risk constraints (e.g., "Is the 10% NAV limit for a single position exceeded?").
6.  If the trade is approved, it is forwarded to the **Execution Service**.
7.  The **Execution Service** simulates the trade against the current order book and returns the actual execution price and cost.
8.  The result of the execution is sent back to the **Portfolio and Risk Service** to update the official portfolio state.
9.  All events (memos, trades, risk checks) are streamed to the **Dashboard Service** for visualization.
10. When a position is closed, the **Learning & Post-Mortem Service** is triggered to perform an analysis.

This modular design ensures that each part of the system has a single responsibility, making the overall system more robust and easier to develop and maintain.
