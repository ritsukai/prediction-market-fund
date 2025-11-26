# System Context

## Overview

This document outlines the architecture of the autonomous prediction market trading system. The system is designed as a modular, service-oriented architecture to ensure separation of concerns, testability, and maintainability.

## Core Components

The system is composed of the following services:

- **Data Ingestion Service**: Responsible for sourcing and normalizing data from various external sources like Polymarket, news APIs, and social media.
- **Strategy Engine**: The core logic unit. It analyzes data, formulates trading hypotheses, and calculates expected value (EV) for potential trades.
- **Execution Service**: Connects to the Polymarket API (simulated for paper trading) to place, manage, and exit trades. It ensures all trades adhere to simulation parameters (e.g., slippage, fees).
- **Portfolio and Risk Service**: Manages the overall portfolio, tracks positions, calculates Net Asset Value (NAV), and enforces risk management rules (e.g., position sizing, sector exposure).
- **Learning Service**: Conducts post-mortems on trades, compares outcomes to initial theses, and updates the strategy engine's models.
- **Dashboard Service**: A web-based UI that provides real-time visibility into the fund's operations, including current positions, historical performance, and the reasoning behind trades (Investment Memos).

## Data Flow

1.  **Ingestion**: The `Data Ingestion Service` continuously monitors and collects data, placing it into a standardized format.
2.  **Analysis**: The `Strategy Engine` consumes the normalized data, identifies potential trading opportunities, and generates a detailed 'Investment Memo' for each.
3.  **Risk Assessment**: The proposed trade is sent to the `Portfolio and Risk Service`, which checks it against all risk constraints.
4.  **Execution**: If the trade is approved, the `Execution Service` places the order on the simulated market.
5.  **Monitoring**: The `Portfolio and Risk Service` tracks the open position.
6.  **Feedback**: When a position is closed, the `Learning Service` analyzes the result and provides feedback to the `Strategy Engine`.
7.  **Visualization**: The `Dashboard Service` polls the other services to display a live view of the entire process.
