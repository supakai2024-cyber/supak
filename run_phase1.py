from src.strategies.cdc_action_zone import CDCActionZone
from src.engine.backtest_engine import BacktestEngine
import pandas as pd

def main():
    print("==========================================")
    print("   StockRobo-US01: Phase 1 Demo Run       ")
    print("==========================================")
    
    # Initialize components
    strategy = CDCActionZone()
    engine = BacktestEngine(initial_capital=10_000)
    
    # Symbols to test
    symbols = ['SPY', 'QQQ', 'NVDA', 'TSLA']
    
    for symbol in symbols:
        print(f"\nProcessing {symbol}...")
        trades, df = engine.run(symbol, strategy, period="2y")
        
        if trades is not None and not trades.empty:
            print("Last 3 Trades:")
            print(trades.tail(3)[['Date', 'Type', 'Price', 'PnL']])
        else:
            print("No trades generated.")
            
if __name__ == "__main__":
    main()
