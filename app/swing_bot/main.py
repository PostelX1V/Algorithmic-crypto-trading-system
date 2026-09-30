from app.swing_bot.paper_trader import run_continuous_paper_trader


def main():
    run_continuous_paper_trader(
        product_ids=("BTC-USD", "SOL-USD"),
        fee_rate=0.006,
        stop_loss_pct=0.04,
        starting_cash=7000.0,
        cycle_seconds=3600
    )


if __name__ == "__main__":
    main()