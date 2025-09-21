from __future__ import annotations
from pathlib import Path
from typing import Sequence, Optional, Dict, Any
import pandas as pd
from .base import Storage


class ParquetStorage(Storage):
    """Parquet storage backend implementation."""

    def read_bars(
        self,
        root: Path,
        symbols: Sequence[str],
        start: pd.Timestamp,
        end: pd.Timestamp,
        interval: str,
        columns: Optional[Sequence[str]] = None,
    ) -> pd.DataFrame:
        """Read bars from a Parquet lake (partitioned by symbol/interval/date)."""
        raise NotImplementedError

    def write_bars(
        self, df: pd.DataFrame, root: Path, partitioning: Dict[str, Any] | None = None
    ) -> None:
        """Write bars to a Parquet lake."""
        raise NotImplementedError

    def read_trades(
        self,
        root: Path,
        symbols: Sequence[str],
        start: pd.Timestamp,
        end: pd.Timestamp,
        columns: Optional[Sequence[str]] = None,
    ) -> pd.DataFrame:
        """Read trades from a Parquet lake."""
        raise NotImplementedError

    def write_trades(
        self, df: pd.DataFrame, root: Path, partitioning: Dict[str, Any] | None = None
    ) -> None:
        """Write trades to a Parquet lake."""
        raise NotImplementedError

    def read_quotes(
        self,
        root: Path,
        symbols: Sequence[str],
        start: pd.Timestamp,
        end: pd.Timestamp,
        columns: Optional[Sequence[str]] = None,
    ) -> pd.DataFrame:
        """Read quotes from a Parquet lake."""
        raise NotImplementedError

    def write_quotes(
        self, df: pd.DataFrame, root: Path, partitioning: Dict[str, Any] | None = None
    ) -> None:
        """Write quotes to a Parquet lake."""
        raise NotImplementedError
