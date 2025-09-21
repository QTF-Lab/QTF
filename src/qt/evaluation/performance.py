"""
Functions for creating interactive, visual performance reports (tearsheets) using Plotly.
"""
from __future__ import annotations
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import tempfile
import os
from typing import List

from qt.backtest.metrics import generate_performance_summary
from qt.types import Fill
from qt.utils.logger import get_logger

logger = get_logger(__name__)


def _show_fig_full_screen(fig, title: str = "Backtest Report"):
    """
    Generates a full-screen HTML file for a Plotly figure with a dark theme.
    """
    html = fig.to_html(full_html=True, include_plotlyjs='cdn')
    style = f"""
    <style>
        body {{
            background-color: #111111;
            margin: 0;
            padding: 0;
        }}
        .plotly-graph-div {{
            height: 100vh !important;
        }}
    </style>
    <title>{title}</title>
    """
    html = html.replace('</head>', f'{style}</head>')

    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
        f.write(html)
        filepath = 'file://' + os.path.abspath(f.name)
    
    webbrowser.open(filepath)
    logger.info(f"Report opened in a new browser tab. Temp file: {filepath}")


def create_plotly_tearsheet(
    equity_curve: pd.Series,
    fills: List[Fill],
    historical_data: pd.DataFrame,
    strategy_name: str = "Strategy",
) -> None:
    """
    Generates and displays a comprehensive, interactive tearsheet.

    Args:
        equity_curve: A pandas Series of the portfolio's NAV over time.
        fills: A list of all Fill objects from the backtest.
        historical_data: A DataFrame containing the market data for all traded symbols.
        strategy_name: The name of the strategy for report titles.
    """
    if equity_curve.empty:
        logger.warning("Equity curve is empty, skipping tearsheet generation.")
        return

    # --- 1. Data Pre-processing ---
    # Convert equity Series to DataFrame for easier plotting
    equity_df = pd.DataFrame(equity_curve).rename(columns={'NAV': 'total'})
    
    # Convert list of Fill objects to a DataFrame
    fills_df = pd.DataFrame()
    if fills:
        fills_df = pd.DataFrame([f.__dict__ for f in fills])
        # Create a 'side' column from the signed quantity for plotting
        fills_df['side'] = np.where(fills_df['qty'] > 0, 'BUY', 'SELL')

    # --- 2. Performance Summary Plot ---
    summary = generate_performance_summary(equity_curve)
    drawdown_series = (equity_df['total'] - equity_df['total'].cummax()) / equity_df['total'].cummax()
    daily_pnl = equity_df['total'].diff() # Simple daily PnL

    fig1 = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.6, 0.2, 0.2])
    fig1.add_trace(go.Scatter(x=equity_df.index, y=equity_df['total'], name='Equity [$]', line=dict(color='cornflowerblue')), row=1, col=1)
    fig1.add_trace(go.Bar(x=daily_pnl.index, y=daily_pnl, name='Daily PnL [$]', marker_color=['red' if x < 0 else 'green' for x in daily_pnl]), row=2, col=1)
    fig1.add_trace(go.Scatter(x=drawdown_series.index, y=100 * drawdown_series, name='Drawdown [%]', fill='tozeroy', line=dict(color='crimson', width=0.5)), row=3, col=1)

    # Add metrics as an annotation
    stats_text = "<br>".join([f"<b>{key.replace('_', ' ').title()}:</b> {val:.2f}" if isinstance(val, float) else f"{key}: {val}" for key, val in summary.items()])
    fig1.add_annotation(x=0.01, y=0.99, xref="paper", yref="paper", text=stats_text, showarrow=False, align="left", bgcolor="rgba(255, 255, 255, 0.5)", font=dict(family="monospace"))
    
    fig1.update_yaxes(title_text='Equity [$]', row=1, col=1, type="log")
    fig1.update_yaxes(title_text='PnL [$]', row=2, col=1)
    fig1.update_yaxes(title_text='Drawdown [%]', row=3, col=1)
    fig1.update_layout(title_text=f'Performance Summary: {strategy_name}', template='plotly_dark')
    _show_fig_full_screen(fig1, title=f"Performance: {strategy_name}")

    # --- 3. Strategy Analysis Plot ---
    symbols_to_plot = sorted(historical_data['symbol'].unique())
    if not symbols_to_plot:
        logger.warning("No symbols found in historical data to plot.")
        return

    # Create the second figure
    num_assets = len(symbols_to_plot)
    if num_assets > 1:
        # Normalized plot for multiple assets
        fig2 = go.Figure()
        price_data_normalized = historical_data.copy()
        first_prices = price_data_normalized.groupby('symbol')['close'].transform('first')
        price_data_normalized['normalized'] = 100 * price_data_normalized['close'] / first_prices
        
        for symbol in symbols_to_plot:
            symbol_data = price_data_normalized[price_data_normalized['symbol'] == symbol]
            fig2.add_trace(go.Scatter(x=symbol_data.index, y=symbol_data['normalized'], name=symbol, legendgroup='prices'))
        
        fig2.update_yaxes(title_text="Normalized Price (Base 100)")
        fig2.update_layout(title_text=f'Strategy Analysis: Normalized Asset Performance ({strategy_name})')

    else:
        # Candlestick plot for a single asset
        symbol = symbols_to_plot[0]
        fig2 = go.Figure()
        price_data = historical_data[historical_data['symbol'] == symbol]
        fig2.add_trace(go.Candlestick(x=price_data.index, open=price_data['open'], high=price_data['high'], low=price_data['low'], close=price_data['close'], name=symbol))
        fig2.update_yaxes(title_text="Price [$]")
        fig2.update_layout(title_text=f'Strategy Analysis: Trades on {symbol} ({strategy_name})')

    # Add buy/sell markers to the second figure
    if not fills_df.empty:
        buys = fills_df[fills_df['side'] == 'BUY']
        sells = fills_df[fills_df['side'] == 'SELL']
        
        # Plot markers based on normalized or absolute price
        y_buy = buys['price']
        y_sell = sells['price']
        if num_assets > 1:
            first_prices_map = historical_data.groupby('symbol')['close'].first()
            buys['first_price'] = buys['symbol'].map(first_prices_map)
            sells['first_price'] = sells['symbol'].map(first_prices_map)
            y_buy = 100 * buys['price'] / buys['first_price']
            y_sell = 100 * sells['price'] / sells['first_price']

        fig2.add_trace(go.Scatter(x=buys['ts_utc'], y=y_buy, mode='markers', marker=dict(symbol='triangle-up', color='lime', size=12, line=dict(width=1, color='black')), name='Buy'))
        fig2.add_trace(go.Scatter(x=sells['ts_utc'], y=y_sell, mode='markers', marker=dict(symbol='triangle-down', color='red', size=12, line=dict(width=1, color='black')), name='Sell'))
        
    fig2.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False)
    _show_fig_full_screen(fig2, title=f"Analysis: {strategy_name}")

