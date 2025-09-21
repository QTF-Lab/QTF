# src/qt/portfolio/rebalancing.py
"""
Logic for determining when the portfolio should be rebalanced.
"""
from __future__ import annotations
import pandas as pd

from qt.types import PortfolioSnapshot, TargetPositions


def should_rebalance_on_schedule(
    current_time: pd.Timestamp, schedule: str = "monthly"
) -> bool:
    """
    Returns True if the current time is on a rebalancing date based on a
    fixed schedule (e.g., 'daily', 'weekly', 'monthly').
    """
    raise NotImplementedError


def should_rebalance_on_drift(
    current_portfolio: PortfolioSnapshot,
    target_portfolio: TargetPositions,
    drift_threshold: float,
) -> bool:
    """
    Returns True if the current portfolio's weights have drifted from the
    target weights by more than a specified threshold.
    """
    raise NotImplementedError