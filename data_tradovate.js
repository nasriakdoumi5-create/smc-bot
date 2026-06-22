/**
 * Tradovate Market Data — بيانات حية
 * يستبدل Yahoo Finance بالكامل
 */

import { tradovate } from './tradovate.js';

const MD_URLS = {
  demo: 'https://md-demo.tradovateapi.com/v1',
  live: 'https://md.tradovateapi.com/v1',
};

const SYMBOL_MAP = {
  MNQ: 'MNQ',
  MES: 'MES',
};

async function mdReq(path, body) {
  await tradovate.ensureToken();
  const base = MD_URLS[process.env.TRADOVATE_ENV || 'demo'];
  const r = await fetch(`${base}${path}`, {
    method:  'POST',
    headers: {
      'Content-Type':  'application/json',
      'Authorization': `Bearer ${tradovate.token}`,
    },
    body: JSON.stringify(body),
  });
  const text = await r.text();
  try { return JSON.parse(text); }
  catch { return { error: text }; }
}

// جلب الشمعات (5M أو 60M)
async function getBars(symbol, minuteSize, count = 200) {
  const sym = SYMBOL_MAP[symbol] || symbol;

  const r = await mdReq('/md/getChart', {
    symbol: sym,
    chartDescription: {
      underlyingType:   'MinuteBar',
      elementSize:      minuteSize,
      elementSizeUnit:  'UnderlyingUnits',
      withHistogram:    false,
    },
    timeRange: { asMuchAsElements: count },
  });

  if (r.error || !r.bars) {
    throw new Error(`Tradovate getBars(${symbol} ${minuteSize}M): ${JSON.stringify(r)}`);
  }

  return r.bars.map(b => ({
    time:   Math.floor(new Date(b.timestamp).getTime() / 1000),
    open:   b.open,
    high:   b.high,
    low:    b.low,
    close:  b.close,
    volume: b.upVolume + b.downVolume,
  }));
}

export const get5mBars  = (sym) => getBars(sym, 5,  300);
export const get15mBars = (sym) => getBars(sym, 15, 200);
export const get1hBars  = (sym) => getBars(sym, 60, 200);
