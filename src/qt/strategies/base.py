"""
Defines the abstract base class for all trading strategies.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd

from qt.types import Bar, Fill, Order, TargetPositions


class Strategy(ABC):
    """
    A strategy is responsible for generating a target portfolio allocation
    based on market data and its internal logic.
    """

    def __init__(self, params: Dict[str, Any] | None = None) -> None:
        """
        Initializes the strategy with a set of parameters.

        The `params` dictionary is expected to contain configuration for the
        strategy, including the 'universe' of symbols it should operate on.
        """
        self.params = params or {}

        self.universe: List[str] = self.params.get("universe", [])
        if not self.universe:
            raise ValueError("Strategy must be initialized with a non-empty 'universe' in its parameters.")

        self.signals: pd.DataFrame | None = None


    @abstractmethod
    def initialize(self, historical_data: Dict[str, pd.DataFrame]) -> None:
        """
        Called once at the start to pre-calculate signals.

        The `historical_data` dictionary will be pre-filtered by the engine
        to contain only the symbols defined in the strategy's universe.
        """
        raise NotImplementedError

    @abstractmethod
    def on_data(self, data_event: Bar) -> TargetPositions:
        """
        Called for each new market data event.

        The strategy should only react to events for symbols within its universe.
        """
        raise NotImplementedError

    def on_fill(self, fill_event: Fill) -> None:
        """
        Optional: Called by the engine when an order is filled.
        """
        pass

    def on_order_status(self, order: Order) -> None:
        """
        Optional: Called by the engine when an order's status changes.
        """
        pass

