"""
Simulates the execution of orders.

This module takes orders from the engine and, based on the market data and
configured slippage/cost models, generates Fill events.
"""
from __future__ import annotations
from typing import List, Dict

from qt.types import Order, Bar, Fill
from .slippage import SlippageModel
from .costs import CostModel


class ExecutionSimulator:
    """
    Simulates the process of order execution at a brokerage or exchange.
    """

    def __init__(self, slippage_model: SlippageModel, cost_model: CostModel) -> None:
        self.slippage_model = slippage_model
        self.cost_model = cost_model

    def process_orders(
        self, orders: List[Order], market_data: Dict[str, Bar]
    ) -> List[Fill]:
        """
        Processes a list of orders and returns a list of resulting fills.

        Args:
            orders: The list of orders to be executed.
            market_data: A dictionary mapping symbols to their most recent Bar.

        Returns:
            A list of Fill events.
        """
        raise NotImplementedError
