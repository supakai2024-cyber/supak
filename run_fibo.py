from src.strategies.fibo_strategy import FiboZoneStrategy
from src.engine.backtest_engine import BacktestEngine
import pandas as pd

def main():
    print("==========================================")
    print("   StockRobo-US01: Fibo Zone Strategy     ")
    print("   Logic: Buy Dip in 50-78.6% Retrace     ")
    print("==========================================")
    
    # Initialize
    strategy = FiboZoneStrategy(lookback_period=120) # 6 months lookback for finding Highs
    engine = BacktestEngine(initial_capital=10_000)
    
    # Test on volatile/growth stocks where corrections are deep
    symbols = ['TSLA', 'NVDA', 'AMD', 'COIN', 'META']
    
    for symbol in symbols:
        print(f"\n--- Processing {symbol} ---")
        trades, df = engine.run(symbol, strategy, period="2y")
        
        if trades is not None and not trades.empty:
            # Calculate Win Rate specific to this strategy
            wins = trades[trades['PnL'] > 0]
            win_rate = (len(wins) / len(trades[trades['Type'] == 'SELL'])) * 100 if len(trades[trades['Type'] == 'SELL']) > 0 else 0
            
            print(f"Win Rate: {win_rate:.2f}%")
            print("Transactions (Sample):")
            print(trades.tail(5))
        else:
            print("No trades triggered (Price maybe didn't hit the deep zone).")

if __name__ == "__main__":
    main()
