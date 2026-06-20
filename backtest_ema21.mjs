/**
 * Backtest — EMA21 Bounce 3TF
 * يولّد بيانات اصطناعية واقعية ويشغّل الاستراتيجية بار بار
 */

import { analyzeSimple } from './strategy_simple.js';

// ── توليد بيانات اصطناعية واقعية ──────────────────
function generateBars(symbol, n5m = 8000) {
  const cfg = {
    MNQ: { p0: 21000, atrPct: 0.00055, driftPct: 0.00010 },
    MCL: { p0: 72.50, atrPct: 0.00095, driftPct: 0.00016 },
  }[symbol];

  const { p0, atrPct, driftPct } = cfg;
  const t0 = Math.floor(Date.now() / 1000) - n5m * 300;

  // ── توليد الـ 5M ─────────────────────────────────
  const bars5m = [];
  let price   = p0;
  let dir     = 1;          // اتجاه الـ trend
  let phaseCount = 0;
  let nextFlip   = 350 + Math.floor(Math.random() * 400);

  for (let i = 0; i < n5m; i++) {
    // تغيير الاتجاه تدريجياً
    phaseCount++;
    if (phaseCount >= nextFlip) {
      dir       *= -1;
      phaseCount = 0;
      nextFlip   = 350 + Math.floor(Math.random() * 400);
    }

    const atrVal  = atrPct * price;
    // موجة جيبية تحاكي تذبذبات حول الـ EMA
    const osc     = Math.sin(i * 0.055) * atrVal * 1.8;
    const drift   = dir * driftPct * price;
    const noise   = (Math.random() - 0.5) * 2 * atrVal;
    const change  = drift + noise + osc;

    const open  = price;
    const close = Math.max(open + change, p0 * 0.5);
    const wick  = Math.random() * atrVal * 0.6;
    const high  = Math.max(open, close) + wick;
    const low   = Math.min(open, close) - wick;

    bars5m.push({
      time:  t0 + i * 300,
      open:  +open.toFixed(2),
      high:  +high.toFixed(2),
      low:   +Math.max(low, 0.01).toFixed(2),
      close: +close.toFixed(2),
    });
    price = close;
  }

  // ── تجميع إلى 15M (كل 3 شمعات 5M) ──────────────
  const bars15m = [];
  for (let i = 0; i + 2 < bars5m.length; i += 3) {
    const s = bars5m.slice(i, i + 3);
    bars15m.push({
      time:  s[0].time,
      open:  s[0].open,
      high:  Math.max(...s.map(b => b.high)),
      low:   Math.min(...s.map(b => b.low)),
      close: s[2].close,
    });
  }

  // ── تجميع إلى 1H (كل 12 شمعة 5M) ───────────────
  const bars1h = [];
  for (let i = 0; i + 11 < bars5m.length; i += 12) {
    const s = bars5m.slice(i, i + 12);
    bars1h.push({
      time:  s[0].time,
      open:  s[0].open,
      high:  Math.max(...s.map(b => b.high)),
      low:   Math.min(...s.map(b => b.low)),
      close: s[11].close,
    });
  }

  return { bars5m, bars15m, bars1h };
}

// ── الباك تست ─────────────────────────────────────
function runBacktest(symbol, maxTrades = 100) {
  process.stdout.write(`\n🔄 توليد بيانات ${symbol}... `);
  const { bars5m, bars15m, bars1h } = generateBars(symbol, 8500);
  console.log(`✅  5M:${bars5m.length} | 15M:${bars15m.length} | 1H:${bars1h.length}`);

  const trades   = [];
  const COOLDOWN = 6; // 6 شمعات 5M = 30 دقيقة
  let inTrade    = false;
  let openTrade  = null;
  let skipUntil  = 0;    // bar index بعد انتهاء الصفقة

  for (let i = 215 * 12; i < bars5m.length - 50; i++) {
    // ── تقييم الصفقة المفتوحة ──
    if (inTrade && openTrade) {
      const bar = bars5m[i];
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
        inTrade   = false;
        openTrade = null;
        skipUntil = i + COOLDOWN;
        if (trades.length >= maxTrades) break;
      }
      continue;
    }

    // ── Cooldown بعد إغلاق الصفقة ──
    if (i < skipUntil) continue;

    // ── محاذاة الـ timeframes (index-based لأن البيانات مجمّعة) ──
    const i15 = Math.floor(i / 3);
    const i1h = Math.floor(i / 12);
    if (i15 < 30 || i1h < 210) continue;

    // ── تشغيل الاستراتيجية ──
    let r;
    try {
      r = analyzeSimple(
        bars5m.slice(0, i + 1),
        bars15m.slice(0, i15 + 1),
        bars1h.slice(0, i1h + 1),
      );
    } catch { continue; }

    if (!r.signal) continue;

    const sig  = r.signal;
    const date = new Date(bars5m[i].time * 1000)
      .toISOString().slice(0, 16).replace('T', ' ');

    inTrade   = true;
    openTrade = {
      n:     trades.length + 1,
      date,
      type:  sig.type,
      score: sig.score,
      price: sig.price,
      sl:    sig.sl,
      tp1:   sig.tp1,
      risk:  +Math.abs(sig.price - sig.sl).toFixed(2),
      sig,
    };
  }

  // ── صفقة مفتوحة لم تُغلق ──
  if (inTrade && openTrade && trades.length < maxTrades) {
    trades.push({ ...openTrade, outcome: 'OPEN', pnl: 0, closeBar: null });
  }

  return trades;
}

