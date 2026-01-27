from src.execution.order_manager import OrderManager
from src.risk.risk_manager import RiskManager

def main():
    print("==========================================")
    print("   StockRobo-US01: Phase 2 Execution Demo ")
    print("   (Paper Trading & Logic Test)           ")
    print("==========================================")
    
    # 1. Initialize Systems
    cash = 50_000
    risk_pct = 2.0
    
    order_mgr = OrderManager(cash_balance=cash)
    risk_mgr = RiskManager(portfolio_value=cash, risk_per_trade_pct=risk_pct)
    
    # 2. Simulate Signal Generation (From Scanner)
    # Scenario: We found 5 signals, but maybe we can't afford all, or need to pick best.
    raw_signals = [
        {'symbol': 'TSLA', 'strategy': 'FiboZone', 'entry': 420.0, 'stop': 380.0, 'win_rate': 87.5, 'change_pct': -5.5},
        {'symbol': 'NVDA', 'strategy': 'FiboZone', 'entry': 140.0, 'stop': 135.0, 'win_rate': 95.0, 'change_pct': -3.2},
        {'symbol': 'AAPL', 'strategy': 'CDCActionZone', 'entry': 230.0, 'stop': 220.0, 'win_rate': 60.0, 'change_pct': 0.5},
        {'symbol': 'GME', 'strategy': 'FiboZone', 'entry': 25.0,  'stop': 20.0,  'win_rate': 40.0, 'change_pct': -10.0}, # High risk
        {'symbol': 'MSFT', 'strategy': 'CDCActionZone', 'entry': 400.0, 'stop': 390.0, 'win_rate': 75.0, 'change_pct': 1.2}
    ]
    
    # 3. Prioritization Logic (Smart Selection)
    ranked_signals = order_mgr.prioritize_signals(raw_signals)
    
    # 4. Processing Best Signals
    orders_to_send = []
    
    print("\n[EXEC] Calculating Sizing & Orders for Top Picks...")
    for sig in ranked_signals:
        # Stop if we run out of simulated 'slots' or just execute top N
        # For now, process all valid ones.
        
        # A. Position Sizing
        sizing = risk_mgr.calculate_position_size(sig['entry'], sig['stop'])
        if sizing['shares'] == 0:
            print(f"  Skipping {sig['symbol']}: {sizing.get('reason', 'Zero shares')}")
            continue
            
        print(f"  {sig['symbol']}: Size {sizing['shares']} shares (Risk ${sizing['total_risk_dollars']:.0f})")
        
        # B. Create Order Ticket (with Market/Limit logic)
        order = order_mgr.create_order(sig, sizing)
        if order:
            orders_to_send.append(order)
            
    # 5. Execution (Paper Trade)
    order_mgr.execute_orders(orders_to_send)
    
    # 6. Reconciliation
    order_mgr.reconcile()

if __name__ == "__main__":
    main()
