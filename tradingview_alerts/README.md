# TradingView Alert Webhook Receiver

## Important: this is not a screener

TradingView does not have a public API for querying quotes, running a
screener, or pulling chart data on demand. The only outbound integration it
offers (on paid plans: Essential and above) is **alert webhooks** — when an
alert you've configured in TradingView's UI fires, it sends one HTTP POST
to a URL you choose.

That means this tool can only ever tell you about conditions you've already
defined as alerts in TradingView (e.g. "RSI crosses above 70", "volume >
3x average", "price crosses a level"). It's push-based and reactive, not a
general "show me what's volatile right now" scanner. For that, use the
Alpaca-based screener in `../screener/`, which supports real on-demand
queries.

These two tools are complementary: use the Alpaca screener to find unusual
activity, and TradingView alerts/webhooks to get notified the instant a
specific setup you already care about triggers.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Choose a long random secret and set it as an environment variable
   (TradingView doesn't sign its webhook requests, so this is the only
   thing stopping randos on the internet from posting fake alerts to your
   endpoint):
   ```
   export TV_WEBHOOK_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
   ```
3. Run the server locally:
   ```
   python webhook_receiver.py
   ```
   It listens on port 8000 by default (`PORT` env var to change it).

4. **Deploy it somewhere with a public URL.** TradingView's servers need to
   reach your endpoint over the internet, so `localhost` will not work.
   Options:
   - Quick testing: `ngrok http 8000` and use the ngrok URL.
   - A small always-on host: Render, Fly.io, Railway, PythonAnywhere, or a
     $5/mo VM.
   Whichever you use, make sure `TV_WEBHOOK_SECRET` is set in that
   environment too.

## Configure the TradingView alert

1. On a chart, click **Alert** and set your condition (price, indicator,
   strategy, etc.).
2. Under **Notifications**, enable **Webhook URL** and enter:
   ```
   https://your-deployed-host/webhook?secret=YOUR_SECRET
   ```
3. In the **Message** box, send JSON using TradingView's placeholders so
   the payload is structured instead of free text:
   ```json
   {
     "ticker": "{{ticker}}",
     "price": {{close}},
     "volume": {{volume}},
     "time": "{{time}}",
     "note": "RSI > 70 and volume > 3x avg"
   }
   ```
   (Requires webhook alerts, available on TradingView's paid plans.)

## Using it

- `POST /webhook?secret=...` — what TradingView calls. Returns 401 if the
  secret doesn't match.
- `GET /alerts` — the most recent 200 alerts received, newest first, as
  JSON. Poll this from another script, a dashboard, or just check it in a
  browser.
- `GET /healthz` — liveness check for your host/uptime monitor.

This script only logs alerts in memory (cleared on restart) and prints
them to stdout. It does not place trades, does not persist to a database,
and is not financial advice — it's plumbing to get your own TradingView
alert conditions somewhere you can act on them.
