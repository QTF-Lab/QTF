"""
Comprehensive unit tests for the ExecutionSimulator class.
"""
import uuid
from datetime import datetime, timezone
import pytest

# Import the components to be tested
from qt.backtest.execution_sim import ExecutionSimulator
from qt.backtest.slippage import NoSlippage
from qt.backtest.costs import NoCost
from qt.events import OrderEvent, BarEvent
from qt.types import Order, Bar
from qt.enums import OrderType

# --- Helper Functions and Fixtures ---

def create_order(
    symbol: str, side: str, order_type: OrderType, qty: float, limit_price: float | None = None
) -> Order:
    """Creates a single Order object for convenience."""
    return Order(
        id=str(uuid.uuid4()),
        ts_utc=datetime.now(timezone.utc),
        symbol=symbol,
        side=side,
        type=order_type,
        qty=qty,
        limit_price=limit_price,
    )

@pytest.fixture
def execution_simulator() -> ExecutionSimulator:
    """Returns a new ExecutionSimulator with ideal (zero) frictions."""
    return ExecutionSimulator(slippage_model=NoSlippage(), cost_model=NoCost())

@pytest.fixture
def sample_bar_event() -> BarEvent:
    """Provides a sample BarEvent for testing limit order fills."""
    ts = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    bars = {
        "AAPL": Bar(
            ts_utc=ts, symbol="AAPL", open=150, high=152, low=148, close=151,
            volume=1e6, interval="1m", venue="XNAS"
        )
    }
    return BarEvent(timestamp=ts, bars=bars)


# --- Test Cases ---

def test_market_order_fills_immediately(execution_simulator: ExecutionSimulator, sample_bar_event: BarEvent):
    """
    Tests that a MARKET order is processed and returns a FillEvent immediately.
    """
    market_order = create_order("AAPL", "BUY", OrderType.MARKET, 100)
    order_event = OrderEvent(timestamp=sample_bar_event.timestamp, orders=[market_order])
    
    # Action
    fill_event = execution_simulator.process_new_orders(order_event, sample_bar_event.bars)

    # Assertions
    assert fill_event is not None
    assert len(fill_event.fills) == 1
    fill = fill_event.fills[0]
    assert fill.order_id == market_order.id
    assert fill.qty == 100
    # With NoSlippage, price should be the bar's close
    assert fill.price == sample_bar_event.bars["AAPL"].close
    assert fill.fee == 0.0
    # The open order book should be empty
    assert not execution_simulator.open_limit_orders


def test_limit_order_is_placed_on_book(execution_simulator: ExecutionSimulator, sample_bar_event: BarEvent):
    """
    Tests that a new LIMIT order is not filled immediately but is added to the
    internal open orders book.
    """
    limit_order = create_order("AAPL", "BUY", OrderType.LIMIT, 100, limit_price=140.0)
    order_event = OrderEvent(timestamp=sample_bar_event.timestamp, orders=[limit_order])

    # Action
    fill_event = execution_simulator.process_new_orders(order_event, sample_bar_event.bars)

    # Assertions
    assert fill_event is None, "A new limit order should not generate an immediate fill"
    assert len(execution_simulator.open_limit_orders) == 1
    assert execution_simulator.open_limit_orders[limit_order.id] == limit_order


def test_buy_limit_order_fills_on_price_drop(execution_simulator: ExecutionSimulator, sample_bar_event: BarEvent):
    """
    Tests that an open BUY LIMIT order is filled when the market low drops to
    or below its limit price.
    """
    # Arrange: Place a BUY LIMIT order on the book
    buy_limit = create_order("AAPL", "BUY", OrderType.LIMIT, 100, limit_price=148.0)
    execution_simulator.open_limit_orders[buy_limit.id] = buy_limit
    
    # Action: The next bar's low price touches the limit price (low is 148)
    fill_event = execution_simulator.check_open_orders(sample_bar_event)

    # Assertions
    assert fill_event is not None
    assert len(fill_event.fills) == 1
    fill = fill_event.fills[0]
    assert fill.order_id == buy_limit.id
    assert fill.qty == 100
    assert fill.price == 148.0 # Fills at the limit price
    assert not execution_simulator.open_limit_orders, "Filled order should be removed from the book"


def test_sell_limit_order_fills_on_price_rise(execution_simulator: ExecutionSimulator, sample_bar_event: BarEvent):
    """
    Tests that an open SELL LIMIT order is filled when the market high rises to
    or above its limit price.
    """
    # Arrange: Place a SELL LIMIT order on the book
    sell_limit = create_order("AAPL", "SELL", OrderType.LIMIT, 50, limit_price=152.0)
    execution_simulator.open_limit_orders[sell_limit.id] = sell_limit
    
    # Action: The next bar's high price touches the limit price (high is 152)
    fill_event = execution_simulator.check_open_orders(sample_bar_event)

    # Assertions
    assert fill_event is not None
    assert len(fill_event.fills) == 1
    fill = fill_event.fills[0]
    assert fill.qty == -50
    assert fill.price == 152.0
    assert not execution_simulator.open_limit_orders


def test_limit_order_does_not_fill_if_price_not_reached(execution_simulator: ExecutionSimulator, sample_bar_event: BarEvent):
    """
    Tests that an open LIMIT order remains on the book if the market price
    does not reach its limit.
    """
    # Arrange: Place a BUY LIMIT order with a price far below the market
    buy_limit = create_order("AAPL", "BUY", OrderType.LIMIT, 100, limit_price=140.0)
    execution_simulator.open_limit_orders[buy_limit.id] = buy_limit
    
    # Action: The bar's low (148) does not reach the limit price (140)
    fill_event = execution_simulator.check_open_orders(sample_bar_event)

    # Assertions
    assert fill_event is None, "No fills should have occurred"
    assert len(execution_simulator.open_limit_orders) == 1, "Order should remain on the book"
    assert buy_limit.id in execution_simulator.open_limit_orders
