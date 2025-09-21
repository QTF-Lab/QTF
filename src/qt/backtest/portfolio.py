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
        This version correctly handles opening, increasing, reducing,
        closing, and flipping positions using a signed quantity.
        """
        for fill in fill_event.fills:
            symbol = fill.symbol
            trade_value = fill.qty * fill.price # This will be negative for buys, positive for sells

            # Update cash based on the trade
            self.cash -= trade_value
            self.cash -= fill.fee

            # --- Position Update Logic ---
            if symbol not in self.positions:
                # 1. Open a new position
                new_position = Position(symbol=symbol, qty=fill.qty, avg_price=fill.price)
                self.positions[symbol] = new_position
            else:
                # 2. Update an existing position
                existing_position = self.positions[symbol]
                
                # Check if the trade is in the same direction as the existing position
                is_same_direction = (existing_position.qty * fill.qty) > 0

                if is_same_direction:
                    # -- Increasing the position --
                    total_qty = existing_position.qty + fill.qty
                    total_value = (existing_position.avg_price * existing_position.qty) + (fill.price * fill.qty)
                    existing_position.avg_price = total_value / total_qty
                    existing_position.qty = total_qty
                else:
                    # -- Reducing, closing, or flipping the position --
                    position_direction = 1 if existing_position.qty > 0 else -1
                    
                    if abs(fill.qty) < abs(existing_position.qty):
                        # -- Partially closing the position --
                        qty_closed = abs(fill.qty)
                        pnl = position_direction * (fill.price - existing_position.avg_price) * qty_closed
                        existing_position.realized_pnl += pnl
                        existing_position.qty += fill.qty
                    else:
                        # -- Fully closing and potentially flipping the position --
                        qty_closed = abs(existing_position.qty)
                        pnl = position_direction * (fill.price - existing_position.avg_price) * qty_closed
                        existing_position.realized_pnl += pnl
                        
                        remaining_qty = fill.qty + existing_position.qty
                        
                        if remaining_qty == 0:
                            del self.positions[symbol]
                        else:
                            # Position is flipped
                            existing_position.qty = remaining_qty
                            existing_position.avg_price = fill.price
            
            side_log = "BUY" if fill.qty > 0 else "SELL"
            side_log = f"{side_log:<4}"
            qty_log = abs(fill.qty)
            logger.info(f"Processed fill: {side_log} {qty_log:<5} {fill.symbol:<5} @ ${fill.price:<8.2f} | Cash: ${self.cash:,.2f}")

    def record_snapshot(self, timestamp: datetime, latest_prices: Dict[str, float]) -> None:
        """
        Records the current state (NAV, cash, positions) of the portfolio.
        """
        market_value = 0.0
        for symbol, position in self.positions.items():
            price = latest_prices.get(symbol, position.avg_price)
            market_value += position.qty * price

        nav = self.cash + market_value

        snapshot = PortfolioSnapshot(
            ts_utc=timestamp,
            nav=nav,
            cash=self.cash,
            positions=self.positions.copy(),
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

