"""
A time-based priority queue for handling events in chronological order.
"""
from __future__ import annotations
import heapq
from typing import List

from qt.events import Event


class EventQueue:
    """
    A priority queue that stores and yields events in chronological order.
    """

    def __init__(self) -> None:
        self._events: List[Event] = []

    def put(self, event: Event) -> None:
        """
        Pushes a new event onto the queue.
        heapq ensures the event with the smallest timestamp is always at the front.
        """
        heapq.heappush(self._events, event)

    def get(self) -> Event:
        """
        Pops the event with the earliest timestamp from the queue.
        """
        return heapq.heappop(self._events)

    def is_empty(self) -> bool:
        """
        Checks if the queue is empty.
        """
        return len(self._events) == 0
