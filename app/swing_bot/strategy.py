import pandas as pd


def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(period).mean()

    return atr


def moving_average_strategy(
    df,
    short_window=10,
    long_window=30,
    rsi_period=14,
    rsi_buy_threshold=60,
    rsi_sell_threshold=70,
    atr_period=14,
    atr_filter_period=20
):
    df = df.copy()

    df["short_ma"] = df["close"].rolling(short_window).mean()
    df["long_ma"] = df["close"].rolling(long_window).mean()
    df["rsi"] = calculate_rsi(df["close"], period=rsi_period)
    df["atr"] = calculate_atr(df, period=atr_period)
    df["atr_avg"] = df["atr"].rolling(atr_filter_period).mean()

    df["long_ma_slope"] = df["long_ma"].diff()

    df["signal"] = 0

    buy_condition = (
        (df["short_ma"] > df["long_ma"]) &
        (df["rsi"] < rsi_buy_threshold) &
        (df["long_ma_slope"] > 0) &
        (df["atr"] > df["atr_avg"])
    )

    sell_condition = (
        (df["short_ma"] < df["long_ma"]) |
        (df["rsi"] > rsi_sell_threshold)
    )

    df.loc[buy_condition, "signal"] = 1
    df.loc[sell_condition, "signal"] = -1

    df["position"] = df["signal"].diff()

    return df