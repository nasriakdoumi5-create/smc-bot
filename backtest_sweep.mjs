/**
 * Backtest — Liquidity Sweep PDH/PDL/PWH/PWL
 * نفس أسلوب backtest_ema21 لكن باستراتيجية السويب
 */

// ── توليد بيانات اصطناعية ──────────────────────
function generateBars(symbol, n5m = 10000) {
  const cfg = {
    MNQ: { p0: 21000, atrPct: 0.00055, driftPct: 0.00008 },
    MCL: { p0: 72.50, atrPct: 0.00095, driftPct: 0.00012 },
  }[symbol];

  const { p0, atrPct, driftPct } = cfg;
  const t0 = Math.floor(Date.now() / 1000) - n5m * 300;

  const bars5m = [];
  let price = p0;
  let dir = 1;
  let phaseCount = 0;
  let nextFlip = 400 + Math.floor(Math.random() * 500);

  for (let i = 0; i < n5m; i++) {
    phaseCount++;
    if (phaseCount >= nextFlip) {
      dir *= -1;
      phaseCount = 0;
      nextFlip = 400 + Math.floor(Math.random() * 500);
    }

    const atrVal = atrPct * price;
    const osc    = Math.sin(i * 0.04) * atrVal * 2.5;
    const drift  = dir * driftPct * price;
    const noise  = (Math.random() - 0.5) * 2 * atrVal * 1.2;
    const change = drift + noise + osc;

    const open  = price;
    const close = Math.max(open + change, p0 * 0.4);
    const wick  = Math.random() * atrVal * 0.8;

    const spikeChance = Math.random();
    let spikeHigh = 0, spikeLow = 0;
    if (spikeChance > 0.985) spikeHigh = atrVal * (1.5 + Math.random() * 2);
    if (spikeChance < 0.015) spikeLow  = atrVal * (1.5 + Math.random() * 2);

    bars5m.push({
      time:  t0 + i * 300,
      open:  +open.toFixed(2),
      high:  +(Math.max(open, close) + wick + spikeHigh).toFixed(2),
      low:   +(Math.max(Math.min(open, close) - wick - spikeLow, 0.01)).toFixed(2),
      close: +close.toFixed(2),
    });
    price = close;
  }

  return bars5m;
}

// ── ATR ───────────────────────────────────────
function calcATR(bars, period = 14) {
  if (bars.length < period + 1) return 0;
  let sum = 0;
  for (let i = bars.length - period; i < bars.length; i++) {
    const tr = Math.max(
      bars[i].high - bars[i].low,
      Math.abs(bars[i].high - bars[i-1].close),
      Math.abs(bars[i].low  - bars[i-1].close)
    );
    sum += tr;
  }
  return sum / period;
}

// ── RSI ───────────────────────────────────────
function calcRSI(bars, period = 14) {
  if (bars.length < period + 1) return 50;
  let gains = 0, losses = 0;
  for (let i = bars.length - period; i < bars.length; i++) {
    const d = bars[i].close - bars[i-1].close;
    if (d > 0) gains += d; else losses -= d;
  }
  const rs = losses === 0 ? 100 : gains / losses;
  return 100 - 100 / (1 + rs);
}

// ── PDH/PDL من البيانات ───────────────────────
function getDayLevels(bars, idx) {
  const BARS_PER_DAY = 288;
  const dayStart = idx - (idx % BARS_PER_DAY);
  const prevDayStart = dayStart - BARS_PER_DAY;
  if (prevDayStart < 0) return null;
  let pdh = -Infinity, pdl = Infinity;
  for (let i = prevDayStart; i < dayStart && i < bars.length; i++) {
    if (bars[i].high > pdh) pdh = bars[i].high;
    if (bars[i].low  < pdl) pdl = bars[i].low;
  }
  return { pdh, pdl };
}

// ── PWH/PWL ───────────────────────────────────
function getWeekLevels(bars, idx) {
  const BARS_PER_WEEK = 288 * 5;
  const weekStart = idx - (idx % BARS_PER_WEEK);
  const prevWeekStart = weekStart - BARS_PER_WEEK;
  if (prevWeekStart < 0) return null;
  let pwh = -Infinity, pwl = Infinity;
  for (let i = prevWeekStart; i < weekStart && i < bars.length; i++) {
    if (bars[i].high > pwh) pwh = bars[i].high;
    if (bars[i].low  < pwl) pwl = bars[i].low;
  }
  return { pwh, pwl };
}

