/**
 * EMA21 Bounce — 1H Bias + 5M Entry
 * ════════════════════════════════════
 * ① 1H: EMA50 > EMA200 → اتجاه صاعد  (أو العكس)
 * ② 5M: السعر لمس EMA21 في آخر 4 شمعات
 * ③ 5M: شمعة ارتداد قوية (جسم > 40% من النطاق)
 * ④ 5M: RSI < 48 للشراء، RSI > 52 للبيع
 * SL:  أدنى قاع في 4 شمعات − 0.3×ATR(5m)
 * TP1: 2:1 | TP2: 3.5:1
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
      : Math.max(
          bars[i].high - bars[i].low,
          Math.abs(bars[i].high - bars[i - 1].close),
          Math.abs(bars[i].low  - bars[i - 1].close)
        );
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

// ══ HTF Bias من 1H ══════════════════════════════
function getHTFBias(bars1h) {
  if (bars1h.length < 210) return { htfBull: false, htfBear: false, trend: 'NEUTRAL' };
  const closes = bars1h.map(b => b.close);
  const e50arr  = ema(closes, 50);
  const e200arr = ema(closes, 200);
  const n = bars1h.length - 1;
  const e50  = e50arr[n];
  const e200 = e200arr[n];
  if (!e50 || !e200) return { htfBull: false, htfBear: false, trend: 'NEUTRAL' };
  const htfBull = e50 > e200;
  const htfBear = e50 < e200;
  const gap = ((e50 - e200) / e200 * 100).toFixed(2);
  return { htfBull, htfBear, trend: htfBull ? 'BULL' : htfBear ? 'BEAR' : 'NEUTRAL', gap };
}

// ══ الاستراتيجية الرئيسية — إشارة 5M ════════════
export function analyzeSimple(bars5m, bars1h) {
  if (bars5m.length < 50)  return { error: 'بيانات 5M غير كافية' };
  if (bars1h.length < 210) return { error: 'بيانات 1H غير كافية' };

  // ① HTF Bias من الساعة
  const { htfBull, htfBear, trend: htfTrend } = getHTFBias(bars1h);
  if (!htfBull && !htfBear) {
    return { error: null, htfTrend: 'NEUTRAL', signal: null,
      debug: { reason: 'EMA50 ≈ EMA200 — لا اتجاه واضح' } };
  }

  // ② حساب EMA21 + ATR + RSI على 5M
  const closes5m = bars5m.map(b => b.close);
  const e21arr   = ema(closes5m, 21);
  const atrArr   = atrCalc(bars5m, 14);
  const rsiArr   = rsiCalc(bars5m, 14);

  const n   = bars5m.length;
  const i   = n - 1;
  const cur = bars5m[i];
  const p1  = bars5m[i - 1];
  const p2  = bars5m[i - 2];
  const p3  = bars5m[i - 3];

  const e21 = e21arr[i];
  const A   = atrArr[i];
  const R   = rsiArr[i];
  if (!e21 || !A) return { error: 'المؤشرات لم تكتمل بعد' };

  // ③ هل لمس EMA21 في آخر 4 شمعات (5M)؟
  const touchedBull = [p1, p2, p3].some((b, j) => b.low  <= (e21arr[i - 1 - j] || e21) * 1.0015);
  const touchedBear = [p1, p2, p3].some((b, j) => b.high >= (e21arr[i - 1 - j] || e21) * 0.9985);

  // ④ شمعة ارتداد قوية
  const body  = Math.abs(cur.close - cur.open);
  const range = cur.high - cur.low || 0.01;
  const strongBody  = body / range > 0.38;
  const bouncedBull = cur.close > cur.open && cur.close > e21;
  const bouncedBear = cur.close < cur.open && cur.close < e21;

  // ⑤ RSI
  const rsiLong  = R < 48;
  const rsiShort = R > 52;

  const longOk  = htfBull && touchedBull && bouncedBull && rsiLong  && strongBody;
  const shortOk = htfBear && touchedBear && bouncedBear && rsiShort && strongBody;

  const price = cur.close;
  let signal = null;

  if (longOk) {
    const recentLow = Math.min(p1.low, p2.low, p3.low);
    const sl   = recentLow - A * 0.3;
    const risk = price - sl;
    if (risk > 0 && risk < A * 5) {
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
        conditions: {
          htfBull, touchedEma21: touchedBull,
          bouncedUp: bouncedBull, rsiOk: rsiLong, strongBody,
        }
      };
    }
  } else if (shortOk) {
    const recentHigh = Math.max(p1.high, p2.high, p3.high);
    const sl   = recentHigh + A * 0.3;
    const risk = sl - price;
    if (risk > 0 && risk < A * 5) {
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
        conditions: {
          htfBear, touchedEma21: touchedBear,
          bouncedDown: bouncedBear, rsiOk: rsiShort, strongBody,
        }
      };
    }
  }

  return {
    price:    +price.toFixed(2),
    htfTrend,
    e21:      +e21.toFixed(2),
    rsi:      +R.toFixed(1),
    atr:      +A.toFixed(2),
    signal,
    debug: { htfBull, htfBear, touchedBull, touchedBear, bouncedBull, bouncedBear, rsiLong, rsiShort, strongBody,
      reason: !htfBull && !htfBear ? 'لا اتجاه HTF' :
              !(touchedBull || touchedBear) ? 'السعر لم يلمس EMA21 بعد' :
              !(bouncedBull || bouncedBear) ? 'لا شمعة ارتداد' :
              !(rsiLong || rsiShort) ? `RSI محايد (${R.toFixed(0)})` :
              !strongBody ? 'جسم الشمعة ضعيف' : 'جميع الشروط متحققة'
    },
  };
}
