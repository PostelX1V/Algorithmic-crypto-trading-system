import csv
import os
import time
from datetime import datetime

from app.shared.market_data import get_btc_candles
from app.swing_bot.strategy import moving_average_strategy
from app.swing_bot.risk import calculate_position_size
from app.swing_bot.paper_portfolio import PaperPortfolio


LOG_FILE = "data/logs/swing_paper_trades.csv"
STATUS_FILE = "data/logs/swing_paper_status.csv"


def ensure_csv_file(filepath, fieldnames):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if not os.path.exists(filepath):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()


def append_csv_row(filepath, fieldnames, row):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file_exists = os.path.exists(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def get_latest_strategy_signal(product_id):
    df = get_btc_candles(product_id=product_id, days=90, granularity="ONE_HOUR")

    df = moving_average_strategy(
        df,
        short_window=12,
        long_window=25,
        rsi_buy_threshold=55,
        atr_filter_period=30
    )

    df = calculate_position_size(
        df,
        target_risk=0.02,
        max_position_size=0.30
    )

    latest = df.iloc[-1]
    latest_price = float(latest["close"])
    position_signal = float(latest["position"])
    position_fraction = float(latest["position_fraction"])

    return {
        "price": latest_price,
        "position_signal": position_signal,
        "position_fraction": position_fraction,
        "df": df
    }


def evaluate_stop_loss(portfolio, product_id, latest_price, stop_loss_pct=0.04):
    if not portfolio.has_position(product_id):
        return False

    entry_price = portfolio.positions[product_id]["entry_price"]
    return latest_price <= entry_price * (1 - stop_loss_pct)


def run_paper_trading_cycle(
    product_ids=("BTC-USD", "SOL-USD"),
    fee_rate=0.006,
    stop_loss_pct=0.04,
    starting_cash=10000.0
):
    portfolio = PaperPortfolio(starting_cash=starting_cash)
    latest_prices = {}

    ensure_csv_file(
        LOG_FILE,
        fieldnames=[
            "timestamp",
            "product_id",
            "side",
            "price",
            "allocation",
            "quantity",
            "fee",
            "reason",
            "pnl"
        ]
    )

    ensure_csv_file(
        STATUS_FILE,
        fieldnames=[
            "timestamp",
            "cash",
            "equity",
            "open_positions",
            "positions"
        ]
    )

    print(f"\n[{datetime.utcnow().isoformat()}] Starting paper trading cycle...")

    for product_id in product_ids:
        result = get_latest_strategy_signal(product_id)

        latest_price = result["price"]
        signal = result["position_signal"]
        position_fraction = result["position_fraction"]

        latest_prices[product_id] = latest_price

        print(f"{product_id} | price={latest_price:.2f} | signal={signal} | pos_frac={position_fraction:.4f}")

        if signal == 0:
            print(f"{product_id}: No trade signal")

        stop_triggered = evaluate_stop_loss(
            portfolio,
            product_id,
            latest_price,
            stop_loss_pct=stop_loss_pct
        )

        trade = None

        # BUY
        if signal == 2 and not portfolio.has_position(product_id):
            allocation = portfolio.cash * position_fraction

            trade = portfolio.buy(
                product_id=product_id,
                price=latest_price,
                allocation=allocation,
                fee_rate=fee_rate
            )

        # SELL by strategy
        elif signal == -2 and portfolio.has_position(product_id):
            trade = portfolio.sell(
                product_id=product_id,
                price=latest_price,
                fee_rate=fee_rate,
                reason="SELL_SIGNAL"
            )

        # SELL by stop loss
        elif stop_triggered and portfolio.has_position(product_id):
            trade = portfolio.sell(
                product_id=product_id,
                price=latest_price,
                fee_rate=fee_rate,
                reason="STOP_LOSS"
            )

        if trade:
            print("TRADE:", trade)

            row = {
                "timestamp": trade.get("timestamp"),
                "product_id": trade.get("product_id"),
                "side": trade.get("side"),
                "price": trade.get("price"),
                "allocation": trade.get("allocation", ""),
                "quantity": trade.get("quantity", ""),
                "fee": trade.get("fee"),
                "reason": trade.get("reason", ""),
                "pnl": trade.get("pnl", "")
            }

            append_csv_row(
                LOG_FILE,
                fieldnames=[
                    "timestamp",
                    "product_id",
                    "side",
                    "price",
                    "allocation",
                    "quantity",
                    "fee",
                    "reason",
                    "pnl"
                ],
                row=row
            )

    equity = portfolio.total_equity(latest_prices)

    status_row = {
        "timestamp": datetime.utcnow().isoformat(),
        "cash": portfolio.cash,
        "equity": equity,
        "open_positions": len(portfolio.positions),
        "positions": str(portfolio.positions)
    }

    append_csv_row(
        STATUS_FILE,
        fieldnames=[
            "timestamp",
            "cash",
            "equity",
            "open_positions",
            "positions"
        ],
        row=status_row
    )

    print(f"Cash: {portfolio.cash:.2f}")
    print(f"Equity: {equity:.2f}")
    print(f"Positions: {portfolio.positions}")

    portfolio.save_state()


def run_continuous_paper_trader(
    product_ids=("BTC-USD", "SOL-USD"),
    fee_rate=0.006,
    stop_loss_pct=0.04,
    starting_cash=10000.0,
    cycle_seconds=3600
):
    while True:
        try:
            run_paper_trading_cycle(
                product_ids=product_ids,
                fee_rate=fee_rate,
                stop_loss_pct=stop_loss_pct,
                starting_cash=starting_cash
            )
        except Exception as e:
            print(f"Cycle error: {e}")

        print(f"Sleeping for {cycle_seconds} seconds...")
        time.sleep(cycle_seconds)