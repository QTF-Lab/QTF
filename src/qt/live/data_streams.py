"""
Connectors for real-time market data feeds.
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class DataStream(ABC):
    """Abstract base class for a real-time market data stream."""

    @abstractmethod
    def connect(self) -> None:
        """Connects to the data source."""
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, symbols: list[str]) -> None:
        """Subscribes to market data for a list of symbols."""
        raise NotImplementedError
