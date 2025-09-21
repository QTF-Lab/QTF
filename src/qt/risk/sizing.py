# src/qt/risk/sizing.py
"""
Position sizing and order generation logic.

This module is responsible for the final step of converting a target portfolio
(in weights) into a set of concrete trade orders (in quantities).
"""
from __future__ import annotations
from typing import List, Dict

from qt.types import Order, TargetPositions, PortfolioSnapshot


def calculate_target_quantities(
    target_weights: TargetPositions,
    portfolio_snapshot: PortfolioSnapshot,
    market_prices: Dict[str, float],
) -> Dict[str, float]:
    """
    Converts target portfolio weights into target quantities (e.g., number of shares).

    Args:
        target_weights: The desired portfolio weights from the optimizer.
        portfolio_snapshot: The current state of the portfolio (NAV, cash, positions).
        market_prices: A dictionary mapping symbols to their current market price.

    Returns:
        A dictionary mapping symbols to their target quantity.
    """
    raise NotImplementedError


def generate_orders(
    current_positions: Dict[str, float],
    target_quantities: Dict[str, float],
) -> List[Order]:
    """
    Compares current positions to target quantities and generates the necessary orders.

    This function calculates the delta between the desired and current state
    and creates BUY or SELL orders to reconcile the difference.

    Args:
        current_positions: A dict of symbol -> current quantity held.
        target_quantities: A dict of symbol -> target quantity to hold.

    Returns:
        A list of Order objects to be sent for execution.
    """
    raise NotImplementedError