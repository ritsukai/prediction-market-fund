# What the Prediction Market Fund Does

## Purpose

This system is an **autonomous trading bot for prediction markets** (like Polymarket). It automatically:
1. Analyzes prediction markets to find trading opportunities
2. Makes buy/sell decisions based on expected value calculations
3. Manages existing positions (takes profits, cuts losses)
4. Enforces risk management rules

## How It Works

### The Complete Workflow

```
┌─────────────────┐
│  Market Data    │  ← Fetches from external sources (Polymarket, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Strategy Engine  │  ← Analyzes data, calculates EV, finds opportunities
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Trade Orders   │  ← Proposes BUY/SELL with Investment Memos
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Risk Manager    │  ← Approves/rejects based on risk limits
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Portfolio Manager│  ← Executes approved trades, updates positions
└─────────────────┘
```

### Key Components

#### 1. **Data Ingestion Service**
- **What it does**: Fetches market data from external sources
- **Current implementation**: Uses `MockDataSourceConnector` for testing
- **Real use**: Would connect to Polymarket API, news feeds, on-chain data

#### 2. **Strategy Engine**
- **What it does**: The "brain" of the system
- **Key functions**:
  - **New Opportunities**: Scans all markets, calculates Expected Value (EV) and conviction
    - If EV > current price AND conviction > threshold → BUY signal
  - **Position Management**: Monitors existing positions
    - If gain ≥ 10% → Profit-taking (SELL)
    - If loss ≥ 5% → Stop-loss (SELL)

#### 3. **Risk Manager**
- **What it does**: Prevents excessive risk
- **Rules**:
  - Max 10% exposure per individual market
  - Max 50% total fund exposure
  - Ensures sufficient cash/shares before trading

#### 4. **Portfolio Manager**
- **What it does**: Executes trades and tracks positions
- **Functions**:
  - Maintains cash balance
  - Tracks all positions (market_id, asset, quantity, cost basis)
  - Executes BUY/SELL orders

## What You Should See When It Works

### Scenario 1: Finding a New Opportunity
```
Input: Market with price $0.50, but EV calculated at $0.75 with 80% conviction
Output: 
  - TradeOrder: BUY 2000 shares @ $0.50
  - InvestmentMemo: "New opportunity: EV is $0.75 above current price $0.50"
```

### Scenario 2: Profit-Taking
```
Input: Position bought at $0.40, now worth $0.50 (25% gain)
Output:
  - TradeOrder: SELL all shares @ $0.50
  - InvestmentMemo: "Profit-taking: Price is 25% above cost basis"
```

### Scenario 3: Stop-Loss
```
Input: Position bought at $0.80, now worth $0.30 (62.5% loss)
Output:
  - TradeOrder: SELL all shares @ $0.30
  - InvestmentMemo: "Stop-loss: Price is 62.5% below cost basis. Thesis invalidated."
```

### Scenario 4: Risk Manager Rejection
```
Input: Trade would put 15% of fund in one market (limit is 10%)
Output:
  - TradeOrder: Generated but NOT executed
  - Risk Manager: "Rejecting trade due to exceeding per-market exposure limit"
```

## How to Verify It Works

### Method 1: Run the Demo Script
```bash
python demo.py
```

This will show:
- ✓ System initialization
- ✓ Market data fetching
- ✓ Strategy execution (finding opportunities)
- ✓ Trade order generation
- ✓ Risk management
- ✓ Trade execution
- ✓ Position management (profit-taking/stop-loss)

### Method 2: Run Unit Tests
```bash
python -m pytest tests/ -v
```

**Note**: Tests currently have import issues but demonstrate expected behavior:
- ✓ Identifies BUY opportunities
- ✓ Identifies SELL opportunities (profit-taking)
- ✓ Identifies stop-loss scenarios
- ✓ Rejects trades with low conviction
- ✓ Respects risk manager decisions

### Method 3: Manual Verification Checklist

When running the system, verify:

- [ ] **Data Ingestion**: System fetches market data
  - Check: `data_service.get_all_market_data()` returns market list

- [ ] **Strategy Analysis**: System analyzes markets
  - Check: `strategy.run_strategy()` returns trade orders and memos

- [ ] **Investment Memos**: Every trade has a justification
  - Check: Each `TradeOrder` has corresponding `InvestmentMemo` with:
    - Calculated EV
    - Conviction level
    - Rationale explaining the decision

- [ ] **Risk Management**: Risk manager prevents bad trades
  - Check: Trades exceeding limits are rejected
  - Check: Console shows "RiskManager: Rejecting trade..." messages

- [ ] **Portfolio Updates**: Trades update portfolio state
  - Check: `portfolio_manager.get_portfolio_state()` shows:
    - Updated cash balance after trades
    - New positions after BUY orders
    - Removed positions after SELL orders

- [ ] **Position Management**: System manages existing positions
  - Check: Profitable positions trigger profit-taking
  - Check: Losing positions trigger stop-loss

## Expected Output Format

### Trade Orders
```python
TradeOrder(
    market_id="market-123",
    action="BUY",
    asset="yes",
    quantity=2000.0,
    price_limit=0.50,
    timestamp=datetime(...)
)
```

### Investment Memos
```python
InvestmentMemo(
    timestamp=datetime(...),
    market_id="market-123",
    action="BUY",
    asset="yes",
    quantity=2000.0,
    price=0.50,
    calculated_ev=0.75,
    conviction=0.80,
    rationale="New opportunity: Calculated EV is 0.75 above current price 0.50",
    data_sources=["polymarket_data_for_market-123"]
)
```

## Current Limitations

1. **Mock Data Only**: Currently uses `MockDataSourceConnector` - needs real API integration
2. **Simplified EV Calculation**: The `_calculate_ev_and_conviction()` method is a placeholder
3. **No Real Trading**: Portfolio manager is a simulation - doesn't actually execute on exchanges
4. **Test Import Issues**: Tests need to be fixed to use correct Position model

## Next Steps for Real Usage

1. **Connect Real Data Source**: Replace `MockDataSourceConnector` with Polymarket API
2. **Implement Real EV Calculation**: Add sophisticated prediction logic
3. **Add Exchange Integration**: Connect to actual prediction market exchange
4. **Add Logging/Monitoring**: Track performance, P&L, trade history
5. **Add Backtesting**: Test strategies on historical data


