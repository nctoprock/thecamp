#!/usr/bin/env python3
"""
Options chain viewer using Alpaca's Trading API (contract metadata) and
Market Data API (live quotes, implied volatility, greeks).

This tool lists option contracts and their characteristics -- strike,
expiry, days-to-expiration, bid/ask spread, implied volatility, delta,
open interest -- filtered by liquidity and moneyness. It does NOT score
or recommend specific contracts as "good trades." It surfaces data so you
can apply your own judgment and risk management.

Requires:
  - An Alpaca account (paper trading is fine for the Trading API contract
    lookup) with API keys:
      export ALPACA_API_KEY_ID=...
      export ALPACA_API_SECRET_KEY=...
  - Options market data access. The free tier returns a delayed
    "indicative" feed; real-time OPRA data requires Alpaca's Algo Trader
    Plus subscription ($99/mo as of this writing -- check your dashboard,
    pricing changes). Use --feed to switch between "indicative" and
    "opra".

Note on field names: this script assumes Alpaca's options snapshot quote
fields follow the same short-key convention as their stock quotes (bp =
bid price, ap = ask price, bs/as = sizes). This has not been verified
against a live account in this environment (no network access to Alpaca's
docs from here). If quotes come back empty, run with --debug-raw to print
one raw snapshot and check the actual field names against
https://docs.alpaca.markets/reference/optionsnapshots, then adjust the
QUOTE_BID_KEYS / QUOTE_ASK_KEYS lists below.
"""

import argparse
import os
import sys
from datetime import date, timedelta

import requests

DATA_BASE = "https://data.alpaca.markets"
TRADING_BASE = os.environ.get("ALPACA_TRADING_BASE", "https://paper-api.alpaca.markets")

# Fallback key names to try, in order, in case the live schema differs
# from what's assumed above.
QUOTE_BID_KEYS = ["bp", "bid_price", "BidPrice", "bid"]
QUOTE_ASK_KEYS = ["ap", "ask_price", "AskPrice", "ask"]


def _headers():
    key = os.environ.get("ALPACA_API_KEY_ID")
    secret = os.environ.get("ALPACA_API_SECRET_KEY")
    if not key or not secret:
        sys.exit(
            "Missing credentials. Set ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY "
            "environment variables."
        )
    return {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret}


