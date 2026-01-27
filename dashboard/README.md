# StockRobo-US01 Dashboard

🤖 **Automated Trading Dashboard** - Real-time portfolio monitoring and performance tracking

---

## 🎯 Features

- 💰 **Portfolio Overview** - Cash balance, total value, and returns
- 📊 **Performance Charts** - Equity curve and win/loss distribution
- 📈 **Current Positions** - Live position tracking with P&L
- 📋 **Trade History** - Recent trades with status
- ⏰ **System Status** - Last update and next scheduled run
- 🔄 **Auto-refresh** - Updates every 30 seconds

---

## 🚀 Quick Start

### Option 1: Local Development

1. **Open the dashboard locally:**
   ```bash
   # Navigate to dashboard folder
   cd dashboard
   
   # Open in browser (or use Live Server in VS Code)
   # File path: file:///C:/Program%20External%20Source/AGI%20Stock%20Analyst/stockrobo-us01/dashboard/index.html
   ```

2. **Using Python HTTP Server:**
   ```bash
   # From project root
   cd dashboard
   python -m http.server 8000
   
   # Open browser to: http://localhost:8000
   ```

### Option 2: GitHub Pages (Recommended)

1. **Push dashboard to GitHub:**
   ```bash
   git add dashboard/
   git commit -m "Add Phase 3 Dashboard"
   git push
   ```

2. **Enable GitHub Pages:**
   - Go to GitHub Repository → Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` → Folder: `/dashboard`
   - Click Save

3. **Access your dashboard:**
   - URL: `https://[your-username].github.io/[repo-name]/`
   - Example: `https://supakai2024-cyber.github.io/supak/`

---

## 📁 File Structure

```
dashboard/
├── index.html          # Main dashboard page
├── styles.css          # Styling (dark theme)
├── dashboard.js        # Dashboard logic
└── README.md           # This file
```

---

## 🔧 Configuration

### Data Source

The dashboard reads from `../data/portfolio_state.json`:

```json
{
  "timestamp": 1706380800,
  "cash_balance": 45000.0,
  "portfolio": {
    "NVDA": 50,
    "TSLA": 30
  },
  "orders": [
    {
      "order_id": "abc123",
      "symbol": "NVDA",
      "action": "BUY",
      "quantity": 50,
      "filled_price": 140.50,
      "status": "FILLED",
      "timestamp": 1706380800
    }
  ]
}
```

### Auto-refresh Interval

Edit `dashboard.js` line ~290:
```javascript
setInterval(() => {
    initDashboard();
}, 30000); // 30 seconds (change as needed)
```

---

## 🎨 Customization

### Change Theme Colors

Edit `styles.css` CSS variables:
```css
:root {
    --primary-color: #6366f1;      /* Main accent color */
    --success-color: #10b981;      /* Profit/Win color */
    --danger-color: #ef4444;       /* Loss/Sell color */
    --bg-primary: #0f172a;         /* Background */
}
```

### Modify Initial Capital

Edit `dashboard.js` line ~2:
```javascript
const INITIAL_CAPITAL = 50000; // Change to your starting capital
```

---

## 📊 Dashboard Sections

### 1. Summary Cards
- **Cash Balance**: Available capital
- **Portfolio Value**: Total equity (cash + positions)
- **Total Return**: Percentage gain/loss since inception
- **Active Positions**: Number of open trades

### 2. Charts
- **Portfolio Performance**: Equity curve over time
- **Win/Loss Distribution**: Pie chart of trade outcomes

### 3. Current Positions Table
- Symbol, Quantity, Avg Price, Current Price, P&L, P&L%

### 4. Recent Trades Table
- Last 10 trades with date, symbol, type, quantity, price, status

### 5. System Info
- Last update timestamp
- Next scheduled run
- Total number of trades

---

## 🔄 How It Works

1. **GitHub Actions runs** → Executes trades → Updates `portfolio_state.json`
2. **Dashboard loads** → Fetches `portfolio_state.json` → Calculates metrics
3. **Charts render** → Using Chart.js library
4. **Auto-refresh** → Every 30 seconds (configurable)

---

## 🐛 Troubleshooting

### Dashboard shows "No data"
- **Cause**: `portfolio_state.json` not found
- **Fix**: Ensure file exists in `data/` folder or run bot at least once

### Charts not rendering
- **Cause**: Chart.js not loaded
- **Fix**: Check internet connection (CDN required)

### GitHub Pages shows 404
- **Cause**: Incorrect folder configuration
- **Fix**: 
  1. Go to Settings → Pages
  2. Set folder to `/dashboard` (not `/docs`)
  3. Wait 1-2 minutes for deployment

### CORS errors on local file
- **Cause**: Browser security restrictions
- **Fix**: Use Python HTTP server or Live Server extension

---

## 🚀 Next Steps (Phase 3 Upgrades)

- [ ] **Firebase Integration** - Real-time database
- [ ] **Price Updates** - Fetch live stock prices
- [ ] **Notifications** - Line/Telegram alerts
- [ ] **Mobile Responsive** - Better mobile UI
- [ ] **Authentication** - Password protection
- [ ] **Historical Data** - Performance over time
- [ ] **Strategy Comparison** - CDC vs Fibo performance

---

## 📱 Mobile Support

The dashboard is fully responsive and works on:
- 📱 Mobile phones
- 📱 Tablets
- 💻 Desktop browsers

---

## 🔒 Security Notes

⚠️ **Important**: This dashboard displays portfolio data publicly if hosted on GitHub Pages.

**For private data:**
1. Use Firebase with authentication
2. Host on private server
3. Add password protection
4. Use environment variables for sensitive data

---

## 📄 License

Part of StockRobo-US01 Project - Phase 3: Dashboard & Visualization

---

## 🤝 Support

For issues or questions:
1. Check troubleshooting section
2. Review browser console for errors
3. Verify `portfolio_state.json` format

---

**Happy Trading! 🚀📈**
