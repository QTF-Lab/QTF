"""
Handles the lifecycle of orders sent to a live broker.
"""
from __future__ import annotations
from typing import List

from qt.types import Order


class OrderRouter:
    """
    Responsible for sending orders to the broker and tracking their state.
    """
    def send_orders(self, orders: List[Order]) -> None:
        """Sends a list of orders to the execution venue."""
        raise NotImplementedError
