"""
Finite sets of categorical values.

Using enums avoids "stringly-typed" bugs and ensures consistency across modules.
"""

from enum import Enum


class Side(str, Enum):
    """Direction of an order or position."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Execution style for an order."""

    MARKET = "MARKET"  # Execute immediately at best price
    LIMIT = "LIMIT"  # Execute at specified price or better
    STOP = "STOP"  # Becomes market once stop price reached
    STOP_LIMIT = "STOP_LIMIT"  # Becomes limit once stop triggered


class TimeInForce(str, Enum):
    """Expiry instructions for orders."""

    DAY = "DAY"  # Expires end of day
    GTC = "GTC"  # Good 'til canceled
    IOC = "IOC"  # Immediate-or-cancel
    FOK = "FOK"  # Fill-or-kill


class Interval(str, Enum):
    """Common bar aggregation intervals."""

    I1S = "1s"
    I1M = "1m"
    I5M = "5m"
    I15M = "15m"
    I1H = "1h"
    I4H = "4h"
    I1D = "1d"


class AssetClass(str, Enum):
    """High-level asset classification."""

    EQUITY = "EQUITY"
    FUTURE = "FUTURE"
    FX = "FX"
    CRYPTO = "CRYPTO"
    OPTION = "OPTION"


class Currency(str, Enum):
    """Supported trading currencies."""

    USD = "USD"
    EUR = "EUR"
    CHF = "CHF"
    GBP = "GBP"
    JPY = "JPY"
    USDT = "USDT"


class Venue(str, Enum):
    """Exchange/broker identifiers."""

    XNAS = "XNAS"  # Nasdaq
    XNYS = "XNYS"  # NYSE
    BINANCE = "BINANCE"  # Binance exchange
    IBKR = "IBKR"  # Interactive Brokers
