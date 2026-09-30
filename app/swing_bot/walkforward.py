from app.swing_bot.strategy import moving_average_strategy
from app.swing_bot.portfolio import run_backtest
from app.swing_bot.analyzer import analyze_results


def run_walkforward_test(
    df,
    starting_balance=10000,
    fee_rate=0.001,
    stop_loss_pct=0.04,
    position_size_pct=0.25,
    train_bars=500,
    test_bars=250
):
    results = []

    start = 0
    window_number = 1

    while start + train_bars + test_bars <= len(df):
        train_df = df.iloc[start:start + train_bars].copy()
        test_df = df.iloc[start + train_bars:start + train_bars + test_bars].copy()

        # For now we are not optimizing on train_df yet,
        # but we keep the structure because that is how real walk-forward systems are built.
        _ = moving_average_strategy(train_df)

        test_df = moving_average_strategy(test_df)

        final_value, trades, equity_curve = run_backtest(
            test_df,
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

        metrics["Window"] = window_number
        results.append(metrics)

        start += test_bars
        window_number += 1

    return results