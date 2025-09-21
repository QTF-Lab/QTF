"""
The core backtesting engine, driven by an event queue.
"""
from __future__ import annotations
from typing import Dict, List
from datetime import datetime, timezone
import uuid

from qt.events import BarEvent, OrderEvent, FillEvent
from qt.types import Order, TargetPositions
from qt.enums import OrderType
from qt.strategies.base import Strategy
from qt.utils.logger import get_logger
from .event_queue import EventQueue
from .data_handler import DataHandler
from .portfolio import Portfolio
from .execution_sim import ExecutionSimulator
from .metrics import generate_performance_summary

logger = get_logger(__name__)


class BacktestEngine:
    """
    The main engine for running a historical backtest, driven by an EventQueue.
    """

    def __init__(
        self,
        event_queue: EventQueue,
        data_handler: DataHandler,
        strategy: Strategy,
        portfolio: Portfolio,
        execution_simulator: ExecutionSimulator,
    ) -> None:
        """Initializes the backtesting engine with all its components."""
        self.event_queue = event_queue
        self.data_handler = data_handler
        self.strategy = strategy
        self.portfolio = portfolio
        self.execution_simulator = execution_simulator
        self.latest_market_data: Dict[str, BarEvent] = {}

    def run(self) -> dict:
        """
        Runs the backtest event loop.
        """
        logger.info("--- Starting Backtest ---")

        logger.info("Initializing strategy with historical data...")
        self.strategy.initialize(self.data_handler.historical_data)
        logger.info("Strategy initialized.")

        # 1. Populate the event queue with market data
        self.data_handler.update_data()

        # 2. Main Event Loop
        while not self.event_queue.is_empty():
            event = self.event_queue.get()
            
            # --- Event Routing ---
            if isinstance(event, BarEvent):
                self._handle_bar_event(event)
            elif isinstance(event, OrderEvent):
                self._handle_order_event(event)
            elif isinstance(event, FillEvent):
                self._handle_fill_event(event)

        logger.info("--- Backtest Finished ---")

        # 3. Generate final performance summary
        equity_curve = self.portfolio.get_equity_curve()
        return generate_performance_summary(equity_curve)

    def _handle_bar_event(self, event: BarEvent) -> None:
        """
        Handles a BarEvent, which is the main heartbeat of the simulation.
        """
        # Update the latest prices and history in the data handler
        self.latest_market_data = event.bars
        
        # Record a snapshot of the portfolio's value at this timestamp
        self.portfolio.record_snapshot(event.timestamp, self.data_handler.get_latest_prices())
        
        # Check for any open limit orders that might be filled by this new bar
        fill_event_from_limit = self.execution_simulator.check_open_orders(event)
        if fill_event_from_limit:
            self.event_queue.put(fill_event_from_limit)
        
        # Give the new bar to the strategy to get its desired positions
        target_positions = self.strategy.on_data(event)
        
        # If the strategy emits new targets, generate orders
        if target_positions:
            orders = self._generate_orders_from_targets(target_positions, event.timestamp)
            if orders:
                order_event = OrderEvent(timestamp=event.timestamp, orders=orders)
                self.event_queue.put(order_event)

    def _handle_order_event(self, event: OrderEvent) -> None:
        """
        Handles an OrderEvent by passing it to the execution simulator.
        """
        fill_event = self.execution_simulator.process_new_orders(event, self.latest_market_data)
        if fill_event:
            self.event_queue.put(fill_event)

    def _handle_fill_event(self, event: FillEvent) -> None:
        """
        Handles a FillEvent by updating the portfolio's state.
        """
        self.portfolio.update_on_fill(event)

    def _generate_orders_from_targets(self, targets: TargetPositions, timestamp: datetime) -> List[Order]:
        """
        A simplified order generator that bypasses the full portfolio construction
        and risk management layers for now. It converts target positions directly
        into market orders.
        """
        orders: List[Order] = []
        
        # For now, we assume a simple logic: if target is not zero and we have no position, buy/sell.
        # A real implementation would live in Phase 8 (Risk/Sizing).
        for symbol, target_weight in targets.items():
            current_position = self.portfolio.positions.get(symbol, None)
            current_qty = current_position.qty if current_position else 0
            
            # Simple logic: Go long if target > 0 and we are flat.
            if target_weight > 0 and current_qty == 0:
                # This is a placeholder for real sizing logic
                orders.append(Order(id=str(uuid.uuid4()), ts_utc=timestamp, symbol=symbol, side="BUY", qty=100, type=OrderType.MARKET))
            
            # Simple logic: Go flat if target is 0 and we are long.
            elif target_weight == 0 and current_qty > 0:
                 orders.append(Order(id=str(uuid.uuid4()), ts_utc=timestamp, symbol=symbol, side="SELL", qty=current_qty, type=OrderType.MARKET))
        
        return orders

