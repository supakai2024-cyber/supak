import pandas as pd
import numpy as np

class CDCActionZone:
    def __init__(self, slow_period=26, fast_period=12):
        self.slow_period = slow_period
        self.fast_period = fast_period

    def calculate(self, df: pd.DataFrame, close_col='Close') -> pd.DataFrame:
        """
        Calculate CDC Action Zone signals.
        
        Args:
            df (pd.DataFrame): DataFrame containing price data.
            close_col (str): The column name for closing prices.
            
        Returns:
            pd.DataFrame: DataFrame with 'Color' and 'Action_Zone_Signal' columns.
        """
        if df.empty:
            return df

        # Calculate EMAs
        df['EMA12'] = df[close_col].ewm(span=self.fast_period, adjust=False).mean()
        df['EMA26'] = df[close_col].ewm(span=self.slow_period, adjust=False).mean()

        # Define Colors/States logic
        # Green: EMA12 > EMA26 and Close > EMA12 (Strong Uptrend - Buy)
        # Blue: EMA12 > EMA26 and Close <= EMA12 (Weak Uptrend - Hold/Correction)
        # Red: EMA12 < EMA26 and Close < EMA12 (Strong Downtrend - Sell)
        # Yellow: EMA12 < EMA26 and Close >= EMA12 (Weak Downtrend - Hold/Rebound)
        
        conditions = [
            (df['EMA12'] > df['EMA26']) & (df[close_col] > df['EMA12']), # Green
            (df['EMA12'] > df['EMA26']) & (df[close_col] <= df['EMA12']),# Blue
            (df['EMA12'] < df['EMA26']) & (df[close_col] < df['EMA12']), # Red
            (df['EMA12'] < df['EMA26']) & (df[close_col] >= df['EMA12']) # Yellow
        ]
        
        choices = ['Green', 'Blue', 'Red', 'Yellow']
        
        df['Color'] = np.select(conditions, choices, default='Neutral')
        
        # Action Zone Signal: 1 (Buy/Green), -1 (Sell/Red), 0 (Neutral)
        df['Action_Zone_Signal'] = 0
        df.loc[df['Color'] == 'Green', 'Action_Zone_Signal'] = 1
        df.loc[df['Color'] == 'Red', 'Action_Zone_Signal'] = -1
        
        return df

if __name__ == "__main__":
    # Test Data
    data = {'Close': [100, 105, 110, 108, 115, 120, 118, 112, 105, 100]}
    df_test = pd.DataFrame(data)
    cdc = CDCActionZone()
    result = cdc.calculate(df_test)
    print(result[['Close', 'EMA12', 'EMA26', 'Color', 'Action_Zone_Signal']])
