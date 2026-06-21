/**
 * Backtest — Triple Sweep System
 * 1. PDH/PDL Sweep       → 2 نقطة
 * 2. Session H/L Sweep   → 1-2 نقطة
 * 3. Swing H/L Sweep     → 1 نقطة
 * كلما زادت النقاط زادت الأولوية ⭐
 */

// ── توليد بيانات ──────────────────────────────
function generateBars(symbol, n = 12000) {
  const cfg = {
    MNQ: { p0: 21000, atrPct: 0.00055, driftPct: 0.00008 },
    MCL: { p0:  72.5, atrPct: 0.00090, driftPct: 0.00010 },
  }[symbol];
  const { p0, atrPct, driftPct } = cfg;
  const t0 = Math.floor(Date.now() / 1000) - n * 300;

  const bars = [];
  let price = p0, dir = 1, phase = 0;
  let nextFlip = 350 + Math.floor(Math.random() * 450);

  for (let i = 0; i < n; i++) {
    if (++phase >= nextFlip) { dir *= -1; phase = 0; nextFlip = 350 + Math.floor(Math.random() * 450); }
    const atrV  = atrPct * price;
    const drift = dir * driftPct * price;
    const noise = (Math.random() - 0.5) * 2 * atrV;
    const osc   = Math.sin(i * 0.045) * atrV * 1.5;
    const bInD  = i % 288;

    // spikes على حدود الجلسات + نهاية أسبوع
    let spkH = 0, spkL = 0;
    const rng = Math.random();
    if ((bInD === 84 || bInD === 156) && rng > 0.4) {  // بداية London/NY
      if (Math.random() > 0.5) spkH = atrV * (0.8 + Math.random() * 1.5);
      else                      spkL = atrV * (0.8 + Math.random() * 1.5);
    }

    const open  = price;
    const close = Math.max(open + drift + noise + osc, p0 * 0.4);
    const wick  = Math.random() * atrV * 0.6;

    bars.push({
      time:  t0 + i * 300,
      bInD,
      open:  +open.toFixed(2),
      high:  +(Math.max(open, close) + wick + spkH).toFixed(2),
      low:   +(Math.max(Math.min(open, close) - wick - spkL, 0.01)).toFixed(2),
      close: +close.toFixed(2),
    });
    price = close;
  }
  return bars;
}

// ── ATR ───────────────────────────────────────
function calcATR(bars, i, p = 14) {
  if (i < p + 1) return bars[i].high - bars[i].low;
  let s = 0;
  for (let j = i - p + 1; j <= i; j++)
    s += Math.max(bars[j].high - bars[j].low,
                  Math.abs(bars[j].high - bars[j-1].close),
                  Math.abs(bars[j].low  - bars[j-1].close));
  return s / p;
}

// ── RSI ───────────────────────────────────────
function calcRSI(bars, i, p = 14) {
  if (i < p + 1) return 50;
  let g = 0, l = 0;
  for (let j = i - p + 1; j <= i; j++) {
    const d = bars[j].close - bars[j-1].close;
    if (d > 0) g += d; else l -= d;
  }
  return l === 0 ? 100 : 100 - 100 / (1 + g / l);
}

// ── Swing High/Low (pivot) ────────────────────
function getSwingLevels(bars, i, len = 8) {
  if (i < len * 2) return { swH: null, swL: null };
  let swH = null, swL = null;
  // أحدث قمة محلية
  for (let k = i - len; k >= Math.max(0, i - len * 4); k--) {
    let isPivotH = true, isPivotL = true;
    for (let j = k - len; j <= k + len; j++) {
      if (j < 0 || j >= bars.length || j === k) continue;
      if (bars[j].high >= bars[k].high) { isPivotH = false; break; }
    }
    for (let j = k - len; j <= k + len; j++) {
      if (j < 0 || j >= bars.length || j === k) continue;
      if (bars[j].low <= bars[k].low) { isPivotL = false; break; }
    }
    if (isPivotH && swH === null) swH = bars[k].high;
    if (isPivotL && swL === null) swL = bars[k].low;
    if (swH !== null && swL !== null) break;
  }
  return { swH, swL };
}

