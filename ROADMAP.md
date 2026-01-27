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

## Phase 2: Execution & Automation (COMPLETED ✅)
**Goal:** Connect to live markets, automate decision making, and handle execution logic.

- [x] **Smart Execution Engine**
  - [x] **Signal Prioritizer:** Logic to rank multiple signals (Win Rate > Risk/Reward)
  - [x] **Order Type Logic:** Smart selection between Market vs Limit orders (Slippage control)
  - [x] **Reconciliation:** Check mechanism to verify order status vs portfolio
- [x] **Paper Trading System**
  - [x] Simulated Broker (Local Portfolio Tracking with Persistence)
  - [x] `OrderManager`: Generate and log orders with state management
- [x] **GitHub Actions Integration**
  - [x] Cloud-based automated execution (5 runs/day, Mon-Fri)
  - [x] Portfolio state persistence across runs
  - [x] Scheduled execution matching US market hours
- [ ] **Real Broker Integration (Future)**
  - [ ] Connect to API (e.g., Interactive Brokers, Alpaca)
  - [ ] Error Handling & Retry Logic


## Phase 3: Dashboard & Visualization (IN PROGRESS 🚧)
**Goal:** Create web-based dashboard for portfolio monitoring and performance tracking.

- [x] **GitHub Pages Dashboard**
  - [x] HTML/CSS/JavaScript dashboard
  - [x] Portfolio overview cards (Cash, Value, Return, Positions)
  - [x] Performance charts (Equity curve, Win/Loss)
  - [x] Current positions table with P&L
  - [x] Recent trades history
  - [x] Auto-refresh functionality (30s)
  - [x] Responsive design (mobile-friendly)
- [ ] **Firebase Integration (Future)**
  - [ ] Real-time database (Firestore)
  - [ ] Live stock price updates
  - [ ] Firebase Hosting
  - [ ] User authentication
- [ ] **Advanced Features (Future)**
  - [ ] Line/Telegram notifications
  - [ ] Strategy comparison charts
  - [ ] Performance analytics
  - [ ] Trade journal

