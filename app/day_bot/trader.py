import csv
import os
import time
from datetime import datetime

from app.shared.market_data import get_btc_candles
from app.shared.alerts import send_telegram_alert
from app.day_bot.strategy import day_trading_strategy
from app.day_bot.paper_portfolio import DayPaperPortfolio


DAY_LOG_FILE = "data/logs/day_paper_trades.csv"
DAY_STATUS_FILE = "data/logs/day_paper_status.csv"


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


def get_latest_day_signal(product_id="BTC-USD"):
    df = get_btc_candles(product_id=product_id, days=30, granularity="FIFTEEN_MINUTE")

    df = day_trading_strategy(
        df,
        fast_ma=8,
        slow_ma=21,
        rsi_period=14
    )

    latest = df.iloc[-1]

    return {
        "price": float(latest["close"]),
        "signal": float(latest["position"]),
        "df": df
    }


def evaluate_exit_conditions(
    portfolio,
    product_id,
    latest_price,
    stop_loss_pct=0.007,
    take_profit_pct=0.018,
    trail_start_pct=0.010,
    trailing_stop_pct=0.005,
    min_profit_sell_pct=0.013
):
    if not portfolio.has_position(product_id):
        return None

    position = portfolio.positions[product_id]

    entry_price = position["entry_price"]

    portfolio.update_highest_price(product_id, latest_price)

    highest_price = portfolio.positions[product_id].get("highest_price", entry_price)

    current_profit_pct = (latest_price - entry_price) / entry_price

    # Always protect downside
    if current_profit_pct <= -stop_loss_pct:
        return "STOP_LOSS"

    # Full take profit
    if current_profit_pct >= take_profit_pct:
        return "TAKE_PROFIT"

    # Trailing stop only activates after price moves enough in our favor
    if highest_price >= entry_price * (1 + trail_start_pct):
        trailing_stop_price = highest_price * (1 - trailing_stop_pct)

        if latest_price <= trailing_stop_price and current_profit_pct >= min_profit_sell_pct:
            return "TRAILING_STOP"

    return None


def run_day_trading_cycle(
    product_id="BTC-USD",
    starting_cash=3000.0,
    fee_rate=0.006,
    stop_loss_pct=0.007,
    take_profit_pct=0.018,
    trail_start_pct=0.010,
    trailing_stop_pct=0.005,
    min_profit_sell_pct=0.013,
    position_size_pct=0.25
):
    portfolio = DayPaperPortfolio(starting_cash=starting_cash)
    latest_prices = {}

    ensure_csv_file(
        DAY_LOG_FILE,
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
        DAY_STATUS_FILE,
        fieldnames=[
            "timestamp",
            "cash",
            "equity",
            "open_positions",
            "positions"
        ]
    )

    print(f"\n[{datetime.utcnow().isoformat()}] Starting DAY bot cycle...")

    result = get_latest_day_signal(product_id)

    latest_price = result["price"]
    signal = result["signal"]

    latest_prices[product_id] = latest_price

    print(f"{product_id} | price={latest_price:.2f} | signal={signal}")

    if signal == 0:
        print(f"{product_id}: No day trade signal")

    exit_reason = evaluate_exit_conditions(
    portfolio=portfolio,
    product_id=product_id,
    latest_price=latest_price,
    stop_loss_pct=stop_loss_pct,
    take_profit_pct=take_profit_pct,
    trail_start_pct=trail_start_pct,
    trailing_stop_pct=trailing_stop_pct,
    min_profit_sell_pct=min_profit_sell_pct
)

    trade = None

    if signal == 2 and not portfolio.has_position(product_id):
        allocation = portfolio.cash * position_size_pct

        trade = portfolio.buy(
            product_id=product_id,
            price=latest_price,
            allocation=allocation,
            fee_rate=fee_rate
        )

    elif signal == -2 and portfolio.has_position(product_id):
        entry_price = portfolio.positions[product_id]["entry_price"]
        current_profit_pct = (latest_price - entry_price) / entry_price

        if current_profit_pct >= min_profit_sell_pct:
            trade = portfolio.sell(
            product_id=product_id,
            price=latest_price,
            fee_rate=fee_rate,
            reason="SELL_SIGNAL_PROFIT"
        )
        else:
            print(
            f"SELL signal ignored. Profit too small: "
            f"{current_profit_pct * 100:.2f}%"
        )

    elif exit_reason and portfolio.has_position(product_id):
        trade = portfolio.sell(
        product_id=product_id,
        price=latest_price,
        fee_rate=fee_rate,
        reason=exit_reason
    )

    if trade:
        print("DAY TRADE:", trade)

        send_telegram_alert(f"DAY BOT TRADE ALERT\n{trade}")

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
            DAY_LOG_FILE,
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
        DAY_STATUS_FILE,
        fieldnames=[
            "timestamp",
            "cash",
            "equity",
            "open_positions",
            "positions"
        ],
        row=status_row
    )

    print(f"Day Cash: {portfolio.cash:.2f}")
    print(f"Day Equity: {equity:.2f}")
    print(f"Day Positions: {portfolio.positions}")

    portfolio.save_state()


def run_continuous_day_trader(
    product_id="BTC-USD",
    starting_cash=3000.0,
    fee_rate=0.006,
    stop_loss_pct=0.012,
    take_profit_pct=0.014,
    trail_start_pct=0.006,
    trailing_stop_pct=0.004,
    min_profit_sell_pct=0.013,
    position_size_pct=0.25,
    cycle_seconds=900
):
    while True:
        try:
            run_day_trading_cycle(
                product_id=product_id,
                starting_cash=starting_cash,
                fee_rate=fee_rate,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct,
                trail_start_pct=trail_start_pct,
                trailing_stop_pct=trailing_stop_pct,
                min_profit_sell_pct=min_profit_sell_pct,
                position_size_pct=position_size_pct
            )
        except Exception as e:
            print(f"DAY bot cycle error: {e}")
            send_telegram_alert(f"DAY BOT ERROR\n{e}")

        print(f"Day bot sleeping for {cycle_seconds} seconds...")
        time.sleep(cycle_seconds)