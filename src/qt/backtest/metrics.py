"""
Functions for calculating portfolio performance metrics.
"""
from __future__ import annotations
import pandas as pd
import numpy as np

from qt.utils.logger import get_logger

logger = get_logger(__name__)


def _infer_trading_periods_per_year(equity_curve: pd.Series) -> int:
    """
    Infers the number of trading periods per year from the equity curve index.
    """
    if equity_curve.empty or len(equity_curve.index) < 2:
        return 252 # Default to daily for equities

    # Calculate the median time difference between consecutive data points
    median_interval = equity_curve.index.to_series().diff().median()

    if pd.isna(median_interval):
        return 252

    # Calculate the number of such intervals in a year
    periods_per_year = pd.Timedelta(days=365.25) / median_interval

    # If the data is roughly daily, use 252 for a more standard equity calculation.
    # Otherwise, use the calculated value (for crypto, hourly, etc.)
    if 240 < periods_per_year < 270:
        return 252
    elif 350 < periods_per_year < 370:
        return 365
    
    return int(periods_per_year)


def calculate_total_return(equity_curve: pd.Series) -> float:
    """
    Calculates the total return over the entire period.
    """
    if equity_curve.empty or len(equity_curve) < 2:
        return 0.0
    start_nav = equity_curve.iloc[0]
    end_nav = equity_curve.iloc[-1]
    if start_nav == 0:
        return 0.0
    return (end_nav / start_nav) - 1


def calculate_annualized_volatility(
    equity_curve: pd.Series, trading_periods_per_year: int
) -> float:
    """
    Calculates the annualized volatility of returns.
    """
    if equity_curve.empty or len(equity_curve) < 2:
        return 0.0
    returns = equity_curve.pct_change().dropna()
    return returns.std() * np.sqrt(trading_periods_per_year)


def calculate_cagr(equity_curve: pd.Series) -> float:
    """
    Calculates the Compound Annual Growth Rate (CAGR).
    """
    if equity_curve.empty or len(equity_curve) < 2:
        return 0.0
    start_nav = equity_curve.iloc[0]
    end_nav = equity_curve.iloc[-1]
    if start_nav <= 0:
        return 0.0
    num_years = (equity_curve.index[-1] - equity_curve.index[0]).days / 365.25
    if num_years <= 0:
        return 0.0
    cagr = (end_nav / start_nav) ** (1 / num_years) - 1
    return cagr


def calculate_sharpe_ratio(
    equity_curve: pd.Series,
    risk_free_rate: float,
    trading_periods_per_year: int,
) -> float:
    """
    Calculates the annualized Sharpe Ratio.
    """
    if equity_curve.empty or len(equity_curve) < 2:
        return 0.0
    returns = equity_curve.pct_change().dropna()
    if returns.std() == 0:
        return 0.0
    
    excess_returns = returns - (risk_free_rate / trading_periods_per_year)
    sharpe_ratio = excess_returns.mean() / excess_returns.std()
    annualized_sharpe = sharpe_ratio * np.sqrt(trading_periods_per_year)
    return annualized_sharpe


def calculate_sortino_ratio(
    equity_curve: pd.Series,
    risk_free_rate: float,
    trading_periods_per_year: int,
) -> float:
    """
    Calculates the annualized Sortino Ratio.
    """
    if equity_curve.empty or len(equity_curve) < 2:
        return 0.0
    returns = equity_curve.pct_change().dropna()
    target_return = risk_free_rate / trading_periods_per_year
    
    downside_returns = returns[returns < target_return]
    downside_deviation = downside_returns.std()

    if downside_deviation == 0 or pd.isna(downside_deviation):
        return 0.0

    expected_return = returns.mean()
    sortino_ratio = (expected_return - target_return) / downside_deviation
    annualized_sortino = sortino_ratio * np.sqrt(trading_periods_per_year)
    return annualized_sortino


def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """
    Calculates the maximum drawdown from a peak.
    """
    if equity_curve.empty:
        return 0.0
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown = drawdown.min()
    return max_drawdown


def calculate_calmar_ratio(equity_curve: pd.Series) -> float:
    """
    Calculates the Calmar Ratio (CAGR / Max Drawdown).
    """
    cagr = calculate_cagr(equity_curve)
    max_dd = calculate_max_drawdown(equity_curve)
    if max_dd >= 0:
        return 0.0
    return cagr / abs(max_dd)


def generate_performance_summary(
    equity_curve: pd.Series, risk_free_rate: float = 0.0
) -> dict:
    """
    Generates a dictionary of key performance indicators.
    """
    logger.info("Generating performance summary...")
    if equity_curve.empty or len(equity_curve) < 2:
        logger.warning("Equity curve is too short to generate performance summary.")
        return {}

    # Infer the annualization factor once from the data
    periods_per_year = _infer_trading_periods_per_year(equity_curve)
    logger.info(f"Inferred {periods_per_year} trading periods per year.")

    summary = {
        "total_return": calculate_total_return(equity_curve),
        "cagr": calculate_cagr(equity_curve),
        "annualized_volatility": calculate_annualized_volatility(
            equity_curve, periods_per_year
        ),
        "sharpe_ratio": calculate_sharpe_ratio(
            equity_curve, risk_free_rate, periods_per_year
        ),
        "sortino_ratio": calculate_sortino_ratio(
            equity_curve, risk_free_rate, periods_per_year
        ),
        "calmar_ratio": calculate_calmar_ratio(equity_curve),
        "max_drawdown": calculate_max_drawdown(equity_curve),
    }
    return summary

