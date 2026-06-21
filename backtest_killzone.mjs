/**
 * Backtest — Kill Zone Sweep
 * PDH/PDL(3) + Asia H/L(2) + Swing H/L(1) | London+NY Kill Zones
 * R:R 1:2 | RSI 58/42 | Wick 0.25 ATR | Cooldown 18 bars
 */

function generateBars(symbol, n5m = 12000) {
  const cfg = {
    MNQ: { p0: 21000, atrPct: 0.00055, driftPct: 0.00007 },
    MCL: { p0: 72.50, atrPct: 0.00090, driftPct: 0.00010 },
  }[symbol];
  const { p0, atrPct, driftPct } = cfg;
  const t0 = Math.floor(Date.now() / 1000) - n5m * 300;

  const bars = [];
  let price = p0, dir = 1, phase = 0;
  let nextFlip = 300 + Math.floor(Math.random() * 400);

  for (let i = 0; i < n5m; i++) {
    if (++phase >= nextFlip) {
      dir *= -1; phase = 0;
      nextFlip = 300 + Math.floor(Math.random() * 400);
    }
    const atrV  = atrPct * price;
    const drift = dir * driftPct * price;
    const noise = (Math.random() - 0.5) * 2 * atrV;
    const osc   = Math.sin(i * 0.04) * atrV * 1.8;

    const barInDay = i % 288;

    // spikes في London KZ (07:00-11:00 = bars 84-132) و NY KZ (13:30-17:00 = 162-204)
    let spike = 0;
    if (barInDay >= 84  && barInDay <= 135 && Math.random() > 0.55)
      spike = (Math.random() > 0.5 ? 1 : -1) * atrV * (0.8 + Math.random() * 1.2);
    if (barInDay >= 162 && barInDay <= 204 && Math.random() > 0.58)
      spike = (Math.random() > 0.5 ? 1 : -1) * atrV * (0.7 + Math.random() * 1.1);

    const open  = price;
    const close = Math.max(open + drift + noise + osc, p0 * 0.4);
    const wick  = Math.random() * atrV * 0.5;

    bars.push({
      time:     t0 + i * 300,
      barInDay,
      open:  +open.toFixed(2),
      high:  +(Math.max(open, close) + wick + Math.max(0, spike)).toFixed(2),
      low:   +(Math.max(Math.min(open, close) - wick + Math.min(0, spike), 0.01)).toFixed(2),
      close: +close.toFixed(2),
    });
    price = close;
  }
  return bars;
}

function calcATR(bars, i, p = 14) {
  if (i < p + 1) return bars[i].high - bars[i].low;
  let s = 0;
  for (let j = i - p + 1; j <= i; j++)
    s += Math.max(bars[j].high - bars[j].low,
                  Math.abs(bars[j].high - bars[j-1].close),
                  Math.abs(bars[j].low  - bars[j-1].close));
  return s / p;
}

function calcRSI(bars, i, p = 14) {
  if (i < p + 1) return 50;
  let g = 0, l = 0;
  for (let j = i - p + 1; j <= i; j++) {
    const d = bars[j].close - bars[j-1].close;
    if (d > 0) g += d; else l -= d;
  }
  return l === 0 ? 100 : 100 - 100 / (1 + g / l);
}

function getPDHL(bars, i) {
  const dayIdx = Math.floor(i / 288);
  const pStart = (dayIdx - 1) * 288;
  if (pStart < 0) return null;
  let hi = -Infinity, lo = Infinity;
  for (let j = pStart; j < pStart + 288 && j < bars.length; j++) {
    if (bars[j].high > hi) hi = bars[j].high;
    if (bars[j].low  < lo) lo = bars[j].low;
  }
  return { pdh: hi, pdl: lo };
}

