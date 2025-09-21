"""
Interface for persisting live portfolio state.
"""
from __future__ import annotations
from abc import ABC, abstractmethod

from qt.types import PortfolioSnapshot


class StateStore(ABC):
    """Abstract base class for a persistent portfolio state store."""

    @abstractmethod
    def save_snapshot(self, snapshot: PortfolioSnapshot) -> None:
        """Saves the current portfolio snapshot."""
        raise NotImplementedError

    @abstractmethod
    def load_latest_snapshot(self) -> PortfolioSnapshot:
        """Loads the most recent portfolio snapshot."""
        raise NotImplementedError
