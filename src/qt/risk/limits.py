# src/qt/risk/limits.py
"""
Pre-trade and post-trade risk limits.

This module provides functions to check if a proposed set of orders or a
portfolio state would violate predefined risk limits. These are the "kill
switches" and safety guardrails of the system.
"""
from __future__ import annotations
from typing import List

from qt.types import Order, PortfolioSnapshot


def check_max_position_exposure(
    orders: List[Order], portfolio: PortfolioSnapshot, max_exposure: float
) -> bool:
    """
    Checks if any single position's notional value would exceed a max limit.
    Returns True if the check passes, False otherwise.
    """
    # This is a pre-trade check.
    raise NotImplementedError


def check_max_gross_exposure(
    orders: List[Order], portfolio: PortfolioSnapshot, max_exposure: float
) -> bool:
    """
    Checks if the total gross exposure (longs + shorts) would exceed a limit.
    Returns True if the check passes, False otherwise.
    """
    # This is a pre-trade check.
    raise NotImplementedError


def check_daily_drawdown_limit(
    portfolio: PortfolioSnapshot, max_drawdown: float
) -> bool:
    """
    Checks if the portfolio's realized PnL for the day has exceeded the
    maximum allowed drawdown.
    Returns True if the check passes, False otherwise.
    """
    # This is a post-trade check.
    raise NotImplementedError