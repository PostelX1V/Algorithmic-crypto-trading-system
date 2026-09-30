def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def day_trading_strategy(df, fast_ma=8, slow_ma=21, rsi_period=14):
    df = df.copy()

    df["fast_ma"] = df["close"].rolling(fast_ma).mean()
    df["slow_ma"] = df["close"].rolling(slow_ma).mean()
    df["rsi"] = calculate_rsi(df["close"], rsi_period)

    df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema_50"] = df["close"].ewm(span=50, adjust=False).mean()

    # New breakout filters
    df["recent_high"] = df["close"].rolling(10).max().shift(1)
    df["volume_avg"] = df["volume"].rolling(20).mean()

    df["signal"] = 0

    buy_condition = (
        (df["fast_ma"] > df["slow_ma"]) &
        (df["ema_20"] > df["ema_50"]) &
        (df["close"] > df["recent_high"]) &
        (df["volume"] > df["volume_avg"]) &
        (df["rsi"] > 55) &
        (df["rsi"] < 72)
    )

    sell_condition = (
        (df["fast_ma"] < df["slow_ma"]) |
        (df["rsi"] > 78)
    )

    df.loc[buy_condition, "signal"] = 1
    df.loc[sell_condition, "signal"] = -1

    df["position"] = df["signal"].diff()

    return df