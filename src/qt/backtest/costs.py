"""
Models for simulating trading costs (commissions and fees).
"""
from __future__ import annotations
from abc import ABC, abstractmethod

from qt.types import Fill


class CostModel(ABC):
    """Abstract base class for a trading cost model."""

    @abstractabstractmethod
    def calculate_fee(self, fill: Fill) -> float:
        """Calculates the fee for a given fill."""
        raise NotImplementedError


class NoCost(CostModel):
    """A simple model that assumes zero trading costs."""

    def calculate_fee(self, fill: Fill) -> float:
        """Returns a fee of 0."""
        return 0.0
