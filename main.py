"""BTC race bot: a patient dip buyer (mean reversion with hard risk limits).

The bot trades one idea, sized at the whole equity, and otherwise sits in
cash:

  - Entry: the close has fallen at least DIP_BPS (1.6%) below the highest
    close of the last LOOK (360) bars, and the bar itself turns up (its close
    is above the previous bar's close), the first sign the fall is stopping.
    Deep pullbacks in BTC minute bars overshoot; buying the stabilising bar
    after a 1.6% slide captures the snap-back instead of chasing breakouts
    that, at these bar lengths, mostly fail.
  - Exit, whichever comes first: the close recovers to within EXIT_BPS
    (0.2%) of the trailing high (the snap-back is done); the close falls
    STOP_BPS (1.5%) below the entry close (the dip was a real break, cut
    it); or MAX_HOLD (480) bars pass (the idea has had its chance).
  - Fallback: if the window is three quarters gone (bar FALLBACK_SEQ) and
    the bot has never held a position, it buys once at a close at least
    0.4% below the trailing high, so a window with no deep dip still sees
    it trade (the race guardrails ask for at least one trade) under the
    same exit rules.

A full-size round trip pays roughly 40 bps in fees, slippage and price
impact, so the bot trades rarely: on the dev window it trades 6 times.
Every order caps its slippage at MAX_SLIPPAGE_BPS past the close it was
decided on, so a fill into a gap is refused and re-decided on the next bar
instead of filled at a ruinous price. All arithmetic is on integers, so
two runs on the same bars give the same orders, byte for byte.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

LOOK = 360
DIP_BPS = 160
EXIT_BPS = 20
STOP_BPS = 150
MAX_HOLD = 480
FALLBACK_SEQ = 1080
FALLBACK_MIN_DIP_BPS = 40
MAX_SLIPPAGE_BPS = 200


class Series:
    """One symbol's state: its closes, and the open trade's marks."""

    def __init__(self):
        self.closes = []
        self.entry_close = None
        self.entry_seq = None
        self.ever_held = False

    def push(self, bar):
        self.closes.append(int(bar["c"]))

    def trailing_high(self, n):
        """Highest close of the last n bars, this one included, or None."""
        if len(self.closes) < n:
            return None
        return max(self.closes[-n:])


SERIES = {}


def _buy(state, symbol, series, close, seq):
    """A whole-equity buy order for the symbol, or None if it cannot be sent."""
    stake = state.equity
    room = state.weight_room(symbol)
    if room < stake:
        stake = room
    if state.cash < stake:
        stake = state.cash
    min_notional = int(state.hello["fees"]["min_notional_quote_units"])
    if stake < min_notional or stake <= 0:
        return None
    series.entry_close = close
    series.entry_seq = seq
    return {
        "side": "buy",
        "symbol": symbol,
        "notional_quote_units": stake,
        "max_slippage_bps": MAX_SLIPPAGE_BPS,
    }


def on_batch(state, batch):
    fresh = set()
    for bar in batch["bars"]:
        s = SERIES.get(bar["symbol"])
        if s is None:
            s = SERIES[bar["symbol"]] = Series()
        s.push(bar)
        fresh.add(bar["symbol"])
    if state.warming_up:
        return []

    orders = []
    for symbol in fresh:
        s = SERIES[symbol]
        if len(s.closes) < 3:
            continue
        close = s.closes[-1]
        prev = s.closes[-2]
        high = s.trailing_high(LOOK)
        held = state.positions.get(symbol)
        if held is not None:
            s.ever_held = True
            exit_now = False
            if high is not None and close >= high * (10000 - EXIT_BPS) // 10000:
                exit_now = True
            if s.entry_close is not None and close < s.entry_close * (10000 - STOP_BPS) // 10000:
                exit_now = True
            if s.entry_seq is not None and state.seq - s.entry_seq >= MAX_HOLD:
                exit_now = True
            if exit_now:
                orders.append({
                    "side": "sell",
                    "symbol": symbol,
                    "qty": held.qty,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                })
                s.entry_close = None
                s.entry_seq = None
        elif high is not None:
            dipped = close <= high * (10000 - DIP_BPS) // 10000
            if dipped and close > prev:
                order = _buy(state, symbol, s, close, state.seq)
                if order is not None:
                    orders.append(order)
            elif (
                not s.ever_held
                and s.entry_close is None
                and state.seq >= FALLBACK_SEQ
                and close <= high * (10000 - FALLBACK_MIN_DIP_BPS) // 10000
            ):
                order = _buy(state, symbol, s, close, state.seq)
                if order is not None:
                    orders.append(order)
    return orders


if __name__ == "__main__":
    makefun_bars.run(on_batch)
