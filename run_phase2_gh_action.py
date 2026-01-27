import sys
import os
import json

# --- CRITICAL FIX: Force Add Paths ---
# 1. หาตำแหน่งไฟล์ปัจจุบัน
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)

# 2. เพิ่ม path ของโฟลเดอร์ปัจจุบัน
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 3. ลองหาโฟลเดอร์ 'src' ว่าอยู่ที่ไหน
# ถ้าไฟล์นี้อยู่ใน stockrobo-us01/run_...py แต่ src อยู่ใน stockrobo-us01/src
src_path = os.path.join(current_dir, 'src')

# ถ้าไม่เจอ src ให้ลองถอยออกไป 1 ชั้น (เผื่อไฟล์อยู่ลึก)
if not os.path.exists(src_path):
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    src_path = os.path.join(parent_dir, 'src')

print(f"[DEBUG] Current Dir: {current_dir}")
print(f"[DEBUG] System Path: {sys.path}")
# -------------------------------------

try:
    from src.engine.scanner import MarketScanner
    from src.execution.order_manager import OrderManager
    from src.risk.risk_manager import RiskManager
    from src.notification.alert_engine import AlertEngine
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    print("Listing files in current directory:")
    print(os.listdir(current_dir))
    if os.path.exists(src_path):
         print(f"Listing files in src directory ({src_path}):")
         print(os.listdir(src_path))
    sys.exit(1)

def main():
    try:
        alert_system = AlertEngine()
    except:
        class MockAlert:
            def send_alert(self, *args): print(f"[MOCK ALERT] {args}")
        alert_system = MockAlert()

    print("--- [GH ACTION] StockRobo-US01 Phase 2 Execution ---")
    alert_system.send_alert("GH_ACTION", "Starting Scheduled Scan...", "INFO")
    
    try:
        # State File (Force Absolute Path)
        state_file_path = os.path.join(current_dir, "data", "portfolio_state.json")
        os.makedirs(os.path.dirname(state_file_path), exist_ok=True)
        
        order_manager = OrderManager(state_file=state_file_path)
        risk_manager = RiskManager(portfolio_value=50000.0, risk_per_trade_pct=2.0)
        scanner = MarketScanner()
        
        # Load watchlist (from file or use default)
        watchlist_path = os.path.join(current_dir, "data", "watchlist.json")
        
        if os.path.exists(watchlist_path):
            try:
                with open(watchlist_path, 'r') as f:
                    watchlist_data = json.load(f)
                    target_symbols = watchlist_data.get('watchlist', [])
                    print(f"[GH ACTION] Loaded watchlist from file: {len(target_symbols)} symbols")
                    print(f"[GH ACTION] Generated at: {watchlist_data.get('generated_at', 'Unknown')}")
            except Exception as e:
                print(f"[GH ACTION] Error loading watchlist: {e}")
                target_symbols = ['SPY', 'QQQ', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'AMD']
        else:
            print("[GH ACTION] No watchlist found. Using default symbols.")
            target_symbols = ['SPY', 'QQQ', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'AMD']
        
        print(f"[GH ACTION] Scanning {len(target_symbols)} symbols...")
        results = scanner.scan(target_symbols)
        
        signals = []
        for item in results.get('buy_signals', []):
            item['strategy'] = 'Scanner_CDC' 
            item['win_rate'] = 75.0 
            signals.append(item)
            
        print(f"[GH ACTION] Found {len(signals)} raw buy signals.")

        
        if signals:
            ranked_signals = order_manager.prioritize_signals(signals)
            
            order_manager.load_state() 
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
                        temp_cash -= cost 

            if final_orders:
                order_manager.execute_orders(final_orders)
                alert_system.send_alert("GH_ACTION", f"Successfully executed {len(final_orders)} orders.", "INFO")
            else:
                 print("[GH ACTION] No orders generated (Insufficient Cash).")
        else:
            print("[GH ACTION] No signals found.")

    except Exception as e:
        print(f"CRITICAL RUNTIME ERROR: {e}")
        alert_system.send_alert("GH_ACTION", f"Critical Error: {e}", "CRITICAL")
        sys.exit(1)

if __name__ == "__main__":
    main()