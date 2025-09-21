# src/qt/risk/models.py
"""
Portfolio-level risk measurement models.

This module is for ongoing risk monitoring, calculating metrics like
Value-at-Risk (VaR) and Expected Shortfall (ES).
"""
from __future__ import annotations
import pandas as pd


def calculate_var(
    portfolio_returns: pd.Series, confidence_level: float = 0.95
) -> float:
    """
    Calculates the historical Value-at-Risk (VaR) of the portfolio.
    """
    raise NotImplementedError


def calculate_es(
    portfolio_returns: pd.Series, confidence_level: float = 0.95
) -> float:
    """
    Calculates the historical Expected Shortfall (ES) of the portfolio.
    """
    raise NotImplementedError