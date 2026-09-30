def aggregate_portfolio_results(all_results):
    """
    Combine walk-forward results from multiple assets into an equal-weight portfolio.

    all_results format:
    {
        "BTC-USD": [ {window metrics}, {window metrics}, ... ],
        "ETH-USD": [ {window metrics}, ... ],
        "SOL-USD": [ {window metrics}, ... ]
    }
    """

    product_ids = list(all_results.keys())

    if not product_ids:
        return [], {}

    num_windows = min(len(all_results[pid]) for pid in product_ids)

    portfolio_windows = []

    for i in range(num_windows):
        window_returns = []
        window_drawdowns = []
        window_trades = 0

        for pid in product_ids:
            w = all_results[pid][i]
            window_returns.append(w["Return %"])
            window_drawdowns.append(w["Max Drawdown %"])
            window_trades += w["Total Trades"]

        portfolio_return = sum(window_returns) / len(window_returns)

        # Conservative choice: take worst drawdown among assets for that window
        portfolio_drawdown = min(window_drawdowns)

        portfolio_windows.append({
            "Window": i + 1,
            "Portfolio Return %": portfolio_return,
            "Portfolio Max Drawdown %": portfolio_drawdown,
            "Portfolio Trades": window_trades
        })

    positive_windows = sum(1 for w in portfolio_windows if w["Portfolio Return %"] > 0)
    negative_windows = sum(1 for w in portfolio_windows if w["Portfolio Return %"] < 0)
    flat_windows = sum(1 for w in portfolio_windows if w["Portfolio Return %"] == 0)

    avg_window_return = (
        sum(w["Portfolio Return %"] for w in portfolio_windows) / len(portfolio_windows)
        if portfolio_windows else 0
    )

    worst_window_return = (
        min(w["Portfolio Return %"] for w in portfolio_windows)
        if portfolio_windows else 0
    )

    worst_window_drawdown = (
        min(w["Portfolio Max Drawdown %"] for w in portfolio_windows)
        if portfolio_windows else 0
    )

    total_trades = sum(w["Portfolio Trades"] for w in portfolio_windows)

    summary = {
        "Windows": len(portfolio_windows),
        "Avg Portfolio Window Return %": avg_window_return,
        "Worst Portfolio Window Return %": worst_window_return,
        "Worst Portfolio Window Drawdown %": worst_window_drawdown,
        "Total Portfolio Trades": total_trades,
        "Positive Windows": positive_windows,
        "Negative Windows": negative_windows,
        "Flat Windows": flat_windows,
    }

    return portfolio_windows, summary