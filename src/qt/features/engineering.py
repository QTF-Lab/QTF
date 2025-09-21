"""
Reusable feature engineering functions.

This module contains a library of common, numerically-stable functions
for transforming raw market data (bars) into features that can be used
by signal-generating logic.

These functions are designed to be:
- Pure (no side effects)
- Vectorized (operate on entire pandas Series/DataFrames)
- Composable
"""
from __future__ import annotations
import pandas as pd

def calculate_sma(prices: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculates the Simple Moving Average (SMA).
    """
    if window <= 0:
        raise ValueError("Window for SMA must be positive.")
    return prices.rolling(window=window).mean()

def calculate_returns(prices: pd.Series, periods: int = 1) -> pd.Series:
    """Calculates the percentage change in price over a given period."""
    raise NotImplementedError

def calculate_rolling_volatility(prices: pd.Series, window: int = 20) -> pd.Series:
    """Calculates the rolling standard deviation of returns."""
    raise NotImplementedError

def calculate_ema(prices: pd.Series, window: int = 20) -> pd.Series:
    """Calculates the Exponential Moving Average (EMA)."""
    raise NotImplementedError
