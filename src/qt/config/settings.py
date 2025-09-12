"""
Centralized project configuration.

This file defines the shape of configuration that the framework expects.
At this stage it is a static dataclass with safe defaults.
Later phases will add loading from YAML and environment variables.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class DataSettings:
    """Configuration for data sources and storage."""

    lake_root: str = "/mnt/data/lake"
    default_storage: str = "parquet"
    provider: str | None = None


@dataclass(frozen=True)
class AdjustmentsSettings:
    """Controls how price series are adjusted."""

    mode: str = "close"  # none|close|ohlc


@dataclass(frozen=True)
class CalendarSettings:
    """Trading calendar settings."""

    default: str = "XNAS"  # Default calendar (XNAS = Nasdaq, 24x7 = crypto)


@dataclass(frozen=True)
class Settings:
    """Global configuration bundle."""

    data: DataSettings = DataSettings()
    adjustments: AdjustmentsSettings = AdjustmentsSettings()
    calendar: CalendarSettings = CalendarSettings()


# Global placeholder instance (to be replaced by loader later).
settings = Settings()
