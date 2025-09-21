"""
Handles loading historical data and populating the event queue.
"""
from __future__ import annotations
from typing import Dict, List, DefaultDict
from collections import defaultdict
import pandas as pd

from qt.events import BarEvent
from qt.types import Bar
from qt.utils.logger import get_logger
from .event_queue import EventQueue

logger = get_logger(__name__)


class DataHandler:
    """
    Loads a combined historical data DataFrame, pushes bundled BarEvents
    to the queue, and provides access to point-in-time historical data.
    """

    def __init__(
        self, event_queue: EventQueue, historical_data: pd.DataFrame
    ) -> None:
        """
        Initializes the DataHandler.
        """
        self.event_queue = event_queue
        self.historical_data = historical_data
        self.latest_prices: Dict[str, float] = {}
        self.current_history: DefaultDict[str, List[Bar]] = defaultdict(list)

    def update_data(self) -> None:
        """
        Groups bars by timestamp, creates a single BarEvent for each timestamp,
        and pushes them to the event queue.
        """
        logger.info("Preparing and pushing historical data...")

        if self.historical_data.empty:
            logger.warning("No historical data provided to the DataHandler.")
            return

        sorted_df = self.historical_data.sort_index()

        for timestamp, group in sorted_df.groupby(level=0):
            bars_for_timestamp: Dict[str, Bar] = {
                row.symbol: Bar(
                    ts_utc=timestamp,
                    symbol=row.symbol,
                    open=row.open,
                    high=row.high,
                    low=row.low,
                    close=row.close,
                    volume=row.volume,
                    interval=row.interval,
                    venue=row.venue,
                )
                for row in group.itertuples()
            }
            bar_event = BarEvent(timestamp=timestamp, bars=bars_for_timestamp)
            self.event_queue.put(bar_event)

            # Update history and latest prices immediately
            self._update_history(bar_event)

        logger.info(f"Successfully pushed events for {len(sorted_df.index.unique())} unique timestamps.")

    def _update_history(self, bar_event: BarEvent) -> None:
        """
        Updates the point-in-time history with the latest bar data.
        The engine will call this method after processing each BarEvent.
        """
        for symbol, bar in bar_event.bars.items():
            self.current_history[symbol].append(bar)
            self.latest_prices[symbol] = bar.close

    def get_history(self, symbol: str, lookback: int = None) -> pd.DataFrame:
        """
        Gets the recent historical data for a symbol as a DataFrame.

        Args:
            symbol: The symbol to get history for.
            lookback: The number of recent bars to return.

        Returns:
            A pandas DataFrame of the historical bars. Returns an empty
            DataFrame if insufficient history is available.
        """
        history = self.current_history.get(symbol, [])

        if lookback is None:
            lookback = len(history)

        if len(history) < lookback:
            return pd.DataFrame() # Not enough data yet

        # Get the most recent `lookback` bars
        recent_bars = history[-lookback:]
        
        # Convert list of Bar objects to a DataFrame
        df = pd.DataFrame([bar.__dict__ for bar in recent_bars])
        df.set_index("ts_utc", inplace=True)
        return df

    def get_latest_prices(self) -> Dict[str, float]:
        """
        Returns the most recent known prices for all symbols.
        """
        return self.latest_prices

