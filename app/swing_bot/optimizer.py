from itertools import product

from app.swing_bot.strategy import moving_average_strategy
from app.swing_bot.portfolio import run_backtest
from app.swing_bot.analyzer import analyze_results


def optimize_strategy(
    df,
    starting_balance=10000,
    fee_rate=0.006,
    stop_loss_pct=0.04,
    position_size_pct=0.25,
    short_windows=(8, 10, 12),
    long_windows=(25, 30, 40),
    rsi_buy_thresholds=(55, 60, 65),
    atr_filter_periods=(10, 20, 30),
):
    results = []

    for short_window, long_window, rsi_buy_threshold, atr_filter_period in product(
        short_windows,
        long_windows,
        rsi_buy_thresholds,
        atr_filter_periods
    ):
        if short_window >= long_window:
            continue

        strategy_df = moving_average_strategy(
            df,
            short_window=short_window,
            long_window=long_window,
            rsi_buy_threshold=rsi_buy_threshold,
            atr_filter_period=atr_filter_period,
        )

        final_value, trades, equity_curve = run_backtest(
            strategy_df,
            starting_balance=starting_balance,
            fee_rate=fee_rate,
            stop_loss_pct=stop_loss_pct,
            position_size_pct=position_size_pct
        )

        metrics = analyze_results(
            trades=trades,
            starting_balance=starting_balance,
            final_value=final_value,
            equity_curve=equity_curve
        )

        results.append({
            "short_window": short_window,
            "long_window": long_window,
            "rsi_buy_threshold": rsi_buy_threshold,
            "atr_filter_period": atr_filter_period,
            "return_pct": metrics["Return %"],
            "profit_factor": metrics["Profit Factor"],
            "max_drawdown_pct": metrics["Max Drawdown %"],
            "total_trades": metrics["Total Trades"],
        })

    # Rank by return first, then lower drawdown
    results.sort(
        key=lambda x: (x["return_pct"], -abs(x["max_drawdown_pct"])),
        reverse=True
    )

    return results