// ── الباك تست ─────────────────────────────────
function runBacktest(symbol, maxTrades = 150) {
  process.stdout.write(`\n🔄 توليد بيانات ${symbol}... `);
  const bars = generateBars(symbol, 10000);
  console.log(`✅  ${bars.length} شمعة 5M`);

  const trades  = [];
  const COOLDOWN = 24;
  let inTrade   = false;
  let openTrade = null;
  let skipUntil = 0;

  for (let i = 600; i < bars.length - 50; i++) {

    // تقييم الصفقة المفتوحة
    if (inTrade && openTrade) {
      const bar = bars[i];
      const sig = openTrade.sig;
      let outcome = null;
      if (sig.type === 'LONG') {
        if (bar.low  <= sig.sl)  outcome = 'SL';
        if (bar.high >= sig.tp1) outcome = 'TP1';
      } else {
        if (bar.high >= sig.sl)  outcome = 'SL';
        if (bar.low  <= sig.tp1) outcome = 'TP1';
      }
      if (outcome) {
        const risk = Math.abs(sig.price - sig.sl);
        const pnl  = outcome === 'TP1' ? +(risk * 2).toFixed(2) : +(-risk).toFixed(2);
        trades.push({ ...openTrade, outcome, pnl, closeBar: i });
        inTrade = false; openTrade = null; skipUntil = i + COOLDOWN;
        if (trades.length >= maxTrades) break;
      }
      continue;
    }

    if (i < skipUntil) continue;

    const day  = getDayLevels(bars, i);
    const week = getWeekLevels(bars, i);
    if (!day) continue;

    const { pdh, pdl } = day;
    const pwh = week?.pwh ?? pdh;
    const pwl = week?.pwl ?? pdl;

    const slice = bars.slice(Math.max(0, i - 20), i + 1);
    const atr   = calcATR(slice);
    const rsi   = calcRSI(slice);
    if (atr === 0) continue;

    const bar     = bars[i];
    const wickUp  = bar.high - Math.max(bar.open, bar.close);
    const wickDn  = Math.min(bar.open, bar.close) - bar.low;

    const sweptH = (bar.high > pdh || bar.high > pwh)
                && bar.close < bar.open
                && wickUp >= atr * 0.3
                && rsi >= 55;

    const sweptL = (bar.low < pdl || bar.low < pwl)
                && bar.close > bar.open
                && wickDn >= atr * 0.3
                && rsi <= 45;

    if (!sweptH && !sweptL) continue;

    const type  = sweptL ? 'LONG' : 'SHORT';
    const price = bar.close;
    const sl    = type === 'LONG' ? bar.low - atr * 0.1 : bar.high + atr * 0.1;
    const risk  = Math.abs(price - sl);
    if (risk <= 0) continue;
    const tp1 = type === 'LONG' ? price + risk * 2 : price - risk * 2;

    const sweepType = type === 'LONG'
      ? (bar.low < pdl && bar.low < pwl ? 'PDL+PWL' : bar.low < pwl ? 'PWL' : 'PDL')
      : (bar.high > pdh && bar.high > pwh ? 'PDH+PWH' : bar.high > pwh ? 'PWH' : 'PDH');

    const date = new Date(bar.time * 1000).toISOString().slice(0, 16).replace('T', ' ');
    inTrade   = true;
    openTrade = {
      n: trades.length + 1, date, type, sweepType,
      price: +price.toFixed(2), sl: +sl.toFixed(2), tp1: +tp1.toFixed(2),
      risk: +risk.toFixed(2), rsi: +rsi.toFixed(1),
      sig: { type, price, sl, tp1 },
    };
  }

  if (inTrade && openTrade && trades.length < maxTrades)
    trades.push({ ...openTrade, outcome: 'OPEN', pnl: 0, closeBar: null });

  return trades;
}

