"""
Command-line script to run a backtest.
"""
from __future__ import annotations
import argparse

# Import all strategy files so their decorators run and they get registered.
from qt.strategies import mr_pairs, xmom_crosssec
from qt.strategies.registry import get_strategy

# Import backtest components
from qt.backtest.engine import BacktestEngine
from qt.backtest.portfolio import Portfolio
from qt.backtest.execution_sim import ExecutionSimulator
from qt.backtest.slippage import NoSlippage
from qt.backtest.costs import NoCost

# Import other components
from qt.portfolio.optimizers import PassThroughOptimizer


def main() -> None:
    """
    Main function to parse arguments and run a backtest.
    """
    parser = argparse.ArgumentParser(description="Run a quantitative trading backtest.")
    parser.add_argument(
        "--strategy",
        required=True,
        type=str,
        help="The name of the strategy to run (e.g., 'xmom_crosssec').",
    )
    args = parser.parse_args()

    print(f"Attempting to run backtest for strategy: '{args.strategy}'")

    # 1. Load Strategy Class from the registry
    try:
        strategy_params = {"universe": ["SPY", "AGG"]} # Dummy params
        strategy_class = get_strategy(args.strategy)
        strategy = strategy_class(params=strategy_params)
    except KeyError:
        print(f"Error: Strategy '{args.strategy}' not found in the registry.")
        return

    # 2. Set up other components (with simple defaults for now)
    # In the future, this data would come from the Data Loader (Phase 3)
    historical_data = {} # Dummy data
    optimizer = PassThroughOptimizer()
    execution_simulator = ExecutionSimulator(slippage_model=NoSlippage(), cost_model=NoCost())
    portfolio = Portfolio(initial_cash=1_000_000)

    # 3. Initialize and run the backtest engine
    engine = BacktestEngine(
        strategy=strategy,
        historical_data=historical_data,
        optimizer=optimizer,
        execution_simulator=execution_simulator,
        portfolio=portfolio,
    )

    # This is the "Hello World" milestone!
    # It proves that all components can be wired together.
    results = engine.run()

    print("\n--- Performance Summary ---")
    print(results)
    print("--------------------------")


if __name__ == "__main__":
    main()
