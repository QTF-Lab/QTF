"""
Manages the state of the portfolio during a backtest.

This stateful class tracks cash, positions, and calculates the Net Asset Value (NAV)
at each time step. It's updated by the backtest engine whenever a fill event occurs.
"""
from __future__ import annotations
from typing import Dict, List
from datetime import datetime
import pandas as pd

from qt.events import FillEvent
from qt.types import Position, PortfolioSnapshot
from qt.utils.logger import get_logger

logger = get_logger(__name__)


class Portfolio:
    """
    A class to track portfolio state and performance through time.
    """

    def __init__(self, initial_cash: float = 1_000_000.0) -> None:
        """
        Initializes the portfolio.

        Args:
            initial_cash: The starting cash balance.
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.history: List[PortfolioSnapshot] = []
        logger.info(f"Portfolio initialized with cash: ${initial_cash:,.2f}")

    def update_on_fill(self, fill_event: FillEvent) -> None:
        """
        Updates the portfolio's state after an order has been filled.
        """
        for fill in fill_event.fills:
            symbol = fill.symbol
            
            # Calculate the cost of the trade
            trade_cost = fill.qty * fill.price
            
            # Update cash
            if fill.side == "BUY":
                self.cash -= trade_cost
            else: # SELL
                self.cash += trade_cost
            
            # Apply fees
            self.cash -= fill.fee

            # Update or create the position
            if symbol not in self.positions:
                # Open a new position
                new_position = Position(
                    symbol=symbol,
                    qty=fill.qty,
                    avg_price=fill.price,
                )
                self.positions[symbol] = new_position
            else:
                # Update an existing position
                existing_position = self.positions[symbol]
                
                # Update average price if it's a buy into an existing long, or a sell into a short
                # This is a simplification; a real implementation would handle more complex cases
                if (existing_position.qty > 0 and fill.side == "BUY") or \
                   (existing_position.qty < 0 and fill.side == "SELL"):
                    total_qty = existing_position.qty + fill.qty
                    total_cost = (existing_position.avg_price * existing_position.qty) + trade_cost
                    existing_position.avg_price = total_cost / total_qty
                
                existing_position.qty += fill.qty

            # If a position's quantity is now zero, remove it
            if self.positions[symbol].qty == 0:
                del self.positions[symbol]
                
            logger.info(f"Processed fill: {fill.side} {fill.qty} {fill.symbol} @ ${fill.price:.2f}")

    def record_snapshot(self, timestamp: datetime, latest_prices: Dict[str, float]) -> None:
        """
        Records the current state (NAV, cash, positions) of the portfolio.
        """
        # 1. Calculate the market value of all current positions
        market_value = 0.0
        for symbol, position in self.positions.items():
            price = latest_prices.get(symbol, position.avg_price) # Use last known price if no update
            market_value += position.qty * price

        # 2. Calculate Net Asset Value (NAV)
        nav = self.cash + market_value

        # 3. Create and store the snapshot
        snapshot = PortfolioSnapshot(
            ts_utc=timestamp,
            nav=nav,
            cash=self.cash,
            positions=self.positions.copy(), # Important to copy
        )
        self.history.append(snapshot)

    def get_equity_curve(self) -> pd.Series:
        """
        Returns the portfolio's Net Asset Value (NAV) over time as a pandas Series.
        """
        if not self.history:
            return pd.Series(dtype=float)

        timestamps = [s.ts_utc for s in self.history]
        navs = [s.nav for s in self.history]
        
        equity_curve = pd.Series(data=navs, index=timestamps, name="NAV")
        return equity_curve

