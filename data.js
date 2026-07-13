/**
 * Market Data — Yahoo Finance (مجاني بدون API key)
 * رموز: NQ=F (Nasdaq Futures), GC=F (Gold), ES=F (S&P)
 */

const SYMBOLS = {
  MNQ: 'NQ=F',   // Micro Nasdaq
  MGC: 'GC=F',   // Micro Gold
  MCL: 'CL=F',   // Micro Crude Oil
  MES: 'ES=F',   // S&P 500
};

const INTERVALS = {
  '5m':  '5m',
  '15m': '15m',
  '1h':  '60m',
  '4h':  '1h',   // Yahoo لا يدعم 4h مباشرة — نحسبه من 1h
  '1d':  '1d',
};

async function fetchYahoo(symbol, interval, range) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=${interval}&range=${range}&includePrePost=true`;
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0' }
  });
  if (!res.ok) throw new Error(`Yahoo Finance error: ${res.status}`);
  const json = await res.json();

  const result = json.chart?.result?.[0];
  if (!result) throw new Error('No data from Yahoo Finance');

  const timestamps = result.timestamp;
  const q = result.indicators.quote[0];

  const bars = timestamps.map((t, i) => ({
    time:   t,
    open:   q.open[i],
    high:   q.high[i],
    low:    q.low[i],
    close:  q.close[i],
    volume: q.volume[i],
  })).filter(b => b.close != null);

  return bars;
}

/**
 * جلب 15m bars لآخر 5 أيام (للـ MTF structure)
 */
export async function get15mBars(symbol = 'MNQ') {
  const ticker = SYMBOLS[symbol] || symbol;
  return fetchYahoo(ticker, '15m', '5d');
}

/**
 * جلب 1m bars لآخر يومين (للدخول الدقيق)
 */
export async function get1mBars(symbol = 'MNQ') {
  const ticker = SYMBOLS[symbol] || symbol;
  return fetchYahoo(ticker, '1m', '2d');
}

/**
 * جلب 5m bars لآخر 5 أيام
 */
export async function get5mBars(symbol = 'MNQ') {
  const ticker = SYMBOLS[symbol] || symbol;
  return fetchYahoo(ticker, '5m', '5d');
}

/**
 * جلب 1h bars لآخر 60 يوم (للـ HTF trend)
 */
export async function get1hBars(symbol = 'MNQ') {
  const ticker = SYMBOLS[symbol] || symbol;
  return fetchYahoo(ticker, '60m', '60d');
}

/**
 * جلب 1d bars لآخر سنة (للـ macro direction)
 */
export async function get1dBars(symbol = 'MNQ') {
  const ticker = SYMBOLS[symbol] || symbol;
  return fetchYahoo(ticker, '1d', '1y');
}

/**
 * جلب آخر سعر
 */
export async function getLastPrice(symbol = 'MNQ') {
  const bars = await get5mBars(symbol);
  return bars[bars.length - 1];
}
