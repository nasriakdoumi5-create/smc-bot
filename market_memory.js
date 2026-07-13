/**
 * Institutional Memory Engine — محرك الذاكرة المؤسسية
 * ────────────────────────────────────────────────────
 * لا يخزّن شموعاً — يخزّن حالة السوق المؤسسية الحالية:
 * انحيازات (يومي/أسبوعي/شهري)، هيكل، BOS/CHOCH رئيسية،
 * نطاق التداول (Premium/Discount/EQ)، سيولة (أسبوعية/يومية/
 * خارجية/داخلية)، مناطق نشطة (OB/FVG/Breaker/Mitigation)،
 * Kill Zone، الجلسة، قوة الترند، وطور السوق.
 *
 * تحديث تفاضلي: كل شمعة جديدة تحدّث الأقسام المتأثرة بإطارها
 * فقط بدلاً من إعادة حساب كل شيء.
 *
 * كل الحسابات هنا — TradingView يرسل شموعاً خاماً فقط.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { swingHighs, swingLows, atr } from './smc.js';
import { getCandles, lastPrice, normalizeTf } from './market_db.js';

const DIR      = dirname(fileURLToPath(import.meta.url));
const MEM_PATH = join(DIR, 'data', 'market_memory.json');

const SWING_LEN  = { '1d': 3, '4h': 3, '1h': 4, '15m': 5 };
const ZONE_SCAN  = 200;   // عمق فحص المناطق (OB/FVG) لكل إطار
const MAX_ZONES  = 3;     // أقصى مناطق نشطة معروضة لكل نوع/إطار

function load() {
  try { return JSON.parse(readFileSync(MEM_PATH, 'utf8')); }
  catch { return {}; }
}

let memory = load();

function persist() {
  try {
    mkdirSync(join(DIR, 'data'), { recursive: true });
    writeFileSync(MEM_PATH, JSON.stringify(memory));
  } catch (e) { console.error('[Memory] persist failed:', e.message); }
}

const iso = t => new Date(t * 1000).toISOString().slice(0, 16).replace('T', ' ');
const r2  = n => (n == null || !isFinite(n) ? null : +Number(n).toFixed(2));

// ══════════════════════════════════════════════════════
//  SWINGS + STRUCTURE (آلة حالة BOS/CHOCH)
// ══════════════════════════════════════════════════════

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

// يعيد الترند + كل أحداث الكسر (للـ trend strength وطور السوق)
function analyzeStructure(bars, len) {
  const swings = detectSwings(bars, len);
  if (swings.length < 2) {
    return {
      trend: `Undetermined — fewer than 2 confirmed swings in the available ${bars.length} bars`,
      lastBOS: null, lastCHOCH: null, swingHigh: null, swingLow: null, events: [],
    };
  }

  let trend = null, lastBOS = null, lastCHOCH = null;
  let refHigh = null, refLow = null;
  let si = 0;
  const events = [];

  for (let i = 0; i < bars.length; i++) {
    while (si < swings.length && swings[si].idx + len <= i) {
      if (swings[si].type === 'H') refHigh = swings[si];
      else refLow = swings[si];
      si++;
    }
    const c = bars[i].close;
    if (refHigh && c > refHigh.price) {
      const type = trend === 'Bearish' ? 'CHOCH' : 'BOS';
      const ev = { type, direction: 'Bullish', level: r2(refHigh.price), time: iso(bars[i].time), idx: i };
      if (type === 'CHOCH') lastCHOCH = ev; else lastBOS = ev;
      events.push(ev);
      trend = 'Bullish';
      refHigh = null;
    } else if (refLow && c < refLow.price) {
      const type = trend === 'Bullish' ? 'CHOCH' : 'BOS';
      const ev = { type, direction: 'Bearish', level: r2(refLow.price), time: iso(bars[i].time), idx: i };
      if (type === 'CHOCH') lastCHOCH = ev; else lastBOS = ev;
      events.push(ev);
      trend = 'Bearish';
      refLow = null;
    }
  }

  const lastH = [...swings].reverse().find(s => s.type === 'H');
  const lastL = [...swings].reverse().find(s => s.type === 'L');

  return {
    trend: trend || 'Range / Undefined',
    lastBOS: lastBOS && { ...lastBOS, idx: undefined },
    lastCHOCH: lastCHOCH && { ...lastCHOCH, idx: undefined },
    swingHigh: lastH ? { price: r2(lastH.price), time: iso(lastH.time) } : null,
    swingLow:  lastL ? { price: r2(lastL.price), time: iso(lastL.time) } : null,
    events,
    barsCount: bars.length,
  };
}

// ══════════════════════════════════════════════════════
//  BIAS — يومي / أسبوعي / شهري
// ══════════════════════════════════════════════════════

// تجميع شموع 1d إلى شموع أسبوعية/شهرية
function aggregate(bars1d, keyFn) {
  const groups = new Map();
  for (const b of bars1d) {
    const key = keyFn(new Date(b.time * 1000));
    const g = groups.get(key);
    if (!g) groups.set(key, { time: b.time, open: b.open, high: b.high, low: b.low, close: b.close, volume: b.volume });
    else {
      g.high = Math.max(g.high, b.high);
      g.low  = Math.min(g.low, b.low);
      g.close = b.close;
      g.volume += b.volume;
    }
  }
  return [...groups.values()].sort((a, b) => a.time - b.time);
}

const weekKey  = d => { const x = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate())); x.setUTCDate(x.getUTCDate() - (x.getUTCDay() + 6) % 7); return x.toISOString().slice(0, 10); };
const monthKey = d => `${d.getUTCFullYear()}-${d.getUTCMonth()}`;

function biasOf(bars, len) {
  if (bars.length < len * 2 + 3) {
    return `Undetermined — only ${bars.length} bars available`;
  }
  const s = analyzeStructure(bars, len);
  if (s.trend.startsWith('Undetermined')) {
    // fallback: موقع الإغلاق داخل نطاق آخر شمعتين مكتملتين
    const prev = bars[bars.length - 2], cur = bars[bars.length - 1];
    if (cur.close > prev.high) return 'Bullish (closing above prior bar range)';
    if (cur.close < prev.low)  return 'Bearish (closing below prior bar range)';
    return 'Neutral (inside prior bar range)';
  }
  return s.trend;
}

// ══════════════════════════════════════════════════════
//  ZONE LIFECYCLE — OB → Mitigation Block → Breaker
// ══════════════════════════════════════════════════════
// - Order Block  : شمعة معاكسة قبل displacement — نشط حتى يُلمس
// - Mitigation   : OB لُمس (دخل السعر المنطقة) دون كسره — لا يزال فاعلاً
// - Breaker      : OB كُسر (إغلاق كامل خلفه) — ينقلب قطبياً ويبقى نشطاً
//                  حتى يُخترق مرة أخرى
function zoneEngine(bars) {
  if (bars.length < 20) return { orderBlocks: [], mitigationBlocks: [], breakers: [] };
  const scan = bars.slice(-ZONE_SCAN);
  const atrArr = atr(scan, 14);

  const zones = [];
  for (let i = 1; i < scan.length - 1; i++) {
    const b = scan[i], next = scan[i + 1];
    const a = atrArr[i + 1] || atrArr[atrArr.length - 1] || 0;
    if (!a) continue;
    const bullDisp = next.close > b.high && (next.close - next.open) > a * 0.8;
    const bearDisp = next.close < b.low  && (next.open - next.close) > a * 0.8;
    if (bullDisp && b.close < b.open) {
      zones.push({ direction: 'Bullish', top: b.open, bottom: b.close, time: b.time, idx: i });
    } else if (bearDisp && b.close > b.open) {
      zones.push({ direction: 'Bearish', top: b.close, bottom: b.open, time: b.time, idx: i });
    }
  }

  const orderBlocks = [], mitigationBlocks = [], breakers = [];

  for (const z of zones) {
    let touched = false, broken = false, brokenIdx = -1;
    for (let i = z.idx + 2; i < scan.length; i++) {
      const bar = scan[i];
      if (z.direction === 'Bullish') {
        if (bar.close < z.bottom) { broken = true; brokenIdx = i; break; }
        if (bar.low <= z.top) touched = true;
      } else {
        if (bar.close > z.top) { broken = true; brokenIdx = i; break; }
        if (bar.high >= z.bottom) touched = true;
      }
    }

    const zone = { direction: z.direction, top: r2(z.top), bottom: r2(z.bottom), time: iso(z.time) };

    if (broken) {
      // Breaker — قطبية معكوسة؛ نشط ما لم يُخترق مجدداً
      const flipped = z.direction === 'Bullish' ? 'Bearish' : 'Bullish';
      let invalidated = false;
      for (let i = brokenIdx + 1; i < scan.length; i++) {
        const bar = scan[i];
        if (flipped === 'Bearish' && bar.close > z.top)    { invalidated = true; break; }
        if (flipped === 'Bullish' && bar.close < z.bottom) { invalidated = true; break; }
      }
      if (!invalidated) breakers.push({ ...zone, direction: flipped, origin: `broken ${z.direction} OB` });
    } else if (touched) {
      mitigationBlocks.push({ ...zone, status: 'mitigated — partially filled, not violated' });
    } else {
      orderBlocks.push({ ...zone, status: 'fresh — untested' });
    }
  }

  return {
    orderBlocks: orderBlocks.slice(-MAX_ZONES).reverse(),
    mitigationBlocks: mitigationBlocks.slice(-MAX_ZONES).reverse(),
    breakers: breakers.slice(-MAX_ZONES).reverse(),
  };
}

// ══ FVGs النشطة (غير المُغطاة) ═════════════════════════
function activeFVGs(bars) {
  const scan = bars.slice(-ZONE_SCAN);
  const out = [];
  for (let i = 2; i < scan.length; i++) {
    let gap = null;
    if (scan[i].low > scan[i - 2].high) {
      gap = { direction: 'Bullish', top: scan[i].low, bottom: scan[i - 2].high, idx: i - 1, time: scan[i - 1].time };
    } else if (scan[i].high < scan[i - 2].low) {
      gap = { direction: 'Bearish', top: scan[i - 2].low, bottom: scan[i].high, idx: i - 1, time: scan[i - 1].time };
    }
    if (gap) out.push(gap);
  }
  const active = out.filter(gap => {
    for (let i = gap.idx + 2; i < scan.length; i++) {
      if (gap.direction === 'Bullish' && scan[i].low <= gap.bottom) return false;
      if (gap.direction === 'Bearish' && scan[i].high >= gap.top)   return false;
    }
    return true;
  });
  return active.slice(-MAX_ZONES).reverse()
    .map(g => ({ direction: g.direction, top: r2(g.top), bottom: r2(g.bottom), time: iso(g.time) }));
}

// ══════════════════════════════════════════════════════
//  KEY LEVELS + LIQUIDITY
// ══════════════════════════════════════════════════════

function keyLevels(bars1d) {
  if (!bars1d.length) return {};
  const cur = new Date(bars1d[bars1d.length - 1].time * 1000);
  const week  = bars1d.filter(b => weekKey(new Date(b.time * 1000)) === weekKey(cur));
  const month = bars1d.filter(b => monthKey(new Date(b.time * 1000)) === monthKey(cur));
  const prevWeekKeyStr = (() => { const d = new Date(cur); d.setUTCDate(d.getUTCDate() - 7); return weekKey(d); })();
  const prevWeek = bars1d.filter(b => weekKey(new Date(b.time * 1000)) === prevWeekKeyStr);
  const yesterday = bars1d.length >= 2 ? bars1d[bars1d.length - 2] : null;

  const hi = a => a.length ? r2(Math.max(...a.map(b => b.high))) : null;
  const lo = a => a.length ? r2(Math.min(...a.map(b => b.low)))  : null;

  return {
    weeklyHigh: hi(week),   weeklyLow: lo(week),
    prevWeekHigh: hi(prevWeek), prevWeekLow: lo(prevWeek),
    monthlyHigh: hi(month), monthlyLow: lo(month),
    yesterdayHigh: yesterday ? r2(yesterday.high) : null,
    yesterdayLow:  yesterday ? r2(yesterday.low)  : null,
  };
}

function sessionLevels(bars5m) {
  if (!bars5m.length) return {};
  const dayStr = new Date(bars5m[bars5m.length - 1].time * 1000).toISOString().slice(0, 10);
  const today  = bars5m.filter(b => new Date(b.time * 1000).toISOString().slice(0, 10) === dayStr);

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

  return { asia: level('asia'), london: level('london'), newYork: level('newyork') || level('york') };
}

// هل أُخذ المستوى بعد تكوّنه (تجاوزه السعر ولو بوِك)
function takenStatus(bars15, price, formedAt, isHigh) {
  if (price == null) return null;
  for (let i = bars15.length - 1; i >= 0; i--) {
    const b = bars15[i];
    if (b.time <= (formedAt || 0)) break;
    if (isHigh  && b.high > price) return { taken: true, at: iso(b.time) };
    if (!isHigh && b.low  < price) return { taken: true, at: iso(b.time) };
  }
  return { taken: false };
}

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

// ══════════════════════════════════════════════════════
//  DEALING RANGE + PREMIUM / DISCOUNT
// ══════════════════════════════════════════════════════

function dealingRange(bars4h, price) {
  if (price == null || bars4h.length < 20) return null;
  const range = bars4h.slice(-60);
  const high = Math.max(...range.map(b => b.high));
  const low  = Math.min(...range.map(b => b.low));
  if (high <= low) return null;

  const eq  = (high + low) / 2;
  const pos = Math.min(1, Math.max(0, (price - low) / (high - low)));
  return {
    high: r2(high),
    low: r2(low),
    equilibrium: r2(eq),
    premiumZone:  { from: r2(eq),  to: r2(high) },
    discountZone: { from: r2(low), to: r2(eq) },
    currentState: pos > 0.5 ? 'Premium' : 'Discount',
    positionInRange: `${Math.round(pos * 100)}%`,
  };
}

// ══════════════════════════════════════════════════════
//  SESSION + KILL ZONE (من الساعة الحالية UTC)
// ══════════════════════════════════════════════════════

function sessionContext() {
  const now = new Date();
  const m = now.getUTCHours() * 60 + now.getUTCMinutes();
  const session =
    m < 7 * 60  ? 'Asia' :
    m < 13 * 60 ? 'London' :
    m < 22 * 60 ? 'New York' : 'Off-hours';
  const killZone =
    m >= 0            && m < 3 * 60           ? 'Asia KZ (00:00–03:00 UTC)' :
    m >= 7 * 60       && m < 10 * 60          ? 'London Open KZ (07:00–10:00 UTC)' :
    m >= 13 * 60 + 30 && m < 16 * 60 + 30     ? 'New York Open KZ (13:30–16:30 UTC)' :
    m >= 19 * 60      && m < 21 * 60          ? 'London Close / NY PM KZ (19:00–21:00 UTC)' :
    'None';
  return { currentSession: session, currentKillZone: killZone };
}

// ══════════════════════════════════════════════════════
//  TREND STRENGTH + MARKET PHASE (على 4H)
// ══════════════════════════════════════════════════════

function trendStrength(structure4h, range) {
  if (!structure4h || structure4h.trend.startsWith('Undetermined')) {
    return { rating: 'Undetermined', detail: 'insufficient structure data' };
  }
  const events = structure4h.events || [];
  let consecutive = 0;
  for (let i = events.length - 1; i >= 0; i--) {
    if (events[i].direction === (structure4h.trend === 'Bullish' ? 'Bullish' : 'Bearish')) consecutive++;
    else break;
  }
  const pos = range ? parseInt(range.positionInRange) : 50;
  const displaced = Math.abs(pos - 50) > 25;

  let rating;
  if (structure4h.trend.startsWith('Range')) rating = 'Weak / Ranging';
  else if (consecutive >= 2 && displaced)    rating = 'Strong';
  else if (consecutive >= 1)                 rating = 'Moderate';
  else                                       rating = 'Weak';

  return { rating, detail: `${consecutive} consecutive structure break(s) in trend direction; price at ${pos}% of dealing range` };
}

function marketPhase(bars4h, structure4h, range) {
  if (!structure4h || bars4h.length < 40) {
    return { phase: 'Undetermined', reasoning: 'insufficient 4H data' };
  }

  // Reversal: CHOCH حديث (ضمن آخر 12 شمعة 4H)
  const lastEv = (structure4h.events || [])[structure4h.events.length - 1];
  if (lastEv?.type === 'CHOCH' && lastEv.idx >= bars4h.slice(-ZONE_SCAN).length - 12) {
    return { phase: 'Reversal', reasoning: `recent ${lastEv.direction} CHOCH at ${lastEv.level} (${lastEv.time})` };
  }

  // Compression: نطاق آخر 12 شمعة مقابل الـ24 السابقة
  const recent = bars4h.slice(-12);
  const prior  = bars4h.slice(-36, -12);
  const rng = a => Math.max(...a.map(b => b.high)) - Math.min(...a.map(b => b.low));
  const compressed = prior.length >= 12 && rng(recent) < rng(prior) * 0.55;

  const state = range?.currentState;
  if (compressed) {
    if (state === 'Premium')  return { phase: 'Distribution', reasoning: 'compression in premium after prior expansion' };
    return { phase: 'Accumulation', reasoning: `compression in ${state ? state.toLowerCase() : 'range'} — building positions` };
  }

  if (structure4h.trend === 'Bullish' || structure4h.trend === 'Bearish') {
    return { phase: 'Expansion', reasoning: `active ${structure4h.trend.toLowerCase()} trend with no significant compression` };
  }

  return { phase: 'Accumulation', reasoning: 'no clear trend, no compression signature — treated as ranging accumulation' };
}

// ══════════════════════════════════════════════════════
//  SECTION COMPUTERS — كل قسم يُحسب مستقلاً
// ══════════════════════════════════════════════════════

const strip = s => s && { trend: s.trend, lastBOS: s.lastBOS, lastCHOCH: s.lastCHOCH, swingHigh: s.swingHigh, swingLow: s.swingLow };

const SECTIONS = {
  price(sym, M) {
    M.currentPrice = r2(lastPrice(sym)?.close ?? null);
  },

  bias(sym, M) {
    const bars1d = getCandles(sym, '1d');
    M.bias = {
      daily:   biasOf(bars1d, SWING_LEN['1d']),
      weekly:  biasOf(aggregate(bars1d, weekKey), 2),
      monthly: biasOf(aggregate(bars1d, monthKey), 2),
    };
  },

  structure(sym, M, tfs = ['1d', '4h', '1h', '15m']) {
    M.structure = M.structure || {};
    M._events = M._events || {};
    for (const tf of tfs) {
      const bars = getCandles(sym, tf);
      const s = bars.length >= 10
        ? analyzeStructure(bars.slice(-ZONE_SCAN), SWING_LEN[tf])
        : { trend: `Insufficient data (${bars.length} bars)` };
      M.structure[tf] = strip(s);
      M._events[tf] = s.events || [];
    }
  },

  major(sym, M) {
    // الأحداث الرئيسية = هيكل اليومي، وإن غاب فالـ 4H
    const src = ['1d', '4h'].find(tf => M.structure?.[tf]?.lastBOS || M.structure?.[tf]?.lastCHOCH);
    M.majorStructure = {
      timeframe: src || null,
      lastMajorBOS:   src ? M.structure[src].lastBOS   : null,
      lastMajorCHOCH: src ? M.structure[src].lastCHOCH : null,
    };
  },

  range(sym, M) {
    M.dealingRange = dealingRange(getCandles(sym, '4h'), lastPrice(sym)?.close);
  },

  levels(sym, M) {
    M.keyLevels = keyLevels(getCandles(sym, '1d'));
  },

  sessions(sym, M) {
    M.sessionLevels = sessionLevels(getCandles(sym, '5m'));
  },

  liquidity(sym, M) {
    const bars15 = getCandles(sym, '15m');
    const price  = lastPrice(sym)?.close;
    const L = M.keyLevels || {};
    const S = M.sessionLevels || {};
    const dayStart = (() => {
      const b = getCandles(sym, '1d');
      if (!b.length) return 0;
      return Math.floor(new Date(new Date(b[b.length - 1].time * 1000).toISOString().slice(0, 10)).getTime() / 1000);
    })();

    const lvl = (price_, formedAt, isHigh) => price_ == null ? null
      : { price: price_, ...takenStatus(bars15, price_, formedAt, isHigh) };

    M.liquidity = {
      weekly: { high: lvl(L.weeklyHigh, dayStart, true),  low: lvl(L.weeklyLow, dayStart, false) },
      daily:  { high: lvl(L.yesterdayHigh, dayStart, true), low: lvl(L.yesterdayLow, dayStart, false) },
      // خارجية: أطراف نطاق التداول — أهداف السيولة الكبرى
      external: M.dealingRange ? {
        buySide:  { level: M.dealingRange.high, note: 'old highs above the dealing range' },
        sellSide: { level: M.dealingRange.low,  note: 'old lows below the dealing range' },
      } : null,
      // داخلية: مناطق عدم التوازن داخل النطاق (FVGs/OBs النشطة)
      internal: {
        note: 'active FVGs and order blocks inside the dealing range act as internal liquidity draws',
        fvgCount: Object.values(M.activeFVGs || {}).flat().length,
        orderBlockCount: Object.values(M.activeOrderBlocks || {}).flat().length,
      },
      lastSweep: bars15.length ? lastLiquiditySweep(bars15, {
        yesterdayHigh: { price: L.yesterdayHigh, formedAt: dayStart },
        yesterdayLow:  { price: L.yesterdayLow,  formedAt: dayStart },
        weeklyHigh:    { price: L.weeklyHigh,    formedAt: dayStart },
        weeklyLow:     { price: L.weeklyLow,     formedAt: dayStart },
        asiaHigh:    { price: S.asia?.high,    formedAt: S.asia?.highTime },
        asiaLow:     { price: S.asia?.low,     formedAt: S.asia?.lowTime },
        londonHigh:  { price: S.london?.high,  formedAt: S.london?.highTime },
        londonLow:   { price: S.london?.low,   formedAt: S.london?.lowTime },
        newYorkHigh: { price: S.newYork?.high, formedAt: S.newYork?.highTime },
        newYorkLow:  { price: S.newYork?.low,  formedAt: S.newYork?.lowTime },
      }) : null,
    };
  },

  zones(sym, M, tfs = ['4h', '1h', '15m']) {
    M.activeOrderBlocks     = M.activeOrderBlocks || {};
    M.activeFVGs            = M.activeFVGs || {};
    M.activeBreakers        = M.activeBreakers || {};
    M.activeMitigationBlocks = M.activeMitigationBlocks || {};
    for (const tf of tfs) {
      const bars = getCandles(sym, tf);
      if (bars.length < 20) continue;
      const z = zoneEngine(bars);
      M.activeOrderBlocks[tf]      = z.orderBlocks;
      M.activeMitigationBlocks[tf] = z.mitigationBlocks;
      M.activeBreakers[tf]         = z.breakers;
      M.activeFVGs[tf]             = activeFVGs(bars);
    }
  },

  context(sym, M) {
    M.context = sessionContext();
  },

  strength(sym, M) {
    const s4h = M.structure?.['4h'] ? { ...M.structure['4h'], events: M._events?.['4h'] || [] } : null;
    M.trendStrength = trendStrength(s4h, M.dealingRange);
  },

  phase(sym, M) {
    const s4h = M.structure?.['4h'] ? { ...M.structure['4h'], events: M._events?.['4h'] || [] } : null;
    M.marketPhase = marketPhase(getCandles(sym, '4h'), s4h, M.dealingRange);
  },
};

// ══════════════════════════════════════════════════════
//  التحديث التفاضلي — كل إطار يحدّث أقسامه المتأثرة فقط
// ══════════════════════════════════════════════════════

const TF_SECTIONS = {
  '5m':  ['price', 'sessions', 'liquidity', 'context'],
  '15m': ['price', ['structure', ['15m']], ['zones', ['15m']], 'liquidity', 'context'],
  '1h':  ['price', ['structure', ['1h']], ['zones', ['1h']], 'context'],
  '4h':  ['price', ['structure', ['4h']], ['zones', ['4h']], 'range', 'liquidity', 'strength', 'phase', 'context'],
  '1d':  ['price', 'bias', ['structure', ['1d']], 'major', 'levels', 'liquidity', 'context'],
};

function runSections(sym, M, sections) {
  for (const entry of sections) {
    const [name, extra] = Array.isArray(entry) ? entry : [entry, undefined];
    try { SECTIONS[name](sym, M, extra); }
    catch (e) { console.error(`[Memory] section ${name} failed:`, e.message); }
  }
  M.updatedAt = iso(Math.floor(Date.now() / 1000));
}

/** تحديث تفاضلي عند وصول شمعة جديدة */
export function updateOnCandle(symbol, timeframe) {
  const sym = String(symbol).toUpperCase();
  if (!memory[sym]) return updateMemory(sym);   // أول مرة: بناء كامل

  const tf = normalizeTf(timeframe) || timeframe;   // يقبل '240' أو '4h'
  const M = memory[sym];
  runSections(sym, M, TF_SECTIONS[tf] || ['price', 'context']);
  persist();
  return M;
}

/** بناء كامل للذاكرة (أول تشغيل أو طلب يدوي) */
export function updateMemory(symbol) {
  const sym = String(symbol).toUpperCase();
  const M = memory[sym] = { symbol: sym };
  runSections(sym, M, [
    'price', 'bias', 'structure', 'major', 'range', 'levels',
    'sessions', 'zones', 'liquidity', 'context', 'strength', 'phase',
  ]);
  persist();
  return M;
}

export function getMemory(symbol) {
  const M = memory[String(symbol).toUpperCase()];
  if (!M) return null;
  // _events داخلية — لا تُعرض في اللقطة
  const { _events, ...snapshot } = M;
  return snapshot;
}
