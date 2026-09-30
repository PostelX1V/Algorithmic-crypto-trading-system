import numpy as np


def analyze_results(trades, starting_balance, final_value, equity_curve):
    results = {}

    results["Starting Balance"] = starting_balance
    results["Final Balance"] = final_value
    results["Return %"] = ((final_value - starting_balance) / starting_balance) * 100

    completed_trade_pnls = []
    wins = 0
    losses = 0

    for trade in trades:
        if trade["side"] == "SELL":
            pnl = trade.get("pnl", 0.0)
            completed_trade_pnls.append(pnl)

            if pnl > 0:
                wins += 1
            else:
                losses += 1

    total_trades = len(completed_trade_pnls)
    results["Total Trades"] = total_trades

    if total_trades > 0:
        results["Win Rate %"] = (wins / total_trades) * 100
        results["Average Trade PnL"] = float(np.mean(completed_trade_pnls))

        gross_profit = sum(p for p in completed_trade_pnls if p > 0)
        gross_loss = abs(sum(p for p in completed_trade_pnls if p < 0))
        results["Profit Factor"] = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    else:
        results["Win Rate %"] = 0
        results["Average Trade PnL"] = 0
        results["Profit Factor"] = 0

    if equity_curve:
        equity_array = np.array(equity_curve, dtype=float)
        running_max = np.maximum.accumulate(equity_array)
        drawdowns = (equity_array - running_max) / running_max
        results["Max Drawdown %"] = float(drawdowns.min() * 100)
    else:
        results["Max Drawdown %"] = 0

    return results