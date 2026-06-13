"""
Telegram Webhook Server — SMC+AMD ULTRA PRO
يستقبل إشارات من TradingView ويرسلها إلى Telegram
"""

from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID   = os.getenv("CHAT_ID",   "YOUR_CHAT_ID_HERE")


def send_telegram(text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(
        url,
        json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
        timeout=10
    )
    return r.ok


@app.route("/webhook", methods=["POST"])
def webhook():
    raw = request.get_data(as_text=True)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return "Invalid JSON", 400

    signal  = str(data.get("signal",   "?")).upper()
    symbol  = data.get("symbol",   "?")
    price   = data.get("price",    "?")
    time_   = data.get("time",     "?")
    session = data.get("session",  "?")

    is_buy = signal == "BUY"
    emoji  = "📈" if is_buy else "📉"
    dot    = "🟢" if is_buy else "🔴"

    msg = (
        f"{emoji} <b>SMC+AMD ULTRA PRO — {signal}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{dot} <b>الإشارة:</b>  {signal}\n"
        f"💹 <b>الرمز:</b>    {symbol}\n"
        f"💰 <b>السعر:</b>    {price}\n"
        f"🏛 <b>الجلسة:</b>   {session}\n"
        f"🕐 <b>الوقت:</b>    {time_}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<i>⚠️ القرار النهائي لك دائماً</i>"
    )

    ok = send_telegram(msg)
    return ("OK" if ok else "Telegram error"), (200 if ok else 500)


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


if __name__ == "__main__":
    print("🤖 SMC+AMD Webhook Server")
    print(f"📡 POST → http://YOUR_SERVER:8080/webhook")
    app.run(host="0.0.0.0", port=8080, debug=False)
