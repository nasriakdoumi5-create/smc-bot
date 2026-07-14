"""
TradingView Live Candle Fetcher — IFA-OS Data Source
────────────────────────────────────────────────────
يتصل بـ TradingView عبر tvdatafeed ويجلب الشموع الخام (OHLCV)
لـ MNQ / MGC / MCL على كل الأطر، ثم يرسلها إلى /webhook بنفس
صيغة IFA Data Feed V2 — فلا حاجة لأي تنبيه يدوي في TradingView.

يعمل كخدمة مستقلة (Railway service ثانية) بجانب bot.js.

متغيرات البيئة:
  WEBHOOK_URL     رابط الـ webhook (مثال: https://<app>.up.railway.app/webhook)
  TV_USERNAME     اسم مستخدم TradingView (اختياري — بدونه يعمل anonymous بحدود)
  TV_PASSWORD     كلمة مرور TradingView (اختياري)
  WEBHOOK_TOKEN   توكن الحماية (اختياري — يطابق WEBHOOK_TOKEN في البوت)
  POLL_SECONDS    فترة التحديث بالثواني (افتراضي 60)
"""

import os
import sys
import time
import logging
from datetime import timezone

import requests

try:
    from tvDatafeed import TvDatafeed, Interval
except ImportError:
    print("خطأ: مكتبة tvdatafeed غير مثبّتة. ثبّتها عبر requirements.txt", file=sys.stderr)
    raise

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [tv_fetcher] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("tv_fetcher")

# ── الإعدادات ──────────────────────────────────────────
WEBHOOK_URL   = os.environ.get("WEBHOOK_URL", "").rstrip("/")
TV_USERNAME   = os.environ.get("TV_USERNAME") or None
TV_PASSWORD   = os.environ.get("TV_PASSWORD") or None
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN") or None
POLL_SECONDS  = int(os.environ.get("POLL_SECONDS", "60"))

if not WEBHOOK_URL:
    log.error("WEBHOOK_URL غير مضبوط — أضفه في متغيرات البيئة")
    sys.exit(1)

# الرمز → (البورصة في TradingView, رمز العقد المستمر)
SYMBOLS = {
    "MNQ": ("CME_MINI", "MNQ1!"),
    "MGC": ("COMEX",    "MGC1!"),
    "MCL": ("NYMEX",    "MCL1!"),
}

# (اسم الإطار كما يقبله البوت, Interval, عدد شموع الـ backfill, عدد الشموع لكل تحديث)
TIMEFRAMES = [
    ("1d", Interval.in_daily,     400, 2),
    ("4h", Interval.in_4_hour,    400, 2),
    ("1h", Interval.in_1_hour,    400, 3),
    ("15m", Interval.in_15_minute, 400, 3),
    ("5m", Interval.in_5_minute,  400, 3),
    ("1m", Interval.in_1_minute,  500, 3),
]


def session_of(dt) -> str:
    """جلسة الشمعة حسب ساعة UTC — تطابق منطق مؤشر Pine."""
    m = dt.hour * 60 + dt.minute
    if m < 7 * 60:  return "Asia"
    if m < 13 * 60: return "London"
    if m < 22 * 60: return "NewYork"
    return "Off"


def post_candle(symbol, exchange, tf_name, dt, o, h, l, c, v):
    """يرسل شمعة واحدة إلى /webhook بصيغة ifa_candle."""
    # نعامل الوقت الخام كـ UTC (tvdatafeed يعيد datetime بلا منطقة زمنية)
    epoch = int(dt.replace(tzinfo=timezone.utc).timestamp())
    payload = {
        "src": "ifa_candle",
        "symbol": symbol,
        "exchange": exchange,
        "timeframe": tf_name,
        "timestamp": epoch * 1000,
        "open": float(o), "high": float(h), "low": float(l), "close": float(c),
        "volume": float(v) if v == v else 0,   # v==v يستبعد NaN
        "session": session_of(dt),
        "bar_index": 0,
    }
    headers = {"Content-Type": "application/json"}
    if WEBHOOK_TOKEN:
        headers["x-webhook-token"] = WEBHOOK_TOKEN
    for attempt in range(3):
        try:
            r = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=15)
            if r.status_code == 200:
                return True
            log.warning("webhook رد %s: %s", r.status_code, r.text[:100])
            return False
        except requests.RequestException as e:
            if attempt == 2:
                log.warning("فشل إرسال شمعة %s %s: %s", symbol, tf_name, e)
            time.sleep(2 ** attempt)
    return False


def fetch_and_send(tv, symbol, exchange, tv_symbol, tf_name, interval, n_bars):
    """يجلب آخر n_bars شمعة ويرسل الشموع المغلقة (يستبعد الشمعة الجارية)."""
    try:
        df = tv.get_hist(symbol=tv_symbol, exchange=exchange,
                         interval=interval, n_bars=n_bars)
    except Exception as e:
        log.warning("get_hist فشل %s %s: %s", symbol, tf_name, e)
        return 0
    if df is None or df.empty:
        log.warning("لا بيانات لـ %s %s", symbol, tf_name)
        return 0

    # آخر صف = شمعة قيد التكوّن — نستبعدها ونرسل المغلقة فقط
    closed = df.iloc[:-1] if len(df) > 1 else df
    sent = 0
    for dt, row in closed.iterrows():
        if post_candle(symbol, exchange, tf_name, dt,
                       row["open"], row["high"], row["low"],
                       row["close"], row.get("volume", 0)):
            sent += 1
    return sent


def main():
    mode = "logged-in" if TV_USERNAME else "anonymous (بحدود)"
    log.info("بدء الاتصال بـ TradingView (%s) → %s", mode, WEBHOOK_URL)
    try:
        tv = TvDatafeed(username=TV_USERNAME, password=TV_PASSWORD)
    except Exception as e:
        log.error("فشل تسجيل الدخول إلى TradingView: %s", e)
        sys.exit(1)

    first_run = True
    while True:
        cycle_start = time.time()
        total = 0
        for symbol, (exchange, tv_symbol) in SYMBOLS.items():
            for tf_name, interval, backfill, tail in TIMEFRAMES:
                n = backfill if first_run else tail
                sent = fetch_and_send(tv, symbol, exchange, tv_symbol,
                                      tf_name, interval, n)
                total += sent
                time.sleep(1)   # تهدئة بين الطلبات لتجنّب الحظر
        if first_run:
            log.info("اكتمل الـ backfill الأولي — أُرسلت %d شمعة", total)
            first_run = False
        else:
            log.info("دورة تحديث — أُرسلت %d شمعة", total)

        elapsed = time.time() - cycle_start
        time.sleep(max(5, POLL_SECONDS - elapsed))


if __name__ == "__main__":
    main()
