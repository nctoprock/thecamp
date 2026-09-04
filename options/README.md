# Options Chain Viewer

Lists option contracts for a given underlying stock, filtered by liquidity
(open interest, spread) and moneyness, with implied volatility and delta
shown. **It does not score or recommend contracts as "good trades."** It
surfaces data so you can apply your own judgment and risk management.

## Setup

1. Alpaca account + API keys (same as `../screener/`):
   ```
   export ALPACA_API_KEY_ID=...
   export ALPACA_API_SECRET_KEY=...
   ```
2. Options market data access:
   - Free tier: delayed "indicative" feed (default, `--feed indicative`).
   - Real-time OPRA data: requires Alpaca's paid options data add-on
     (Algo Trader Plus, ~$99/mo as of this writing — check your Alpaca
     dashboard, this changes). Use `--feed opra`.
3. Install deps: `pip install -r requirements.txt`

## Usage

```
python options_screener.py AAPL
python options_screener.py TSLA --type call --dte-min 14 --dte-max 30 --moneyness-pct 5
python options_screener.py NVDA --min-oi 200 --max-spread-pct 8 --sort-by iv
```

Columns:
- **Moneyness%** — how far the strike is from the current underlying price (0 = at-the-money).
- **Spread%** — (ask − bid) / mid, as a percent. Wider spread = more cost to enter/exit.
- **IV** — implied volatility from the snapshot.
- **Delta** — from Alpaca's greeks calculation.
- **OI** — open interest (contracts outstanding). Low OI = harder to exit at a fair price.

Default sort is by open interest (liquidity first) — deliberately not by
IV or any composite "best trade" score.

## A note on accuracy

This was built without a live Alpaca account or network access to verify
the exact options API response schema in this environment. The quote
field names (bid/ask) are assumed to follow Alpaca's standard short-key
convention (`bp`/`ap`), consistent with their stock quotes, but this
hasn't been confirmed against a real response. If bid/ask/IV columns come
back empty when you run it:
```
python options_screener.py AAPL --debug-raw
```
This prints one raw snapshot to stderr — check the actual field names
against [Alpaca's options snapshot docs](https://docs.alpaca.markets/reference/optionsnapshots)
and adjust `QUOTE_BID_KEYS` / `QUOTE_ASK_KEYS` at the top of
`options_screener.py` if needed.

## Risk notes specific to options

Options carry risks beyond the underlying stock's own volatility:
- **Time decay (theta)** — an option loses value as expiration approaches, even if the stock doesn't move against you.
- **Liquidity risk** — low open interest or wide spreads can mean a poor fill price or difficulty exiting at all.
- **Leverage** — a small move in the underlying can mean a much larger percentage move in the option's price, in either direction.
- **Assignment/expiration risk** — know your contract's exercise style and what happens if it expires in/out of the money.

This tool is for informational/research purposes only and is not financial advice.
