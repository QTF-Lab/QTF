# src/qt/features/signals/microstructure.py
"""Signals derived from high-frequency trade and quote data."""
from __future_ import annotations
import pandas as pd

def calculate_bid_ask_spread(quotes: pd.DataFrame) -> pd.Series:
    """Calculates the bid-ask spread from quote data."""
    raise NotImplementedError