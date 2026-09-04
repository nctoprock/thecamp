#!/usr/bin/env python3
"""
TradingView alert webhook receiver.

TradingView does not expose a public API for pulling quotes or running a
screener on demand. What it does offer (on paid plans) is outgoing alert
webhooks: when an alert you configure in the TradingView UI fires, it sends
one HTTP POST to a URL you specify. This script is a minimal server for
receiving those POSTs, logging them, and exposing the recent ones over a
simple JSON endpoint.

This is push-based and reactive only -- it can only tell you about
conditions you've already set up as alerts inside TradingView. It cannot
scan the market or answer "what's moving right now" the way a real
screener API (like the Alpaca-based one in ../screener/) can.

Setup:
  1. pip install -r requirements.txt
  2. Set a shared secret so random internet traffic can't spoof alerts:
       export TV_WEBHOOK_SECRET=some-long-random-string
  3. Run the server:
       python webhook_receiver.py
     It listens on 0.0.0.0:8000 by default (set PORT to change).
  4. Deploy it somewhere with a public URL TradingView can reach (this
     sandbox is not internet-reachable). Options: a small VM, Render,
     Fly.io, PythonAnywhere, or `ngrok http 8000` for local testing.
  5. In TradingView, create an alert -> under "Notifications" enable
     "Webhook URL" -> set it to:
       https://your-host/webhook?secret=some-long-random-string
     Message body (JSON is easiest to parse), using TradingView's
     placeholders:
       {
         "ticker": "{{ticker}}",
         "price": {{close}},
         "volume": {{volume}},
         "time": "{{time}}",
         "note": "your alert condition description"
       }

Endpoints:
  POST /webhook?secret=...   receive one alert
  GET  /alerts               list the most recent received alerts (JSON)
  GET  /healthz              liveness check
"""

import json
import os
import time
from collections import deque

from flask import Flask, jsonify, request

app = Flask(__name__)

MAX_ALERTS = 200
_alerts = deque(maxlen=MAX_ALERTS)


def _check_secret():
    expected = os.environ.get("TV_WEBHOOK_SECRET")
    if not expected:
        # No secret configured -- refuse to run open to the internet.
        return False
    provided = request.args.get("secret") or request.headers.get("X-Webhook-Secret")
    return provided == expected


@app.route("/webhook", methods=["POST"])
def webhook():
    if not _check_secret():
        return jsonify({"error": "unauthorized"}), 401

    raw = request.get_data(as_text=True)
    payload = None
    if request.is_json:
        payload = request.get_json(silent=True)
    if payload is None:
        try:
            payload = json.loads(raw)
        except (ValueError, TypeError):
            payload = {"raw_message": raw}

    record = {
        "received_at": time.time(),
        "remote_addr": request.remote_addr,
        "payload": payload,
    }
    _alerts.appendleft(record)
    print(f"[alert] {record}")
    return jsonify({"status": "ok"}), 200


@app.route("/alerts", methods=["GET"])
def alerts():
    return jsonify(list(_alerts))


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    if not os.environ.get("TV_WEBHOOK_SECRET"):
        raise SystemExit(
            "Set TV_WEBHOOK_SECRET before starting the server -- otherwise "
            "anyone who finds this URL can post fake alerts."
        )
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
