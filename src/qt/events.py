"""
Defines the base Event class and all specific event types used in the system.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from qt.types import Bar, Order, Fill


@dataclass(frozen=True)
class Event:
    """
    Base class for all events in the system.
    Makes events comparable based on their timestamp for the priority queue.
    """
    timestamp: datetime

    def __lt__(self, other):
        return self.timestamp < other.timestamp


@dataclass(frozen=True)
class BarEvent(Event):
    """
    Handles the event of receiving a collection of new market data bars
    for a single timestamp. This represents one "tick" of the backtest clock.
    """
    bars: Dict[str, Bar]
    event_type: str = field(default="BAR", init=False)


@dataclass(frozen=True)
class OrderEvent(Event):
    """
    Handles the event of sending a list of Orders to the execution system.
    This typically represents a single portfolio rebalancing decision.
    """
    orders: List[Order]
    event_type: str = field(default="ORDER", init=False)


@dataclass(frozen=True)
class FillEvent(Event):
    """
    Handles the event of a list of Orders being filled.
    """
    fills: List[Fill]
    event_type: str = field(default="FILL", init=False)

