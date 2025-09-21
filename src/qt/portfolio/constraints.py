# src/qt/portfolio/constraints.py
"""
Defines constraints for the portfolio optimization process.

Constraints are rules that the final portfolio weights must adhere to, such as:
- Weight limits for individual assets (e.g., max 5%)
- Sector exposure limits (e.g., max 20% in tech)
- Net/gross exposure limits
- Turnover limits
"""
from __future__ import annotations
from typing import List

from qt.types import TargetPositions


def apply_weight_constraints(
    target_weights: TargetPositions, max_weight: float, min_weight: float
) -> TargetPositions:
    """
    Clips the target weights to be within the specified min/max bounds.
    """
    raise NotImplementedError


def apply_sector_constraints(
    target_weights: TargetPositions, sector_map: dict, sector_limits: dict
) -> TargetPositions:
    """
    Adjusts weights to conform to sector exposure limits.
    """
    raise NotImplementedError