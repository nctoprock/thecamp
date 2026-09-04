# Volatility Screener

A small script that pulls market data from Alpaca and surfaces stocks that
are moving unusually today. It does **not** place trades and does **not**
tell you what to buy — it ranks and displays data so you can do your own
research and apply your own risk management.

## Setup

1. Create a free Alpaca account (paper trading tier is enough for market
   data access): https://alpaca.markets/
2. Generate an API key/secret pair from your Alpaca dashboard.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set your credentials as environment variables:
   ```
   export ALPACA_API_KEY_ID=your_key_id
   export ALPACA_API_SECRET_KEY=your_secret_key
   ```

## Usage

Market-wide top gainers/losers and most-active stocks:
```
python volatility_screener.py
```

Score your own watchlist by relative volume x ATR% (today's volatility vs.
that stock's own 20-day norm — this is what actually flags a stock "acting
crazy" relative to itself, rather than just "moved a lot in dollar terms"):
```
python volatility_screener.py --watchlist watchlist.example.txt
```

Limit output rows or skip the market-wide sections:
```
python volatility_screener.py --top 5 --skip-market-movers --watchlist watchlist.example.txt
```

## What the numbers mean

- **% Chg** — today's close vs. prior close (or latest available bar).
- **RelVol** — today's volume divided by the symbol's average daily volume
  over the past 20 sessions. > 2 means today's volume is 2x+ normal.
- **ATR%** — 20-day average true range as a percent of price. A rough
  measure of how much a stock typically swings per day.
- **Score** — RelVol x ATR%, a simple combined "this is moving more than
  usual" ranking. Higher = more unusual activity, not "better trade."

Free-tier Alpaca market data (IEX feed) is real-time-ish but not the full
consolidated tape — treat exact prices/volumes as indicative, not
execution-grade.

## Risk management (read this before trading anything this script surfaces)

Volatile stocks cut both ways — the same swings that create opportunity can
blow up an account fast. Two rules to actually use:

**Position sizing** — risk a fixed % of account equity per trade (commonly
1-2%), not a fixed number of shares:
```
shares = (account_equity x risk_%) / (entry_price - stop_price)
```
A wider stop on a volatile name should shrink your share count
automatically — don't fight that by tightening the stop just to buy more
shares.

**Stop losses** — decide the exit before you enter, and use a real stop
order (not a mental one — volatile stocks move too fast to react by hand):
- Base the stop on a real level (support, moving average) or a
  volatility-based distance like 1.5-3x ATR, not an arbitrary %.
- Never move a stop further away once set.
- Volatile names can gap through stops overnight — size for that risk, not
  just the stop distance.

This tool is for informational/research purposes only and is not financial
advice.
