/**
 * AMD Strategy Engine — Accumulation / Manipulation / Distribution
 * ICT Methodology — NQ Futures
 *
 * Asia Session   → يحدد الـ Range (Accumulation)
 * London Open    → يكسر الـ Range (Manipulation / Stop Hunt)
 * NY Session     → الاتجاه الحقيقي (Distribution)
 */

// ══ Session Times (UTC) ══════════════════════
const SESSIONS = {
  asia:   { start: 23 * 60,      end:  4 * 60 },   // 23:00 – 04:00 UTC
  london: { start:  7 * 60,      end:  9 * 60 },   // 07:00 – 09:00 UTC
  ny:     { start: 13 * 60 + 30, end: 16 * 60 },   // 13:30 – 16:00 UTC
};

function minsUTC(bar) {
  const d = new Date(bar.time * 1000);
  return d.getUTCHours() * 60 + d.getUTCMinutes();
}

function dateKeyUTC(bar) {
  const d = new Date(bar.time * 1000);
  // Asia session crosses midnight — نُسند لليوم التالي
  const m = minsUTC(bar);
  if (m >= SESSIONS.asia.start) {
    const next = new Date(d.getTime() + 86400000);
    return `${next.getUTCFullYear()}-${next.getUTCMonth()}-${next.getUTCDate()}`;
  }
  return `${d.getUTCFullYear()}-${d.getUTCMonth()}-${d.getUTCDate()}`;
}

function inAsia(bar) {
  const m = minsUTC(bar);
  return m >= SESSIONS.asia.start || m < SESSIONS.asia.end;
}

function inLondon(bar) {
  const m = minsUTC(bar);
  return m >= SESSIONS.london.start && m < SESSIONS.london.end;
}

function inNY(bar) {
  const m = minsUTC(bar);
  return m >= SESSIONS.ny.start && m < SESSIONS.ny.end;
}

// ══ بناء Asia Range لكل يوم ═══════════════════
function buildAsiaRanges(bars) {
  const days = {};
  for (const b of bars) {
    if (!inAsia(b)) continue;
    const key = dateKeyUTC(b);
    if (!days[key]) days[key] = { high: -Infinity, low: Infinity, bars: [] };
    days[key].high = Math.max(days[key].high, b.high);
    days[key].low  = Math.min(days[key].low,  b.low);
    days[key].bars.push(b);
  }
  return days;
}

// ══ التحليل الرئيسي ════════════════════════════
export function analyzeAMD(bars5m) {
  if (!bars5m || bars5m.length < 100) return { error: 'not enough data' };

  const last = bars5m[bars5m.length - 1];
  const now  = minsUTC(last);
  const price = last.close;

  // ── بناء Asia Ranges ──────────────────────
  const asiaRanges = buildAsiaRanges(bars5m);
  const todayKey   = dateKeyUTC(last);
  const asia       = asiaRanges[todayKey];

  if (!asia || asia.bars.length < 3) {
    return { error: 'Asia range not ready', price, session: getSession(now) };
  }

  const asiaHigh = +asia.high.toFixed(2);
  const asiaLow  = +asia.low.toFixed(2);
  const asiaSize = +(asiaHigh - asiaLow).toFixed(2);

  // ── كشف Manipulation ──────────────────────
  // هل كسرت London أو NY طرف الـ Range؟
  let manipHigh = false;  // كسر فوق Asia High (Stop Hunt للمشترين)
  let manipLow  = false;  // كسر تحت Asia Low  (Stop Hunt للبائعين)
  let manipBar  = null;

  // نفحص الشموع بعد نهاية Asia
  const postAsia = bars5m.filter(b => {
    const m = minsUTC(b);
    const k = dateKeyUTC(b);
    return k === todayKey && m >= SESSIONS.asia.end && m < SESSIONS.ny.end;
  });

  for (const b of postAsia) {
    if (b.high > asiaHigh + asiaSize * 0.1) {
      manipHigh = true;
      if (!manipBar || b.high > manipBar.high) manipBar = b;
    }
    if (b.low < asiaLow - asiaSize * 0.1) {
      manipLow = true;
      if (!manipBar || b.low < manipBar.low) manipBar = b;
    }
  }

  // ── الجلسة الحالية ────────────────────────
  const session = getSession(now);
  const inDistribution = inNY(last);

  // ── إشارة الصفقة ──────────────────────────
  let signal = null;

  if (inDistribution) {
    // Manipulation فوق Asia High → Distribution = SHORT
    if (manipHigh && !manipLow) {
      const sl  = manipBar ? +(manipBar.high + asiaSize * 0.1).toFixed(2) : +(asiaHigh + asiaSize * 0.5).toFixed(2);
      const risk = Math.abs(price - sl);
      signal = {
        type:  'SHORT',
        price: +price.toFixed(2),
        sl,
        tp1:   +(price - risk * 2).toFixed(2),
        tp2:   +(asiaLow).toFixed(2),
        phase: 'Distribution',
        manipulation: `Stop Hunt فوق Asia High عند ${manipBar?.high?.toFixed(2) || asiaHigh}`,
        conditions: {
          asiaRangeDefined: true,
          manipulationUp:   manipHigh,
          nySession:        true,
          priceBelowAsiaHigh: price < asiaHigh,
          sweepReverted:    price < (manipBar?.high || asiaHigh),
        }
      };
    }

    // Manipulation تحت Asia Low → Distribution = LONG
    if (manipLow && !manipHigh) {
      const sl  = manipBar ? +(manipBar.low - asiaSize * 0.1).toFixed(2) : +(asiaLow - asiaSize * 0.5).toFixed(2);
      const risk = Math.abs(price - sl);
      signal = {
        type:  'LONG',
        price: +price.toFixed(2),
        sl,
        tp1:   +(price + risk * 2).toFixed(2),
        tp2:   +(asiaHigh).toFixed(2),
        phase: 'Distribution',
        manipulation: `Stop Hunt تحت Asia Low عند ${manipBar?.low?.toFixed(2) || asiaLow}`,
        conditions: {
          asiaRangeDefined:  true,
          manipulationDown:  manipLow,
          nySession:         true,
          priceAboveAsiaLow: price > asiaLow,
          sweepReverted:     price > (manipBar?.low || asiaLow),
        }
      };
    }
  }

  return {
    price:      +price.toFixed(2),
    session,
    asiaHigh,
    asiaLow,
    asiaSize,
    manipHigh,
    manipLow,
    manipPrice: manipBar ? +(manipHigh ? manipBar.high : manipBar.low).toFixed(2) : null,
    inDistribution,
    signal,
  };
}

function getSession(minsUTC) {
  if (minsUTC >= SESSIONS.asia.start || minsUTC < SESSIONS.asia.end) return 'Asia 🌏';
  if (minsUTC >= SESSIONS.london.start && minsUTC < SESSIONS.london.end) return 'London 🇬🇧';
  if (minsUTC >= SESSIONS.ny.start && minsUTC < SESSIONS.ny.end) return 'NY 🇺🇸';
  return 'مغلق ⏸';
}
