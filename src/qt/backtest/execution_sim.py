"""
Simulates the execution of orders.

This module takes orders from the engine and, based on the market data and
configured slippage/cost models, generates Fill events. This version is
stateful to handle open LIMIT orders.
"""
from __future__ import annotations
from typing import List, Dict

from qt.events import OrderEvent, FillEvent, BarEvent
from qt.types import Order, Bar, Fill
from qt.enums import OrderType
from qt.utils.logger import get_logger
from .slippage import SlippageModel
from .costs import CostModel

logger = get_logger(__name__)


class ExecutionSimulator:
    """
    Simulates the process of order execution at a brokerage or exchange.
    This stateful version handles both MARKET and LIMIT orders.
    """

    def __init__(self, slippage_model: SlippageModel, cost_model: CostModel) -> None:
        self.slippage_model = slippage_model
        self.cost_model = cost_model
        # This "order book" is the key to handling limit orders.
        self.open_limit_orders: Dict[str, Order] = {}

    def process_new_orders(self, order_event: OrderEvent, market_data: Dict[str, Bar]) -> FillEvent | None:
        """
        Processes a list of newly-created orders. Market orders are filled
        immediately, while limit orders are placed on the open orders book.
        """
        fills: List[Fill] = []
        for order in order_event.orders:
            if order.type == OrderType.MARKET:
                fill = self._fill_market_order(order, market_data)
                if fill:
                    fills.append(fill)
            elif order.type == OrderType.LIMIT:
                logger.info(f"Placing LIMIT order {order.id} on the book for {order.symbol}.")
                self.open_limit_orders[order.id] = order
        
        if not fills:
            return None
        return FillEvent(timestamp=order_event.timestamp, fills=fills)

    def check_open_orders(self, bar_event: BarEvent) -> FillEvent | None:
        """
        Checks all open limit orders against the latest market data to see
        if any should be filled. Called by the engine on every BarEvent.
        """
        fills: List[Fill] = []
        filled_order_ids: List[str] = []

        for order_id, order in self.open_limit_orders.items():
            if order.symbol not in bar_event.bars:
                continue

            bar = bar_event.bars[order.symbol]
            
            # Check for fill condition
            should_fill = False
            if order.side == "BUY" and bar.low <= order.limit_price:
                should_fill = True
            elif order.side == "SELL" and bar.high >= order.limit_price:
                should_fill = True

            if should_fill:
                # In a simple model, we fill at the limit price
                execution_price = order.limit_price
                
                # Create a temporary fill to calculate cost
                signed_qty = order.qty if order.side == "BUY" else -order.qty
                temp_fill = Fill(
                    order_id=order.id, ts_utc=bar.ts_utc, symbol=order.symbol,
                    qty=signed_qty, price=execution_price
                )
                fee = self.cost_model.calculate_fee(temp_fill)
                
                # Create the final fill with the fee
                final_fill = Fill(
                    order_id=order.id, ts_utc=bar.ts_utc, symbol=order.symbol,
                    qty=signed_qty, price=execution_price, fee=fee
                )
                
                fills.append(final_fill)
                filled_order_ids.append(order_id)
                logger.info(f"LIMIT order {order.id} filled: {order.side} {order.qty} {order.symbol} @ ${execution_price:.2f}")

        # Remove the filled orders from the open book
        for order_id in filled_order_ids:
            del self.open_limit_orders[order_id]

        if not fills:
            return None
        return FillEvent(timestamp=bar_event.timestamp, fills=fills)

    def _fill_market_order(self, order: Order, market_data: Dict[str, Bar]) -> Fill | None:
        """Helper function to process a single market order."""
        if order.symbol not in market_data:
            logger.warning(f"No market data for {order.symbol} at {order.ts_utc}. Cannot execute order.")
            return None

        bar = market_data[order.symbol]
        execution_price = self.slippage_model.get_execution_price(order, bar)
        signed_qty = order.qty if order.side == "BUY" else -order.qty
        
        # Create a temporary fill to calculate the fee
        temp_fill = Fill(
            order_id=order.id, ts_utc=order.ts_utc, symbol=order.symbol,
            qty=signed_qty, price=execution_price
        )
        fee = self.cost_model.calculate_fee(temp_fill)

        # Create the final fill with the fee included
        final_fill = Fill(
            order_id=order.id, ts_utc=order.ts_utc, symbol=order.symbol,
            qty=signed_qty, price=execution_price, fee=fee
        )

        logger.info(f"Simulated fill for order {order.id}: {order.side} {order.qty} {order.symbol} @ ${execution_price:.2f}")
        return final_fill