// ── مستويات الجلسة ────────────────────────────
// Asia  : bInD  0-83  (00:00-07:00 UTC = 84 شمعة)
// London: bInD 84-155 (07:00-13:00 UTC = 72 شمعة)
// NY    : bInD 156-251

function buildSessions(bars) {
  const days = {};
  for (let i = 0; i < bars.length; i++) {
    const d = Math.floor(i / 288);
    if (!days[d]) days[d] = { asia: null, lon: null };
    const b = bars[i].bInD;
    if (b <= 83) {
      if (!days[d].asia) days[d].asia = { high: -Infinity, low: Infinity };
      days[d].asia.high = Math.max(days[d].asia.high, bars[i].high);
      days[d].asia.low  = Math.min(days[d].asia.low,  bars[i].low);
    } else if (b <= 155) {
      if (!days[d].lon) days[d].lon = { high: -Infinity, low: Infinity };
      days[d].lon.high = Math.max(days[d].lon.high, bars[i].high);
      days[d].lon.low  = Math.min(days[d].lon.low,  bars[i].low);
    }
  }
  return days;
}

function getPDH(bars, i) {
  const dayIdx = Math.floor(i / 288);
  const start  = (dayIdx - 1) * 288;
  if (start < 0) return null;
  let pdh = -Infinity, pdl = Infinity;
  for (let j = start; j < start + 288 && j < bars.length; j++) {
    pdh = Math.max(pdh, bars[j].high);
    pdl = Math.min(pdl, bars[j].low);
  }
  return { pdh, pdl };
}

