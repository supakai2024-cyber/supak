from src.engine.scanner import MarketScanner
import pandas as pd

def main():
    scanner = MarketScanner()
    
    # A list of popular US Tech & High Volume stocks for demo
    # In production, this could be loaded from a CSV or API
    target_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX', # Big Tech
        'AMD', 'INTC', 'QCOM', 'MU', # Semis
        'COIN', 'HOOD', 'PLTR', 'U', # Growth/Retail faves
        'SPY', 'QQQ', 'IWM', # Indices
        'DIS', 'BA', 'MCD', 'KO', 'JNJ', # Traditional
        'MARA', 'RIOT' # Crypto miners (high volatility)
    ]
    
    print("==========================================")
    print("   StockRobo-US01: Market Scanner         ")
    print("==========================================")
    
    results = scanner.scan(target_symbols)
    
    # --- Report: Buy Signals ---
    print("\n[ BUY SIGNALS ] - Newly turned Green (Bullish)")
    if results['buy_signals']:
        df_buy = pd.DataFrame(results['buy_signals'])
        print(df_buy[['symbol', 'price', 'change_pct']])
    else:
        print("No new buy signals today.")
        
    # --- Report: Sell Signals ---
    print("\n[ SELL SIGNALS ] - Newly turned Red (Bearish)")
    if results['sell_signals']:
        df_sell = pd.DataFrame(results['sell_signals'])
        print(df_sell[['symbol', 'price', 'change_pct']])
    else:
        print("No new sell signals today.")

    # --- Report: Heavy Drops ---
    print("\n[ HEAVY DROPS ] - Daily Drop > 3% (Watchlist for Rebound/Crash)")
    if results['heavy_drops']:
        df_drop = pd.DataFrame(results['heavy_drops'])
        print(df_drop[['symbol', 'price', 'change_pct', 'color']])
    else:
        print("No heavy drops detected today.")

if __name__ == "__main__":
    main()
