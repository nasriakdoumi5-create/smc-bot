/**
 * Market Data
 * السعر الفوري:   Yahoo query2 /v8/chart 1m  (دقيقة واحدة تأخير فقط، بدون API key)
 * البيانات التاريخية: Yahoo query2 /v8/chart 5m
 * الاحتياطي المؤسسي: Tradovate WebSocket (إذا كانت credentials متوفرة)
 */

import { getHistoricalBars, getRealtimePrice } from './tradovate.js';

const YAHOO = {
  MNQ: 'NQ=F',
  MES: 'ES=F',
  MGC: 'GC=F',
  MCL: 'CL=F',
};

async function fetchYahoo(ticker, interval, range) {
  const url = `https://query2.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${interval}&range=${range}&includePrePost=false`;
  const res  = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  if (!res.ok) throw new Error(`Yahoo ${res.status}`);
  const json = await res.json();
  const r    = json.chart?.result?.[0];
  if (!r) throw new Error('No data');
  const ts = r.timestamp;
  const q  = r.indicators.quote[0];
  return ts.map((t, i) => ({
    time: t, open: q.open[i], high: q.high[i],
    low: q.low[i], close: q.close[i], volume: q.volume[i],
  })).filter(b => b.close != null);
}

// ══ السعر الفوري (Tradovate أولاً → Yahoo احتياطي) ═
export async function getRealTimeQuote(symbol = 'MNQ') {
  // Tradovate subscribeQuote — فوري 100%
  if (['MNQ', 'MES'].includes(symbol)) {
    const tvSym = process.env.TRADOVATE_SYMBOL || 'NQM6';
    try {
      const q = await getRealtimePrice(tvSym);
      if (q?.price) {
        console.log(`[data] ✅ Tradovate فوري: ${q.price}`);
        return q;
      }
    } catch {}
    console.log('[data] Tradovate quote فشل — Yahoo احتياطي');
  }
  // Yahoo 1m — تأخير دقيقة واحدة فقط
  const ticker = YAHOO[symbol] || symbol;
  const bars   = await fetchYahoo(ticker, '1m', '1d');
  if (!bars.length) throw new Error('لا بيانات');
  const last = bars[bars.length - 1];
  return { price: last.close, time: last.time };
}

// ══ 5m bars مع تحديث آخر سعر ═══════════════════
export async function get5mBars(symbol = 'MNQ') {
  // 1. Tradovate أولاً (فوري 100%)
  if (['MNQ', 'MES'].includes(symbol)) {
    const tvSym = process.env.TRADOVATE_SYMBOL || 'NQM6';
    try {
      const bars = await getHistoricalBars(tvSym, 5, 500);
      if (bars?.length > 50) {
        console.log(`[data] ✅ Tradovate — ${bars.length} bars`);
        return bars;
      }
    } catch {}
    console.log('[data] Tradovate غير متاح — Yahoo');
  }

  // 2. Yahoo 5m تاريخي
  const ticker = YAHOO[symbol] || symbol;
  const bars   = await fetchYahoo(ticker, '5m', '5d');

  // 3. تحديث آخر بار بالسعر الفوري (Tradovate أو Yahoo 1m)
  try {
    const quote = await getRealTimeQuote(symbol);
    if (quote?.price) {
      const last = bars[bars.length - 1];
      last.close = quote.price;
      last.high  = Math.max(last.high,  quote.price);
      last.low   = Math.min(last.low,   quote.price);
    }
  } catch {
    console.log('[data] تحديث السعر الفوري فشل — نستخدم آخر بار Yahoo 5m');
  }

  return bars;
}

// ══ 1h bars للـ HTF ════════════════════════════
export async function get1hBars(symbol = 'MNQ') {
  if (['MNQ', 'MES'].includes(symbol)) {
    const tvSym = process.env.TRADOVATE_SYMBOL || 'NQM6';
    try {
      const bars = await getHistoricalBars(tvSym, 60, 500);
      if (bars?.length > 50) return bars;
    } catch {}
  }
  const ticker = YAHOO[symbol] || symbol;
  return fetchYahoo(ticker, '60m', '60d');
}

export async function getLastPrice(symbol = 'MNQ') {
  try   { return await getRealTimeQuote(symbol); }
  catch { const b = await get5mBars(symbol); return b[b.length - 1]; }
}