// ── الباك تست ─────────────────────────────────
function runBacktest(symbol, maxTrades = 250) {
  process.stdout.write(`\n🔄 ${symbol}... `);
  const bars     = generateBars(symbol, 12000);
  const sessions = buildSessions(bars);
  console.log(`✅ ${bars.length} شمعة (${Math.round(bars.length/288)} يوم)`);

  const trades  = [];
  const COOL    = 12;
  let inTrade   = false, openTrade = null, skipUntil = 0;

  for (let i = 400; i < bars.length - 30; i++) {
    // تقييم صفقة مفتوحة
    if (inTrade && openTrade) {
      const b = bars[i], s = openTrade.sig;
      let outcome = null;
      if (s.type === 'LONG') { if (b.low <= s.sl) outcome='SL'; if (b.high >= s.tp1) outcome='TP1'; }
      else                    { if (b.high >= s.sl) outcome='SL'; if (b.low <= s.tp1) outcome='TP1'; }
      if (outcome) {
        const risk = Math.abs(s.price - s.sl);
        const pnl  = outcome === 'TP1' ? +(risk*2).toFixed(2) : +(-risk).toFixed(2);
        trades.push({ ...openTrade, outcome, pnl });
        inTrade = false; openTrade = null; skipUntil = i + COOL;
        if (trades.length >= maxTrades) break;
      }
      continue;
    }
    if (i < skipUntil) continue;

    const b    = bars[i];
    const bInD = b.bInD;
    const atrV = calcATR(bars, i);
    const rsiV = calcRSI(bars, i);
    if (atrV === 0) continue;

    const dayIdx = Math.floor(i / 288);
    const pd     = getPDH(bars, i);
    const curDay = sessions[dayIdx]   || {};
    const prvDay = sessions[dayIdx-1] || {};
    const { swH, swL } = getSwingLevels(bars, i);

    const wickUp = b.high  - Math.max(b.open, b.close);
    const wickDn = Math.min(b.open, b.close) - b.low;

    const sweptUp = (lvl) => lvl !== null && b.high > lvl && b.close < lvl && b.close < b.open && wickUp >= atrV * 0.2;
    const sweptDn = (lvl) => lvl !== null && b.low  < lvl && b.close > lvl && b.close > b.open && wickDn >= atrV * 0.2;

    // ── حساب النقاط ──────────────────────────
    let sPts = 0, lPts = 0;
    const reasons = [];

    // PDH/PDL (2 نقطة)
    if (pd) {
      if (sweptUp(pd.pdh) && rsiV >= 58) { sPts += 2; reasons.push('PDH'); }
      if (sweptDn(pd.pdl) && rsiV <= 42) { lPts += 2; reasons.push('PDL'); }
    }

    // Asia H/L — فقط في London/NY session
    if (bInD >= 84) {
      const asia = curDay.asia;
      if (asia) {
        if (sweptUp(asia.high) && rsiV >= 56) { sPts += 2; reasons.push('AsiaH'); }
        if (sweptDn(asia.low)  && rsiV <= 44) { lPts += 2; reasons.push('AsiaL'); }
      }
    }

    // London H/L — فقط في NY session
    if (bInD >= 156) {
      const lon = curDay.lon;
      if (lon && lon.high > -Infinity) {
        if (sweptUp(lon.high) && rsiV >= 56) { sPts += 1; reasons.push('LonH'); }
        if (sweptDn(lon.low)  && rsiV <= 44) { lPts += 1; reasons.push('LonL'); }
      }
    }

    // Swing H/L (1 نقطة)
    if (sweptUp(swH) && rsiV >= 56) { sPts += 1; reasons.push('SwingH'); }
    if (sweptDn(swL) && rsiV <= 44) { lPts += 1; reasons.push('SwingL'); }

    if (sPts === 0 && lPts === 0) continue;

    const type  = lPts >= sPts ? 'LONG' : 'SHORT';
    const score = Math.max(lPts, sPts);
    const stars = score >= 3 ? '⭐⭐⭐' : score >= 2 ? '⭐⭐' : '⭐';
    const price = b.close;
    const sl    = type === 'LONG' ? b.low - atrV * 0.15 : b.high + atrV * 0.15;
    const risk  = Math.abs(price - sl);
    if (risk <= 0 || risk > atrV * 6) continue;
    const tp1  = type === 'LONG' ? price + risk * 2 : price - risk * 2;
    const date = new Date(b.time * 1000).toISOString().slice(0,16).replace('T',' ');

    inTrade   = true;
    openTrade = {
      n: trades.length + 1, date, type, score, stars,
      reason: reasons.join('+'),
      price: +price.toFixed(2), sl: +sl.toFixed(2), tp1: +tp1.toFixed(2),
      risk: +risk.toFixed(2), rsi: +rsiV.toFixed(1),
      sig: { type, price, sl, tp1 },
    };
  }

  if (inTrade && openTrade && trades.length < maxTrades)
    trades.push({ ...openTrade, outcome:'OPEN', pnl:0 });

  return trades;
}

