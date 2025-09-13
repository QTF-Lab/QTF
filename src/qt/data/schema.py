# src/qt/data/schema.py
"""
Defines the canonical data schemas used throughout the framework.

These schemas enforce consistency at the data layer, ensuring that all data
ingested and processed conforms to a predefined structure. This prevents
downstream errors and simplifies data handling.

Each schema defines:
- Column names
- Data types (e.g., float, int, str)
- Nullability

These schemas are used by:
- Data providers to normalize data upon ingestion.
- Storage backends to define table structures.
- The data loader to validate data upon retrieval.
"""

from typing import Dict, Annotated
import pandera as pa
from pandera.dtypes import Timestamp


# Type alias for a timezone-aware timestamp for clarity and reuse.
# Annotated tells Pandera to use a Timestamp, and the "UTC" string is
# metadata that Pandera uses to set the timezone.
UTC_TIMESTAMP = Annotated[Timestamp, "UTC"]


# Defines the schema for candlestick (bar) data.
BarSchema = pa.DataFrameSchema(
    columns={
        "ts_utc": pa.Column(UTC_TIMESTAMP, nullable=False),
        "symbol": pa.Column(pa.String, nullable=False),
        "open": pa.Column(pa.Float, nullable=False),
        "high": pa.Column(pa.Float, nullable=False),
        "low": pa.Column(pa.Float, nullable=False),
        "close": pa.Column(pa.Float, nullable=False),
        "volume": pa.Column(pa.Float, nullable=False),
        "interval": pa.Column(pa.String, nullable=False),
        "venue": pa.Column(pa.String, nullable=False),
        "currency": pa.Column(pa.String, nullable=True),
        "adj_close": pa.Column(pa.Float, nullable=True),
        "source": pa.Column(pa.String, nullable=True),
    },
    strict=True,
    coerce=True,
)

# Defines the schema for individual trade (tick) data.
TradeSchema = pa.DataFrameSchema(
    columns={
        "ts_utc": pa.Column(UTC_TIMESTAMP, nullable=False),
        "symbol": pa.Column(pa.String, nullable=False),
        "price": pa.Column(pa.Float, nullable=False),
        "size": pa.Column(pa.Float, nullable=False),
        "venue": pa.Column(pa.String, nullable=False),
        "trade_id": pa.Column(pa.String, nullable=True),
    },
    strict=True,
    coerce=True,
)

# Defines the schema for top-of-book quote data.
QuoteSchema = pa.DataFrameSchema(
    columns={
        "ts_utc": pa.Column(UTC_TIMESTAMP, nullable=False),
        "symbol": pa.Column(pa.String, nullable=False),
        "bid_px": pa.Column(pa.Float, nullable=False),
        "bid_sz": pa.Column(pa.Float, nullable=False),
        "ask_px": pa.Column(pa.Float, nullable=False),
        "ask_sz": pa.Column(pa.Float, nullable=False),
        "venue": pa.Column(pa.String, nullable=False),
    },
    strict=True,
    coerce=True,
)

# Defines the schema for reference data (e.g., asset metadata).
ReferenceDataSchema = pa.DataFrameSchema(
    columns={
        "symbol": pa.Column(pa.String, nullable=False),
        "asset_class": pa.Column(pa.String, nullable=False),
        "currency": pa.Column(pa.String, nullable=False),
        "exchange": pa.Column(pa.String, nullable=False),
        "description": pa.Column(pa.String, nullable=True),
        "first_traded": pa.Column(UTC_TIMESTAMP, nullable=True),
        "last_traded": pa.Column(UTC_TIMESTAMP, nullable=True),
    },
    strict=True,
    coerce=True,
    unique=["symbol"],
)

# A registry to easily access schemas by name.
SCHEMA_REGISTRY: Dict[str, pa.DataFrameSchema] = {
    "bars": BarSchema,
    "trades": TradeSchema,
    "quotes": QuoteSchema,
    "refdata": ReferenceDataSchema,
}
