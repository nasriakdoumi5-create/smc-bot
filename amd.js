/**
 * AMD SNIPER Engine — إشارة واحدة يومياً
 *
 * مُحسَّن لـ NQ (ناسداك فيوتشرز) و NG (الغاز الطبيعي)
 *
 * دورة AMD للفيوتشرز:
 *   Accumulation = نطاق آخر جلسة آسيا (00:00-07:00 UTC)
 *   Manipulation = لندن + Pre-NY يكسر النطاق (07:00-13:30 UTC)
 *   Distribution = NY Open Killzone (أقوى نقطة): 13:30-15:30 UTC
 *                  + London Close KZ: 10:00-12:00 UTC (ثانوي)
 */

// NY Open Killzone: 09:30–11:30 ET = 13:30–15:30 UTC (الأقوى)
// London Close KZ:  10:00–12:00 UTC (ثانوي للغاز)
const KZ_START = 13 * 60 + 30; // 13:30 UTC
const KZ_END   = 15 * 60 + 30; // 15:30 UTC

function minsUTC(bar) {
  const d = new Date(bar.time * 1000);
  return d.getUTCHours() * 60 + d.getUTCMinutes();
}

function dateUTC(ts) {
  const d = new Date(ts);
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}-${String(d.getUTCDate()).padStart(2, '0')}`;
}

function inKillzone(bar) {
  const m = minsUTC(bar);
  return m >= KZ_START && m < KZ_END;
}

function calcATR(bars, period = 14) {
  if (bars.length < period + 1) return null;
  let sum = 0;
  for (let i = bars.length - period; i < bars.length; i++) {
    const tr = Math.max(
      bars[i].high - bars[i].low,
      Math.abs(bars[i].high - bars[i - 1].close),
      Math.abs(bars[i].low  - bars[i - 1].close)
    );
    sum += tr;
  }
  return sum / period;
}

// نطاق يوم أمس (PDH/PDL) + اتجاهه
function getPrevDay(bars, todayKey) {
  const byDay = {};
  for (const b of bars) {
    const k = dateUTC(b.time * 1000);
    if (k === todayKey) continue;
    if (!byDay[k]) byDay[k] = { high: b.high, low: b.low, open: b.open, close: b.close };
    byDay[k].high  = Math.max(byDay[k].high, b.high);
    byDay[k].low   = Math.min(byDay[k].low,  b.low);
    byDay[k].close = b.close;
  }
  const keys = Object.keys(byDay).sort();
  if (keys.length === 0) return null;
  const prev = byDay[keys[keys.length - 1]];
  return {
    high: +prev.high.toFixed(4),
    low:  +prev.low.toFixed(4),
    bias: prev.close > prev.open ? 'bull' : 'bear',
  };
}

export function analyzeAMD(bars5m) {
  if (!bars5m || bars5m.length < 50) return { error: 'not enough data' };

  const last     = bars5m[bars5m.length - 1];
  const price    = last.close;
  const atr      = calcATR(bars5m, 14);
  if (!atr) return { error: 'ATR not ready' };

  const todayKey = dateUTC(Date.now());

  // ── PDH/PDL = نطاق التراكم ────────────────────
  const prev = getPrevDay(bars5m, todayKey);
  if (!prev) return { error: 'No previous day data', price };

  const asiaHigh = prev.high;
  const asiaLow  = prev.low;
  const asiaSize = +(asiaHigh - asiaLow).toFixed(4);
  const rangePct = asiaLow > 0 ? asiaSize / asiaLow : 0;
  const rangeOK  = rangePct >= 0.003; // ≥ 0.3%
  const htfBias  = prev.bias;

  // ── بارات اليوم فقط ───────────────────────────
  const todayBars = bars5m.filter(b => dateUTC(b.time * 1000) === todayKey);
  const minSweep  = asiaSize * 0.2; // 20% من نطاق أمس

  // ── كشف Hunt ──────────────────────────────────
  let mUp = false, mDn = false;
  let mUpBar = null, mDnBar = null;
  let mUpClosed = false, mDnClosed = false;

  for (const b of todayBars) {
    if (!mUp && b.high > asiaHigh + minSweep) {
      mUp = true; mUpBar = b;
      mUpClosed = b.close < asiaHigh;
    }
    if (!mDn && b.low < asiaLow - minSweep) {
      mDn = true; mDnBar = b;
      mDnClosed = b.close > asiaLow;
    }
    if (mUp && !mUpClosed && b.close < asiaHigh) mUpClosed = true;
    if (mDn && !mDnClosed && b.close > asiaLow)  mDnClosed = true;
  }

  // ── Displacement (شمعة > 1.5× ATR بعد Hunt) ──
  let dispBull = false;
  let dispBear = false;

  for (const b of todayBars) {
    const body = Math.abs(b.close - b.open);
    if (mDn && mDnClosed && !dispBull && b.close > b.open && body > atr * 1.5) dispBull = true;
    if (mUp && mUpClosed && !dispBear && b.open > b.close && body > atr * 1.5) dispBear = true;
  }

  const killActive = inKillzone(last);

  // ── نظام النقاط (5 نقاط) ──────────────────────
  const lS1 = killActive          ? 1 : 0; // توقيت NY Open
  const lS2 = mDn && rangeOK     ? 1 : 0; // Hunt DN + Range كافٍ
  const lS3 = mDnClosed          ? 1 : 0; // Hunt أغلق داخل النطاق ✅ الأهم
  const lS4 = dispBull           ? 1 : 0; // Displacement صعودي
  const lS5 = htfBias === 'bull' ? 1 : 0; // أمس كان صاعداً
  const longScore = lS1 + lS2 + lS3 + lS4 + lS5;

  const sS1 = killActive          ? 1 : 0;
  const sS2 = mUp && rangeOK     ? 1 : 0;
  const sS3 = mUpClosed          ? 1 : 0;
  const sS4 = dispBear           ? 1 : 0;
  const sS5 = htfBias === 'bear' ? 1 : 0;
  const shortScore = sS1 + sS2 + sS3 + sS4 + sS5;

  // ── إشارة: Hunt+Closed إلزاميان + نقطتان أخريان ─
  let signal = null;

  if (mDn && mDnClosed && longScore >= 3 && price > asiaLow) {
    const sl   = mDnBar ? +(mDnBar.low - atr * 0.3).toFixed(4) : +(asiaLow - atr * 1.5).toFixed(4);
    const risk = Math.abs(price - sl);
    signal = {
      type:         'LONG',
      price:        +price.toFixed(4),
      sl,
      tp1:          +(price + risk * 1.5).toFixed(4),
      tp2:          +(price + risk * 3.0).toFixed(4),
      score:        `${longScore}/5`,
      phase:        'Distribution',
      manipulation: `Hunt DN تحت PDL عند ${(mDnBar?.low || asiaLow).toFixed(4)}`,
    };
  }

  if (mUp && mUpClosed && shortScore >= 3 && price < asiaHigh) {
    const sl   = mUpBar ? +(mUpBar.high + atr * 0.3).toFixed(4) : +(asiaHigh + atr * 1.5).toFixed(4);
    const risk = Math.abs(sl - price);
    signal = {
      type:         'SHORT',
      price:        +price.toFixed(4),
      sl,
      tp1:          +(price - risk * 1.5).toFixed(4),
      tp2:          +(price - risk * 3.0).toFixed(4),
      score:        `${shortScore}/5`,
      phase:        'Distribution',
      manipulation: `Hunt UP فوق PDH عند ${(mUpBar?.high || asiaHigh).toFixed(4)}`,
    };
  }

  return {
    price:     +price.toFixed(4),
    session:   killActive ? 'NY Open Killzone 🎯' : 'Outside Killzone ⏸',
    asiaHigh,
    asiaLow,
    asiaSize,
    rangeOK,
    mUp, mDn,
    mUpClosed, mDnClosed,
    dispBull, dispBear,
    htfBias,
    longScore,
    shortScore,
    killActive,
    manipPrice: mUpBar ? +mUpBar.high.toFixed(4) : mDnBar ? +mDnBar.low.toFixed(4) : null,
    signal,
  };
}