// ── التقرير ───────────────────────────────────
function report(symbol, trades) {
  const closed = trades.filter(t => t.outcome !== 'OPEN');
  const wins   = trades.filter(t => t.outcome === 'TP1').length;
  const losses = trades.filter(t => t.outcome === 'SL').length;
  const longs  = trades.filter(t => t.type === 'LONG').length;
  const shorts = trades.filter(t => t.type === 'SHORT').length;
  const totPnl = +trades.reduce((s,t) => s+t.pnl, 0).toFixed(2);
  const wr     = closed.length ? (wins/closed.length*100).toFixed(1) : '0';
  const grossW = trades.filter(t=>t.pnl>0).reduce((s,t)=>s+t.pnl,0);
  const grossL = Math.abs(trades.filter(t=>t.pnl<0).reduce((s,t)=>s+t.pnl,0));
  const pf     = grossL > 0 ? (grossW/grossL).toFixed(2) : '∞';

  // حسب الجودة
  const byScore = {};
  for (const t of trades) {
    if (!byScore[t.score]) byScore[t.score] = { t:0, w:0 };
    byScore[t.score].t++;
    if (t.outcome === 'TP1') byScore[t.score].w++;
  }

  // max streaks
  let mxW=0,mxL=0,cW=0,cL=0;
  for (const t of closed) {
    if (t.outcome==='TP1'){cW++;cL=0;mxW=Math.max(mxW,cW);}
    else{cL++;cW=0;mxL=Math.max(mxL,cL);}
  }

  let eq=0;
  const curve = trades.map(t=>{eq+=t.pnl;return eq>=0?'▲':'▼';});

  const S = '═'.repeat(72);
  console.log(`\n${S}`);
  console.log(`  📊  ${symbol}  |  Triple Sweep System`);
  console.log(S);
  console.log(`  ✅ TP1: ${String(wins).padStart(4)}   ❌ SL: ${String(losses).padStart(4)}   🔵 مفتوح: ${trades.filter(t=>t.outcome==='OPEN').length}`);
  console.log(`  📈 LONG: ${String(longs).padStart(3)}   📉 SHORT: ${String(shorts).padStart(3)}   مجموع: ${trades.length}`);
  console.log(`  🎯 Win Rate:      ${wr}%  (${closed.length} صفقة)`);
  console.log(`  💰 Total PnL:     ${totPnl>=0?'+':''}${totPnl} pts`);
  console.log(`  ⚡ Profit Factor:  ${pf}`);
  console.log(`  🔥 Max Win Streak: ${mxW}   ❄️  Max Loss Streak: ${mxL}`);

  console.log(`\n  📌 حسب الجودة:`);
  for (const [sc, v] of Object.entries(byScore).sort((a,b)=>+b[0]-+a[0])) {
    const stars = +sc >= 3 ? '⭐⭐⭐' : +sc >= 2 ? '⭐⭐' : '⭐';
    const wr2   = (v.w/v.t*100).toFixed(0);
    console.log(`     ${stars} (score ${sc})  → ${v.w}/${v.t} (${wr2}%)`);
  }

  console.log(`\n  منحنى: ${curve.join('')}`);
  console.log(S);

  // جدول
  console.log(`\n  #   Date            Dir    Score  السبب           RSI   دخول       SL         TP1        خطر   PnL`);
  console.log(`  ${'─'.repeat(104)}`);
  for (const t of trades) {
    const ic = t.outcome==='TP1'?'✅':t.outcome==='SL'?'❌':'🔵';
    console.log(
      `  ${String(t.n).padStart(3)} ${t.date}  ${t.type.padEnd(5)} ${t.stars}  ${t.reason.padEnd(16)}` +
      ` ${String(t.rsi).padEnd(5)} ${String(t.price).padEnd(10)} ${String(t.sl).padEnd(10)}` +
      ` ${String(t.tp1).padEnd(10)} ${String(t.risk).padEnd(5)} ${ic} ${t.pnl>=0?'+':''}${t.pnl}`
    );
  }

  return { wr:+wr, pf, totPnl, total:trades.length, byScore };
}

// ══ Main ══════════════════════════════════════
const S = '═'.repeat(72);
console.log(S);
console.log('  🔬  Triple Sweep Backtest  |  PDH/PDL + Session + Swing');
console.log('  📐  R:R 1:2  |  Cooldown 1h  |  بيانات اصطناعية 12,000 شمعة');
console.log(S);

const summary = {};
for (const sym of ['MNQ','MCL']) {
  const trades = runBacktest(sym, 250);
  if (!trades.length) { console.log(`\n⚠️  ${sym}: لا إشارات`); continue; }
  summary[sym] = report(sym, trades);
}

// ملخص نهائي
console.log(`\n${S}`);
console.log('  📋  الخلاصة النهائية');
console.log(S);
for (const [sym, r] of Object.entries(summary)) {
  console.log(`\n  ${sym}:  ${r.total} صفقة  |  Win ${r.wr}%  |  PnL ${r.totPnl>=0?'+':''}${r.totPnl}  |  PF ${r.pf}`);
  for (const [sc, v] of Object.entries(r.byScore).sort((a,b)=>+b[0]-+a[0])) {
    const stars = +sc>=3?'⭐⭐⭐':+sc>=2?'⭐⭐':'⭐';
    console.log(`       ${stars} → Win ${(v.w/v.t*100).toFixed(0)}%  (${v.t} صفقة)`);
  }
}
console.log(`\n${S}`);
