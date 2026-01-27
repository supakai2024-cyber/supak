import yfinance as yf
import pandas as pd
from typing import Optional

class MarketData:
    """
    Handler for fetching market data using yfinance.
    """
    
    def __init__(self):
        pass

    def get_history(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical data for a given symbol.
        
        Args:
            symbol (str): The ticker symbol (e.g., 'AAPL', 'TSLA').
            period (str): The period to download (default '1y'). 
                          Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            interval (str): The interval (default '1d').
                            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                            
        Returns:
            pd.DataFrame: DataFrame containing Open, High, Low, Close, Volume.
                          Returns empty DataFrame if failed.
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                print(f"Warning: No data found for {symbol}")
                return df
                
            # Ensure standard column names and simple index
            df.reset_index(inplace=True)
            
            # yfinance returns 'Date' or 'Datetime' depending on interval
            # We want to ensure we handle it gracefully, but usually it's fine.
            
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    def get_realtime_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest price (delayed real-time).
        """
        try:
            ticker = yf.Ticker(symbol)
            # fast_info is often faster/more reliable for simple price
            return ticker.fast_info['last_price']
        except Exception as e:
            # Fallback to history
            try:
                df = self.get_history(symbol, period='1d', interval='1m')
                if not df.empty:
                    return df['Close'].iloc[-1]
            except:
                pass
            print(f"Error fetching price for {symbol}: {e}")
            return None

if __name__ == "__main__":
    # Test Code
    md = MarketData()
    symbol = "AAPL"
    print(f"Fetching data for {symbol}...")
    df = md.get_history(symbol)
    print(f"Data shape: {df.shape}")
    print(df.head())
    
    price = md.get_realtime_price(symbol)
    print(f"Current Price of {symbol}: {price}")
