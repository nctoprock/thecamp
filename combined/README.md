# Combined Report

Ties together the three tools in this repo into one report:

1. **Equity screener** (`../screener/`) — market-wide movers/most-actives, plus your own watchlist scored by relative volume x ATR%.
2. **Options chain viewer** (`../options/`) — for the top few symbols from step 1, pulls near-the-money contracts filtered by liquidity.
3. **TradingView alerts** (`../tradingview_alerts/`) — if you're running the webhook receiver somewhere public, pulls in any alerts that recently fired on the same symbols.

It prints one report grouped by symbol. **It does not score "best trades" or tell you what to buy.** Every number in it comes from a threshold you set (min open interest, max spread, DTE range, etc.) — it's a faster way to see your own criteria applied across several symbols and two data sources, not a signal.

## Setup

Same Alpaca credentials as the other tools:
```
export ALPACA_API_KEY_ID=...
export ALPACA_API_SECRET_KEY=...
```

Optional, if you have the TradingView webhook receiver deployed somewhere public:
```
export TV_ALERTS_URL=https://your-deployed-host
export TV_WEBHOOK_SECRET=the-same-secret-you-configured-there
```
Without these two set, the report just skips the TradingView alerts section.

Install deps (shared with the other two tools, `requests` is the only one needed here beyond what they already require):
```
pip install -r ../screener/requirements.txt
```

## Usage

```
python combined_report.py
python combined_report.py --watchlist ../screener/watchlist.example.txt
python combined_report.py --watchlist my_list.txt --max-candidates 3 --option-type call
```

Key flags:
- `--max-candidates` — caps how many symbols get an options chain pulled (keeps API call count bounded; each symbol costs one contracts call + one snapshot call).
- `--option-dte-min` / `--option-dte-max` — expiration window for the options chain.
- `--option-moneyness-pct` — how far from the current price to include strikes.
- `--feed indicative|opra` — options data feed; `opra` needs Alpaca's real-time options subscription.

See `../options/README.md` for a note on unverified quote field names in the options data (this was built without live-account access to confirm the exact schema) — if IV/bid/ask show up blank, that's the first thing to check.

## Risk management

Read `../screener/README.md` and `../options/README.md` before acting on anything this prints — position sizing, stop losses, and options-specific risks (theta decay, liquidity, leverage) are covered there. This tool is informational only and is not financial advice.
