# src/qt/portfolio/optimizers.py
"""
Portfolio optimizers that convert target weights into final, optimized weights.
"""
from __future__ import annotations
from abc import ABC, abstractmethod

from qt.types import TargetPositions
from .risk_models import RiskModel


class Optimizer(ABC):
    """Abstract base class for a portfolio optimizer."""

    @abstractmethod
    def optimize(
        self,
        raw_weights: TargetPositions,
        risk_model: RiskModel,
        constraints: list | None = None,
    ) -> TargetPositions:
        """
        Takes raw target weights from a strategy and returns optimized weights.

        Args:
            raw_weights: The strategy's desired portfolio weights.
            risk_model: A risk model instance for covariance data.
            constraints: A list of constraints to apply during optimization.

        Returns:
            The final, optimized target portfolio weights.
        """
        raise NotImplementedError


class PassThroughOptimizer(Optimizer):
    """
    A simple optimizer that does not perform any optimization.
    It simply returns the raw weights provided by the strategy.
    This is useful for strategies that generate their own final weights.
    """

    def optimize(
        self,
        raw_weights: TargetPositions,
        risk_model: RiskModel | None = None,
        constraints: list | None = None,
    ) -> TargetPositions:
        """Simply returns the raw weights, ignoring other arguments."""
        print(f"[{self.__class__.__name__}] Passing through raw weights.")
        return raw_weights