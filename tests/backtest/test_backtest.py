"""
Integration test for the full backtesting engine pipeline.
"""
from typing import Dict, List
import pandas as pd
import pytest
from datetime import datetime, timezone

# Import all framework components
from qt.backtest.engine import BacktestEngine
from qt.backtest.data_handler import DataHandler
from qt.backtest.event_queue import EventQueue
from qt.backtest.portfolio import Portfolio
from qt.backtest.execution_sim import ExecutionSimulator
from qt.backtest.slippage import NoSlippage
from qt.backtest.costs import NoCost
from qt.events import BarEvent
from qt.strategies.base import Strategy
from qt.types import TargetPositions

# --- Test Fixtures and Mocks ---

@pytest.fixture
def sample_backtest_data() -> pd.DataFrame:
    """
    Creates a simple, predictable DataFrame for an end-to-end test.
    Data for one symbol ('TEST') over three days.
    """
    data = [
        ("2025-01-01 10:00:00", "TEST", 100, 103, 99, 102, 1e6, "1d", "XNYS"), # Buy day
        ("2025-01-02 10:00:00", "TEST", 102, 104, 101, 103, 1e6, "1d", "XNYS"), # Hold day
        ("2025-01-03 10:00:00", "TEST", 103, 106, 102, 105, 1e6, "1d", "XNYS"), # Sell day
    ]
    columns = ["ts_utc", "symbol", "open", "high", "low", "close", "volume", "interval", "venue"]
    
    df = pd.DataFrame(data, columns=columns)
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
    df.set_index("ts_utc", inplace=True)
    
    return df


class BuyAndHoldStrategy(Strategy):
    """
    A simple test strategy that buys on the first day and sells on the last.
    """
    def __init__(self, params: Dict[str, any]):
        super().__init__(params)
        self.first_event = True
        self.last_event_timestamp = params.get("last_event_timestamp")

    def initialize(self, historical_data: Dict[str, pd.DataFrame]) -> None:
        # No pre-computation needed for this simple strategy
        pass

    def on_data(self, bar_event: BarEvent) -> TargetPositions:
        """
        Generates target positions based on the event.
        """
        targets: TargetPositions = {}
        # On the first event, signal to go 100% long
        if self.first_event:
            targets[self.universe[0]] = 1.0
            self.first_event = False
        
        # On the last event, signal to go flat
        if bar_event.timestamp == self.last_event_timestamp:
            targets[self.universe[0]] = 0.0

        return targets


# --- The Integration Test ---

def test_full_backtest_run(sample_backtest_data: pd.DataFrame):
    """
    Tests the entire backtesting pipeline from data to final P&L.
    """
    # 1. Setup all components
    event_queue = EventQueue()
    data_handler = DataHandler(event_queue=event_queue, historical_data=sample_backtest_data)
    portfolio = Portfolio(initial_cash=100_000.0)
    execution_simulator = ExecutionSimulator(slippage_model=NoSlippage(), cost_model=NoCost())
    
    # Configure the strategy
    strategy_params = {
        "universe": ["TEST"],
        "last_event_timestamp": sample_backtest_data.index[-1]
    }
    strategy = BuyAndHoldStrategy(params=strategy_params)
    
    # Instantiate the engine
    engine = BacktestEngine(
        event_queue=event_queue,
        data_handler=data_handler,
        strategy=strategy,
        portfolio=portfolio,
        execution_simulator=execution_simulator,
    )

    # 2. Action: Run the backtest
    results = engine.run()

    # 3. Assertions: Verify the final state of the portfolio
    
    # Expected outcome:
    # - Buy 100 shares @ $102 (close of day 1) = -$10,200
    # - Sell 100 shares @ $105 (close of day 3) = +$10,500
    # - P&L = $300
    # - Final Cash = $100,000 - $10,200 + $10,500 = $100,300
    
    final_cash = portfolio.cash
    assert final_cash == pytest.approx(100_300.0)
    
    # The final position should be zero
    assert not portfolio.positions
    
    # The final equity curve should reflect the final NAV
    equity_curve = portfolio.get_equity_curve()
    assert not equity_curve.empty
    final_nav = equity_curve.iloc[-1]
    assert final_nav == pytest.approx(100_300.0)
