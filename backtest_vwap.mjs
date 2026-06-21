/**
 * Backtest — VWAP Band Bounce (MNQ / MCL)
 * الدخول عند لمس VWAP ± 1.5 ATR مع رفض RSI
 * R:R 1:2
 */

function generateBars(symbol, n5m = 14000) {
  const cfg = {
    MNQ: { p0: 21000, atrPct: 0.00055, driftPct: 0.00006 },
    MCL: { p0: 72.50, atrPct: 0.00090, driftPct: 0.00009 },
  }[symbol];
  const { p0, atrPct, driftPct } = cfg;
  const t0 = Math.floor(Date.now() / 1000) - n5m * 300;
  const bars = [];
  let price = p0, dir = 1, phase = 0;
  let nextFlip = 200 + Math.floor(Math.random() * 300);

  for (let i = 0; i < n5m; i++) {
    if (++phase >= nextFlip) {
      dir *= -1; phase = 0;
      nextFlip = 200 + Math.floor(Math.random() * 300);
    }
    const atrV  = atrPct * price;
    const drift = dir * driftPct * price;
    const noise = (Math.random() - 0.5) * 2 * atrV;
    const osc   = Math.sin(i * 0.03) * atrV * 2.0;
    const open  = price;
    const close = Math.max(open + drift + noise + osc, p0 * 0.4);
    const wick  = Math.random() * atrV * 0.6;

    // mean-reversion spikes عند الأطراف
    const barInDay = i % 288;
    let spike = 0;
    if (Math.random() > 0.94) spike = (Math.random() > 0.5 ? 1 : -1) * atrV * (1.0 + Math.random());

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

// Daily VWAP: يحسب من أول شمعة اليوم حتى i
function calcVWAP(bars, i) {
  const dayStart = Math.floor(i / 288) * 288;
  let tpv = 0, vol = 0;
  for (let j = dayStart; j <= i; j++) {
    const tp = (bars[j].high + bars[j].low + bars[j].close) / 3;
    tpv += tp; vol += 1;
  }
  return tpv / vol;
}

// inSession: barInDay 84-240 (07:00-20:00 UTC)
const inSession = bid => bid >= 84 && bid <= 240;

function runBacktest(symbol, maxTrades = 250) {
  process.stdout.write(`\n🔄 ${symbol}... `);
  const bars = generateBars(symbol, 14000);
  console.log(`✅ ${bars.length} شمعة (${Math.round(bars.length/288)} يوم)`);

  const BAND_MULT = 1.2;
  const RSI_OB   = 55;
  const RSI_OS   = 45;
  const MIN_WICK = 0.10;
  const COOLDOWN = 12;

  const trades  = [];
  let inTrade   = false;
  let openTrade = null;
  let skipUntil = 0;

  for (let i = 300; i < bars.length - 10; i++) {
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
    if (!inSession(bars[i].barInDay)) continue;

    const b    = bars[i];
    const a    = calcATR(bars, i);
    const r    = calcRSI(bars, i);
    const vwap = calcVWAP(bars, i);
    if (a === 0) continue;

    const upper = vwap + a * BAND_MULT;
    const lower = vwap - a * BAND_MULT;

    const wUp = b.high - Math.max(b.open, b.close);
    const wDn = Math.min(b.open, b.close) - b.low;

    // SHORT: لمس Upper Band + رفض + RSI مرتفع
    const shortCond = b.high >= upper
                   && b.close < upper
                   && b.close < b.open
                   && wUp >= a * MIN_WICK
                   && r >= RSI_OB;

    // LONG: لمس Lower Band + ارتداد + RSI منخفض
    const longCond  = b.low  <= lower
                   && b.close > lower
                   && b.close > b.open
                   && wDn >= a * MIN_WICK
                   && r <= RSI_OS;

    if (!longCond && !shortCond) continue;

    const type  = longCond ? 'LONG' : 'SHORT';
    const price = b.close;
    const sl    = type === 'LONG' ? b.low  - a * 0.1 : b.high + a * 0.1;
    const risk  = Math.abs(price - sl);
    if (risk <= 0 || risk > a * 5) continue;
    const tp1 = type === 'LONG' ? price + risk * 2 : price - risk * 2;

    const date  = new Date(b.time * 1000).toISOString().slice(0,16).replace('T',' ');
    inTrade   = true;
    openTrade = {
      n: trades.length + 1, date, type,
      price: +price.toFixed(2), sl: +sl.toFixed(2), tp1: +tp1.toFixed(2),
      risk: +risk.toFixed(2), rsi: +r.toFixed(1),
      vwap: +vwap.toFixed(2),
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
  const days   = Math.round(14000 / 288);

  let mxW = 0, mxL = 0, cW = 0, cL = 0;
  for (const t of closed) {
    if (t.outcome === 'TP1') { cW++; cL=0; mxW=Math.max(mxW,cW); }
    else                      { cL++; cW=0; mxL=Math.max(mxL,cL); }
  }
  let eq = 0;
  const curve = trades.map(t => { eq += t.pnl; return eq >= 0 ? '▲' : '▼'; });

  const S = '═'.repeat(68);
  console.log(`\n${S}`);
  console.log(`  📊  ${symbol}  |  VWAP Band Bounce`);
  console.log(S);
  console.log(`  ✅ TP1: ${String(wins).padStart(4)}   ❌ SL: ${String(losses).padStart(4)}   🔵 مفتوح: ${trades.filter(t=>t.outcome==='OPEN').length}`);
  console.log(`  📈 LONG: ${String(trades.filter(t=>t.type==='LONG').length).padStart(3)}   📉 SHORT: ${String(trades.filter(t=>t.type==='SHORT').length).padStart(3)}   مجموع: ${trades.length}  (~${(trades.length/days).toFixed(1)}/يوم)`);
  console.log(`  🎯 Win Rate:       ${wr}%   (${closed.length} صفقة)`);
  console.log(`  💰 Total PnL:      ${totPnl >= 0 ? '+' : ''}${totPnl}`);
  console.log(`  ⚡ Profit Factor:   ${pf}`);
  console.log(`  🔥 Max Win Streak: ${mxW}   ❄️  Max Loss Streak: ${mxL}`);
  console.log(`\n  منحنى: ${curve.slice(0, 80).join('')}`);
  console.log(S);

  console.log(`\n  #   Date            Dir    RSI   VWAP       دخول       SL         TP1        PnL`);
  console.log(`  ${'─'.repeat(90)}`);
  for (const t of trades.slice(0, 30)) {
    const ic = t.outcome === 'TP1' ? '✅' : t.outcome === 'SL' ? '❌' : '🔵';
    console.log(
      `  ${String(t.n).padStart(3)} ${t.date}  ${t.type.padEnd(5)}  ${String(t.rsi).padEnd(5)} ` +
      `${String(t.vwap).padEnd(10)} ${String(t.price).padEnd(10)} ${String(t.sl).padEnd(10)} ${String(t.tp1).padEnd(10)} ${ic} ${t.pnl>=0?'+':''}${t.pnl}`
    );
  }
  if (trades.length > 30) console.log(`  ... و ${trades.length - 30} صفقة أخرى`);

  return { wins, losses, totPnl, winRate: +wr, pf, total: trades.length, perDay: +(trades.length/days).toFixed(1) };
}

const S = '═'.repeat(68);
console.log(S);
console.log('  🔬  VWAP Band Bounce Backtest');
console.log('  📐  VWAP ± 1.5 ATR | RSI 60/40 | R:R 1:2 | Session 07-20 UTC');
console.log(S);

const summary = {};
for (const sym of ['MNQ', 'MCL']) {
  const trades = runBacktest(sym, 250);
  if (!trades.length) { console.log(`\n⚠️  ${sym}: لا إشارات`); continue; }
  summary[sym] = report(sym, trades);
}

if (Object.keys(summary).length > 1) {
  console.log(`\n${S}`);
  console.log('  📋  الملخص');
  console.log(S);
  for (const [sym, r] of Object.entries(summary))
    console.log(`  ${sym}: ${r.total} صفقة (~${r.perDay}/يوم) | Win ${r.winRate}% | PnL ${r.totPnl>=0?'+':''}${r.totPnl} | PF ${r.pf}`);
  console.log(S);
}
