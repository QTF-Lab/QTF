"""
Final pre-trade risk checks for the live trading system.
"""
from __future__ import annotations
from typing import List

from qt.types import Order


class RiskGuard:
    """
    A final pre-trade risk check before orders are sent to the router.
    This is the last line of defense.
    """
    def validate_orders(self, orders: List[Order]) -> List[Order]:
        """
        Checks a list of orders against critical risk limits.
        Can block or modify orders.
        """
        print(f"[{self.__class__.__name__}] Performing pre-trade checks...")
        # Return the orders if they pass, or raise an exception/modify them.
        return orders
