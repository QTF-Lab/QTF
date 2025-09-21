"""
Comprehensive unit tests for the Portfolio class.
"""
from datetime import datetime, timezone
import pytest
import pandas as pd

# Import the components to be tested
from qt.backtest.portfolio import Portfolio
from qt.events import FillEvent
from qt.types import Fill

# Helper function to create a FillEvent for convenience
def create_fill_event(
    symbol: str, side: str, qty: float, price: float, fee: float = 0.0
) -> FillEvent:
    """Creates a FillEvent containing a single Fill object."""
    # The key change is here: we determine the sign of the quantity based on the side.
    signed_qty = qty if side == "BUY" else -qty
    fill = Fill(
        order_id="dummy_order_id",
        ts_utc=datetime.now(timezone.utc),
        symbol=symbol,
        qty=signed_qty, # Use the signed quantity
        price=price,
        fee=fee,
    )
    return FillEvent(timestamp=fill.ts_utc, fills=[fill])


@pytest.fixture
def portfolio() -> Portfolio:
    """Returns a new Portfolio instance with $100,000 cash for each test."""
    return Portfolio(initial_cash=100_000.0)


def test_portfolio_initialization(portfolio: Portfolio):
    """Tests that the portfolio initializes with the correct state."""
    assert portfolio.initial_cash == 100_000.0
    assert portfolio.cash == 100_000.0
    assert not portfolio.positions
    assert not portfolio.history


def test_open_new_long_position(portfolio: Portfolio):
    """Tests buying a stock to open a new long position."""
    fill_event = create_fill_event(symbol="AAPL", side="BUY", qty=100, price=150.0)
    
    # Action
    portfolio.update_on_fill(fill_event)

    # Assertions
    assert portfolio.cash == 100_000.0 - (100 * 150.0)
    assert "AAPL" in portfolio.positions
    aapl_pos = portfolio.positions["AAPL"]
    assert aapl_pos.qty == 100
    assert aapl_pos.avg_price == 150.0
    assert aapl_pos.realized_pnl == 0.0


def test_increase_long_position(portfolio: Portfolio):
    """Tests buying more of a stock we are already long (averaging up)."""
    # Initial position
    portfolio.update_on_fill(create_fill_event("AAPL", "BUY", 100, 150.0))
    
    # Action: Buy more at a higher price
    portfolio.update_on_fill(create_fill_event("AAPL", "BUY", 50, 160.0))

    # Assertions
    expected_cash = 100_000.0 - (100 * 150.0) - (50 * 160.0)
    assert portfolio.cash == pytest.approx(expected_cash)
    
    aapl_pos = portfolio.positions["AAPL"]
    assert aapl_pos.qty == 150
    
    # Check that average price is correctly recalculated
    expected_avg_price = ((100 * 150.0) + (50 * 160.0)) / 150
    assert aapl_pos.avg_price == pytest.approx(expected_avg_price)


def test_partially_close_long_position_for_profit(portfolio: Portfolio):
    """Tests selling some shares of a long position for a profit."""
    portfolio.update_on_fill(create_fill_event("AAPL", "BUY", 100, 150.0))

    # Action: Sell 40 shares at a higher price
    portfolio.update_on_fill(create_fill_event("AAPL", "SELL", 40, 160.0))

    # Assertions
    expected_cash = 100_000.0 - (100 * 150.0) + (40 * 160.0)
    assert portfolio.cash == pytest.approx(expected_cash)

    aapl_pos = portfolio.positions["AAPL"]
    assert aapl_pos.qty == 60 # Remaining position
    assert aapl_pos.avg_price == 150.0 # Avg price should NOT change on a partial close
    
    # Check that P&L was realized
    expected_pnl = (160.0 - 150.0) * 40
    assert aapl_pos.realized_pnl == pytest.approx(expected_pnl)


def test_fully_close_long_position(portfolio: Portfolio):
    """Tests selling all shares to close a long position."""
    portfolio.update_on_fill(create_fill_event("AAPL", "BUY", 100, 150.0))
    portfolio.update_on_fill(create_fill_event("AAPL", "SELL", 100, 155.0))

    assert "AAPL" not in portfolio.positions, "Position should be removed after closing"
    expected_cash = 100_000.0 - (100 * 150.0) + (100 * 155.0)
    assert portfolio.cash == pytest.approx(expected_cash)


def test_flip_position_from_long_to_short(portfolio: Portfolio):
    """Tests a single large sell order that flips a long position to short."""
    portfolio.update_on_fill(create_fill_event("AAPL", "BUY", 100, 150.0))
    
    # Action: Sell 150 shares (100 to close, 50 to open short)
    portfolio.update_on_fill(create_fill_event("AAPL", "SELL", 150, 160.0))

    # Assertions
    expected_pnl = (160.0 - 150.0) * 100 # PnL from closing the 100 long shares
    
    aapl_pos = portfolio.positions["AAPL"]
    assert aapl_pos.qty == -50 # New short position
    assert aapl_pos.avg_price == 160.0 # Avg price of the new short position is the flip price
    assert aapl_pos.realized_pnl == pytest.approx(expected_pnl)
    
    expected_cash = 100_000.0 - (100 * 150.0) + (150 * 160.0)
    assert portfolio.cash == pytest.approx(expected_cash)


def test_open_new_short_position(portfolio: Portfolio):
    """Tests selling a stock to open a new short position."""
    portfolio.update_on_fill(create_fill_event("TSLA", "SELL", 50, 200.0))

    assert portfolio.cash == 100_000.0 + (50 * 200.0)
    assert "TSLA" in portfolio.positions
    tsla_pos = portfolio.positions["TSLA"]
    assert tsla_pos.qty == -50
    assert tsla_pos.avg_price == 200.0


def test_fully_close_short_position_for_loss(portfolio: Portfolio):
    """Tests buying back shares to close a short position for a loss."""
    portfolio.update_on_fill(create_fill_event("TSLA", "SELL", 50, 200.0))
    
    # Action: Buy back at a higher price
    portfolio.update_on_fill(create_fill_event("TSLA", "BUY", 50, 210.0))

    assert "TSLA" not in portfolio.positions
    expected_cash = 100_000.0 + (50 * 200.0) - (50 * 210.0)
    assert portfolio.cash == pytest.approx(expected_cash)


def test_snapshot_and_equity_curve(portfolio: Portfolio):
    """Tests the NAV calculation and history tracking."""
    ts1 = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    ts2 = datetime(2025, 1, 1, 10, 1, 0, tzinfo=timezone.utc)
    
    # Time 1: Initial state
    portfolio.record_snapshot(ts1, {})
    assert portfolio.history[0].nav == 100_000.0

    # Time 2: Buy AAPL
    portfolio.update_on_fill(create_fill_event("AAPL", "BUY", 100, 150.0))
    # At this exact moment, let's say AAPL price is 152
    latest_prices = {"AAPL": 152.0}
    portfolio.record_snapshot(ts2, latest_prices)

    # Assert NAV calculation
    expected_market_value = 100 * 152.0 # 15,200
    expected_cash = 100_000.0 - (100 * 150.0) # 85,000
    expected_nav = expected_cash + expected_market_value # 100,200
    
    assert portfolio.history[1].nav == pytest.approx(expected_nav)
    
    # Test equity curve generation
    equity_curve = portfolio.get_equity_curve()
    assert isinstance(equity_curve, pd.Series)
    assert len(equity_curve) == 2
    assert equity_curve.iloc[1] == pytest.approx(expected_nav)

