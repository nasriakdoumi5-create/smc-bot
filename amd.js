/**
 * AMD SNIPER Engine — إشارة واحدة يومياً
 * نفس منطق Pine Script: Displacement + Score + Killzone
 */

// Sessions UTC  (Madrid summer = UTC+2)
// Pre-market / Accumulation: قبل افتتاح السوق
// Killzone: 15:00–17:00 Madrid = 13:00–15:00 UTC
const SESSIONS = {
  asia:  { start: 0,            end: 13 * 60 + 30 }, // قبل الافتتاح
  kill:  { start: 13 * 60,      end: 15 * 60 },       // 13:00–15:00 UTC
  mktEnd:{ start: 20 * 60,      end: 24 * 60 },       // بعد إغلاق السوق
};

function minsUTC(bar) {
  const d = new Date(bar.time * 1000);
  return d.getUTCHours() * 60 + d.getUTCMinutes();
}

function dateKey(bar) {
  const d = new Date(bar.time * 1000);
  return `${d.getUTCFullYear()}-${d.getUTCMonth()}-${d.getUTCDate()}`;
}

function inPreMkt(bar) {
  const m = minsUTC(bar);
  return m >= SESSIONS.asia.start && m < SESSIONS.asia.end;
}

function inKillzone(bar) {
  const m = minsUTC(bar);
  return m >= SESSIONS.kill.start && m < SESSIONS.kill.end;
}

// ATR بسيط على آخر N شمعة
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

// HTF bias: هل أمس كان يوم صاعد أم هابط؟
function getDailyBias(bars) {
  const todayKey = dateKey(bars[bars.length - 1]);
  const yesterday = {};

  for (const b of bars) {
    const k = dateKey(b);
    if (k === todayKey) continue;
    if (!yesterday[k]) yesterday[k] = { open: b.open, close: b.close };
    yesterday[k].close = b.close;
  }

  const keys = Object.keys(yesterday).sort();
  if (keys.length === 0) return null;
  const last = yesterday[keys[keys.length - 1]];
  return last.close > last.open ? 'bull' : 'bear';
}

