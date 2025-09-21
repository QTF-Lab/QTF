"""
A classic Simple Moving Average (SMA) Crossover strategy.
"""
from __future__ import annotations
from typing import Dict, Any
import pandas as pd
import numpy as np

from qt.events import BarEvent
from qt.types import TargetPositions
from qt.features.engineering import calculate_sma
from qt.utils.logger import get_logger
from .base import Strategy
from .registry import register_strategy

logger = get_logger(__name__)

@register_strategy("sma_crossover")
class SmaCrossoverStrategy(Strategy):
    """
    Trades based on the crossover of two SMAs.
    - Signals a long position (weight=1.0) when the fast SMA crosses above the slow SMA.
    - Signals a flat position (weight=0.0) when the fast SMA crosses below.
    """

    def __init__(self, params: Dict[str, Any] | None = None) -> None:
        """
        Initializes the strategy.
        Expected params: 'universe', 'fast_window', 'slow_window'.
        """
        super().__init__(params)
        self.fast_window = self.params.get("fast_window", 20)
        self.slow_window = self.params.get("slow_window", 50)
        # This is a single-asset strategy, so it operates on the first symbol in its universe
        self.traded_symbol = self.universe[0]

        if self.fast_window >= self.slow_window:
            raise ValueError("Fast window must be smaller than slow window.")

    def initialize(self, historical_data: pd.DataFrame) -> None:
        """
        Pre-calculates the moving averages and the trading signal.
        The strategy is responsible for filtering the data for the symbol it needs.
        """
        logger.info(f"[{self.__class__.__name__}] Calculating signals for {self.traded_symbol}...")

        # Filter the main DataFrame to get the data for the symbol we care about
        bars_df = historical_data[historical_data["symbol"] == self.traded_symbol]
        
        fast_sma = calculate_sma(bars_df["close"], window=self.fast_window)
        slow_sma = calculate_sma(bars_df["close"], window=self.slow_window)

        signals_df = pd.DataFrame(index=bars_df.index)
        signals_df["signal"] = np.where(fast_sma > slow_sma, 1, 0)
        signals_df["signal"] = signals_df["signal"].diff()
        
        self.signals = signals_df
        logger.info("Signal calculation complete.")

    def on_data(self, bar_event: BarEvent) -> TargetPositions:
        """
        This is the event-driven part. It looks up the pre-computed signal
        for the current timestamp and emits a target position.
        """
        targets: TargetPositions = {}
        
        if self.traded_symbol not in bar_event.bars:
            return targets

        current_timestamp = bar_event.timestamp
        
        try:
            signal_change = self.signals.loc[current_timestamp, "signal"]
        except (KeyError, IndexError):
            return targets

        if pd.isna(signal_change):
            return targets

        if signal_change > 0:
            logger.info(f"{current_timestamp} | Bullish crossover detected for {self.traded_symbol}. Target: 100%")
            targets[self.traded_symbol] = 1.0
        elif signal_change < 0:
            logger.info(f"{current_timestamp} | Bearish crossover detected for {self.traded_symbol}. Target: 0%")
            targets[self.traded_symbol] = 0.0

        return targets

