"""
Manages the state of the portfolio during a backtest.

This stateful class tracks cash, positions, and calculates the Net Asset Value (NAV)
at each time step. It's updated by the backtest engine whenever a fill event occurs.
"""
from __future__ import annotations
from typing import Dict, List
from datetime import datetime
import pandas as pd

from qt.types import Fill, Position, PortfolioSnapshot


class Portfolio:
    """
    A class to track portfolio state and performance through time.
    """

    def __init__(self, initial_cash: float = 1_000_000.0) -> None:
        """
        Initializes the portfolio.

        Args:
            initial_cash: The starting cash balance.
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.history: List[PortfolioSnapshot] = []

    def update_on_fill(self, fill: Fill, current_prices: Dict[str, float]) -> None:
        """
        Updates the portfolio's state after an order has been filled.
        """
        raise NotImplementedError

    def record_snapshot(self, timestamp: datetime, current_prices: Dict[str, float]) -> None:
        """
        Records the current state (NAV, cash, positions) of the portfolio.
        """
        raise NotImplementedError

    def get_equity_curve(self) -> pd.Series:
        """
        Returns the portfolio's Net Asset Value (NAV) over time.
        """
        raise NotImplementedError