export function analyzeAMD(bars5m) {
  if (!bars5m || bars5m.length < 120) return { error: 'not enough data' };

  const last  = bars5m[bars5m.length - 1];
  const price = last.close;
  const atr   = calcATR(bars5m, 14);
  if (!atr) return { error: 'ATR not ready' };

  const todayKey = dateKey(last);
  const htfBias  = getDailyBias(bars5m);

  // ── بناء نطاق ما قبل السوق (Accumulation) ─────
  const todayBarsPreMkt = bars5m.filter(b => dateKey(b) === todayKey && inPreMkt(b));
  if (todayBarsPreMkt.length < 5) {
    return { error: 'Pre-market range not ready', price };
  }

  const asiaHigh = +Math.max(...todayBarsPreMkt.map(b => b.high)).toFixed(4);
  const asiaLow  = +Math.min(...todayBarsPreMkt.map(b => b.low)).toFixed(4);
  const asiaSize = +(asiaHigh - asiaLow).toFixed(4);
  const rangePct = asiaLow > 0 ? asiaSize / asiaLow : 0;

  // فلتر: Range لازم ≥ 0.3% من السعر
  const rangeOK = rangePct >= 0.003;

  // ── كشف الـ Hunt (Manipulation) ───────────────
  const minSweep = asiaSize * 0.3; // الكسر لازم يكون 30% من حجم النطاق
  const postAsiaBars = bars5m.filter(b => dateKey(b) === todayKey && !inPreMkt(b));

  let mUp = false, mDn = false;
  let mUpBar = null, mDnBar = null;
  let mUpClosed = false, mDnClosed = false;

  for (const b of postAsiaBars) {
    if (b.high > asiaHigh + minSweep && !mUp) {
      mUp    = true;
      mUpBar = b;
      mUpClosed = b.close < asiaHigh; // أغلق داخل النطاق في نفس الشمعة
    }
    if (b.low < asiaLow - minSweep && !mDn) {
      mDn    = true;
      mDnBar = b;
      mDnClosed = b.close > asiaLow;
    }
    // تحقق من الإغلاق في الشموع اللاحقة
    if (mUp && !mUpClosed && b.close < asiaHigh) mUpClosed = true;
    if (mDn && !mDnClosed && b.close > asiaLow)  mDnClosed = true;
  }

  // ── كشف الـ Displacement (شمعة قوية 2× ATR) ──
  let dispBull = false; // بعد Hunt DN → صعود قوي
  let dispBear = false; // بعد Hunt UP → هبوط قوي

  for (const b of postAsiaBars) {
    const body = Math.abs(b.close - b.open);
    if (mDn && mDnClosed && !dispBull && b.close > b.open && body > atr * 2.0) dispBull = true;
    if (mUp && mUpClosed && !dispBear && b.open > b.close && body > atr * 2.0) dispBear = true;
  }

  // ── Killzone نشطة؟ ────────────────────────────
  const killActive = inKillzone(last);

  // ── نظام النقاط ────────────────────────────────
  // LONG: Hunt DN → Disp UP → Killzone → HTF Bull
  const lS1 = killActive              ? 1 : 0; // Killzone
  const lS2 = mDn && !mUp && rangeOK ? 1 : 0; // Hunt نظيف + Range كافٍ
  const lS3 = mDnClosed              ? 1 : 0; // Hunt أغلق داخل النطاق
  const lS4 = dispBull               ? 1 : 0; // Displacement قوي
  const lS5 = htfBias === 'bull'     ? 1 : 0; // HTF يؤيد الصعود
  const longScore = lS1 + lS2 + lS3 + lS4 + lS5;

  // SHORT: Hunt UP → Disp DN → Killzone → HTF Bear
  const sS1 = killActive              ? 1 : 0;
  const sS2 = mUp && !mDn && rangeOK ? 1 : 0;
  const sS3 = mUpClosed              ? 1 : 0;
  const sS4 = dispBear               ? 1 : 0;
  const sS5 = htfBias === 'bear'     ? 1 : 0;
  const shortScore = sS1 + sS2 + sS3 + sS4 + sS5;

  // ── الإشارة: تحتاج 4 نقاط من 5 ───────────────
  let signal = null;

  if (longScore >= 4 && price > asiaLow) {
    const sl   = mDnBar ? +(mDnBar.low  - atr * 0.3).toFixed(4) : +(asiaLow  - atr * 1.5).toFixed(4);
    const risk = Math.abs(price - sl);
    signal = {
      type:   'LONG',
      price:  +price.toFixed(4),
      sl,
      tp1:    +(price + risk * 1.5).toFixed(4),
      tp2:    +(price + risk * 3.0).toFixed(4),
      score:  `${longScore}/5`,
      phase:  'Distribution',
      manipulation: `Hunt DN تحت Asia Low عند ${(mDnBar?.low || asiaLow).toFixed(4)}`,
    };
  }

  if (shortScore >= 4 && price < asiaHigh) {
    const sl   = mUpBar ? +(mUpBar.high + atr * 0.3).toFixed(4) : +(asiaHigh + atr * 1.5).toFixed(4);
    const risk = Math.abs(sl - price);
    signal = {
      type:   'SHORT',
      price:  +price.toFixed(4),
      sl,
      tp1:    +(price - risk * 1.5).toFixed(4),
      tp2:    +(price - risk * 3.0).toFixed(4),
      score:  `${shortScore}/5`,
      phase:  'Distribution',
      manipulation: `Hunt UP فوق Asia High عند ${(mUpBar?.high || asiaHigh).toFixed(4)}`,
    };
  }

  const session = killActive ? 'NY Killzone 🎯' : 'Outside Killzone ⏸';

  return {
    price:    +price.toFixed(4),
    session,
    asiaHigh,
    asiaLow,
    asiaSize: +asiaSize.toFixed(4),
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
