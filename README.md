# Algorithmic Crypto Trading System

A modular Python-based cryptocurrency trading system built around the Coinbase Advanced API.

The project contains separate day-trading and swing-trading workflows along with shared infrastructure for market data, trade execution, logging, alerts, configuration, and portfolio management.

The system was built to experiment with algorithmic strategy design, paper trading, backtesting, risk management, and automated market analysis.

---

## Project Overview

This project is organized into three primary components:

### Day Trading Bot

The `day_bot` package contains the shorter-term trading workflow.

It includes modules for:

- Trading strategy logic
- Trade execution
- Paper portfolio tracking
- Bot orchestration

### Swing Trading Bot

The `swing_bot` package contains a more extensive swing-trading and portfolio-analysis system.

It includes functionality for:

- Trading strategies
- Paper trading
- Portfolio management
- Risk management
- Multi-asset analysis
- Strategy optimization
- Walk-forward analysis
- Portfolio aggregation

### Shared Infrastructure

The `shared` package contains reusable components used across the trading system, including:

- Coinbase REST API client
- Market data retrieval
- Trade execution utilities
- Configuration management
- Logging
- Alerts

---

## Project Structure

```text
coinbase_bot/
├── app/
│   ├── day_bot/
│   │   ├── main.py
│   │   ├── paper_portfolio.py
│   │   ├── strategy.py
│   │   └── trader.py
│   │
│   ├── shared/
│   │   ├── alerts.py
│   │   ├── coinbase_client.py
│   │   ├── config.py
│   │   ├── execution.py
│   │   ├── logger.py
│   │   └── market_data.py
│   │
│   └── swing_bot/
│       ├── analyzer.py
│       ├── main.py
│       ├── multi_asset_analyzer.py
│       ├── multi_asset.py
│       ├── optimizer.py
│       ├── paper_portfolio.py
│       ├── paper_trader.py
│       ├── portfolio_aggregator.py
│       ├── portfolio.py
│       ├── risk.py
│       ├── strategy.py
│       └── walkforward.py
│
├── data/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Technologies

- Python
- Coinbase Advanced API
- Pandas
- NumPy
- Requests
- WebSockets
- python-dotenv
- Cryptography
- PyJWT

## Concepts Demonstrated

This project gave me hands-on experience with:

- Algorithmic trading system design
- REST API integration
- Modular Python application architecture
- Environment-variable configuration
- Paper trading
- Portfolio state management
- Risk-management logic
- Market-data processing
- Multi-asset analysis
- Strategy optimization
- Walk-forward analysis
- Logging and alerting
- Dependency management
- Git and GitHub workflow

## Environment Setup

Create and activate a virtual environment, then install the project dependencies.

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Coinbase API Configuration

This project uses environment variables to keep Coinbase API credentials out of the source code.

Create a `.env` file in the project root based on `.env.example`:

```text
COINBASE_API_KEY=your_api_key_here
COINBASE_API_SECRET=your_api_secret_here
```

The real `.env` file is excluded from Git through `.gitignore` and should never be committed.

---

## Running the Application

The project contains separate entry points for the day-trading and swing-trading systems.

### Day Trading Bot

From the project root:

```bash
python -m app.day_bot.main
```

### Swing Trading Bot

From the project root:

```bash
python -m app.swing_bot.main
```

Before using either workflow, make sure:

- the virtual environment is activated
- dependencies are installed
- the `.env` file contains valid Coinbase API credentials
- strategy and risk-management settings have been reviewed

Paper-trading functionality should be used to test strategy behavior before enabling any live trading functionality.

---

## Data and Runtime Files

Generated runtime data is intentionally excluded from version control.

This includes:

- paper-trading records
- portfolio state files
- trading status files
- logs
- downloaded market data
- local environment files

These files remain available locally while keeping the public repository focused on the source code.

---

## Security

API credentials are not hard-coded into the application.

Credentials are loaded from environment variables:

```python
API_KEY = os.getenv("COINBASE_API_KEY")
API_SECRET = os.getenv("COINBASE_API_SECRET")
```

The repository contains only `.env.example` so users can see which environment variables are required without exposing real credentials.

---

## Purpose

I built this project to develop a deeper understanding of:

- Python software architecture
- REST API integration
- automated trading systems
- market-data processing
- strategy development
- portfolio management
- risk management
- paper trading
- optimization and analysis
- reusable application components

The project evolved from individual trading scripts into a modular system with separate trading workflows and shared infrastructure for data retrieval, execution, configuration, logging, alerts, and portfolio management.

---

## Disclaimer

This project is intended for educational and experimental purposes.

It is not financial advice, and the strategies contained in this repository are not guaranteed to produce profitable results. Automated trading involves significant financial risk.