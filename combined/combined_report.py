#!/usr/bin/env python3
"""
Combined activity report: equity movers/watchlist scoring (Alpaca) +
near-the-money options chains for the most active names (Alpaca) +
any TradingView alerts that recently fired (via the webhook receiver).

This prints a single report grouped by symbol. It is a data summary
built from criteria you control (thresholds below, your watchlist, your
TradingView alerts) -- it does not decide or claim that any of this is a
"good trade." Treat it as a faster way to see everything in one place,
not a signal to act on.

Requires:
  - ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY (see ../screener/README.md)
  - Optionally TV_ALERTS_URL and TV_WEBHOOK_SECRET, if you're running the
    TradingView webhook receiver in ../tradingview_alerts/ somewhere with
    a public URL. Without these, the alerts section is skipped.
"""

import argparse
import os
import sys

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "screener"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "options"))

import volatility_screener as eq  # noqa: E402
import options_screener as opt  # noqa: E402


def fetch_recent_alerts():
    base = os.environ.get("TV_ALERTS_URL")
    secret = os.environ.get("TV_WEBHOOK_SECRET")
    if not base:
        return []
    try:
        resp = requests.get(
            base.rstrip("/") + "/alerts", params={"secret": secret}, timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"[warn] could not fetch TradingView alerts: {e}", file=sys.stderr)
        return []


def pick_candidate_symbols(movers, watchlist_rows, max_candidates):
    candidates = []
    for direction in ("gainers", "losers"):
        for e in movers.get(direction, [])[:3]:
            candidates.append(e["symbol"])
    for r in watchlist_rows[:5]:
        candidates.append(r["symbol"])
    # de-dup, preserve order
    seen = set()
    unique = []
    for s in candidates:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique[:max_candidates]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--watchlist",
        help="Optional path to a text file of tickers to include alongside market-wide movers.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=5,
        help="Cap on how many underlyings to pull option chains for (keeps API calls bounded).",
    )
    parser.add_argument(
        "--top-movers", type=int, default=10, help="How many market-wide movers to fetch."
    )
    parser.add_argument(
        "--option-type", choices=["call", "put", "both"], default="both"
    )
    parser.add_argument("--option-dte-min", type=int, default=7)
    parser.add_argument("--option-dte-max", type=int, default=45)
    parser.add_argument("--option-moneyness-pct", type=float, default=8.0)
    parser.add_argument("--option-min-oi", type=int, default=50)
    parser.add_argument("--option-max-spread-pct", type=float, default=15.0)
    parser.add_argument(
        "--feed",
        choices=["indicative", "opra"],
        default="indicative",
        help="Options data feed -- 'opra' requires Alpaca's real-time options subscription.",
    )
    args = parser.parse_args()

    print("=== Market-wide movers ===")
    movers = eq.get_movers(top=args.top_movers)

    watchlist_rows = []
    if args.watchlist:
        with open(args.watchlist) as f:
            symbols = [line.strip().upper() for line in f if line.strip()]
        watchlist_rows = eq.score_watchlist(symbols)

    candidates = pick_candidate_symbols(movers, watchlist_rows, args.max_candidates)
    if not candidates:
        print("No candidate symbols found (empty movers and no watchlist). Exiting.")
        return

    alerts = fetch_recent_alerts()

    watchlist_by_symbol = {r["symbol"]: r for r in watchlist_rows}
    gainers_by_symbol = {e["symbol"]: e for e in movers.get("gainers", [])}
    losers_by_symbol = {e["symbol"]: e for e in movers.get("losers", [])}

    print(f"\nCandidates selected for detail: {', '.join(candidates)}\n")

    for sym in candidates:
        print("=" * 60)
        print(f"{sym}")
        print("=" * 60)

        if sym in gainers_by_symbol:
            e = gainers_by_symbol[sym]
            print(f"  Market mover (gainer): price {e['price']}, {e['percent_change']:.2f}%")
        if sym in losers_by_symbol:
            e = losers_by_symbol[sym]
            print(f"  Market mover (loser): price {e['price']}, {e['percent_change']:.2f}%")
        if sym in watchlist_by_symbol:
            r = watchlist_by_symbol[sym]
            print(
                f"  Watchlist score: price {r['price']:.2f}, %chg {r['pct_change']:.2f}, "
                f"RelVol {r['rel_volume']:.2f}x, ATR%% {r['atr_pct']:.2f}, score {r['score']:.2f}"
            )

        sym_alerts = [
            a for a in alerts if str(a.get("payload", {}).get("ticker", "")).upper() == sym
        ]
        if sym_alerts:
            print(f"  TradingView alerts fired ({len(sym_alerts)} recent):")
            for a in sym_alerts[:3]:
                p = a.get("payload", {})
                print(f"    - {p.get('note', p)}")
        else:
            print("  TradingView alerts: none recent (or receiver not configured)")

        try:
            price, rows = opt.build_chain_view(
                sym,
                args.option_dte_min,
                args.option_dte_max,
                args.option_type,
                args.option_max_spread_pct,
                args.option_min_oi,
                args.option_moneyness_pct,
                args.feed,
            )
        except Exception as e:  # noqa: BLE001 -- keep the report going for other symbols
            print(f"  Options chain: could not fetch ({e})")
            continue

        rows.sort(key=lambda r: r.get("oi") or 0, reverse=True)
        rows = rows[:5]
        if rows:
            print(f"  Near-the-money options (underlying price {price}), top {len(rows)} by open interest:")
            for r in rows:
                print(
                    f"    - {r['symbol']}: {r['type']} strike {r['strike']} exp {r['expiry']} "
                    f"(DTE {r['dte']}), mid {r['mid']}, spread {r['spread_pct']}%, "
                    f"IV {r['iv']}, delta {r['delta']}, OI {r['oi']}"
                )
        else:
            print("  Near-the-money options: none matched the liquidity filters")
        print()

    print(
        "This report summarizes data against thresholds you configured -- it is not a "
        "recommendation. Verify everything against your own broker/data before trading, "
        "and apply position sizing and stop-loss discipline (see ../screener/README.md)."
    )


if __name__ == "__main__":
    main()
