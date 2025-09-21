"""
Models for simulating slippage in trade execution.

Slippage is the difference between the expected price of a trade and the price
at which the trade is actually executed.
"""
from __future__ import annotations
from abc import ABC, abstractmethod

from qt.types import Order, Bar


class SlippageModel(ABC):
    """Abstract base class for a slippage model."""

    @abstractmethod
    def get_execution_price(self, order: Order, bar: Bar) -> float:
        """
        Calculates the execution price for an order, including slippage.
        """
        raise NotImplementedError


class NoSlippage(SlippageModel):
    """A simple model that assumes no slippage (ideal execution)."""

    def get_execution_price(self, order: Order, bar: Bar) -> float:
        """Assumes the execution price is the closing price of the bar."""
        return bar.close
