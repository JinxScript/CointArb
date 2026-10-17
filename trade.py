import requests


def get_current_prices(symbols):
    prices = {}
    for symbol in symbols:
        response = requests.get(
            f"https://api-pub.bitfinex.com/v2/ticker/{symbol}", timeout=10
        )
        response.raise_for_status()
        ticker = response.json()
        if not isinstance(ticker, list) or len(ticker) <= 6:
            raise ValueError(f"Unexpected ticker response for {symbol}: {ticker}")
        prices[symbol] = float(ticker[6])
    return prices


class Trade:

    def __init__(self):
        self.position = None
        self.last_realized_pnl = 0.0

    @property
    def is_open(self):
        return self.position is not None

    def open_spread(self, direction, pair1, pair2, hedge_ratio, entry_prices, quantity=1.0):
        if self.is_open:
            raise RuntimeError("A paper position is already open.")
        if direction not in ("long", "short"):
            raise ValueError("direction must be 'long' or 'short'.")
        if quantity <= 0:
            raise ValueError("quantity must be positive.")

        self.position = {
            "direction": direction,
            "pair1": pair1,
            "pair2": pair2,
            "hedge_ratio": float(hedge_ratio),
            "quantity": float(quantity),
            "entry_prices": {
                pair1: float(entry_prices[pair1]),
                pair2: float(entry_prices[pair2]),
            },
        }
        print(
            f"Opened paper {direction} spread {pair1}-{pair2} at "
            f"{pair1}={self.position['entry_prices'][pair1]}, "
            f"{pair2}={self.position['entry_prices'][pair2]}"
        )

    def get_pnl(self, current_prices):
        position = self.position
        if position is None:
            return 0.0

        pair1 = position["pair1"]
        pair2 = position["pair2"]
        entry_prices = position["entry_prices"]
        spread_change = (
            current_prices[pair2] - entry_prices[pair2]
            - position["hedge_ratio"]
            * (current_prices[pair1] - entry_prices[pair1])
        )
        direction = 1 if position["direction"] == "long" else -1
        return direction * position["quantity"] * spread_change

    def close_spread(self, current_prices):
        if not self.is_open:
            raise RuntimeError("There is no paper position to close.")
        self.last_realized_pnl = self.get_pnl(current_prices)
        self.position = None
        return self.last_realized_pnl