/**
 * Gamma Exposure (GEX) Calculator
 * ══════════════════════════════════════════════
 * Source: Yahoo Finance Options Chain (free)
 * Proxy:  QQQ  ← correlated with NQ/MNQ
 *
 * GEX > 0  →  Dealers long gamma → market stays in range
 *              VWAP Bounce signals work well ✅
 *
 * GEX < 0  →  Dealers short gamma → market trends hard
 *              Kill Zone + trend-following only ⚠️
 * ══════════════════════════════════════════════
 */

// ── Black-Scholes helpers ────────────────────────────
function normPDF(x) {
  return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
}

function bsGamma(S, K, T, r, sigma) {
  if (T <= 0 || sigma <= 0 || S <= 0 || K <= 0) return 0;
  const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T));
  return normPDF(d1) / (S * sigma * Math.sqrt(T));
}

// ── Fetch with timeout ────────────────────────────────
async function fetchJSON(url, ms = 10_000) {
  const r = await fetch(url, {
    signal:  AbortSignal.timeout(ms),
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible)' },
  });
  if (!r.ok) throw new Error(`HTTP ${r.status} — ${url}`);
  return r.json();
}

// ── Calculate GEX for one expiry ──────────────────────
function computeGEX(calls, puts, spot, T) {
  const R = 0.05;   // risk-free rate ~5%
  const gexByStrike = {};
  let total = 0;

  for (const c of calls) {
    const iv = c.impliedVolatility;
    const oi = c.openInterest || 0;
    if (!iv || oi <= 0) continue;
    const g   = bsGamma(spot, c.strike, T, R, iv);
    const gex = g * oi * 100 * spot;   // dealer gamma exposure in $
    total += gex;
    gexByStrike[c.strike] = (gexByStrike[c.strike] || 0) + gex;
  }

  for (const p of puts) {
    const iv = p.impliedVolatility;
    const oi = p.openInterest || 0;
    if (!iv || oi <= 0) continue;
    const g   = bsGamma(spot, p.strike, T, R, iv);
    const gex = g * oi * 100 * spot;
    total -= gex;                       // puts subtract (dealers short puts)
    gexByStrike[p.strike] = (gexByStrike[p.strike] || 0) - gex;
  }

  return { total, gexByStrike };
}

// ── Find Gamma Wall & Zero Gamma ─────────────────────
function findLevels(gexByStrike, spot) {
  const entries = Object.entries(gexByStrike)
    .map(([k, v]) => ({ strike: +k, gex: v }))
    .sort((a, b) => a.strike - b.strike);

  // Gamma Wall = strike with largest absolute GEX near spot (±10%)
  const near = entries.filter(e => Math.abs(e.strike - spot) / spot < 0.10);
  const wall  = near.sort((a, b) => Math.abs(b.gex) - Math.abs(a.gex))[0];

  // Zero Gamma = strike where cumulative GEX crosses zero
  let cum = 0, zeroGamma = spot;
  for (const e of entries) {
    const prev = cum;
    cum += e.gex;
    if (prev !== 0 && prev * cum <= 0) { zeroGamma = e.strike; break; }
  }

  // Call Wall (largest positive GEX) & Put Wall (largest negative GEX)
  const callWall = entries.reduce((m, e) => e.gex > m.gex ? e : m, { gex: -Infinity });
  const putWall  = entries.reduce((m, e) => e.gex < m.gex ? e : m, { gex: +Infinity });

  return {
    gammaWall:  wall?.strike  ?? spot,
    zeroGamma,
    callWall:   callWall.strike,
    putWall:    putWall.strike,
  };
}

// ── Main: fetch + calculate ───────────────────────────
export async function calcGEX(ticker = 'QQQ') {
  // Step 1: get spot + nearest expiry
  const base = await fetchJSON(
    `https://query1.finance.yahoo.com/v7/finance/options/${ticker}`
  );
  const res0 = base?.optionChain?.result?.[0];
  if (!res0) throw new Error('No options data from Yahoo');

  const spot  = res0.quote.regularMarketPrice;
  const exps  = res0.expirationDates;   // array of Unix timestamps
  if (!exps?.length) throw new Error('No expirations');

  // Use nearest 2 expiries for better accuracy
  const expiry = exps[0];
  const now    = Date.now() / 1000;
  const T      = Math.max((expiry - now) / (365 * 86_400), 1 / 365);

  // Step 2: get full chain for nearest expiry
  const chain = await fetchJSON(
    `https://query1.finance.yahoo.com/v7/finance/options/${ticker}?date=${expiry}`
  );
  const opts   = chain?.optionChain?.result?.[0]?.options?.[0];
  if (!opts) throw new Error('No options chain');

  const { total, gexByStrike } = computeGEX(opts.calls, opts.puts, spot, T);
  const levels = findLevels(gexByStrike, spot);

  const totalM = Math.round(total / 1e6);  // in millions

  return {
    ticker,
    spot:       +spot.toFixed(2),
    totalGEX:   totalM,
    positive:   total > 0,
    regime:     total > 0 ? 'RANGE' : 'TREND',
    expires:    new Date(expiry * 1000).toISOString().slice(0, 10),
    ...levels,
  };
}

// ── Format for Telegram ───────────────────────────────
export function formatGEX(g) {
  const icon    = g.positive ? '🟢' : '🔴';
  const regime  = g.positive
    ? 'نطاق — VWAP Bounce يعمل ✅'
    : 'اتجاه — Kill Zone فقط ⚠️';
  const gexStr  = g.totalGEX > 0
    ? `+$${g.totalGEX}M`
    : `-$${Math.abs(g.totalGEX)}M`;

  return [
    `${icon} <b>GEX اليوم — ${g.ticker} (proxy NQ)</b>`,
    ``,
    `📊 الوضع:      ${regime}`,
    `💵 GEX إجمالي: <b>${gexStr}</b>`,
    ``,
    `🧲 Gamma Wall: <b>${g.gammaWall}</b>  ← دعم/مقاومة قوية`,
    `📍 Zero Gamma: <b>${g.zeroGamma}</b>  ← تحته = volatile`,
    `📞 Call Wall:  ${g.callWall}  ← سقف طبيعي`,
    `🟡 Put Wall:   ${g.putWall}   ← أرضية طبيعية`,
    ``,
    `⏰ Expires: ${g.expires}`,
  ].join('\n');
}

// ── Cache (refresh max once per hour) ────────────────
let cache = null;
let cacheTime = 0;

export async function getGEX() {
  const now = Date.now();
  if (cache && now - cacheTime < 60 * 60 * 1000) return cache;
  try {
    cache     = await calcGEX('QQQ');
    cacheTime = now;
    console.log(`[GEX] ✅ ${cache.regime} | Wall:${cache.gammaWall} | GEX:${cache.totalGEX}M`);
  } catch (e) {
    console.error('[GEX] ⚠️ Failed:', e.message);
    // Return last cache or null on first fail
  }
  return cache;
}
