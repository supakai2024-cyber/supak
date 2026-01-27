import pandas as pd
import numpy as np
from typing import Dict, Any

class RiskManager:
    def __init__(self, portfolio_value: float, risk_per_trade_pct: float = 1.0):
        """
        Manages Position Sizing and Risk Metrics.
        
        Args:
            portfolio_value (float): Total capital available (or Total Equity).
            risk_per_trade_pct (float): Max risk per trade as % of portfolio (e.g. 1.0 = 1%).
        """
        self.portfolio_value = portfolio_value
        self.risk_pct = risk_per_trade_pct / 100.0

    def calculate_position_size(self, entry_price: float, stop_loss_price: float) -> Dict[str, Any]:
        """
        Calculate ideal position size based on risk and stop loss distance.
        The Golden Rule: Money Risked = (Entry - StopLoss) * NumberOfShares
        
        Returns:
            Dict with 'shares', 'position_value', 'risk_amount', 'actual_risk_pct'
        """
        if entry_price <= stop_loss_price:
             # Stop loss must be below entry for long position
             # Unless we handle short, but for now we assume Long Only.
             return {
                 'shares': 0,
                 'reason': 'Stop Loss is above or equal to Entry Price (Invalid for Long)'
             }
             
        risk_per_share = entry_price - stop_loss_price
        max_risk_amount = self.portfolio_value * self.risk_pct
        
        # Calculate shares
        shares = int(max_risk_amount // risk_per_share)
        
        # Ensure we don't exceed portfolio cash (Buying Power check)
        # Though often Risk limits size before buying power does for tight stops.
        total_cost = shares * entry_price
        if total_cost > self.portfolio_value:
            # If cost exceeds cash, we are limited by Cash, not Risk.
            shares_cash_limit = int(self.portfolio_value // entry_price)
            shares = shares_cash_limit
            # In this case, our risk is actually LESS than max_risk_amount
        
        position_value = shares * entry_price
        actual_risk_dollars = shares * risk_per_share
        
        return {
            'shares': shares,
            'entry': entry_price,
            'stop_loss': stop_loss_price,
            'position_value': position_value,
            'risk_per_share': risk_per_share,
            'total_risk_dollars': actual_risk_dollars,
            'risk_pct_of_port': (actual_risk_dollars / self.portfolio_value) * 100
        }

    def assess_market_regime(self, market_data_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Simple Market Regime Filter using SMA200.
        market_data_df must contain 'Close' and sufficient history.
        """
        if market_data_df.empty or len(market_data_df) < 200:
            return {'regime': 'Unknown', 'safety_level': 'Neutral'}
            
        current_price = market_data_df['Close'].iloc[-1]
        sma200 = market_data_df['Close'].rolling(window=200).mean().iloc[-1]
        
        if current_price > sma200:
            return {
                'regime': 'Bullish',
                'description': 'Price is above 200-day SMA.',
                'safety_level': 'Safe'
            }
        else:
            return {
                'regime': 'Bearish',
                'description': 'Price is below 200-day SMA. Caution advised.',
                'safety_level': 'Caution'
            }
