import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone


PUBLIC_CANDLES_URL = "https://api.coinbase.com/api/v3/brokerage/market/products/{product_id}/candles"

GRANULARITY_TO_SECONDS = {
    "ONE_MINUTE": 60,
    "FIVE_MINUTE": 300,
    "FIFTEEN_MINUTE": 900,
    "THIRTY_MINUTE": 1800,
    "ONE_HOUR": 3600,
    "TWO_HOUR": 7200,
    "FOUR_HOUR": 14400,
    "SIX_HOUR": 21600,
    "ONE_DAY": 86400,
}


def fetch_candle_batch(product_id, start_time, end_time, granularity="FIVE_MINUTE", limit=350):
    params = {
        "start": str(int(start_time.timestamp())),
        "end": str(int(end_time.timestamp())),
        "granularity": granularity,
        "limit": limit,
    }

    url = PUBLIC_CANDLES_URL.format(product_id=product_id)
    response = requests.get(url, params=params, timeout=30)

    if response.status_code != 200:
        print(f"Batch failed: start={params['start']} end={params['end']} granularity={granularity} limit={limit}")
        print(f"Response: {response.text}")

    response.raise_for_status()

    data = response.json()
    return data.get("candles", [])


def get_btc_candles(product_id="BTC-USD", days=30, granularity="FIVE_MINUTE"):
    if granularity not in GRANULARITY_TO_SECONDS:
        raise ValueError(f"Unsupported granularity: {granularity}")

    seconds_per_candle = GRANULARITY_TO_SECONDS[granularity]

    # Stay comfortably below Coinbase's 350-candle max
    candles_per_batch = 300
    batch_seconds = candles_per_batch * seconds_per_candle

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days)

    current_start = start_time
    all_candles = []

    while current_start < end_time:
        current_end = min(
            current_start + timedelta(seconds=batch_seconds),
            end_time
        )

        candles = fetch_candle_batch(
            product_id=product_id,
            start_time=current_start,
            end_time=current_end,
            granularity=granularity,
            limit=350,
        )

        all_candles.extend(candles)

        # Move forward by exactly one candle to avoid overlap issues
        current_start = current_end + timedelta(seconds=seconds_per_candle)

        # Small pause to be polite to the API
        time.sleep(0.15)

    if not all_candles:
        raise ValueError("No candle data returned from Coinbase.")

    df = pd.DataFrame(all_candles)

    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["start"] = pd.to_datetime(df["start"].astype(int), unit="s", utc=True)

    df = (
        df.sort_values("start")
        .drop_duplicates(subset=["start"])
        .reset_index(drop=True)
    )

    return df


def save_candles_to_csv(df, filename="data/raw/btc_usd_5min.csv"):
    df.to_csv(filename, index=False)
    return filename