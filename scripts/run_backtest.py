"""
User-facing script to configure and run a backtest.
"""
from __future__ import annotations
import argparse
import pandas as pd

# Important: Import all strategy files so the @register_strategy decorator runs
from qt.strategies import sma_crossover
from qt.strategies.registry import get_strategy

# Import framework components
from qt.backtest.engine import BacktestEngine
from qt.backtest.data_handler import DataHandler
from qt.backtest.event_queue import EventQueue
from qt.backtest.portfolio import Portfolio
from qt.backtest.execution_sim import ExecutionSimulator
from qt.backtest.slippage import NoSlippage
from qt.backtest.costs import NoCost
from qt.evaluation.tearsheet import create_plotly_tearsheet


def main() -> None:
    """
    Parses command-line arguments to configure and run a backtest.
    """
    parser = argparse.ArgumentParser(description="Run a quantitative trading backtest.")
    parser.add_argument(
        "--strategy",
        required=True,
        type=str,
        help="The name of the strategy to run (e.g., 'sma_crossover').",
    )
    parser.add_argument(
        "--data",
        required=True,
        type=str,
        help="Path to the CSV file containing historical market data.",
    )
    args = parser.parse_args()

    # --- 1. Load Data ---
    # This is a temporary substitute for the real DataLoader (Phase 3)
    try:
        data = pd.read_csv(args.data)
        data["ts_utc"] = pd.to_datetime(data["ts_utc"], utc=True)
        data.set_index("ts_utc", inplace=True)
    except FileNotFoundError:
        print(f"Error: Data file not found at {args.data}")
        return
    
    universe = list(data["symbol"].unique())

    # --- 2. Configure Strategy ---
    try:
        strategy_params = {
            "universe": universe,
            "fast_window": 5,
            "slow_window": 10,
        }
        strategy_class = get_strategy(args.strategy)
        strategy = strategy_class(params=strategy_params)
    except KeyError:
        print(f"Error: Strategy '{args.strategy}' not found in the registry.")
        return

    # --- 3. Assemble Backtest Components ---
    event_queue = EventQueue()
    data_handler = DataHandler(event_queue=event_queue, historical_data=data)
    portfolio = Portfolio(initial_cash=100_000.0)
    execution_simulator = ExecutionSimulator(slippage_model=NoSlippage(), cost_model=NoCost())
    
    # Instantiate the engine
    engine = BacktestEngine(
        event_queue=event_queue,
        data_handler=data_handler,
        strategy=strategy,
        portfolio=portfolio,
        execution_simulator=execution_simulator,
    )

    # --- 4. Run the Backtest ---
    results = engine.run()

    # --- 5. Generate and Display Tearsheet ---
    if results:
        equity_curve = portfolio.get_equity_curve()
        # The tearsheet needs a list of all fills, which we don't store yet.
        # For now, we'll pass an empty list.
        all_fills = [] 
        create_plotly_tearsheet(
            equity_curve,
            fills=all_fills,
            historical_data=data,
            strategy_name=args.strategy
        )
    else:
        print("Backtest produced no results to display.")


if __name__ == "__main__":
    main()

