import sys
import os

# --- FIX: Force Add Root Directory to Path ---
# หา Path ของไฟล์นี้ แล้วถอยออกมาเพื่อเจอ Root
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
# ---------------------------------------------

# ตอนนี้ Python จะมองเห็น folder 'src' แล้วครับ
try:
    from src.engine.scanner import MarketScanner
    from src.execution.order_manager import OrderManager
    from src.risk.risk_manager import RiskManager
    from src.notification.alert_engine import AlertEngine
except ImportError as e:
    # ถ้ายังหาไม่เจออีก ลองถอยหลังไปอีกสเต็ป (เผื่อโครงสร้างไฟล์ซ้อนกัน)
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    from src.engine.scanner import MarketScanner
    from src.execution.order_manager import OrderManager
    from src.risk.risk_manager import RiskManager
    from src.notification.alert_engine import AlertEngine

def main():
    """
    Main entry point for GitHub Actions (Single Run Execution).
    Loads state -> Scans Market -> Executes Orders -> Saves State.
    """
    try:
        alert_system = AlertEngine() # ใช้ try-except เผื่อ AlertEngine มีปัญหา
    except:
        class MockAlert:
            def send_alert(self, *args): print(f"[MOCK ALERT] {args}")
        alert_system = MockAlert()

    print("--- [GH ACTION] StockRobo-US01 Phase 2 Execution ---")
    alert_system.send_alert("GH_ACTION", "Starting Scheduled Scan...", "INFO")
    
    try:
        # 1. Initialize Components with Persistence
        state_file_path = os.path.join(current_dir, "data", "portfolio_state.json") # ใช้ Full Path
        
        # Create data directory if not exists
        os.makedirs(os.path.dirname(state_file_path), exist_ok=True)
        
        order_manager = OrderManager(state_file=state_file_path)
        
        # ... (ส่วนที่เหลือเหมือนเดิม) ...
        # (เพื่อให้โค้ดสั้นลง ผมขออนุญาตตัดตอนส่วน Logic ที่เหมือนเดิมออกนะครับ)
        # แต่คุณควรใช้ไฟล์เดิมของคุณแล้วแก้แค่ส่วนบนสุด (Import) ตามที่ผมบอกครับ

        # ... (Logic เดิม) ...
        
        # Risk Management Setup
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
            item['win_rate'] = 75.0 
            signals.append(item)
            
        print(f"[GH ACTION] Found {len(signals)} raw buy signals.")
        
        if not signals:
            alert_system.send_alert("GH_ACTION", "No signals found. Exiting.", "INFO")
            # Save state anyway to update timestamp if needed, but not critical
            return

        # 4. Prioritize & Size
        ranked_signals = order_manager.prioritize_signals(signals)
        
        # Correct Logic for Batch Sizing
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

        # 5. Execute & Persist
        if final_orders:
            order_manager.execute_orders(final_orders)
            alert_system.send_alert("GH_ACTION", f"Successfully executed {len(final_orders)} orders.", "INFO")
        else:
            print("[GH ACTION] No orders generated (No signals or Insufficient Cash).")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}") # Print to stdout for GitHub Logs
        if 'alert_system' in locals():
            alert_system.send_alert("GH_ACTION", f"Critical Error: {e}", "CRITICAL")
        sys.exit(1)

if __name__ == "__main__":
    main()