def _first_present(d, keys):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def get_underlying_price(symbol: str):
    """Latest trade price for the underlying, via the stock snapshot endpoint."""
    url = f"{DATA_BASE}/v2/stocks/{symbol}/snapshot"
    resp = requests.get(url, headers=_headers(), params={"feed": "iex"}, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    latest_trade = data.get("latestTrade") or {}
    if "p" in latest_trade:
        return latest_trade["p"]
    daily_bar = data.get("dailyBar") or {}
    return daily_bar.get("c")


def get_contracts(underlying: str, dte_min: int, dte_max: int, contract_type: str = "both"):
    """Contract metadata (strike, expiry, open interest) from the Trading API."""
    today = date.today()
    params = {
        "underlying_symbols": underlying,
        "expiration_date_gte": (today + timedelta(days=dte_min)).isoformat(),
        "expiration_date_lte": (today + timedelta(days=dte_max)).isoformat(),
        "status": "active",
        "limit": 200,
    }
    if contract_type in ("call", "put"):
        params["type"] = contract_type

    contracts = []
    url = f"{TRADING_BASE}/v2/options/contracts"
    page_token = None
    while True:
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(url, headers=_headers(), params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        contracts.extend(data.get("option_contracts", []))
        page_token = data.get("next_page_token")
        if not page_token:
            break
    return contracts


def get_snapshots(underlying: str, feed: str = "indicative"):
    """Latest quote, implied volatility, and greeks per contract symbol."""
    url = f"{DATA_BASE}/v1beta1/options/snapshots/{underlying}"
    params = {"feed": feed, "limit": 200}
    snapshots = {}
    page_token = None
    while True:
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(url, headers=_headers(), params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        snapshots.update(data.get("snapshots", {}))
        page_token = data.get("next_page_token")
        if not page_token:
            break
    return snapshots


def build_chain_view(
    underlying: str,
    dte_min: int,
    dte_max: int,
    contract_type: str,
    max_spread_pct: float,
    min_oi: int,
    moneyness_pct: float,
    feed: str,
    debug_raw: bool = False,
):
    price = get_underlying_price(underlying)
    contracts = get_contracts(underlying, dte_min, dte_max, contract_type)
    snapshots = get_snapshots(underlying, feed=feed)

    if debug_raw and snapshots:
        sample_symbol = next(iter(snapshots))
        print(f"[debug] raw snapshot for {sample_symbol}:", file=sys.stderr)
        print(snapshots[sample_symbol], file=sys.stderr)

    today = date.today()
    rows = []
    for c in contracts:
        sym = c.get("symbol")
        try:
            oi = int(c.get("open_interest") or 0)
        except (TypeError, ValueError):
            oi = 0
        if oi < min_oi:
            continue

        try:
            strike = float(c.get("strike_price"))
        except (TypeError, ValueError):
            continue

        if price and moneyness_pct is not None:
            if abs(strike - price) / price * 100 > moneyness_pct:
                continue

        exp = c.get("expiration_date")
        try:
            dte = (date.fromisoformat(exp) - today).days if exp else None
        except ValueError:
            dte = None

        snap = snapshots.get(sym, {}) or {}
        quote = snap.get("latestQuote") or {}
        bid = _first_present(quote, QUOTE_BID_KEYS)
        ask = _first_present(quote, QUOTE_ASK_KEYS)
        mid = (bid + ask) / 2 if bid and ask else None
        spread_pct = ((ask - bid) / mid * 100) if mid else None
        if spread_pct is not None and spread_pct > max_spread_pct:
            continue

        greeks = snap.get("greeks") or {}
        iv = snap.get("impliedVolatility")

        rows.append(
            {
                "symbol": sym,
                "type": c.get("type"),
                "strike": strike,
                "expiry": exp,
                "dte": dte,
                "moneyness_pct": ((strike - price) / price * 100) if price else None,
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "spread_pct": spread_pct,
                "iv": iv,
                "delta": greeks.get("delta"),
                "oi": oi,
            }
        )
    return price, rows


def _display(v):
    if isinstance(v, float):
        return f"{v:.2f}"
    return f"{v}" if v is not None else "-"


def print_table(rows, columns, headers):
    if not rows:
        print("  (no contracts matched the filters)")
        return
    displayed = [{c: _display(r.get(c)) for c in columns} for r in rows]
    widths = [
        max(len(h), *(len(d[c]) for d in displayed))
        for c, h in zip(columns, headers)
    ]
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for d in displayed:
        line = [d[c].ljust(w) for c, w in zip(columns, widths)]
        print("  ".join(line))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("underlying", help="Underlying stock symbol, e.g. AAPL")
    parser.add_argument("--dte-min", type=int, default=7, help="Minimum days to expiration.")
    parser.add_argument("--dte-max", type=int, default=45, help="Maximum days to expiration.")
    parser.add_argument(
        "--type", choices=["call", "put", "both"], default="both", dest="contract_type"
    )
    parser.add_argument(
        "--max-spread-pct",
        type=float,
        default=15.0,
        help="Drop contracts with bid/ask spread wider than this %% of mid price.",
    )
    parser.add_argument(
        "--min-oi", type=int, default=50, help="Drop contracts with less open interest than this."
    )
    parser.add_argument(
        "--moneyness-pct",
        type=float,
        default=10.0,
        help="Only show strikes within this %% of the current underlying price.",
    )
    parser.add_argument(
        "--feed",
        choices=["indicative", "opra"],
        default="indicative",
        help="Options data feed. 'opra' requires Alpaca's real-time options subscription.",
    )
    parser.add_argument(
        "--sort-by",
        choices=["oi", "iv", "spread_pct", "dte"],
        default="oi",
        help="Sort order. Default is open interest (liquidity first), not IV or any 'best trade' score.",
    )
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument(
        "--debug-raw",
        action="store_true",
        help="Print one raw snapshot to stderr, to check field names against live data.",
    )
    args = parser.parse_args()

    price, rows = build_chain_view(
        args.underlying.upper(),
        args.dte_min,
        args.dte_max,
        args.contract_type,
        args.max_spread_pct,
        args.min_oi,
        args.moneyness_pct,
        args.feed,
        args.debug_raw,
    )

    print(f"=== {args.underlying.upper()} options (underlying price: {price}) ===")
    print(
        f"Filters: DTE {args.dte_min}-{args.dte_max}, type={args.contract_type}, "
        f"max spread {args.max_spread_pct}%, min OI {args.min_oi}, "
        f"moneyness within {args.moneyness_pct}%, feed={args.feed}\n"
    )

    reverse = args.sort_by != "spread_pct" and args.sort_by != "dte"
    rows.sort(key=lambda r: (r.get(args.sort_by) if r.get(args.sort_by) is not None else -1), reverse=reverse)
    rows = rows[: args.top]

    print_table(
        rows,
        ["symbol", "type", "strike", "expiry", "dte", "moneyness_pct", "bid", "ask", "spread_pct", "iv", "delta", "oi"],
        ["Symbol", "Type", "Strike", "Expiry", "DTE", "Moneyness%", "Bid", "Ask", "Spread%", "IV", "Delta", "OI"],
    )
    print(
        "\nThis is contract data only, sorted by your chosen filter -- not a recommendation. "
        "Low OI / wide spreads mean it may be hard to exit the position at a fair price."
    )


if __name__ == "__main__":
    main()
