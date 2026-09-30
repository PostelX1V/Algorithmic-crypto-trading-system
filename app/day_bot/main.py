from app.day_bot.trader import run_continuous_day_trader


def main():
    run_continuous_day_trader(
        product_id="BTC-USD",
        starting_cash=3000.0,
        fee_rate=0.006,
        stop_loss_pct=0.007,
        take_profit_pct=0.018,
        trail_start_pct=0.010,
        trailing_stop_pct=0.005,
        min_profit_sell_pct=0.013,
        position_size_pct=0.25,
        cycle_seconds=900
    )


if __name__ == "__main__":
    main()