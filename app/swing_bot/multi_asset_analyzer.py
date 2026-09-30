def summarize_multi_asset_results(all_results):
    summary = {}

    for product_id, windows in all_results.items():
        total_return = 0
        total_trades = 0
        positive_windows = 0
        negative_windows = 0
        flat_windows = 0
        max_drawdown = 0

        for w in windows:
            total_return += w["Return %"]
            total_trades += w["Total Trades"]

            if w["Return %"] > 0:
                positive_windows += 1
            elif w["Return %"] < 0:
                negative_windows += 1
            else:
                flat_windows += 1

            max_drawdown = min(max_drawdown, w["Max Drawdown %"])

        avg_return = total_return / len(windows) if windows else 0

        summary[product_id] = {
            "Windows": len(windows),
            "Avg Window Return %": avg_return,
            "Total Trades": total_trades,
            "Positive Windows": positive_windows,
            "Negative Windows": negative_windows,
            "Flat Windows": flat_windows,
            "Worst Window Drawdown %": max_drawdown,
        }

    return summary