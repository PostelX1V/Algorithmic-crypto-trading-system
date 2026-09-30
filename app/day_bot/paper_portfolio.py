import json
import os
from datetime import datetime


class DayPaperPortfolio:
    def __init__(self, starting_cash=3000.0, state_file="data/logs/day_paper_portfolio_state.json"):
        self.state_file = state_file
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.positions = {}
        self.trade_history = []

        self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.cash = data.get("cash", self.starting_cash)
                self.positions = data.get("positions", {})
                self.trade_history = data.get("trade_history", [])

    def save_state(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "cash": self.cash,
                    "positions": self.positions,
                    "trade_history": self.trade_history,
                },
                f,
                indent=2
            )

    def has_position(self, product_id):
        return product_id in self.positions

    def update_highest_price(self, product_id, latest_price):
        if product_id not in self.positions:
            return

        current_high = self.positions[product_id].get("highest_price", self.positions[product_id]["entry_price"])

        if latest_price > current_high:
            self.positions[product_id]["highest_price"] = latest_price
            self.save_state()

    def buy(self, product_id, price, allocation, fee_rate=0.006):
        if allocation > self.cash:
            allocation = self.cash

        fee = allocation * fee_rate
        spendable_cash = allocation - fee

        if spendable_cash <= 0:
            return None

        quantity = spendable_cash / price
        self.cash -= allocation

        self.positions[product_id] = {
            "quantity": quantity,
            "entry_price": price,
            "highest_price": price,
            "entry_time": datetime.utcnow().isoformat()
        }

        trade = {
            "timestamp": datetime.utcnow().isoformat(),
            "product_id": product_id,
            "side": "BUY",
            "price": price,
            "allocation": allocation,
            "quantity": quantity,
            "fee": fee
        }

        self.trade_history.append(trade)
        self.save_state()
        return trade

    def sell(self, product_id, price, fee_rate=0.006, reason="SELL_SIGNAL"):
        if product_id not in self.positions:
            return None

        position = self.positions[product_id]
        quantity = position["quantity"]
        entry_price = position["entry_price"]

        gross_value = quantity * price
        fee = gross_value * fee_rate
        proceeds = gross_value - fee

        original_cost = quantity * entry_price
        pnl = proceeds - original_cost
        pnl_pct = pnl / original_cost if original_cost > 0 else 0

        self.cash += proceeds
        del self.positions[product_id]

        trade = {
            "timestamp": datetime.utcnow().isoformat(),
            "product_id": product_id,
            "side": "SELL",
            "price": price,
            "quantity": quantity,
            "fee": fee,
            "reason": reason,
            "pnl": pnl,
            "pnl_pct": pnl_pct
        }

        self.trade_history.append(trade)
        self.save_state()
        return trade

    def total_equity(self, latest_prices):
        equity = self.cash

        for product_id, position in self.positions.items():
            if product_id in latest_prices:
                equity += position["quantity"] * latest_prices[product_id]

        return equity