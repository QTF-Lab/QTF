# src/qt/portfolio/allocators.py
"""
Logic for allocating capital across multiple strategies or alphas.
"""
from __future__ import annotations
from typing import List, Dict

from qt.types import TargetPositions


def equal_weight_allocator(
    strategy_weights: List[TargetPositions],
) -> TargetPositions:
    """
    Combines target portfolios from multiple strategies by averaging them.
    """
    raise NotImplementedError


def static_weight_allocator(
    strategy_weights: List[TargetPositions],
    allocations: Dict[str, float],
) -> TargetPositions:
    """
    Combines target portfolios using a fixed allocation for each strategy.
    """
    raise NotImplementedError