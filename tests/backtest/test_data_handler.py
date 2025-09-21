"""
Unit tests for the DataHandler class.
"""
import pandas as pd
import pytest
from datetime import datetime, timezone

# Import the components we need to test
from qt.backtest.data_handler import DataHandler
from qt.backtest.event_queue import EventQueue
from qt.events import BarEvent


@pytest.fixture
def sample_market_data() -> pd.DataFrame:
    """
    Creates a sample multi-symbol DataFrame for testing.
    The data is intentionally out of chronological order to test sorting.
    """
    data = [
        # Timestamp, Symbol, O, H, L, C, V, Interval, Venue
        ("2025-01-01 10:01:00", "MSFT", 300, 302, 300, 301.0, 5e5, "1m", "XNAS"),
        ("2025-01-01 10:00:00", "AAPL", 150, 151, 149, 150.5, 1e6, "1m", "XNAS"),
        ("2025-01-01 10:01:00", "AAPL", 150.5, 152, 150, 151.8, 1.2e6, "1m", "XNAS"),
        ("2025-01-01 10:00:00", "MSFT", 299, 300, 298, 299.5, 6e5, "1m", "XNAS"),
    ]
    columns = ["ts_utc", "symbol", "open", "high", "low", "close", "volume", "interval", "venue"]
    
    df = pd.DataFrame(data, columns=columns)
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
    df.set_index("ts_utc", inplace=True)
    
    return df


def test_update_data_pushes_correct_events(sample_market_data: pd.DataFrame):
    """
    Verifies that `update_data` correctly sorts the input data and pushes
    chronologically ordered, bundled BarEvents to the queue.
    """
    event_queue = EventQueue()
    data_handler = DataHandler(event_queue=event_queue, historical_data=sample_market_data)

    # Action
    data_handler.update_data()

    # Assertions
    assert not event_queue.is_empty(), "Event queue should not be empty after pushing data"

    # Check first event (10:00:00)
    first_event = event_queue.get()
    assert isinstance(first_event, BarEvent)
    assert first_event.timestamp == datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    assert len(first_event.bars) == 2, "Should be two bars for the first timestamp"
    assert "AAPL" in first_event.bars and "MSFT" in first_event.bars
    assert first_event.bars["AAPL"].close == 150.5
    assert first_event.bars["MSFT"].close == 299.5

    # Check second event (10:01:00)
    second_event = event_queue.get()
    assert isinstance(second_event, BarEvent)
    assert second_event.timestamp == datetime(2025, 1, 1, 10, 1, 0, tzinfo=timezone.utc)
    assert len(second_event.bars) == 2, "Should be two bars for the second timestamp"
    assert second_event.bars["AAPL"].close == 151.8
    assert second_event.bars["MSFT"].close == 301.0

    assert event_queue.is_empty(), "Event queue should be empty after processing all events"


def test_history_and_price_tracking_after_update(sample_market_data: pd.DataFrame):
    """
    Verifies that after `update_data` is called, the history and latest prices
    are fully populated and can be retrieved correctly.
    """
    event_queue = EventQueue()
    data_handler = DataHandler(event_queue=event_queue, historical_data=sample_market_data)

    # Action
    data_handler.update_data()

    # --- Assertions for get_latest_prices ---
    # It should return the prices from the very last timestamp in the data
    latest_prices = data_handler.get_latest_prices()
    assert latest_prices["AAPL"] == 151.8
    assert latest_prices["MSFT"] == 301.0

    # --- Assertions for get_history ---
    # 1. Get full history for a symbol
    aapl_history = data_handler.get_history("AAPL")
    assert isinstance(aapl_history, pd.DataFrame)
    assert len(aapl_history) == 2
    assert aapl_history.index.is_monotonic_increasing
    assert list(aapl_history["close"]) == [150.5, 151.8]

    # 2. Get history with a lookback
    msft_history_lookback = data_handler.get_history("MSFT", lookback=1)
    assert len(msft_history_lookback) == 1
    assert msft_history_lookback.iloc[0]["close"] == 301.0

    # 3. Requesting more history than available should return an empty DataFrame
    # (Note: This is based on your current implementation. We'll simulate this by
    # creating a handler with less data)
    one_row_df = sample_market_data[sample_market_data['symbol'] == 'AAPL'].head(1)
    short_history_handler = DataHandler(EventQueue(), one_row_df)
    short_history_handler.update_data()
    assert short_history_handler.get_history("AAPL", lookback=5).empty