// ── طباعة التقرير ─────────────────────────────────
function printReport(symbol, trades) {
  const closed   = trades.filter(t => t.outcome !== 'OPEN');
  const wins     = trades.filter(t => t.outcome === 'TP1').length;
  const losses   = trades.filter(t => t.outcome === 'SL').length;
  const open     = trades.filter(t => t.outcome === 'OPEN').length;
  const longs    = trades.filter(t => t.type === 'LONG').length;
  const shorts   = trades.filter(t => t.type === 'SHORT').length;
  const totalPnl = +trades.reduce((s, t) => s + t.pnl, 0).toFixed(2);
  const winRate  = closed.length ? (wins / closed.length * 100).toFixed(1) : '0.0';
  const grossW   = trades.filter(t => t.pnl > 0).reduce((s, t) => s + t.pnl, 0);
  const grossL   = Math.abs(trades.filter(t => t.pnl < 0).reduce((s, t) => s + t.pnl, 0));
  const pf       = grossL > 0 ? (grossW / grossL).toFixed(2) : '∞';
  const avgW     = wins   ? (grossW / wins).toFixed(1)   : '0';
  const avgL     = losses ? (grossL / losses).toFixed(1) : '0';

  // score distribution
  const scoreMap = { 3: 0, 4: 0, 5: 0 };
  trades.forEach(t => { scoreMap[t.score] = (scoreMap[t.score] || 0) + 1; });

  // أطول سلسلة
  let maxW = 0, maxL = 0, cW = 0, cL = 0;
  for (const t of closed) {
    if (t.outcome === 'TP1') { cW++; cL = 0; maxW = Math.max(maxW, cW); }
    else                      { cL++; cW = 0; maxL = Math.max(maxL, cL); }
  }

  // منحنى رأس المال (كل رمز = ▲ ربح / ▼ خسارة)
  let equity = 0;
  const curve = [];
  for (const t of trades) {
    equity += t.pnl;
    curve.push(equity >= 0 ? '▲' : '▼');
  }

  const SEP = '═'.repeat(64);
  console.log(`\n${SEP}`);
  console.log(`  📊  BACKTEST — ${symbol}   (${trades.length} صفقة مُولَّدة)`);
  console.log(SEP);
  console.log(`  ✅ TP1:          ${String(wins).padStart(4)}   ❌ SL:   ${String(losses).padStart(4)}   🔵 مفتوح: ${open}`);
  console.log(`  📈 LONG:         ${String(longs).padStart(4)}   📉 SHORT: ${String(shorts).padStart(4)}`);
  console.log(`  🎯 Win Rate:     ${winRate}%  (من ${closed.length} صفقة مغلقة)`);
  console.log(`  💰 Total PnL:    ${totalPnl >= 0 ? '+' : ''}${totalPnl} pts`);
  console.log(`  ⚡ Profit Factor: ${pf}`);
  console.log(`  📐 Avg Win:  +${avgW} pts   |   Avg Loss: -${avgL} pts`);
  console.log(`  🔥 Max Win Streak: ${maxW}   |   ❄️  Max Loss Streak: ${maxL}`);
  console.log(`  ⭐ Score:  3/5 → ${scoreMap[3]||0}   4/5 → ${scoreMap[4]||0}   5/5 → ${scoreMap[5]||0}`);
  console.log(`\n  منحنى رأس المال:`);
  for (let i = 0; i < curve.length; i += 60) {
    console.log(`  ${curve.slice(i, i + 60).join('')}`);
  }
  console.log(`\n${SEP}`);

  // ── جدول الصفقات ──
  console.log(`\n  #    Date            Dir    Score  دخول       SL         TP1        خطر   نتيجة     PnL`);
  console.log(`  ${'─'.repeat(102)}`);
  for (const t of trades) {
    const icon = t.outcome === 'TP1' ? '✅' : t.outcome === 'SL' ? '❌' : '🔵';
    console.log(
      `  ${String(t.n).padStart(3)}  ${t.date}  ${t.type.padEnd(5)}  ${t.score}/5   ` +
      `${String(t.price).padEnd(10)} ${String(t.sl).padEnd(10)} ${String(t.tp1).padEnd(10)} ` +
      `${String(t.risk).padEnd(5)} ${icon} ${t.outcome.padEnd(7)} ${t.pnl >= 0 ? '+' : ''}${t.pnl}`
    );
  }

  return { wins, losses, totalPnl, winRate: +winRate, pf };
}

// ══ Main ══════════════════════════════════════════
const SEP = '═'.repeat(64);
console.log(SEP);
console.log('  🔬  EMA21 Bounce Backtest — بيانات اصطناعية واقعية');
console.log('  📐  1H Bias + 15M Structure + 5M Entry | R:R 1:2');
console.log('  ⚠️  ملاحظة: البيانات مولَّدة (Yahoo Finance محجوب هنا)');
console.log(SEP);

const summary = {};
for (const sym of ['MNQ', 'MCL']) {
  const trades = runBacktest(sym, 100);
  if (trades.length === 0) {
    console.log(`\n⚠️  ${sym}: لم تُولَّد إشارات كافية`);
    continue;
  }
  summary[sym] = printReport(sym, trades);
}

// ملخص مقارن
if (Object.keys(summary).length > 1) {
  console.log(`\n${SEP}`);
  console.log('  📋  المقارنة النهائية');
  console.log(SEP);
  console.log(`  ${'الرمز'.padEnd(8)}  ${'Win%'.padEnd(8)}  ${'PnL (pts)'.padEnd(12)}  Profit Factor`);
  console.log(`  ${'─'.repeat(45)}`);
  for (const [sym, r] of Object.entries(summary)) {
    const pnlStr = (r.totalPnl >= 0 ? '+' : '') + r.totalPnl;
    console.log(`  ${sym.padEnd(8)}  ${r.winRate}%`.padEnd(18) +
      `  ${pnlStr.padEnd(14)}  ${r.pf}`);
  }
  console.log(SEP);
}
