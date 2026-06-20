/**
 * Market Data — Tradovate MD API
 * يجلب بيانات OHLC من Tradovate بدلاً من Yahoo Finance
 */

import { tradovate } from './tradovate.js';

// ── تحويل شمعة Tradovate → تنسيقنا ────────────
function parseBars(rawBars) {
  return rawBars
    .map(b => ({
      time:   Math.floor(new Date(b.timestamp).getTime() / 1000),
      open:   b.open,
      high:   b.high,
      low:    b.low,
      close:  b.close,
      volume: (b.upVolume || 0) + (b.downVolume || 0),
    }))
    .filter(b => b.close != null && !isNaN(b.close) && b.close > 0);
}

// ── كاش العقود (يُجدَّد كل 6 ساعات) ─────────────
const contractCache = {};
const CACHE_TTL = 6 * 60 * 60 * 1000; // 6 ساعات

async function getContractName(symbol) {
  const cached = contractCache[symbol];
  if (cached && Date.now() - cached.ts < CACHE_TTL) return cached.name;

  const contract = await tradovate.findContract(symbol);
  const name = contract.name;
  contractCache[symbol] = { name, ts: Date.now() };
  console.log(`[Data] ${symbol} → عقد: ${name}`);
  return name;
}

// ══ دوال الجلب ═══════════════════════════════════

export async function get5mBars(symbol = 'MNQ') {
  const name = await getContractName(symbol);
  return parseBars(await tradovate.getChartData(name, 5, 500));
}

export async function get15mBars(symbol = 'MNQ') {
  const name = await getContractName(symbol);
  return parseBars(await tradovate.getChartData(name, 15, 250));
}

export async function get1hBars(symbol = 'MNQ') {
  const name = await getContractName(symbol);
  return parseBars(await tradovate.getChartData(name, 60, 350));
}

export async function getLastPrice(symbol = 'MNQ') {
  const bars = await get5mBars(symbol);
  return bars[bars.length - 1];
}

// ── للتوافق مع ملفات أخرى ──────────────────────
export async function get1mBars(symbol = 'MNQ') {
  const name = await getContractName(symbol);
  return parseBars(await tradovate.getChartData(name, 1, 500));
}
