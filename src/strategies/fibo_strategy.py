import pandas as pd
import numpy as np

class FiboZoneStrategy:
    def __init__(self, lookback_period=60):
        # lookback_period: timeframe to find the Swing High/Low
        self.lookback = lookback_period

    def calculate(self, df: pd.DataFrame, close_col='Close', high_col='High', low_col='Low') -> pd.DataFrame:
        """
        Calculates Fibo Retracement Zones and generates signals.
        Focus: Catching dips in an uptrend (Pullback Strategy).
        """
        if df.empty:
            return df

        # Create copies to avoid SettingWithCopy warnings
        df = df.copy()

        # 1. Identify Swing High (Rolling Max)
        # We assume the 'Trend' is the move from a recent Low to the recent High.
        # This is a simplified dynamic Fibo logic.
        
        # Current Swing High over the lookback window
        df['Swing_High'] = df[high_col].rolling(window=self.lookback).max()
        
        # Low of the lookback window (This is a simplification; ideally we find the low *preceding* the high)
        # For efficiency, we'll take the Rolling Min.
        df['Swing_Low'] = df[low_col].rolling(window=self.lookback).min()
        
        df['Range'] = df['Swing_High'] - df['Swing_Low']
        
        # Calculate Retracement Levels (from High going down)
        # Fibo 0% = High
        # Fibo 100% = Low
        # Deep Pullback Area: 50% to 78.6% Retracement
        
        # Price at 50% pullback
        df['Fibo_500'] = df['Swing_High'] - (df['Range'] * 0.5)
        
        # Price at 78.6% pullback (Golden Ratio extension for deep deeps)
        df['Fibo_786'] = df['Swing_High'] - (df['Range'] * 0.786)
        
        # Signal Logic
        # BUY (1): If Close is > Fibo_786 AND Close < Fibo_500
        # (Meaning price is inside the deep discount zone)
        # AND Price is NOT making new lows (basic filter, maybe RSI < 30 can be added later)
        
        # Let's add an RSI filter to ensure it's oversold (optional but good for specific strategy)
        # delta = df[close_col].diff()
        # gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        # loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        # rs = gain / loss
        # df['RSI'] = 100 - (100 / (1 + rs))

        conditions = [
            (df[close_col] <= df['Fibo_500']) & (df[close_col] >= df['Fibo_786'])
        ]
        
        df['In_Fibo_Zone'] = np.where(conditions[0], True, False)
        
        # Generate Signals compatible with BacktestEngine
        # 1 = Buy, -1 = Sell
        # Logic: Buy when we enter the zone? or stay in zone?
        # Let's Buy when we enter the zone.
        
        df['Action_Zone_Signal'] = 0
        
        # Buy if in Zone
        # We might want to hold until valid exit. 
        # For this test: Enter when in zone. Exit when Price > Fibo_500 (Recovery) OR Stop Loss (New Low)
        
        # To keep it simple for the engine:
        # Signal = 1 when In_Zone. 
        # Signal = -1 when Close > Fibo_500 (Profit Taking) or Close < Swing_Low (Stop Out)
        
        buy_cond = df['In_Fibo_Zone']
        sell_cond_profit = df[close_col] > df['Fibo_500'] 
        sell_cond_loss   = df[close_col] < df['Swing_Low']
        
        df.loc[buy_cond, 'Action_Zone_Signal'] = 1
        df.loc[sell_cond_profit, 'Action_Zone_Signal'] = -1 # Take profit when bounces back above 50%
        df.loc[sell_cond_loss, 'Action_Zone_Signal'] = -1   # Stop loss if breaks low
        
        return df
