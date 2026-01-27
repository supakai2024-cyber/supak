# StockRobo-US01 Project Roadmap

## Phase 1: Foundation & Strategies (COMPLETED)
**Goal:** Build the core logic, data handling, and strategy engine.

- [x] **Project Initialization**
  - [x] Create project structure
  - [x] Basic Security (Authenticator)
- [x] **Data Layer**
  - [x] `MarketData`: Module to fetch historical/real-time data (e.g., yfinance)
  - [x] Data validation and cleaning
- [x] **Strategy Engine**
  - [x] Base `Strategy` class interface (CDC, Fibo implemented)
  - [x] CDC Action Zone implementation
  - [x] Fibo Zone Strategy (High Win rate for mean reversion)
- [x] **Backtesting System**
  - [x] `BacktestEngine`: Run strategies against historical data
  - [x] Performance metrics (Win Rate, PnL)
- [x] **Risk Management (Critical)**
  - [x] Position Sizing Calculator (Risk-based)
  - [x] Market Regime Filter (SPY Trend)

## Phase 2: Execution & Automation (Current Focus)
**Goal:** Connect to live markets, automate decision making, and handle execution logic.

- [ ] **Smart Execution Engine**
  - [ ] **Signal Prioritizer:** Logic to rank multiple signals (Win Rate > Risk/Reward)
  - [ ] **Order Type Logic:** Smart selection between Market vs Limit orders (Slippage control)
  - [ ] **Reconciliation:** Check mechanism to verify order status vs portfolio
- [ ] **Paper Trading System**
  - [ ] Simulated Broker (Local Portfolio Tracking)
  - [ ] `OrderManager`: Generate and log orders
- [ ] **Real Broker Integration (Future)**
  - [ ] Connect to API (e.g., Interactive Brokers, Alpaca)
  - [ ] Error Handling & Retry Logic

## Phase 3: Interface & Monitoring
**Goal:** User interaction, visualization, and notifications.

- [ ] **Dashboard**
  - [ ] Web UI (showing portfolio, signals, charts)
  - [ ] Performance reporting
- [ ] **Notifications**
  - [ ] Line/Telegram/Email alerts on signals
- [ ] **Deployment**
  - [ ] Docker containerization
  - [ ] Cloud deployment setup
