import pandas as pd
from typing import List, Dict, Any
from src.data.market_data import MarketData
from src.strategies.cdc_action_zone import CDCActionZone

class MarketScanner:
    def __init__(self):
        self.market_data = MarketData()
        self.strategy = CDCActionZone()

    def scan(self, symbols: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scans values for Buy and Sell signals.
        
        Returns:
            Dict containing lists of 'buy_signals' and 'sell_signals'.
        """
        results = {
            'buy_signals': [],
            'sell_signals': [],
            'heavy_drops': [] # For stocks dropping hard (regardless of trend change)
        }
        
        print(f"Scanning {len(symbols)} symbols...")
        
        for symbol in symbols:
            try:
                # We need enough data for EMA26 + some buffer. 
                # 60 days is usually enough for calculation, but 3mo is safer.
                df = self.market_data.get_history(symbol, period="6mo")
                
                if df.empty or len(df) < 30:
                    continue
                
                # Apply Strategy
                df = self.strategy.calculate(df)
                
                # Get the last two rows to check for crossover
                last_row = df.iloc[-1]
                prev_row = df.iloc[-2]
                
                current_price = last_row['Close']
                prev_price = prev_row['Close']
                pct_change = ((current_price - prev_price) / prev_price) * 100
                
                # 1. Detect Buy Signal (Just turned Green)
                # Current is Green, Previous was NOT Green (Red, Blue, Yellow)
                if last_row['Color'] == 'Green' and prev_row['Color'] != 'Green':
                    results['buy_signals'].append({
                        'symbol': symbol,
                        'price': current_price,
                        'change_pct': pct_change,
                        'date': last_row['Date'] if 'Date' in last_row else last_row.name
                    })

                # 2. Detect Sell Signal (Just turned Red)
                # Current is Red, Previous was NOT Red
                if last_row['Color'] == 'Red' and prev_row['Color'] != 'Red':
                    results['sell_signals'].append({
                        'symbol': symbol,
                        'price': current_price,
                        'change_pct': pct_change,
                        'date': last_row['Date'] if 'Date' in last_row else last_row.name
                    })
                    
                # 3. Detect "Heavy Drop" (Panic Selling Watchlist)
                # Criteria: Drop more than 3% in one day (configurable)
                # regardless of trend, though usually happens in Red/Yellow.
                if pct_change <= -3.0:
                    results['heavy_drops'].append({
                        'symbol': symbol,
                        'price': current_price,
                        'change_pct': pct_change,
                        'color': last_row['Color']
                    })

            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
                continue
                
        return results
