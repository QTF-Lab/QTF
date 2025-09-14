# src/qt/strategies/sma_crossover.py
"""
A classic Simple Moving Average (SMA) Crossover strategy.
"""
from __future__ import annotations
import uuid
from typing import List, Dict, Any
import pandas as pd

# Import the core building blocks from your framework
from qt.enums import OrderType, Side
from qt.types import Bar, Order
from qt.features.engineering import calculate_sma  # Assuming this will be implemented

from .base import Strategy
from .registry import register_strategy


def _generate_order_id() -> str:
    """Generates a unique order ID."""
    return str(uuid.uuid4())


@register_strategy("sma_crossover")
class SmaCrossoverStrategy(Strategy):
    """
    Trades based on the crossover of two SMAs.
    - Enters a long position when the fast SMA crosses above the slow SMA.
    - Flattens the position when the fast SMA crosses below the slow SMA.
    """

    def __init__(self, params: Dict[str, Any] | None = None) -> None:
        """
        Initializes the strategy.
        Expected params: 'symbol', 'fast_window', 'slow_window'.
        """
        super().__init__(params)
        # --- Parameters ---
        self.symbol = self.params.get("symbol", "SPY")  # Default to SPY
        self.fast_window = self.params.get("fast_window", 20)
        self.slow_window = self.params.get("slow_window", 50)

        # --- Strategy State ---
        # Stores the pre-computed signals. This is our "lookup table".
        self.signals: pd.DataFrame | None = None
        # Tracks our current position: 0 for flat, 1 for long.
        self.current_position: int = 0

    def initialize(self, historical_data: Dict[str, pd.DataFrame]) -> None:
        """
        1.  This is where we do the heavy, vectorized calculations.
        2.  It's called only ONCE at the start of the backtest.
        """
        print(f"[{self.__class__.__name__}] Initializing and calculating signals for {self.symbol}...")

        # Get the historical data for the symbol we care about
        bars_df = historical_data[self.symbol]

        # --- Vectorized Signal Calculation ---
        # Use pandas to efficiently calculate SMAs over the entire dataset at once.
        fast_sma = calculate_sma(bars_df["close"], window=self.fast_window)
        slow_sma = calculate_sma(bars_df["close"], window=self.slow_window)

        # Create a DataFrame to hold our signals
        signals_df = pd.DataFrame(index=bars_df.index)
        signals_df["fast_sma"] = fast_sma
        signals_df["slow_sma"] = slow_sma

        # The signal is 1 if fast > slow, and 0 otherwise.
        # np.where is a fast, vectorized way to do this conditional logic.
        signals_df["signal"] = 0
        signals_df.loc[fast_sma > slow_sma, "signal"] = 1
        signals_df.loc[fast_sma <= slow_sma, "signal"] = 0 # Explicitly set exit signal

        # Store the computed signals DataFrame for later use in on_data
        self.signals = signals_df
        print(f"[{self.__class__.__name__}] Signal calculation complete.")

    def on_bar(self, data_event: Bar) -> List[Order]:
        """
        1.  This is the event-driven part of the strategy.
        2.  It's called for EVERY SINGLE BAR in the backtest, one by one.
        3.  It should be very fast and avoid heavy calculations.
        """
        orders_to_place: List[Order] = []

        # Ignore events for other symbols (if any)
        if data_event.symbol != self.symbol:
            return orders_to_place

        # Get the current timestamp from the incoming bar event
        current_timestamp = data_event.ts_utc

        try:
            # --- Fast Signal Lookup ---
            # Look up the pre-computed signal for this exact moment in time.
            # This is much faster than recalculating the SMA on every bar.
            signal_value = self.signals.loc[current_timestamp, "signal"]
        except KeyError:
            # This can happen at the start of the backtest before the SMA
            # windows are filled. We just do nothing.
            return orders_to_place

        # --- Trading Logic ---
        # 1. Bullish Crossover: Signal is 1 and we are currently flat (0).
        if signal_value == 1 and self.current_position == 0:
            print(f"{current_timestamp}: Bullish crossover detected. Placing BUY order for {self.symbol}.")
            # Create a market order to buy 100 shares
            new_order = Order(
                id=_generate_order_id(),
                ts_utc=current_timestamp,
                symbol=self.symbol,
                side=Side.BUY,
                qty=100.0,
                type=OrderType.MARKET,
            )
            orders_to_place.append(new_order)
            self.current_position = 1  # Update our state to show we are now long

        # 2. Bearish Crossover: Signal is 0 and we are currently long (1).
        elif signal_value == 0 and self.current_position == 1:
            print(f"{current_timestamp}: Bearish crossover detected. Placing SELL order for {self.symbol} to flatten position.")
            # Create a market order to sell 100 shares (to close our long)
            new_order = Order(
                id=_generate_order_id(),
                ts_utc=current_timestamp,
                symbol=self.symbol,
                side=Side.SELL,
                qty=100.0,
                type=OrderType.MARKET,
            )
            orders_to_place.append(new_order)
            self.current_position = 0  # Update our state to show we are now flat

        # Return the list of orders for the engine to execute
        return orders_to_place

    def on_fill(self, fill_event: Fill) -> None:
        """
        When the backtest engine confirms our order was filled, this is called.
        We could use it to track our position more accurately if needed.
        """
        print(
            f"Received fill confirmation: {fill_event.side} {fill_event.qty} "
            f"{fill_event.symbol} @ {fill_event.price}"
        )