// ── التقرير ───────────────────────────────────
function printReport(symbol, trades) {
  const closed  = trades.filter(t => t.outcome !== 'OPEN');
  const wins    = trades.filter(t => t.outcome === 'TP1').length;
  const losses  = trades.filter(t => t.outcome === 'SL').length;
  const open    = trades.filter(t => t.outcome === 'OPEN').length;
  const longs   = trades.filter(t => t.type === 'LONG').length;
  const shorts  = trades.filter(t => t.type === 'SHORT').length;
  const totPnl  = +trades.reduce((s,t) => s + t.pnl, 0).toFixed(2);
  const winRate = closed.length ? (wins / closed.length * 100).toFixed(1) : '0.0';
  const grossW  = trades.filter(t => t.pnl > 0).reduce((s,t) => s + t.pnl, 0);
  const grossL  = Math.abs(trades.filter(t => t.pnl < 0).reduce((s,t) => s + t.pnl, 0));
  const pf      = grossL > 0 ? (grossW / grossL).toFixed(2) : '∞';
  const avgW    = wins   ? (grossW / wins).toFixed(2)   : '0';
  const avgL    = losses ? (grossL / losses).toFixed(2) : '0';

  const sweepMap = {};
  for (const t of trades) {
    if (!sweepMap[t.sweepType]) sweepMap[t.sweepType] = { total: 0, wins: 0 };
    sweepMap[t.sweepType].total++;
    if (t.outcome === 'TP1') sweepMap[t.sweepType].wins++;
  }

  let maxW = 0, maxL = 0, cW = 0, cL = 0;
  for (const t of closed) {
    if (t.outcome === 'TP1') { cW++; cL = 0; maxW = Math.max(maxW, cW); }
    else                      { cL++; cW = 0; maxL = Math.max(maxL, cL); }
  }

  let equity = 0;
  const curve = trades.map(t => { equity += t.pnl; return equity >= 0 ? '▲' : '▼'; });

  const SEP = '═'.repeat(68);
  console.log(`\n${SEP}`);
  console.log(`  📊  BACKTEST — ${symbol}  |  Liquidity Sweep PDH/PDL/PWH/PWL`);
  console.log(SEP);
  console.log(`  ✅ TP1: ${String(wins).padStart(4)}   ❌ SL: ${String(losses).padStart(4)}   🔵 مفتوح: ${open}`);
  console.log(`  📈 LONG: ${String(longs).padStart(3)}   📉 SHORT: ${String(shorts).padStart(3)}`);
  console.log(`  🎯 Win Rate:      ${winRate}%  (من ${closed.length} صفقة)`);
  console.log(`  💰 Total PnL:     ${totPnl >= 0 ? '+' : ''}${totPnl} pts`);
  console.log(`  ⚡ Profit Factor:  ${pf}`);
  console.log(`  📐 Avg Win: +${avgW}  |  Avg Loss: -${avgL}`);
  console.log(`  🔥 Max Win Streak: ${maxW}   |   ❄️  Max Loss Streak: ${maxL}`);
  console.log(`\n  📌 حسب نوع السويب:`);
  for (const [type, d] of Object.entries(sweepMap))
    console.log(`     ${type.padEnd(10)} → ${d.wins}/${d.total} (${(d.wins/d.total*100).toFixed(0)}%)`);

  console.log(`\n  منحنى رأس المال:`);
  for (let i = 0; i < curve.length; i += 60)
    console.log(`  ${curve.slice(i, i+60).join('')}`);
  console.log(`\n${SEP}`);

  console.log(`\n  #    Date            Dir    Sweep      RSI   دخول       SL         TP1       خطر    نتيجة    PnL`);
  console.log(`  ${'─'.repeat(104)}`);
  for (const t of trades) {
    const icon = t.outcome === 'TP1' ? '✅' : t.outcome === 'SL' ? '❌' : '🔵';
    console.log(
      `  ${String(t.n).padStart(3)}  ${t.date}  ${t.type.padEnd(5)}  ${t.sweepType.padEnd(10)}` +
      ` ${String(t.rsi).padEnd(5)} ${String(t.price).padEnd(10)} ${String(t.sl).padEnd(10)}` +
      ` ${String(t.tp1).padEnd(9)} ${String(t.risk).padEnd(6)} ${icon} ${t.outcome.padEnd(6)} ${t.pnl >= 0 ? '+' : ''}${t.pnl}`
    );
  }

  return { wins, losses, totPnl, winRate: +winRate, pf, total: trades.length };
}

// ══ Main ══════════════════════════════════════
const SEP = '═'.repeat(68);
console.log(SEP);
console.log('  🔬  Liquidity Sweep Backtest — PDH/PDL/PWH/PWL');
console.log('  📐  R:R 1:2  |  Cooldown 2h  |  بيانات اصطناعية 10,000 شمعة');
console.log(SEP);

const summary = {};
for (const sym of ['MNQ', 'MCL']) {
  const trades = runBacktest(sym, 150);
  if (!trades.length) { console.log(`\n⚠️  ${sym}: لا توجد إشارات`); continue; }
  summary[sym] = printReport(sym, trades);
}

if (Object.keys(summary).length > 1) {
  const SEP2 = '═'.repeat(68);
  console.log(`\n${SEP2}`);
  console.log('  📋  المقارنة النهائية');
  console.log(SEP2);
  console.log(`  ${'الرمز'.padEnd(6)} ${'صفقات'.padEnd(8)} ${'Win%'.padEnd(8)} ${'PnL'.padEnd(14)} Profit Factor`);
  console.log(`  ${'─'.repeat(48)}`);
  for (const [sym, r] of Object.entries(summary)) {
    const p = (r.totPnl >= 0 ? '+' : '') + r.totPnl;
    console.log(`  ${sym.padEnd(6)} ${String(r.total).padEnd(8)} ${r.winRate}%`.padEnd(26) + `  ${p.padEnd(14)} ${r.pf}`);
  }
  console.log(SEP2);
}
