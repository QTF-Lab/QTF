"""
Functions for creating visual performance reports (tearsheets).
"""
from __future__ import annotations
import pandas as pd


def create_html_tearsheet(
    equity_curve: pd.Series, trades: pd.DataFrame, output_path: str
) -> None:
    """
    Generates a standalone HTML tearsheet from backtest results.
    """
    print(f"Generating HTML tearsheet at: {output_path}")
    # This function would use a plotting library like Plotly or Matplotlib
    # and the functions from performance.py to create charts and tables.
    pass
