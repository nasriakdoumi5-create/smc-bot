/**
 * Simple EMA21 Bounce Strategy — 1H
 * ════════════════════════════════
 * 4 شروط فقط:
 * ① HTF: EMA50 > EMA200 (صاعد) أو EMA50 < EMA200 (هابط)
 * ② السعر لمس EMA21 في آخر 3 شمعات
 * ③ الشمعة الحالية ارتدت: صاعدة + أغلقت فوق EMA21
 * ④ RSI < 45 للشراء، RSI > 55 للبيع
 * SL: تحت أدنى قاع في 3 شمعات - 0.3×ATR
 * TP: RR 2:1
 */

function ema(arr, period) {
  const k = 2 / (period + 1);
  const out = [];
  for (let i = 0; i < arr.length; i++) {
    if (i < period - 1) { out.push(null); continue; }
    if (i === period - 1) {
      out.push(arr.slice(0, period).reduce((a, b) => a + b, 0) / period);
      continue;
    }
    out.push(arr[i] * k + out[i - 1] * (1 - k));
  }
  return out;
}

function atrCalc(bars, period = 14) {
  const out = [];
  for (let i = 0; i < bars.length; i++) {
    const tr = i === 0
      ? bars[i].high - bars[i].low
      : Math.max(bars[i].high - bars[i].low,
          Math.abs(bars[i].high - bars[i - 1].close),
          Math.abs(bars[i].low  - bars[i - 1].close));
    if (i < period - 1) { out.push(null); continue; }
    if (i === period - 1) {
      const trs = bars.slice(0, period).map((b, j) =>
        j === 0 ? b.high - b.low :
        Math.max(b.high - b.low, Math.abs(b.high - bars[j-1].close), Math.abs(b.low - bars[j-1].close))
      );
      out.push(trs.reduce((a, b) => a + b, 0) / period);
      continue;
    }
    out.push((out[i - 1] * (period - 1) + tr) / period);
  }
  return out;
}

function rsiCalc(bars, period = 14) {
  const out = new Array(bars.length).fill(50);
  let g = 0, l = 0;
  for (let i = 1; i <= period; i++) {
    const d = bars[i].close - bars[i - 1].close;
    d > 0 ? (g += d) : (l += -d);
  }
  g /= period; l /= period;
  out[period] = l === 0 ? 100 : 100 - 100 / (1 + g / l);
  for (let i = period + 1; i < bars.length; i++) {
    const d = bars[i].close - bars[i - 1].close;
    g = (g * (period - 1) + Math.max(d, 0)) / period;
    l = (l * (period - 1) + Math.max(-d, 0)) / period;
    out[i] = l === 0 ? 100 : 100 - 100 / (1 + g / l);
  }
  return out;
}

export function analyzeSimple(bars1h) {
  if (bars1h.length < 210) return { error: 'بيانات غير كافية' };

  const closes = bars1h.map(b => b.close);
  const e21arr  = ema(closes, 21);
  const e50arr  = ema(closes, 50);
  const e200arr = ema(closes, 200);
  const atrArr  = atrCalc(bars1h, 14);
  const rsiArr  = rsiCalc(bars1h, 14);

  const n = bars1h.length;
  const i = n - 1;

  const e21  = e21arr[i];
  const e50  = e50arr[i];
  const e200 = e200arr[i];
  const A    = atrArr[i];
  const R    = rsiArr[i];

  if (!e21 || !e50 || !e200 || !A) return { error: 'لم تكتمل المؤشرات بعد' };

  const htfBull = e50 > e200;
  const htfBear = e50 < e200;
  const htfTrend = htfBull ? (e21arr[i] > e50arr[i] ? 'BULL↑' : 'BULL') :
                   htfBear ? (e21arr[i] < e50arr[i] ? 'BEAR↓' : 'BEAR') : 'NEUTRAL';

  const cur  = bars1h[i];
  const p1   = bars1h[i - 1];
  const p2   = bars1h[i - 2];
  const p3   = bars1h[i - 3];

  const body  = Math.abs(cur.close - cur.open);
  const range = cur.high - cur.low || 0.01;
  const strongCandle = body / range > 0.38;

  // شرط ②: لمس EMA21 في آخر 3 شمعات
  const touchedBull = p1.low <= e21arr[i-1] * 1.002
                   || p2.low <= e21arr[i-2] * 1.002
                   || p3.low <= e21arr[i-3] * 1.002;

  const touchedBear = p1.high >= e21arr[i-1] * 0.998
                   || p2.high >= e21arr[i-2] * 0.998
                   || p3.high >= e21arr[i-3] * 0.998;

  // شرط ③: ارتداد مؤكد
  const bouncedBull = cur.close > e21 && cur.close > cur.open;
  const bouncedBear = cur.close < e21 && cur.close < cur.open;

  const longOk  = htfBull && touchedBull && bouncedBull && R < 48 && strongCandle;
  const shortOk = htfBear && touchedBear && bouncedBear && R > 52 && strongCandle;

  const price = cur.close;
  let signal = null;

  if (longOk) {
    const recentLow = Math.min(p1.low, p2.low, p3.low);
    const sl   = recentLow - A * 0.3;
    const risk = price - sl;
    if (risk > 0 && risk < A * 4) {
      signal = {
        type:  'LONG',
        price: +price.toFixed(2),
        sl:    +sl.toFixed(2),
        tp1:   +(price + risk * 2).toFixed(2),
        tp2:   +(price + risk * 3.5).toFixed(2),
        risk:  +risk.toFixed(2),
        rr:    '2:1 / 3.5:1',
        rsi:   +R.toFixed(1),
        atr:   +A.toFixed(2),
        e21:   +e21.toFixed(2),
        conditions: { htfBull, touchedEma21: touchedBull, bouncedUp: bouncedBull, rsiOk: R < 48, strongBody: strongCandle }
      };
    }
  } else if (shortOk) {
    const recentHigh = Math.max(p1.high, p2.high, p3.high);
    const sl   = recentHigh + A * 0.3;
    const risk = sl - price;
    if (risk > 0 && risk < A * 4) {
      signal = {
        type:  'SHORT',
        price: +price.toFixed(2),
        sl:    +sl.toFixed(2),
        tp1:   +(price - risk * 2).toFixed(2),
        tp2:   +(price - risk * 3.5).toFixed(2),
        risk:  +risk.toFixed(2),
        rr:    '2:1 / 3.5:1',
        rsi:   +R.toFixed(1),
        atr:   +A.toFixed(2),
        e21:   +e21.toFixed(2),
        conditions: { htfBear, touchedEma21: touchedBear, bouncedDown: bouncedBear, rsiOk: R > 52, strongBody: strongCandle }
      };
    }
  }

  return {
    price:    +price.toFixed(2),
    htfTrend,
    e21:      +e21.toFixed(2),
    e50:      +e50.toFixed(2),
    e200:     +e200.toFixed(2),
    rsi:      +R.toFixed(1),
    atr:      +A.toFixed(2),
    longOk, shortOk,
    debug: {
      htfBull, htfBear,
      touchedBull, touchedBear,
      bouncedBull, bouncedBear,
      rsiLong: R < 48, rsiShort: R > 52,
      strongCandle
    },
    signal,
  };
}
