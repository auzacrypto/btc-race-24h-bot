[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/auzacrypto/btc-race-24h-bot/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/auzacrypto/btc-race-24h-bot/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

# BTC race bot — patient dip buyer

A long-only cbBTC bot for the agent-fun/bars-replay/v1 protocol (1-minute
bars, paper USDC). It buys a stabilising bar after a >=1.6% pullback from
the trailing 6-hour high, sells on recovery to near the highs, a 1.5% hard
stop, or after 480 bars, and otherwise holds cash. See the docstring in
`main.py` for the full rules.

Run: `python3 -P -s main.py` (Python 3.13, standard library only;
`vendor/makefun_bars.py` is the kit's protocol shim, byte for byte).
