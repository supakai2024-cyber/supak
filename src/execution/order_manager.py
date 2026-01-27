from typing import List, Dict, Any, Optional
import time
import uuid
import json
import os

class OrderManager:
    """
    Simulates the Execution Engine for Phase 2.
    Handles Priority, Order Type Selection, and Reconciliation (Simulated).
    Supports Persistence for stateless environments (e.g., GitHub Actions).
    """
    
    def __init__(self, cash_balance: float = 50000.0, state_file: str = "data/portfolio_state.json"):
        self.state_file = state_file
        # Default starting values
        self.cash_balance = cash_balance
        self.orders = []
        self.portfolio: Dict[str, int] = {} # Symbol -> Quantity
        
        # Load previous state if available
        self.load_state()

    def load_state(self):
        """Load portfolio and orders from JSON file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.cash_balance = data.get('cash_balance', self.cash_balance)
                    self.portfolio = data.get('portfolio', {})
                    self.orders = data.get('orders', [])
                    print(f"[EXEC] Loaded persistence state from {self.state_file}")
                    print(f"       Cash: ${self.cash_balance:.2f} | Positions: {len(self.portfolio)}")
            except Exception as e:
                print(f"[EXEC] Error loading state: {e}")
        else:
            print("[EXEC] No saved state found. Starting fresh.")

    def save_state(self):
        """Save current portfolio and orders to JSON file."""
        data = {
            'timestamp': time.time(),
            'cash_balance': self.cash_balance,
            'portfolio': self.portfolio,
            'orders': self.orders[-50:] # Keep last 50 orders history
        }
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"[EXEC] State saved to {self.state_file}")
        except Exception as e:
            print(f"[EXEC] Error saving state: {e}")
        
    def prioritize_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank signals based on criteria:
        1. Backtest Win Rate (if available)
        2. Signal Strength (e.g., Fibo Deep Discount > Shallow Dip)
        3. Risk/Reward Ratio (implied)
        """
        print(f"\n[EXEC] Prioritizing {len(signals)} signals...")
        
        # Scoring Logic
        for sig in signals:
            score = 0
            
            # Criterion 1: Strategy Type Preference
            if sig['strategy'] == 'FiboZone':
                score += 50 # Base preference for Mean Reversion (Deep Value)
            elif sig['strategy'] == 'CDCActionZone':
                score += 30 # Trend Following
            
            # Criterion 2: Win Rate (Simulated data field)
            win_rate = sig.get('win_rate', 50.0)
            score += win_rate # e.g., +80 points for 80% win rate
            
            sig['priority_score'] = score
            
        # Sort by Score descending
        sorted_signals = sorted(signals, key=lambda x: x['priority_score'], reverse=True)
        
        for i, sig in enumerate(sorted_signals):
            print(f"  #{i+1}: {sig['symbol']} ({sig['strategy']}) - Score: {sig['priority_score']}")
            
        return sorted_signals

    def determine_order_type(self, symbol: str, price: float, current_volatility: float = 1.0) -> str:
        """
        Decide between Market vs Limit Order.
        Logic:
        - High Volatility -> Limit Order (to avoid slippage)
        - Low Volatility -> Market Order (speed)
        """
        # Threshold: If daily move > 2%, use LIMIT.
        if current_volatility > 2.0:
            return "LIMIT"
        else:
            return "MARKET"

    def create_order(self, signal: Dict[str, Any], position_size: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate an Order Ticket.
        """
        shares = position_size['shares']
        if shares <= 0:
            return None
            
        price = position_size['entry']
        # Simulating fetching recent volatility (change_pct) from signal
        volatility = signal.get('change_pct', 0.0)
        
        order_type = self.determine_order_type(signal['symbol'], price, abs(volatility))
        limit_price = price if order_type == 'LIMIT' else None
        
        order = {
            'order_id': str(uuid.uuid4())[:8],
            'symbol': signal['symbol'],
            'action': 'BUY',
            'quantity': shares,
            'order_type': order_type,
            'limit_price': limit_price, # Only for LIMIT
            'status': 'PENDING',
            'timestamp': time.time(),
            'notes': f"Strategy: {signal['strategy']} | Score: {signal.get('priority_score')}"
        }
        
        return order

    def execute_orders(self, orders: List[Dict[str, Any]]):
        """
        Process the orders (Paper Trade Execution).
        """
        print(f"\n[EXEC] Processing {len(orders)} Orders...")
        
        for order in orders:
            cost = order['quantity'] * (order['limit_price'] if order['limit_price'] else 0) # Estimates
            
            # 1. Validation (Liquidity Check / Cash Check)
            # (In simulation we assume we calculated size correctly already)
            
            # 2. Execution
            if order['status'] == 'PENDING':
                print(f"  >>> Sending {order['order_type']} ORDER: Buy {order['quantity']} {order['symbol']} @ {order['limit_price'] if order['limit_price'] else 'Market'} ...")
                time.sleep(0.5) # Simulate network
                
                # 3. Fill Simulation
                order['status'] = 'FILLED'
                order['filled_price'] = order['limit_price'] if order['limit_price'] else 100.00 # Mock fill
                
                print(f"  [FILLED]: {order['symbol']} (ID: {order['order_id']})")
                self.orders.append(order)
                
                # Update Portfolio
                qty = self.portfolio.get(order['symbol'], 0)
                self.portfolio[order['symbol']] = qty + order['quantity']
                
                # Update Cash (Simulated)
                self.cash_balance -= cost
                print(f"  [CASH] Deducted ${cost:.2f}. New Balance: ${self.cash_balance:.2f}")

        # Save State after batch execution
        self.save_state()

    def reconcile(self):
        """
        Verify internal state matches 'Broker'. 
        In simulation, we just print the portfolio.
        """
        print("\n[EXEC] --- Reconciliation Check ---")
        print(f"Internal Portfolio Record: {self.portfolio}")
        print("Broker Status: MATCHED (Simulated)")
        # In real world, we would call broker_api.get_positions() and compare.

