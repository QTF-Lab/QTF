"""
Abstract base class for all broker/exchange adapters.
"""
from __future__ import annotations
from abc import ABC

from qt.live.data_streams import DataStream
from qt.live.order_router import OrderRouter


class BrokerAdapter(ABC):
    """
    An interface that combines a data stream and an order router for a specific broker.
    """
    data_stream: DataStream
    order_router: OrderRouter
