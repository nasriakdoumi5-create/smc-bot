/**
 * TradingView Live Market Data — مخزن الشموع
 * ─────────────────────────────────────────────
 * المصدر الوحيد للبيانات الحية لمحرك IFA-OS.
 * يُغذّى من مؤشر "IFA Data Feed" (tradingview_datafeed.pine)
 * عبر نفس قناة الـ webhook الموجودة: TradingView Alert → POST /webhook
 * payload: { src:"ifa_feed", s:"MNQ", bars:{ "5m":[[timeMs,o,h,l,c,v],...], ... } }
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const DIR        = dirname(fileURLToPath(import.meta.url));
const STORE_PATH = join(DIR, 'data', 'tv_bars.json');

export const TIMEFRAMES = ['5m', '15m', '1h', '4h', '1d'];

// أقصى عدد شموع محفوظ لكل إطار
const MAX_BARS = { '5m': 600, '15m': 500, '1h': 400, '4h': 300, '1d': 300 };

// ── تحميل المخزن من القرص (يبقى بعد إعادة التشغيل) ────
function load() {
  try { return JSON.parse(readFileSync(STORE_PATH, 'utf8')); }
  catch { return {}; }
}

let store = load();               // { MNQ: { '5m': [{time,open,high,low,close,volume},...] } }
let lastIngest = {};              // { MNQ: epochMs }

function persist() {
  try {
    mkdirSync(join(DIR, 'data'), { recursive: true });
    writeFileSync(STORE_PATH, JSON.stringify(store));
  } catch (e) { console.error('[TV Feed] persist failed:', e.message); }
}

// ── استقبال دفعة شموع من TradingView ──────────────────
export function ingestFeed(payload) {
  const symbol = String(payload.s || '').toUpperCase();
  if (!symbol || typeof payload.bars !== 'object') return { ok: false };

  store[symbol] = store[symbol] || {};
  let added = 0;

  for (const tf of TIMEFRAMES) {
    const incoming = payload.bars[tf];
    if (!Array.isArray(incoming)) continue;

    const existing = store[symbol][tf] || [];
    const byTime = new Map(existing.map(b => [b.time, b]));

    for (const row of incoming) {
      if (!Array.isArray(row) || row.length < 5) continue;
      const [t, o, h, l, c, v] = row.map(Number);
      if (!isFinite(t) || !isFinite(c)) continue;
      const time = t > 1e12 ? Math.floor(t / 1000) : Math.floor(t);   // ms → s
      if (!byTime.has(time)) added++;
      byTime.set(time, { time, open: o, high: h, low: l, close: c, volume: isFinite(v) ? v : 0 });
    }

    store[symbol][tf] = [...byTime.values()]
      .sort((a, b) => a.time - b.time)
      .slice(-MAX_BARS[tf]);
  }

  lastIngest[symbol] = Date.now();
  persist();
  return { ok: true, added };
}

// ── قراءة الشموع ───────────────────────────────────────
export function getBars(symbol, tf) {
  return store[String(symbol).toUpperCase()]?.[tf] || [];
}

export function getLastPrice(symbol) {
  for (const tf of TIMEFRAMES) {
    const bars = getBars(symbol, tf);
    if (bars.length) return bars[bars.length - 1];
  }
  return null;
}

// ── حالة التغذية (لأمر /feed وللتقارير) ────────────────
export function feedStatus(symbol) {
  const sym = String(symbol).toUpperCase();
  const depth = {};
  for (const tf of TIMEFRAMES) depth[tf] = getBars(sym, tf).length;
  return {
    symbol: sym,
    depth,
    hasData: Object.values(depth).some(n => n > 0),
    lastIngest: lastIngest[sym] || null,
  };
}
