#!/usr/bin/env python3
"""
Volatility screener using Alpaca's Market Data API.

Surfaces stocks that are "acting crazy" today via two independent views:
  1. Market-wide movers/most-actives (Alpaca's built-in screener endpoints)
  2. A custom watchlist scored by relative volume and intraday range vs. its
     own recent average (ATR%), so you can see which names are moving more
     than they normally do -- not just which ones moved the most in $ terms.

Requires a free Alpaca account (paper trading is fine) and API keys:
  https://alpaca.markets/  ->  generate a key/secret pair
  export ALPACA_API_KEY_ID=...
  export ALPACA_API_SECRET_KEY=...

This tool only reads market data. It does not place trades and does not
recommend specific trades -- it ranks and displays data so you can do your
own research. See README.md in this folder for risk-management notes.
"""

import argparse
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone

import requests

DATA_BASE = "https://data.alpaca.markets"


def _headers():
    key = os.environ.get("ALPACA_API_KEY_ID")
    secret = os.environ.get("ALPACA_API_SECRET_KEY")
    if not key or not secret:
        sys.exit(
            "Missing credentials. Set ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY "
            "environment variables (see README.md)."
        )
    return {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret}


def get_movers(top: int = 10):
    """Top gainers/losers by % change, market-wide (Alpaca screener endpoint)."""
    url = f"{DATA_BASE}/v1beta1/screener/stocks/movers"
    resp = requests.get(url, headers=_headers(), params={"top": top}, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_most_actives(top: int = 10, by: str = "volume"):
    """Top names by trading volume or trade count, market-wide."""
    url = f"{DATA_BASE}/v1beta1/screener/stocks/most-actives"
    resp = requests.get(
        url, headers=_headers(), params={"top": top, "by": by}, timeout=15
    )
    resp.raise_for_status()
    return resp.json()


def get_daily_bars(symbol: str, lookback_days: int = 30):
    """Recent daily OHLCV bars for one symbol, oldest first."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days * 2)  # pad for weekends/holidays
    url = f"{DATA_BASE}/v2/stocks/{symbol}/bars"
    params = {
        "timeframe": "1Day",
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": lookback_days,
        "adjustment": "raw",
        "feed": "iex",
    }
    resp = requests.get(url, headers=_headers(), params=params, timeout=15)
    resp.raise_for_status()
    bars = resp.json().get("bars", [])
    return bars[-lookback_days:]


def score_watchlist(symbols, lookback_days: int = 20):
    """
    For each symbol, compute:
      - today's %% change (last close vs. prior close)
      - relative volume: today's volume / average volume over lookback
      - ATR%%: average true range over lookback, as a %% of price
    Returns rows sorted by relative volume * ATR%% (a simple "acting crazy" score).
    """
    rows = []
    for sym in symbols:
        try:
            bars = get_daily_bars(sym, lookback_days + 5)
        except requests.HTTPError as e:
            print(f"  skip {sym}: {e}", file=sys.stderr)
            continue
        if len(bars) < 3:
            print(f"  skip {sym}: not enough bars returned", file=sys.stderr)
            continue

        today = bars[-1]
        prior = bars[-2]
        history = bars[:-1][-lookback_days:]  # exclude today from the baseline

        pct_change = (today["c"] - prior["c"]) / prior["c"] * 100

        avg_volume = statistics.mean(b["v"] for b in history) if history else 0
        rel_volume = (today["v"] / avg_volume) if avg_volume else float("nan")

        true_ranges = []
        prev_close = history[0]["c"] if history else prior["c"]
        for b in history:
            tr = max(
                b["h"] - b["l"],
                abs(b["h"] - prev_close),
                abs(b["l"] - prev_close),
            )
            true_ranges.append(tr)
            prev_close = b["c"]
        atr = statistics.mean(true_ranges) if true_ranges else float("nan")
        atr_pct = (atr / today["c"] * 100) if today["c"] else float("nan")

        score = (rel_volume if rel_volume == rel_volume else 0) * (
            atr_pct if atr_pct == atr_pct else 0
        )

        rows.append(
            {
                "symbol": sym,
                "price": today["c"],
                "pct_change": pct_change,
                "rel_volume": rel_volume,
                "atr_pct": atr_pct,
                "score": score,
            }
        )

    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows


def print_table(rows, columns, headers):
    widths = [max(len(h), *(len(str(r.get(c, ""))) for r in rows)) if rows else len(h)
              for c, h in zip(columns, headers)]
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        line = []
        for c, w in zip(columns, widths):
            v = r.get(c, "")
            if isinstance(v, float):
                v = f"{v:.2f}"
            line.append(str(v).ljust(w))
        print("  ".join(line))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--watchlist",
        help="Path to a text file of tickers (one per line) to score by "
        "relative volume x ATR%%. Optional.",
    )
    parser.add_argument(
        "--top", type=int, default=10, help="How many rows to show per section."
    )
    parser.add_argument(
        "--skip-market-movers",
        action="store_true",
        help="Skip the market-wide movers/most-actives sections.",
    )
    args = parser.parse_args()

    if not args.skip_market_movers:
        print(f"=== Top {args.top} gainers/losers (market-wide) ===")
        movers = get_movers(top=args.top)
        for direction in ("gainers", "losers"):
            entries = movers.get(direction, [])
            rows = [
                {
                    "symbol": e["symbol"],
                    "price": e["price"],
                    "pct_change": e["percent_change"],
                }
                for e in entries
            ]
            print(f"\n-- {direction} --")
            print_table(
                rows, ["symbol", "price", "pct_change"], ["Symbol", "Price", "% Chg"]
            )

        print(f"\n=== Top {args.top} most active by volume (market-wide) ===")
        actives = get_most_actives(top=args.top).get("most_actives", [])
        rows = [
            {"symbol": e["symbol"], "volume": e["volume"], "trade_count": e["trade_count"]}
            for e in actives
        ]
        print_table(
            rows,
            ["symbol", "volume", "trade_count"],
            ["Symbol", "Volume", "Trades"],
        )

    if args.watchlist:
        with open(args.watchlist) as f:
            symbols = [line.strip().upper() for line in f if line.strip()]
        print(f"\n=== Watchlist volatility score ({len(symbols)} symbols) ===")
        print("score = relative volume (today vs 20-day avg) x ATR%% (20-day)\n")
        rows = score_watchlist(symbols)[: args.top]
        print_table(
            rows,
            ["symbol", "price", "pct_change", "rel_volume", "atr_pct", "score"],
            ["Symbol", "Price", "% Chg", "RelVol", "ATR%", "Score"],
        )


if __name__ == "__main__":
    main()
