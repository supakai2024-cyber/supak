import pandas as pd
from src.data.market_data import MarketData

class BacktestEngine:
    def __init__(self, initial_capital=10000.0):
        self.market_data = MarketData()
        self.initial_capital = initial_capital

    def run(self, symbol: str, strategy, period="1y"):
        print(f"--- Starting Backtest for {symbol} ---")
        
        # 1. Get Data
        # Ensure we are passing the column CDC needs. MarketData returns 'Close'.
        df = self.market_data.get_history(symbol, period=period)
        if df.empty:
            print("No data found.")
            return None, None
        
        # 2. Apply Strategy
        # Strategy MUST have a calculate(df) method that returns df with signals
        df = strategy.calculate(df)
        
        if 'Action_Zone_Signal' not in df.columns:
            print("Strategy did not generate 'Action_Zone_Signal' column.")
            return None, None

        # 3. Simulate Trades
        # Signal: 1 (Buy/Hold), -1 (Sell), 0 (Neutral)
        
        trades = []
        position = 0 # 0: None, 1: Long
        capital = self.initial_capital
        shares = 0
        
        # Simplified Logic:
        # Buy when Signal turns 1 (Green) from non-1 (or just check state if we want to valid always being in market)
        # CDC typically: Green = Buy/Hold, Red = Sell/Stay Out.
        # So we enter if Green AND position=0. We exit if Red AND position=1.
        
        for index, row in df.iterrows():
            current_signal = row['Action_Zone_Signal']
            price = row['Close']
            # Date might be in index or column depending on reset_index in market_data
            date = row['Date'] if 'Date' in row else index
            
            if position == 0:
                if current_signal == 1:
                    # BUY SIGNAL
                    position = 1
                    shares = capital / price
                    trades.append({
                        'Date': date,
                        'Type': 'BUY',
                        'Price': price,
                        'Shares': shares,
                        'Value': capital,
                        'PnL': 0.0
                    })
            elif position == 1:
                # Check for Exit
                if current_signal == -1:
                    # SELL SIGNAL
                    position = 0
                    new_capital = shares * price
                    pnl = new_capital - capital
                    capital = new_capital
                    
                    trades.append({
                        'Date': date,
                        'Type': 'SELL',
                        'Price': price,
                        'Shares': shares,
                        'Value': capital,
                        'PnL': pnl
                    })
                    shares = 0
        
        # Calculate final portfolio value
        final_value = capital
        if position == 1:
            current_price = df.iloc[-1]['Close']
            final_value = shares * current_price
            
        print(f"Initial Capital: {self.initial_capital:,.2f}")
        print(f"Final Value: {final_value:,.2f}")
        print(f"Return: {((final_value - self.initial_capital) / self.initial_capital) * 100:.2f}%")
        print(f"Total Trades: {len(trades)}")
        
        return pd.DataFrame(trades), df
