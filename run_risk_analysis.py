from src.risk.risk_manager import RiskManager
from src.data.market_data import MarketData
from src.strategies.fibo_strategy import FiboZoneStrategy

def main():
    print("==========================================")
    print("   StockRobo-US01: Risk & Ready (Battle Prep) ")
    print("==========================================")
    
    # 1. Setup
    total_portfolio = 50_000 # Let's say we have $50k
    risk_pct = 2.0           # We want to risk MAX 2% per trade ($1,000)
    
    risk_mgr = RiskManager(portfolio_value=total_portfolio, risk_per_trade_pct=risk_pct)
    market_data = MarketData()
    
    # Let's say our Scanner found these opportunities
    # Simulation: We found signals on these stocks
    candidates = [
        {'symbol': 'TSLA', 'entry': 420.00, 'stop': 380.00}, # Volatile, wide stop
        {'symbol': 'NVDA', 'entry': 140.00, 'stop': 135.00}, # Tight stop
        {'symbol': 'KO',   'entry': 60.00,  'stop': 58.00},  # Low volatility
    ]
    
    # 2. Check Market Regime (Filter)
    print("\n[ Step 1: Market Regime Check (SPY) ]")
    spy_df = market_data.get_history('SPY', period='2y')
    regime = risk_mgr.assess_market_regime(spy_df)
    
    print(f"Market Status: {regime['regime']} ({regime['safety_level']})")
    print(f"Details: {regime['description']}")
    
    if regime['safety_level'] == 'Caution':
        print(">> WARNING: Bear Market Detected. Reducing Risk to 1%...")
        risk_mgr.risk_pct = 0.01
    
    # 3. Calculate Sizing for Candidates
    print("\n[ Step 2: Position Sizing Calculator ]")
    print(f"Portfolio: ${total_portfolio:,.2f}")
    print(f"Risk per Trade: {risk_mgr.risk_pct * 100}% (${total_portfolio * risk_mgr.risk_pct:,.2f})")
    print("-" * 60)
    print(f"{'SYMBOL':<10} {'ENTRY':<10} {'STOP':<10} {'SHARES':<10} {'POSITION $':<15} {'RISK $':<10}")
    print("-" * 60)
    
    for item in candidates:
        sizing = risk_mgr.calculate_position_size(item['entry'], item['stop'])
        
        print(f"{item['symbol']:<10} "
              f"{sizing['entry']:<10.2f} "
              f"{sizing['stop_loss']:<10.2f} "
              f"{sizing['shares']:<10} "
              f"${sizing['position_value']:<14,.2f} "
              f"${sizing['total_risk_dollars']:<10.2f}")
              
    print("-" * 60)
    print("Observation: Notice how 'Shares' adjust based on Stop Loss width.")
    print("TSLA (Wide Stop) -> Fewer Shares to cap risk.")
    print("NVDA (Tight Stop) -> More Shares allowed.")

if __name__ == "__main__":
    main()
