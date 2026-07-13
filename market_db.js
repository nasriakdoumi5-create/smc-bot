/**
 * Market Database — قاعدة بيانات الشموع الدائمة
 * ─────────────────────────────────────────────
 * تخزّن كل شمعة مؤكدة تصل من IFA Data Feed V2:
 * { src:"ifa_candle", symbol, exchange, timeframe, timestamp,
 *   open, high, low, close, volume, session, bar_index }
 * TradingView يرسل البيانات الخام فقط — كل التحليل في IFA-OS.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const DIR     = dirname(fileURLToPath(import.meta.url));
const DB_PATH = join(DIR, 'data', 'market_db.json');

export const TIMEFRAMES = ['5m', '15m', '1h', '4h', '1d'];
export const DB_SYMBOLS = ['MNQ', 'MGC', 'MCL'];

// أقصى عدد شموع محفوظ لكل إطار
const MAX_BARS = { '5m': 1200, '15m': 900, '1h': 600, '4h': 400, '1d': 400 };

// تطبيع الإطار الزمني القادم من TradingView (timeframe.period)
const TF_MAP = {
  '5': '5m',  '5m': '5m',
  '15': '15m', '15m': '15m',
  '60': '1h', '1h': '1h',
  '240': '4h', '4h': '4h',
  'd': '1d', '1d': '1d', 'daily': '1d',
};

export function normalizeTf(raw) {
  return TF_MAP[String(raw).toLowerCase()] || null;
}

// ── التحميل / الحفظ ────────────────────────────────────
function load() {
  try { return JSON.parse(readFileSync(DB_PATH, 'utf8')); }
  catch { return {}; }
}

let db = load();          // { MNQ: { '5m': [{time,open,high,low,close,volume,session},...] } }
let lastIngest = {};      // { MNQ: epochMs }
let persistTimer = null;

function persist() {
  // كتابة مؤجلة — تنبيهات عدة أطر قد تصل في نفس اللحظة
  if (persistTimer) return;
  persistTimer = setTimeout(() => {
    persistTimer = null;
    try {
      mkdirSync(join(DIR, 'data'), { recursive: true });
      writeFileSync(DB_PATH, JSON.stringify(db));
    } catch (e) { console.error('[Market DB] persist failed:', e.message); }
  }, 2000);
}

// ── استقبال شمعة مؤكدة واحدة ───────────────────────────
export function ingestCandle(p) {
  const symbol = String(p.symbol || '').toUpperCase();
  const tf     = normalizeTf(p.timeframe);
  const t      = Number(p.timestamp);
  const o = Number(p.open), h = Number(p.high), l = Number(p.low), c = Number(p.close);

  if (!symbol || !tf || !isFinite(t) || !isFinite(c)) {
    return { ok: false, reason: 'invalid candle payload' };
  }

  const time = t > 1e12 ? Math.floor(t / 1000) : Math.floor(t);   // ms → s
  const candle = {
    time,
    open: o, high: h, low: l, close: c,
    volume: isFinite(Number(p.volume)) ? Number(p.volume) : 0,
    session: String(p.session || ''),
  };

  db[symbol] = db[symbol] || {};
  const bars = db[symbol][tf] || [];

  const idx = bars.findIndex(b => b.time === time);
  let isNew = false;
  if (idx >= 0) {
    bars[idx] = candle;                       // تحديث شمعة موجودة
  } else {
    isNew = true;
    bars.push(candle);
    bars.sort((a, b) => a.time - b.time);
    if (bars.length > MAX_BARS[tf]) bars.splice(0, bars.length - MAX_BARS[tf]);
  }
  db[symbol][tf] = bars;

  lastIngest[symbol] = Date.now();
  persist();
  return { ok: true, symbol, timeframe: tf, isNew };
}

// ── القراءة ────────────────────────────────────────────
export function getCandles(symbol, tf, limit = 0) {
  const bars = db[String(symbol).toUpperCase()]?.[tf] || [];
  return limit > 0 ? bars.slice(-limit) : bars;
}

export function lastPrice(symbol) {
  for (const tf of TIMEFRAMES) {
    const bars = getCandles(symbol, tf);
    if (bars.length) return bars[bars.length - 1];
  }
  return null;
}

// ── الحالة (لأمر /feed) ────────────────────────────────
export function dbStatus(symbol) {
  const sym = String(symbol).toUpperCase();
  const depth = {};
  for (const tf of TIMEFRAMES) depth[tf] = getCandles(sym, tf).length;
  return {
    symbol: sym,
    depth,
    hasData: Object.values(depth).some(n => n > 0),
    lastIngest: lastIngest[sym] || null,
  };
}
