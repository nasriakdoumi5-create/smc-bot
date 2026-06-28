/**
 * Market Data
 * أولوية: TradingView Bridge (محلي، بيانات حية) → Yahoo Finance (احتياطي)
 */

const BRIDGE = 'http://localhost:3031';

// رموز Yahoo Finance المقابلة
const YAHOO_MAP = {
  MNQ: 'MNQ=F', MGC: 'MGC=F', MCL: 'MCL=F', MES: 'MES=F',
  NQ:  'NQ=F',  ES:  'ES=F',  GC:  'GC=F',  CL:  'CL=F',
};

const TF_YAHOO = {
  '1m': { interval: '1m',  range: '7d'  },
  '5m': { interval: '5m',  range: '60d' },
  '15m':{ interval: '15m', range: '60d' },
  '1h': { interval: '60m', range: '60d' },
};

async function fetchBridge(symbol, tf, count) {
  const res = await fetch(`${BRIDGE}/?symbol=${symbol}&tf=${tf}`, { signal: AbortSignal.timeout(3000) });
  if (!res.ok) throw new Error(`Bridge ${res.status}`);
  const { bars, age_seconds } = await res.json();
  if (!bars?.length) throw new Error('no bars');
  if (age_seconds > 300) console.warn(`[data] ⚠️ ${symbol} ${tf} عمرها ${age_seconds}ث`);
  return bars.slice(-count);
}

async function fetchYahoo(symbol, tf, count) {
  const ticker = YAHOO_MAP[symbol] || symbol;
  const { interval, range } = TF_YAHOO[tf] || TF_YAHOO['5m'];
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${interval}&range=${range}&includePrePost=false`;
  const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  if (!res.ok) throw new Error(`Yahoo ${res.status}`);
  const j   = await res.json();
  const r   = j.chart?.result?.[0];
  if (!r)   throw new Error(`Yahoo: لا بيانات لـ ${symbol}`);
  const ts  = r.timestamp, q = r.indicators.quote[0];
  const bars = ts.map((t, i) => ({
    time: t, open: q.open[i], high: q.high[i],
    low: q.low[i], close: q.close[i], volume: q.volume[i] || 0
  })).filter(b => b.close != null);
  return bars.slice(-count);
}

async function getBars(symbol, tf, count) {
  try {
    const bars = await fetchBridge(symbol, tf, count);
    console.log(`[data] 🔴 Bridge ${symbol} ${tf} — ${bars.length} شمعة`);
    return bars;
  } catch {
    console.log(`[data] 📡 Yahoo ${symbol} ${tf}`);
    return fetchYahoo(symbol, tf, count);
  }
}

export async function get1mBars(symbol = 'MNQ')  { return getBars(symbol, '1m',  300); }
export async function get5mBars(symbol = 'MNQ')  { return getBars(symbol, '5m',  200); }
export async function get15mBars(symbol = 'MNQ') { return getBars(symbol, '15m', 200); }
export async function get1hBars(symbol = 'MNQ')  { return getBars(symbol, '1h',  200); }

export async function getLastPrice(symbol = 'MNQ') {
  const bars = await get5mBars(symbol);
  return bars[bars.length - 1];
}
