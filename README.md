# BTC race bot — patient dip buyer

A long-only cbBTC bot for the agent-fun/bars-replay/v1 protocol (1-minute
bars, paper USDC). It buys a stabilising bar after a >=1.6% pullback from
the trailing 6-hour high, sells on recovery to near the highs, a 1.5% hard
stop, or after 480 bars, and otherwise holds cash. See the docstring in
`main.py` for the full rules.

Run: `python3 -P -s main.py` (Python 3.13, standard library only;
`vendor/makefun_bars.py` is the kit's protocol shim, byte for byte).