function getAsia(bars, i) {
  const dayStart = Math.floor(i / 288) * 288;
  let hi = -Infinity, lo = Infinity;
  for (let j = dayStart; j < dayStart + 84 && j < bars.length; j++) {
    if (bars[j].high > hi) hi = bars[j].high;
    if (bars[j].low  < lo) lo = bars[j].low;
  }
  return hi > -Infinity ? { asiaH: hi, asiaL: lo } : null;
}

// Swing: أحدث pivot high/low مؤكد
function getSwing(bars, i, N = 8) {
  let swH = null, swL = null;
  const start = Math.max(0, i - 100);
  for (let j = start; j <= i - N; j++) {
    if (j < N) continue;
    let isH = true, isL = true;
    for (let k = j - N; k <= j + N; k++) {
      if (k === j || k < 0 || k >= bars.length) continue;
      if (bars[k].high >= bars[j].high) { isH = false; }
      if (bars[k].low  <= bars[j].low)  { isL = false; }
    }
    if (isH) swH = bars[j].high;
    if (isL) swL = bars[j].low;
  }
  return { swH, swL };
}

// London KZ: 07:00-11:00 UTC = barInDay 84-132
// NY KZ:     13:30-17:00 UTC = barInDay 162-204
const inLonKZ = bid => bid >= 84  && bid <= 132;
const inNYKZ  = bid => bid >= 162 && bid <= 204;

function runBacktest(symbol, maxTrades = 200) {
  process.stdout.write(`\n🔄 ${symbol}... `);
  const bars = generateBars(symbol, 12000);
  console.log(`✅ ${bars.length} شمعة (${Math.round(bars.length/288)} يوم)`);

  const MIN_WICK = 0.25;
  const RSI_OB   = 58;
  const RSI_OS   = 42;
  const COOLDOWN = 18;

  const trades  = [];
  let inTrade   = false;
  let openTrade = null;
  let skipUntil = 0;

  for (let i = 300; i < bars.length - 20; i++) {
    if (inTrade && openTrade) {
      const b = bars[i], s = openTrade.sig;
      let outcome = null;
      if (s.type === 'LONG') {
        if (b.low  <= s.sl)  outcome = 'SL';
        if (b.high >= s.tp1) outcome = 'TP1';
      } else {
        if (b.high >= s.sl)  outcome = 'SL';
        if (b.low  <= s.tp1) outcome = 'TP1';
      }
      if (outcome) {
        const risk = Math.abs(s.price - s.sl);
        const pnl  = outcome === 'TP1' ? +(risk * 2).toFixed(2) : +(-risk).toFixed(2);
        trades.push({ ...openTrade, outcome, pnl });
        inTrade = false; openTrade = null; skipUntil = i + COOLDOWN;
        if (trades.length >= maxTrades) break;
      }
      continue;
    }
    if (i < skipUntil) continue;

    const b   = bars[i];
    const bid = b.barInDay;
    const lonKZ = inLonKZ(bid);
    const nyKZ  = inNYKZ(bid);
    if (!lonKZ && !nyKZ) continue;

    const day = getPDHL(bars, i);
    if (!day) continue;
    const { pdh, pdl } = day;

    // Asia range متاحة لـ London KZ فقط (Asia تنتهي عند bar 84)
    const asia  = lonKZ ? getAsia(bars, i) : null;
    const swing = getSwing(bars, i, 8);

    const a = calcATR(bars, i);
    const r = calcRSI(bars, i);
    if (a === 0) continue;

    const wUp = b.high - Math.max(b.open, b.close);
    const wDn = Math.min(b.open, b.close) - b.low;

    const sweptUp = (lvl) => lvl != null
      && b.high > lvl && b.close < lvl
      && b.close < b.open
      && wUp >= a * MIN_WICK && r >= RSI_OB;

    const sweptDn = (lvl) => lvl != null
      && b.low < lvl && b.close > lvl
      && b.close > b.open
      && wDn >= a * MIN_WICK && r <= RSI_OS;

    let shortPts = 0, longPts = 0;
    const sRsn = [], lRsn = [];

    if (sweptUp(pdh))              { shortPts += 3; sRsn.push('PDH'); }
    if (sweptDn(pdl))              { longPts  += 3; lRsn.push('PDL'); }
    if (asia) {
      if (sweptUp(asia.asiaH))     { shortPts += 2; sRsn.push('AsiaH'); }
      if (sweptDn(asia.asiaL))     { longPts  += 2; lRsn.push('AsiaL'); }
    }
    if (sweptUp(swing.swH))        { shortPts += 1; sRsn.push('SwH'); }
    if (sweptDn(swing.swL))        { longPts  += 1; lRsn.push('SwL'); }

    let type = null, pts = 0, reasons = [];
    if (longPts > 0 && longPts >= shortPts) {
      type = 'LONG'; pts = longPts; reasons = lRsn;
    } else if (shortPts > 0) {
      type = 'SHORT'; pts = shortPts; reasons = sRsn;
    }
    if (!type) continue;

    const price = b.close;
    const sl    = type === 'LONG' ? b.low - a * 0.1 : b.high + a * 0.1;
    const risk  = Math.abs(price - sl);
    if (risk <= 0 || risk > a * 6) continue;
    const tp1 = type === 'LONG' ? price + risk * 2 : price - risk * 2;

    const stars  = pts >= 5 ? '⭐⭐⭐' : pts >= 3 ? '⭐⭐' : '⭐';
    const zone   = lonKZ ? 'London KZ' : 'NY KZ';
    const reason = reasons.join('+');
    const date   = new Date(b.time * 1000).toISOString().slice(0, 16).replace('T', ' ');

    inTrade   = true;
    openTrade = {
      n: trades.length + 1, date, type, reason, stars, zone, pts,
      price: +price.toFixed(2), sl: +sl.toFixed(2), tp1: +tp1.toFixed(2),
      risk: +risk.toFixed(2), rsi: +r.toFixed(1),
      sig: { type, price, sl, tp1 },
    };
  }

  if (inTrade && openTrade && trades.length < maxTrades)
    trades.push({ ...openTrade, outcome: 'OPEN', pnl: 0 });

  return trades;
}

