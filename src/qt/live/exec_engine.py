"""
The core live trading engine.
"""
from __future__ import annotations


class LiveTradingEngine:
    """
    The main engine for running a strategy in a live market.
    Its event loop is driven by real-time market data.
    """

    def run(self) -> None:
        """
        Connects to data streams and starts the live trading event loop.
        """
        print(f"[{self.__class__.__name__}] Starting live trading engine...")
        # This would connect to data_streams, listen for events, and drive
        # the same strategy -> portfolio -> risk -> order pipeline as the backtester.
        raise NotImplementedError
