
import sys
import os
# Ensure the root directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.engine.scanner import MarketScanner
from src.execution.order_manager import OrderManager
from src.risk.risk_manager import RiskManager
from src.notification.alert_engine import AlertEngine

def main():
    """
    Main entry point for GitHub Actions (Single Run Execution).
    Loads state -> Scans Market -> Executes Orders -> Saves State.
    """
    alert_system = AlertEngine()
    print("--- [GH ACTION] StockRobo-US01 Phase 2 Execution ---")
    alert_system.send_alert("GH_ACTION", "Starting Scheduled Scan...", "INFO")
    
    try:
        # 1. Initialize Components with Persistence
        state_file_path = os.path.join("data", "portfolio_state.json")
        order_manager = OrderManager(state_file=state_file_path)
        
        # Risk Management Setup
        # We assume a fixed portfolio baseline for risk calcs (e.g. 50k), 
        # but execution is limited by actual available cash in OrderManager.
        risk_manager = RiskManager(portfolio_value=50000.0, risk_per_trade_pct=2.0)
        
        scanner = MarketScanner()
        target_symbols = ['SPY', 'QQQ', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'AMD']
        
        # 2. Market Scan
        print(f"[GH ACTION] Scanning {len(target_symbols)} symbols...")
        results = scanner.scan(target_symbols)
        
        # 3. Process Signals
        signals = []
        for item in results.get('buy_signals', []):
            item['strategy'] = 'Scanner_CDC' 
            item['win_rate'] = 75.0 # Mock Win Rate
            signals.append(item)
            
        print(f"[GH ACTION] Found {len(signals)} raw buy signals.")
        
        if not signals:
            alert_system.send_alert("GH_ACTION", "No signals found. Exiting.", "INFO")
            return

        # 4. Prioritize & Size
        ranked_signals = order_manager.prioritize_signals(signals)
        orders_to_send = []
        
        for sig in ranked_signals:
            entry_price = sig['price']
            stop_price = entry_price * 0.95 # Mock Stop Loss 5%
            
            # Risk Calc
            sizing = risk_manager.calculate_position_size(entry_price, stop_price)
            
            # Liquidity Check against persisted Cash Balance
            potential_cost = sizing['shares'] * entry_price
            if potential_cost > order_manager.cash_balance:
                # Resize down to available cash
                max_shares = int(order_manager.cash_balance // entry_price)
                print(f"[RISK] Adjusting size for {sig['symbol']} due to cash limit: {sizing['shares']} -> {max_shares}")
                sizing['shares'] = max_shares
            
            if sizing['shares'] > 0:
                sig['entry'] = entry_price
                order = order_manager.create_order(sig, sizing)
                if order:
                    orders_to_send.append(order)
                    # Temporarily deduct cash from local variable to prevent double spending in same batch
                    # (Though OrderManager.execute_orders does it, we need to know remaining cash for NEXT signal in this loop)
                    order_manager.cash_balance -= (sizing['shares'] * entry_price) 

        # Restore OrderManager cash balance because execute_orders will deduct it again?
        # WAIT: modifying order_manager.cash_balance directly here affects the object.
        # But execute_orders ALSO deducts.
        # If I deducted it here, execute_orders will deduct AGAIN from the already reduced amount.
        # FIX: I should probably NOT deduct it permanently here, OR let execute_orders handle it.
        # BUT for the purposes of the loop (buying multiple stocks), I MUST track remaining cash.
        # Let's reload state or just accept that execute_orders logic needs to be robust.
        # Simpler approach for this script:
        # Calculate all orders, Filter them, Then Execute.
        # But I need to know cumulative cost.
        
        # Refined Loop Logic:
        # Reset cash to start of loop for calculation
        # (This implies I need to re-read cash, or just use a temp variable)
        
        # Let's re-instantiate OrderManager to be safe or just manually revert the changes?
        # Actually, simpler: Use a 'temp_cash' variable.
        
        pass 
        # (Re-running logic correctly in next block)
        
    except Exception as e:
        alert_system.send_alert("GH_ACTION", f"Critical Error: {e}", "CRITICAL")
        sys.exit(1)

    # Correct Logic for Batch Sizing
    # We need to re-do the sizing loop properly using a temp cash variable
    order_manager.load_state() # Reset to actual state
    temp_cash = order_manager.cash_balance
    final_orders = []
    
    for sig in ranked_signals:
        entry_price = sig['price']
        stop_price = entry_price * 0.95
        
        sizing = risk_manager.calculate_position_size(entry_price, stop_price)
        cost = sizing['shares'] * entry_price
        
        if cost > temp_cash:
             sizing['shares'] = int(temp_cash // entry_price)
             cost = sizing['shares'] * entry_price
        
        if sizing['shares'] > 0:
            sig['entry'] = entry_price
            order = order_manager.create_order(sig, sizing)
            if order:
                final_orders.append(order)
                temp_cash -= cost # Deduct from available budget for this run

    # 5. Execute & Persist
    if final_orders:
        # Note: execute_orders will update self.cash_balance and call save_state()
        order_manager.execute_orders(final_orders)
        alert_system.send_alert("GH_ACTION", f"Successfully executed {len(final_orders)} orders.", "INFO")
    else:
        print("[GH ACTION] No orders generated (No signals or Insufficient Cash).")
        # Ensure we save state anyway (e.g. to update timestamps or log empty run if we added that)
        # order_manager.save_state() 

if __name__ == "__main__":
    main()
