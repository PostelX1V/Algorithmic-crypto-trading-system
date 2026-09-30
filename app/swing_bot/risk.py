import pandas as pd


def calculate_volatility(df, period=50):
    returns = df["close"].pct_change()
    volatility = returns.rolling(period).std()
    return volatility


def calculate_position_size(df, target_risk=0.02, max_position_size=0.30):

    df = df.copy()

    df["volatility"] = calculate_volatility(df)

    # Prevent divide-by-zero
    df["volatility"] = df["volatility"].replace(0, 1e-8)

    # Fill missing values
    df["volatility"] = df["volatility"].bfill()
    df["volatility"] = df["volatility"].ffill()

    df["position_fraction"] = target_risk / df["volatility"]

    # Cap position size
    df["position_fraction"] = df["position_fraction"].clip(upper=max_position_size)

    return df