function report(symbol, trades) {
  const closed = trades.filter(t => t.outcome !== 'OPEN');
  const wins   = trades.filter(t => t.outcome === 'TP1').length;
  const losses = trades.filter(t => t.outcome === 'SL').length;
  const totPnl = +trades.reduce((s, t) => s + t.pnl, 0).toFixed(2);
  const wr     = closed.length ? (wins / closed.length * 100).toFixed(1) : '0';
  const grossW = trades.filter(t => t.pnl > 0).reduce((s, t) => s + t.pnl, 0);
  const grossL = Math.abs(trades.filter(t => t.pnl < 0).reduce((s, t) => s + t.pnl, 0));
  const pf     = grossL > 0 ? (grossW / grossL).toFixed(2) : '∞';

  const byReason = {}, byZone = {}, byStars = {};
  for (const t of trades) {
    for (const [m, k] of [[byReason, t.reason], [byZone, t.zone], [byStars, t.stars]]) {
      if (!m[k]) m[k] = { t: 0, w: 0 };
      m[k].t++;
      if (t.outcome === 'TP1') m[k].w++;
    }
  }

  let mxW = 0, mxL = 0, cW = 0, cL = 0;
  for (const t of closed) {
    if (t.outcome === 'TP1') { cW++; cL = 0; mxW = Math.max(mxW, cW); }
    else                      { cL++; cW = 0; mxL = Math.max(mxL, cL); }
  }

  let eq = 0;
  const curve = trades.map(t => { eq += t.pnl; return eq >= 0 ? '▲' : '▼'; });
  const daysCount = 42;

  const S = '═'.repeat(72);
  console.log(`\n${S}`);
  console.log(`  📊  ${symbol}  |  Kill Zone Sweep`);
  console.log(S);
  console.log(`  ✅ TP1: ${String(wins).padStart(4)}   ❌ SL: ${String(losses).padStart(4)}   🔵 مفتوح: ${trades.filter(t=>t.outcome==='OPEN').length}`);
  console.log(`  📈 LONG: ${String(trades.filter(t=>t.type==='LONG').length).padStart(3)}   📉 SHORT: ${String(trades.filter(t=>t.type==='SHORT').length).padStart(3)}   مجموع: ${trades.length}  (~${(trades.length/daysCount).toFixed(1)}/يوم)`);
  console.log(`  🎯 Win Rate:       ${wr}%   (${closed.length} صفقة)`);
  console.log(`  💰 Total PnL:      ${totPnl >= 0 ? '+' : ''}${totPnl}`);
  console.log(`  ⚡ Profit Factor:   ${pf}`);
  console.log(`  🔥 Max Win Streak: ${mxW}   ❄️  Max Loss Streak: ${mxL}`);

  console.log(`\n  📌 حسب السبب:`);
  for (const [k, v] of Object.entries(byReason))
    console.log(`     ${k.padEnd(16)} → ${v.w}/${v.t} (${(v.w/v.t*100).toFixed(0)}%)`);

  console.log(`\n  🕐 حسب الجلسة:`);
  for (const [k, v] of Object.entries(byZone))
    console.log(`     ${k.padEnd(12)} → ${v.w}/${v.t} (${(v.w/v.t*100).toFixed(0)}%)`);

  console.log(`\n  ⭐ حسب الجودة:`);
  for (const [k, v] of Object.entries(byStars))
    console.log(`     ${k.padEnd(6)} → ${v.w}/${v.t} (${(v.w/v.t*100).toFixed(0)}%)`);

  console.log(`\n  منحنى: ${curve.join('')}`);
  console.log(S);

  console.log(`\n  #   Date            Dir    Stars  Zone          السبب            RSI   دخول       SL         TP1       PnL`);
  console.log(`  ${'─'.repeat(112)}`);
  for (const t of trades) {
    const ic = t.outcome === 'TP1' ? '✅' : t.outcome === 'SL' ? '❌' : '🔵';
    console.log(
      `  ${String(t.n).padStart(3)} ${t.date}  ${t.type.padEnd(5)}  ${t.stars.padEnd(5)}  ${t.zone.padEnd(12)}  ${t.reason.padEnd(16)} ` +
      `${String(t.rsi).padEnd(5)} ${String(t.price).padEnd(10)} ${String(t.sl).padEnd(10)} ${String(t.tp1).padEnd(9)} ${ic} ${t.pnl>=0?'+':''}${t.pnl}`
    );
  }

  return { wins, losses, totPnl, winRate: +wr, pf, total: trades.length };
}

const S = '═'.repeat(72);
console.log(S);
console.log('  🎯  Kill Zone Sweep Backtest');
console.log('  📐  PDH/PDL(3) + Asia H/L(2) + Swing(1) | R:R 1:2');
console.log('  ⚙️   RSI 58/42 | Wick ≥0.25 ATR | Cooldown 90min | London 07-11 + NY 13:30-17 UTC');
console.log(S);

const summary = {};
for (const sym of ['MNQ', 'MCL']) {
  const trades = runBacktest(sym, 200);
  if (!trades.length) { console.log(`\n⚠️  ${sym}: لا إشارات`); continue; }
  summary[sym] = report(sym, trades);
}

if (Object.keys(summary).length > 1) {
  console.log(`\n${S}`);
  console.log('  📋  الملخص');
  console.log(S);
  for (const [sym, r] of Object.entries(summary))
    console.log(`  ${sym}:  ${r.total} صفقة  |  Win ${r.winRate}%  |  PnL ${r.totPnl>=0?'+':''}${r.totPnl}  |  PF ${r.pf}`);
  console.log(S);
}
