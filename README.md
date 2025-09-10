# Quant Framework

A complete **quantitative trading research & execution framework** built in Python.  
It covers the full lifecycle of systematic trading:

- **Data ingestion & management** (equities, crypto, FX, …)
- **Feature engineering & signal generation**
- **Strategy development & backtesting**
- **Portfolio construction & risk management**
- **Execution** (simulation & live)
- **Evaluation, reporting & monitoring**

---

## Project Structure

```
quant-framework/
├── configs/            # Runtime configuration (YAML)
├── data/               # Local data lake (gitignored)
├── artifacts/          # Saved models, tearsheets, reports (gitignored)
├── logs/               # Structured logs (gitignored)
├── notebooks/          # Jupyter notebooks for research
├── scripts/            # CLI-friendly scripts
├── tests/              # Unit & integration tests
└── src/qt/             # Main Python package (import as qt)
```

### Top-level files
- **`pyproject.toml`** – project dependencies & tooling (black, ruff, mypy, pytest)  
- **`README.md`** – this document  
- **`.env.example`** – template for environment variables (API keys, DB URIs)  
- **`docker-compose.yml`** – optional services (Postgres, Redis, DuckDB, …)  
- **`Makefile`** – developer shortcuts (`make lint`, `make test`, `make backtest`)  

---

## Core Package (`src/qt/`)

### 📦 Core contracts
- **`types.py`** – canonical dataclasses: Bar, Signal, Order, Fill, Position, PnL  
- **`enums.py`** – finite sets: Side, OrderType, Interval, AssetClass, Venue  
- **`utils/`** – helpers for time, math, logging, serialization  
- **`config/settings.py`** – centralized config loader (YAML + env → Pydantic Settings)

### 📊 Data layer (`data/`)
- **`providers/`** – vendor adapters (Binance, Polygon, Quandl, Filesystem)  
- **`storage/`** – storage backends (Parquet, DuckDB, Postgres)  
- **`schema.py`** – validation schemas (bars, trades, quotes, events, refdata)  
- **`loader.py`** – canonical read API (`get_bars(symbols, start, end, interval, adjust=…)`)  
- **`pipelines/`** – ETL jobs: history backfills, daily refreshes  

### 🛠️ Features (`features/`)
- **`engineering.py`** – rolling stats, returns, volatility, resampling  
- **`signals/`** – alpha factor definitions (momentum, mean reversion, microstructure)  
- **`labeling/`** – supervised learning targets (triple-barrier, forward returns)

### 📑 Strategies (`strategies/`)
- **`base.py`** – strategy interface (on_data, on_fill, etc.)  
- **`registry.py`** – strategy discovery / registration  
- **Examples** – `mr_pairs.py`, `xmom_crosssec.py`

### 📐 Portfolio construction (`portfolio/`)
- **`optimizers.py`** – convert signals → target weights (proportional, risk parity, Markowitz, BL)  
- **`risk_models.py`** – covariance estimators, factor models  
- **`constraints.py`** – leverage, sector caps, turnover limits  
- **`rebalancing.py`** – rebalance schedules & drift bands  
- **`allocators.py`** – combine multiple strategies into one book (multi-strategy layer)

### ⚠️ Risk (`risk/`)
- **`sizing.py`** – weights → quantities (shares/contracts), vol targeting  
- **`limits.py`** – exposure limits, stop trading rules, kill switches  
- **`models.py`** – VaR/ES models, drawdown tracking  
- **`stress.py`** – scenario testing & shocks  

### 🔄 Backtesting (`backtest/`)
- **`engine.py`** – deterministic event loop (bars → strategy → portfolio → orders → fills)  
- **`execution_sim.py`** – fill models (VWAP, slippage, queue priority)  
- **`slippage.py`, `costs.py`** – trading frictions  
- **`portfolio.py`** – simulated holdings, PnL accounting  
- **`metrics.py`** – standardized performance stats  

### ⚡ Live trading (`live/`)
- **`adapters/`** – broker/exchange integrations (Alpaca, IBKR, Binance)  
- **`data_streams.py`** – websockets → normalized ticks/bars  
- **`order_router.py`** – order routing, retries, idempotency  
- **`exec_engine.py`** – live twin of backtest engine  
- **`state_store.py`** – Redis/Postgres cache of positions/orders  
- **`risk_guard.py`** – pre-trade checks, intraday risk limits, circuit breakers  

### 📈 Evaluation (`evaluation/`)
- **`performance.py`** – return decomposition, factor analysis, drawdown stats  
- **`tearsheet.py`** – HTML/PDF performance reports  

### 📢 Reporting & monitoring (`reporting/`)
- **`reporters.py`** – notifications (Slack, email, alerts)  
- **`dashboards/`** – Streamlit / FastAPI dashboards for live status & risk  

### 🗂️ Pipelines (`pipelines/`)
- **`dags.py`**, **`tasks.py`** – orchestration (Prefect/Airflow jobs)  

### 🚀 API (`api/`)
- **`cli.py`** – CLI entrypoints (`qt backtest`, `qt live`, `qt fetch`)  
- **`server.py`** – optional FastAPI server (REST endpoints for jobs, health)  

### 🔌 Plugins (`plugins/`)
- **`example_plugin.py`** – extension point for external strategies/data  

---

## Research & Scripts

- **`notebooks/`** – exploratory analysis, factor research, sanity checks  
- **`scripts/`** – runnable utilities (fetch history, run backtest/live, generate tearsheet)  
- **`tests/`** – unit & integration tests (pytest)

---

## Typical Workflow

1. **Data ingestion**  
   - Load raw vendor files or APIs → normalized schema (`data/providers/*`).  
   - Persist in Parquet or DB (`data/storage/*`).  
   - Access uniformly via `data/loader.get_bars()`.

2. **Feature engineering & signals**  
   - Compute rolling returns, vol, factors (`features/engineering`, `features/signals`).  
   - Label data if training ML strategies (`features/labeling`).

3. **Strategy definition**  
   - Implement `on_data` in `strategies/*` to turn signals into portfolio views.  
   - Register in `registry.py` for discovery.

4. **Portfolio construction**  
   - Convert signals → target weights (`portfolio/optimizers.py`).  
   - For multi-strategy, combine portfolios via `allocators.py`.

5. **Risk management**  
   - Size into notional exposures (`risk/sizing.py`).  
   - Apply leverage, vol targets, and limits (`risk/limits.py`).

6. **Execution**  
   - **Backtest**: deterministic sim (`backtest/engine.py`, `execution_sim.py`).  
   - **Live**: event-driven engine (`live/exec_engine.py`) → broker adapters.

7. **Evaluation**  
   - Analyze PnL, drawdowns, exposures (`evaluation/performance.py`).  
   - Generate reports (`evaluation/tearsheet.py`).

8. **Reporting & monitoring**  
   - Send daily/weekly reports (`reporting/reporters.py`).  
   - Monitor live systems via dashboards.

---

## Philosophy

- **Separation of concerns** – data vs signals vs portfolio vs risk vs execution  
- **Deterministic backtests** – reproducibility is first-class  
- **Adapters everywhere** – easy to swap data providers, storage, brokers  
- **Schema validation** – data contracts enforced at entry points  
- **Promotion path** – notebooks → modules when stable  

---

## Next Steps

1. Fill in schemas (`src/qt/data/schema.py`)  
2. Implement a provider + storage backend  
3. Write a toy signal + strategy (e.g., SMA crossover)  
4. Run first backtest (`scripts/run_backtest.py`)  
5. Add evaluation report (`scripts/make_tearsheet.py`)  

---