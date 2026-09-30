from app.swing_bot.risk import calculate_position_size


def run_backtest(
    df,
    starting_balance=10000,
    fee_rate=0.006,
    stop_loss_pct=0.04,
    position_size_pct=0.25,
    use_volatility_sizing=True,
    target_risk=0.02,
    max_position_size=0.30
):
    df = df.copy()

    # Add dynamic position sizing
    if use_volatility_sizing:
        df = calculate_position_size(
            df,
            target_risk=target_risk,
            max_position_size=max_position_size
        )
    else:
        df["position_fraction"] = position_size_pct

    cash = starting_balance
    btc = 0.0
    in_position = False
    entry_price = None
    entry_cash_value = None

    trades = []
    equity_curve = []

    for i in range(len(df)):
        price = float(df.iloc[i]["close"])
        signal = df.iloc[i]["position"]

        equity = cash + (btc * price)
        equity_curve.append(equity)

        stop_triggered = (
            in_position and
            entry_price is not None and
            price <= entry_price * (1 - stop_loss_pct)
        )

        # BUY
        if signal == 2 and not in_position:
            position_fraction = float(df.iloc[i]["position_fraction"])

            # Safety guard
            if position_fraction <= 0:
                continue

            allocation = cash * position_fraction
            fee = allocation * fee_rate
            spendable_cash = allocation - fee

            if spendable_cash > 0:
                btc = spendable_cash / price
                cash -= allocation
                entry_price = price
                entry_cash_value = allocation
                in_position = True

                trades.append({
                    "side": "BUY",
                    "price": price,
                    "fee": fee,
                    "allocation": allocation,
                    "position_fraction": position_fraction,
                    "equity_after": cash + btc * price
                })

        # SELL
        elif in_position and (signal == -2 or stop_triggered):
            gross_value = btc * price
            fee = gross_value * fee_rate
            proceeds = gross_value - fee
            cash += proceeds

            trade_pnl = proceeds - entry_cash_value if entry_cash_value is not None else 0.0

            trades.append({
                "side": "SELL_STOP" if stop_triggered else "SELL",
                "price": price,
                "fee": fee,
                "equity_after": cash,
                "pnl": trade_pnl
            })

            btc = 0.0
            in_position = False
            entry_price = None
            entry_cash_value = None

        equity_curve[-1] = cash + (btc * price)

    final_value = cash + (btc * float(df.iloc[-1]["close"]))

    return final_value, trades, equity_curve