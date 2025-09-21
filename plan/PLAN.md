# Implementation Plan

This document describes the recommended order of implementation for the Quant Framework.  
Each phase builds on the previous one, freezing **interfaces first** before adding logic.  
This ensures reproducibility, clean abstractions, and minimal rewrites.

---

## Phase 0 — Groundwork

**Goal:** Prepare repo, tooling, and configs.

- Create:
  - `pyproject.toml`
  - `.pre-commit-config.yaml`
  - `.gitignore`, `.env.example`, `LICENSE`
  - `README.md`, `Makefile`
  - `configs/base.yaml`, `configs/research.yaml`
  - `src/qt/__init__.py`
- **Done when:**
  - `make lint`, `make typecheck`, `make test` run successfully (even with no tests).
  - Pre-commit hooks trigger.

---

## Phase 1 — Core Contracts & Config

**Goal:** Establish types & settings (used everywhere).

- Create:
  - `src/qt/types.py` — Bar, Signal, Order, Fill, Position, PnL (names only)
  - `src/qt/enums.py` — Side, OrderType, Interval, AssetClass, Venue
  - `src/qt/utils/` — `time.py`, `math.py`, `logging.py` (docstrings only)
  - `src/qt/config/settings.py` — loader for YAML + env (docstring)
- **Done when:**
  - `qt.types` and `qt.enums` importable.
  - `qt.config.settings` importable.

---

## Phase 2 — Data Schema & Storage Abstraction

**Goal:** Define the shape of the data & how it’s stored.

- Create:
  - `src/qt/data/schema.py` — schemas for bars/trades/quotes/events/refdata
  - `src/qt/data/storage/parquet.py`, `duckdb.py`, `postgres.py` — docstrings only
- **Done when:**
  - Schema documented (columns, dtypes, partitioning).
  - Storage modules import.

---

## Phase 3 — Data Loader (canonical read API)

**Goal:** Provide one function all modules can call for historical data.

- Create:
  - `src/qt/data/loader.py` — define API surface (`get_bars(...)`) with docstring
  - Update `configs/base.yaml` with `lake_root`, `adjustments`, `calendar`
- **Done when:**
  - Loader importable with expected function signatures.

---

## Phase 4 — Providers (adapters) & Legacy Filesystem

**Goal:** Support both APIs and existing HDD datasets.

- Create:
  - `src/qt/data/providers/base.py` — abstract interface
  - `src/qt/data/providers/filesystem.py` — manifest-driven legacy reader (docstring)
  - `configs/research.yaml` — enable filesystem provider
- **Done when:**
  - Loader can reference a provider by name.

---

## Phase 5 — Feature Engineering & Signals

**Goal:** Define where alphas & labels live.

- Create:
  - `src/qt/features/engineering.py`
  - `src/qt/features/signals/{momentum.py, mean_reversion.py, microstructure.py}`
  - `src/qt/features/labeling/triple_barrier.py`
- **Done when:**
  - Strategies can import signal functions (stubs only).

---

## Phase 6 — Strategy Interface

**Goal:** Freeze how strategies talk to the engine.

- Create:
  - `src/qt/strategies/base.py` — defines `initialize`, `on_data`, optional hooks
  - `src/qt/strategies/registry.py`
  - Example: `mr_pairs.py`, `xmom_crosssec.py`
- **Done when:**
  - Strategies can be registered & resolved by name.

---

## Phase 7 — Portfolio Construction

**Goal:** Decide how signals → target weights.

- Create:
  - `src/qt/portfolio/optimizers.py`
  - `src/qt/portfolio/risk_models.py`
  - `src/qt/portfolio/constraints.py`
  - `src/qt/portfolio/rebalancing.py`
  - `src/qt/portfolio/allocators.py`
- **Done when:**
  - Portfolio layer returns dict[symbol → weight].

---

## Phase 8 — Risk (sizing & limits)

**Goal:** Enforce limits & convert weights → notional orders.

- Create:
  - `src/qt/risk/sizing.py`
  - `src/qt/risk/limits.py`
  - `src/qt/risk/models.py`
  - `src/qt/risk/stress.py`
- **Done when:**
  - Risk stage produces dict[symbol → quantity] with guardrails.

---

## Phase 9 — Backtest Engine

**Goal:** Deterministic simulator of the pipeline.

- Create:
  - `src/qt/backtest/engine.py` — event loop (docstring of flow)
  - `src/qt/backtest/execution_sim.py`, `slippage.py`, `costs.py`
  - `src/qt/backtest/portfolio.py`, `metrics.py`
  - `scripts/run_backtest.py`
- **Done when:**
  - Can dry-run a backtest that executes all stages (logs only).

---

## Phase 10 — Evaluation & Reporting

**Goal:** Define outputs for research.

- Create:
  - `src/qt/evaluation/performance.py`, `tearsheet.py`
  - `src/qt/reporting/reporters.py`, `dashboards/__init__.py`
  - `scripts/make_tearsheet.py`
- **Done when:**
  - Backtest results can be written to artifact path.

---

## Phase 11 — Live Trading Surface

**Goal:** Mirror backtest engine with broker adapters.

- Create:
  - `src/qt/live/exec_engine.py`, `data_streams.py`
  - `src/qt/live/order_router.py`, `state_store.py`, `risk_guard.py`
  - `src/qt/live/adapters/{alpaca.py, ibkr.py, binance.py}`
  - `scripts/run_live.py`
- **Done when:**
  - Live engine can run with fake adapters.

---

## Milestone — “Hello World” Pipeline

After **Phase 9**:

1. Run `scripts/run_backtest.py --strategy xmom_crosssec`.
2. Engine logs each stage executed.
3. Produces a dummy metrics dict and placeholder artifact.

This proves **end-to-end wiring** before adding heavy logic.

---

## Practical Tips

- **Freeze interfaces early** — types, loader, strategy hooks, optimizer I/O.
- **Write contract tests first** — even if functions are empty, prevents drift.
- **Centralize constants in configs** — fail fast on missing params.
- **Document assumptions** — UTC timestamps, symbol mapping, partitioning.