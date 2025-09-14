# src/qt/features/signals/momentum.py
"""Momentum-based signal functions."""
from __future__ import annotations
import pandas as pd

def calculate_roc(prices: pd.Series, window: int = 10) -> pd.Series:
    """Calculates the Rate of Change (ROC)."""
    raise NotImplementedError

def calculate_price_vs_sma(prices: pd.Series, window: int = 50) -> pd.Series:
    """Calculates the ratio of price to its Simple Moving Average."""
    raise NotImplementedError