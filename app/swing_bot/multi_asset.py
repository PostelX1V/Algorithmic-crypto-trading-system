from app.shared.market_data import get_btc_candles
from app.swing_bot.walkforward import run_walkforward_test


def run_multi_asset_walkforward(
    product_ids,
    days=365,
    granularity="ONE_HOUR",
    starting_balance=10000,
    fee_rate=0.006,
    stop_loss_pct=0.04,
    position_size_pct=0.25,
    train_bars=500,
    test_bars=250
):
    all_results = {}

    for product_id in product_ids:
        print(f"\nDownloading data for {product_id}...")

        df = get_btc_candles(
            product_id=product_id,
            days=days,
            granularity=granularity
        )

        print(f"{product_id}: {len(df)} rows downloaded")

        results = run_walkforward_test(
            df=df,
            starting_balance=starting_balance,
            fee_rate=fee_rate,
            stop_loss_pct=stop_loss_pct,
            position_size_pct=position_size_pct,
            train_bars=train_bars,
            test_bars=test_bars
        )

        all_results[product_id] = results

    return all_results