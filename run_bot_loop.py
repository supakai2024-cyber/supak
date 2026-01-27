import time
import datetime
import schedule
import sys
import traceback
from src.engine.scanner import MarketScanner
from src.execution.order_manager import OrderManager
from src.risk.risk_manager import RiskManager
from src.notification.alert_engine import AlertEngine

class AutonomousBot:
    def __init__(self):
        self.alert_system = AlertEngine(log_file="logs/bot_activity.log")
        self.alert_system.send_alert("SYSTEM", "Initializing StockRobo-US01...", "INFO")
        
        try:
            self.scanner = MarketScanner()
            self.order_manager = OrderManager(cash_balance=50000.0) # Paper Portfolio
            self.risk_manager = RiskManager(portfolio_value=50000.0, risk_per_trade_pct=2.0)
            self.target_symbols = [
                'SPY', 'QQQ', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'AMD'
            ]
            self.is_running = True
            self.alert_system.send_alert("SYSTEM", "Initialization Complete.", "INFO")
        except Exception as e:
            self.alert_system.send_alert("CRITICAL", f"Initialization Failed: {e}", "CRITICAL")
            raise e

    def heartbeat(self):
        """Simple check to show bot is alive."""
        # Using a lower log level or just console for heartbeat to avoid flooding logs?
        # For now, let's keep it visible but maybe distinct.
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [HEARTBEAT] System Operational.")

    def job_market_scan(self):
        """
        Main Routine: Scan -> Signal -> Size -> Execute
        """
        self.alert_system.send_alert("SCANNER", "Starting Scheduled Market Scan...", "INFO")
        
        try:
            # 1. Scan
            results = self.scanner.scan(self.target_symbols)
            
            # Combine signals (Buy + Sell if we were handling shorts/exits)
            # For this demo phase, let's focus on BUY signals from Scanner
            signals = []
            
            # Process Buy Signals
            for item in results.get('buy_signals', []):
                # Alert for each signal found
                self.alert_system.send_alert("SIGNAL", f"Found BUY signal: {item['symbol']} at {item['price']:.2f}", "INFO")
                
                # Enrich signal with Strategy Tag (Scanner mostly does CDC currently)
                item['strategy'] = 'Scanner_CDC' # Simplification
                # Mock win rate for simulation
                item['win_rate'] = 75.0 
                signals.append(item)
                
            # Process Heavy Drops (Alert Only for now)
            for item in results.get('heavy_drops', []):
                 self.alert_system.send_alert("WATCH", f"Heavy Drop Detected: {item['symbol']} ({item['change_pct']:.2f}%)", "WARNING")
                 # In real implementation, FiboStrategy would run here
                 pass

            if not signals:
                self.alert_system.send_alert("SCANNER", "No actionable signals found this cycle.", "INFO")
                return

            self.alert_system.send_alert("OPPORTUNITY", f"Found {len(signals)} potential candidates.", "INFO")
            
            # 2. Prioritize
            ranked_signals = self.order_manager.prioritize_signals(signals)
            
            # 3. Execution Loop
            orders_to_send = []
            for sig in ranked_signals:
                # Check Risk/Sizing
                # stop loss logic usually comes from strategy. 
                # For scanner results, we might assume a trailing stop or % stop
                # Let's mock a Stop Loss 5% below entry for scanner results
                entry_price = sig['price']
                stop_price = entry_price * 0.95
                
                sizing = self.risk_manager.calculate_position_size(entry_price, stop_price)
                if sizing['shares'] > 0:
                    sig['entry'] = entry_price # Normalize keys
                    
                    order = self.order_manager.create_order(sig, sizing)
                    if order:
                        orders_to_send.append(order)
                        self.alert_system.send_alert("ORDER_GEN", f"Generated Order for {sig['symbol']}: {sizing['shares']} shares", "INFO")
            
            # 4. Execute
            if orders_to_send:
                self.order_manager.execute_orders(orders_to_send)
                self.alert_system.send_alert("EXECUTION", f"Sent {len(orders_to_send)} orders to market.", "INFO")
            
            # 5. Reconcile
            self.order_manager.reconcile()

        except Exception as e:
            self.alert_system.send_alert("ERROR", f"Error during market scan loop: {e}", "ERROR")
            traceback.print_exc() 
            # We do NOT raise here, effectively keeping the loop alive despite a crash in this job.

    def start_loop(self):
        self.alert_system.send_alert("SYSTEM", "StockRobo-US01: Autonomous Loop STARTED", "INFO")
        self.alert_system.send_alert("SYSTEM", f"Monitoring {len(self.target_symbols)} Symbols", "INFO")
        
        # Schedule Jobs
        # In real world: Market hours check. Here: Run every 1 minute for DEMO.
        schedule.every(1).minutes.do(self.job_market_scan)
        schedule.every(30).seconds.do(self.heartbeat)
        
        # Initial Run immediately
        self.job_market_scan()
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.alert_system.send_alert("SYSTEM", "Bot Stopped by User (KeyboardInterrupt).", "WARNING")
        except Exception as e:
            self.alert_system.send_alert("CRITICAL", f"Main Loop Crash: {e}", "CRITICAL")
            raise e

if __name__ == "__main__":
    bot = AutonomousBot()
    bot.start_loop()
