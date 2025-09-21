# src/qt/features/signals/mean_reversion.py
"""Mean-reversion signal functions."""
from __future__ import annotations
import pandas as pd

def calculate_zscore(prices: pd.Series, window: int = 20) -> pd.Series:
    """Calculates the rolling z-score of a price series."""
    raise NotImplementedError

def calculate_bollinger_bands(
    prices: pd.Series, window: int = 20, num_std: float = 2.0
) -> pd.DataFrame:
    """Calculates the upper, middle, and lower Bollinger Bands."""
    raise NotImplementedError