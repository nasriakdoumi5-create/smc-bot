/**
 * Market Memory Engine — محرك ذاكرة السوق
 * ─────────────────────────────────────────
 * يعمل عند وصول كل شمعة جديدة (Event Engine):
 *   DB → Structure → Swings → BOS → CHOCH → Liquidity
 *      → FVG → Order Blocks → Premium/Discount → Memory
 *
 * كل الحسابات هنا — TradingView يرسل شموعاً خاماً فقط.
 * يعيد استخدام swingHighs/swingLows/atr من smc.js الموجود.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { swingHighs, swingLows, atr } from './smc.js';
import { getCandles, lastPrice } from './market_db.js';

const DIR      = dirname(fileURLToPath(import.meta.url));
const MEM_PATH = join(DIR, 'data', 'market_memory.json');

const SWING_LEN = { '1d': 3, '4h': 3, '1h': 4, '15m': 5 };
const STRUCT_TFS = ['1d', '4h', '1h', '15m'];

function load() {
  try { return JSON.parse(readFileSync(MEM_PATH, 'utf8')); }
  catch { return {}; }
}

let memory = load();     // { MNQ: {...memory snapshot...} }

function persist() {
  try {
    mkdirSync(join(DIR, 'data'), { recursive: true });
    writeFileSync(MEM_PATH, JSON.stringify(memory));
  } catch (e) { console.error('[Memory] persist failed:', e.message); }
}

const iso = t => new Date(t * 1000).toISOString().slice(0, 16).replace('T', ' ');
const r2  = n => (n == null ? null : +Number(n).toFixed(2));

// ══ Swings ════════════════════════════════════════════
// [{type:'H'|'L', price, time, idx}] مرتبة زمنياً — مؤكدة فقط
function detectSwings(bars, len) {
  const highs = swingHighs(bars, len);
  const lows  = swingLows(bars, len);
  const out = [];
  for (let i = 0; i < bars.length; i++) {
    if (highs[i] != null) out.push({ type: 'H', price: highs[i], time: bars[i].time, idx: i });
    if (lows[i]  != null) out.push({ type: 'L', price: lows[i],  time: bars[i].time, idx: i });
  }
  return out;
}

// ══ Structure: Trend + BOS + CHOCH ════════════════════
// آلة حالة: كسر آخر قمة سوينغ = حدث صاعد، كسر آخر قاع = حدث هابط.
// الحدث مع الترند = BOS، ضد الترند = CHOCH (يقلب الترند).
function analyzeStructure(bars, len) {
  const swings = detectSwings(bars, len);
  if (swings.length < 2) {
    return {
      trend: `Undetermined — fewer than 2 confirmed swings in the available ${bars.length} bars`,
      lastBOS: null, lastCHOCH: null, swingHigh: null, swingLow: null,
    };
  }

  let trend = null, lastBOS = null, lastCHOCH = null;
  let refHigh = null, refLow = null;
  let si = 0;

  for (let i = 0; i < bars.length; i++) {
    // فعّل السوينغات التي تأكدت حتى هذه الشمعة (تتأكد بعد len شموع)
    while (si < swings.length && swings[si].idx + len <= i) {
      if (swings[si].type === 'H') refHigh = swings[si];
      else refLow = swings[si];
      si++;
    }
    const c = bars[i].close;
    if (refHigh && c > refHigh.price) {
      const ev = { direction: 'Bullish', level: r2(refHigh.price), time: iso(bars[i].time) };
      if (trend === 'Bearish') { lastCHOCH = ev; } else { lastBOS = ev; }
      trend = 'Bullish';
      refHigh = null;                       // ينتظر قمة سوينغ جديدة
    } else if (refLow && c < refLow.price) {
      const ev = { direction: 'Bearish', level: r2(refLow.price), time: iso(bars[i].time) };
      if (trend === 'Bullish') { lastCHOCH = ev; } else { lastBOS = ev; }
      trend = 'Bearish';
      refLow = null;
    }
  }

  const lastH = [...swings].reverse().find(s => s.type === 'H');
  const lastL = [...swings].reverse().find(s => s.type === 'L');

  return {
    trend: trend || 'Range / Undefined',
    lastBOS, lastCHOCH,
    swingHigh: lastH ? { price: r2(lastH.price), time: iso(lastH.time) } : null,
    swingLow:  lastL ? { price: r2(lastL.price), time: iso(lastL.time) } : null,
  };
}

// ══ Key Levels (من الشموع اليومية) ════════════════════
function keyLevels(bars1d) {
  if (!bars1d.length) return {};
  const latest = bars1d[bars1d.length - 1];
  const cur = new Date(latest.time * 1000);

  const sameWeek = t => {
    const d = new Date(t * 1000);
    const day = (dt) => { const x = new Date(Date.UTC(dt.getUTCFullYear(), dt.getUTCMonth(), dt.getUTCDate())); const dow = (x.getUTCDay() + 6) % 7; x.setUTCDate(x.getUTCDate() - dow); return x.getTime(); };
    return day(d) === day(cur);
  };
  const sameMonth = t => {
    const d = new Date(t * 1000);
    return d.getUTCFullYear() === cur.getUTCFullYear() && d.getUTCMonth() === cur.getUTCMonth();
  };

  const week  = bars1d.filter(b => sameWeek(b.time));
  const month = bars1d.filter(b => sameMonth(b.time));
  const yesterday = bars1d.length >= 2 ? bars1d[bars1d.length - 2] : null;

  return {
    weeklyHigh:  week.length  ? r2(Math.max(...week.map(b => b.high)))  : null,
    weeklyLow:   week.length  ? r2(Math.min(...week.map(b => b.low)))   : null,
    monthlyHigh: month.length ? r2(Math.max(...month.map(b => b.high))) : null,
    monthlyLow:  month.length ? r2(Math.min(...month.map(b => b.low)))  : null,
    yesterdayHigh: yesterday ? r2(yesterday.high) : null,
    yesterdayLow:  yesterday ? r2(yesterday.low)  : null,
  };
}

// ══ Session Levels (من شموع 5M لليوم الحالي UTC) ══════
// يسجّل أيضاً وقت تكوّن كل مستوى — الكسح لا يُحتسب قبله
function sessionLevels(bars5m) {
  if (!bars5m.length) return {};
  const latest  = bars5m[bars5m.length - 1];
  const dayStr  = new Date(latest.time * 1000).toISOString().slice(0, 10);
  const today   = bars5m.filter(b => new Date(b.time * 1000).toISOString().slice(0, 10) === dayStr);

  const level = name => {
    const s = today.filter(b => (b.session || '').toLowerCase().includes(name));
    if (!s.length) return null;
    let hi = s[0], lo = s[0];
    for (const b of s) {
      if (b.high > hi.high) hi = b;
      if (b.low  < lo.low)  lo = b;
    }
    return { high: r2(hi.high), low: r2(lo.low), highTime: hi.time, lowTime: lo.time };
  };

  return {
    asia:    level('asia'),
    london:  level('london'),
    newYork: level('newyork') || level('york'),
  };
}

// ══ Liquidity Sweep ═══════════════════════════════════
// وِك يتجاوز مستوى سيولة ثم إغلاق يعود خلفه.
// levels: { name: { price, formedAt } } — يُشترط أن يقع الكسح بعد تكوّن المستوى
function lastLiquiditySweep(bars15, levels) {
  const named = Object.entries(levels).filter(([, v]) => v?.price != null);
  let last = null;
  for (let i = Math.max(0, bars15.length - 96); i < bars15.length; i++) {
    const b = bars15[i];
    for (const [name, lv] of named) {
      if (b.time <= (lv.formedAt || 0)) continue;
      const isHigh = /high/i.test(name);
      if (isHigh && b.high > lv.price && b.close < lv.price) {
        last = { level: name, price: r2(lv.price), direction: 'Buy-side liquidity taken', time: iso(b.time) };
      } else if (!isHigh && b.low < lv.price && b.close > lv.price) {
        last = { level: name, price: r2(lv.price), direction: 'Sell-side liquidity taken', time: iso(b.time) };
      }
    }
  }
  return last;
}

// ══ FVG — آخر فجوة غير مُغطاة ═════════════════════════
function lastFVG(bars) {
  const gaps = [];
  for (let i = 2; i < bars.length; i++) {
    if (bars[i].low > bars[i - 2].high) {
      gaps.push({ direction: 'Bullish', top: bars[i].low, bottom: bars[i - 2].high, idx: i - 1, time: bars[i - 1].time });
    } else if (bars[i].high < bars[i - 2].low) {
      gaps.push({ direction: 'Bearish', top: bars[i - 2].low, bottom: bars[i].high, idx: i - 1, time: bars[i - 1].time });
    }
  }
  for (let g = gaps.length - 1; g >= 0; g--) {
    const gap = gaps[g];
    let filled = false;
    for (let i = gap.idx + 2; i < bars.length; i++) {
      if (gap.direction === 'Bullish' && bars[i].low <= gap.bottom) { filled = true; break; }
      if (gap.direction === 'Bearish' && bars[i].high >= gap.top)   { filled = true; break; }
    }
    if (!filled) return { direction: gap.direction, top: r2(gap.top), bottom: r2(gap.bottom), time: iso(gap.time) };
  }
  return null;
}

// ══ Order Block — آخر شمعة معاكسة قبل Displacement ════
function lastOrderBlock(bars) {
  if (bars.length < 20) return null;
  const atrArr = atr(bars, 14);
  let last = null;
  for (let i = 1; i < bars.length - 1; i++) {
    const b = bars[i], next = bars[i + 1];
    const a = atrArr[i + 1] || atrArr[atrArr.length - 1] || 0;
    if (!a) continue;
    const bullDisp = next.close > b.high && (next.close - next.open) > a * 0.8;
    const bearDisp = next.close < b.low  && (next.open - next.close) > a * 0.8;
    if (bullDisp && b.close < b.open) {
      last = { direction: 'Bullish', top: r2(b.open), bottom: r2(b.close), time: iso(b.time) };
    } else if (bearDisp && b.close > b.open) {
      last = { direction: 'Bearish', top: r2(b.close), bottom: r2(b.open), time: iso(b.time) };
    }
  }
  return last;
}

// ══ Premium / Discount (نطاق التداول الحالي على 4H) ═══
// النطاق = أعلى قمة وأدنى قاع في آخر 60 شمعة 4H (~10 أيام تداول)
function premiumDiscount(bars4h, price) {
  if (price == null || bars4h.length < 20) return null;
  const range = bars4h.slice(-60);
  const rangeHigh = Math.max(...range.map(b => b.high));
  const rangeLow  = Math.min(...range.map(b => b.low));
  if (rangeHigh <= rangeLow) return null;

  const eq  = (rangeHigh + rangeLow) / 2;
  const pos = Math.min(1, Math.max(0, (price - rangeLow) / (rangeHigh - rangeLow)));
  return {
    state: pos > 0.5 ? 'Premium' : 'Discount',
    rangeHigh: r2(rangeHigh),
    rangeLow: r2(rangeLow),
    equilibrium: r2(eq),
    positionInRange: `${Math.round(pos * 100)}%`,
  };
}

// ══ Event Engine — يُشغَّل عند كل شمعة جديدة ══════════
export function updateMemory(symbol) {
  const sym = String(symbol).toUpperCase();

  const bars1d = getCandles(sym, '1d');
  const bars4h = getCandles(sym, '4h');
  const bars1h = getCandles(sym, '1h');
  const bars15 = getCandles(sym, '15m');
  const bars5  = getCandles(sym, '5m');

  const price = lastPrice(sym)?.close ?? null;

  const structure = {};
  for (const tf of STRUCT_TFS) {
    const bars = { '1d': bars1d, '4h': bars4h, '1h': bars1h, '15m': bars15 }[tf];
    structure[tf] = bars.length >= 10
      ? analyzeStructure(bars, SWING_LEN[tf])
      : { trend: `Insufficient data (${bars.length} bars)` };
  }

  const levels   = keyLevels(bars1d);
  const sessions = sessionLevels(bars5);

  // بداية اليوم الحالي UTC — مستويات الأمس/الأسبوع تكوّنت قبله
  const latest1d = bars1d[bars1d.length - 1];
  const dayStart = latest1d
    ? Math.floor(new Date(new Date(latest1d.time * 1000).toISOString().slice(0, 10)).getTime() / 1000)
    : 0;

  const sweepLevels = {
    yesterdayHigh: { price: levels.yesterdayHigh, formedAt: dayStart },
    yesterdayLow:  { price: levels.yesterdayLow,  formedAt: dayStart },
    weeklyHigh:    { price: levels.weeklyHigh,    formedAt: dayStart },
    weeklyLow:     { price: levels.weeklyLow,     formedAt: dayStart },
    asiaHigh:    { price: sessions.asia?.high,    formedAt: sessions.asia?.highTime },
    asiaLow:     { price: sessions.asia?.low,     formedAt: sessions.asia?.lowTime },
    londonHigh:  { price: sessions.london?.high,  formedAt: sessions.london?.highTime },
    londonLow:   { price: sessions.london?.low,   formedAt: sessions.london?.lowTime },
    newYorkHigh: { price: sessions.newYork?.high, formedAt: sessions.newYork?.highTime },
    newYorkLow:  { price: sessions.newYork?.low,  formedAt: sessions.newYork?.lowTime },
  };

  memory[sym] = {
    symbol: sym,
    updatedAt: iso(Math.floor(Date.now() / 1000)),
    currentPrice: r2(price),
    structure,
    keyLevels: levels,
    sessionLevels: sessions,
    lastLiquiditySweep: bars15.length ? lastLiquiditySweep(bars15, sweepLevels) : null,
    fvg: {
      '4h':  bars4h.length ? lastFVG(bars4h) : null,
      '1h':  bars1h.length ? lastFVG(bars1h) : null,
      '15m': bars15.length ? lastFVG(bars15) : null,
    },
    orderBlocks: {
      '1h':  bars1h.length ? lastOrderBlock(bars1h) : null,
      '15m': bars15.length ? lastOrderBlock(bars15) : null,
    },
    premiumDiscount: premiumDiscount(bars4h, price),
  };

  persist();
  return memory[sym];
}

export function getMemory(symbol) {
  return memory[String(symbol).toUpperCase()] || null;
}
