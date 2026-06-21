/**
 * Backtest — Session Sweep (Asia + London High/Low)
 * Asia range → London تكسحه → إشارة
 * London range → NY تكسحه → إشارة
 */

// ── توليد بيانات ──────────────────────────────
function generateBars(symbol, n5m = 12000) {
  const cfg = {
    MNQ: { p0: 21000, atrPct: 0.00055, driftPct: 0.00008 },
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
    const atrV   = atrPct * price;
    const drift  = dir * driftPct * price;
    const noise  = (Math.random() - 0.5) * 2 * atrV;
    const osc    = Math.sin(i * 0.045) * atrV * 1.5;

    // محاكاة السيولة على حدود الجلسات (spikes)
    const barInDay = i % 288;
    let sessionSpike = 0;
    // بداية London (bar 96) و NY (bar 156) → غالباً يكون هناك سويب
    if (barInDay === 96 && Math.random() > 0.35)
      sessionSpike = (Math.random() > 0.5 ? 1 : -1) * atrV * (1.2 + Math.random());
    if (barInDay === 156 && Math.random() > 0.40)
      sessionSpike = (Math.random() > 0.5 ? 1 : -1) * atrV * (1.0 + Math.random());

    const open  = price;
    const close = Math.max(open + drift + noise + osc, p0 * 0.4);
    const wick  = Math.random() * atrV * 0.6;

    bars.push({
      time:    t0 + i * 300,
      barInDay,
      open:    +open.toFixed(2),
      high:    +(Math.max(open, close) + wick + Math.max(0, sessionSpike)).toFixed(2),
      low:     +(Math.max(Math.min(open, close) - wick + Math.min(0, sessionSpike), 0.01)).toFixed(2),
      close:   +close.toFixed(2),
    });
    price = close;
  }
  return bars;
}

// ── ATR ───────────────────────────────────────
function atr(bars, i, p = 14) {
  if (i < p + 1) return bars[i].high - bars[i].low;
  let s = 0;
  for (let j = i - p + 1; j <= i; j++)
    s += Math.max(bars[j].high - bars[j].low,
                  Math.abs(bars[j].high - bars[j-1].close),
                  Math.abs(bars[j].low  - bars[j-1].close));
  return s / p;
}

// ── RSI ───────────────────────────────────────
function rsi(bars, i, p = 14) {
  if (i < p + 1) return 50;
  let g = 0, l = 0;
  for (let j = i - p + 1; j <= i; j++) {
    const d = bars[j].close - bars[j-1].close;
    if (d > 0) g += d; else l -= d;
  }
  return l === 0 ? 100 : 100 - 100 / (1 + g / l);
}

// ── Session ranges ─────────────────────────────
// كل يوم = 288 شمعة 5M
// Asia   : barInDay  0 →  95  (00:00-08:00 UTC)
// London : barInDay 96 → 191  (08:00-16:00 UTC)
// NY     : barInDay 156 → 251 (13:00-21:00 UTC)

const ASIA_END   = 95;
const LONDON_END = 191;

function buildSessionRanges(bars) {
  // نبني جدول نطاقات الجلسات لكل يوم
  const days = {};
  for (let i = 0; i < bars.length; i++) {
    const dayIdx  = Math.floor(i / 288);
    const barInD  = bars[i].barInDay;
    if (!days[dayIdx]) days[dayIdx] = { asia: null, london: null };

    const d = days[dayIdx];
    if (barInD <= ASIA_END) {
      if (!d.asia) d.asia = { high: -Infinity, low: Infinity };
      d.asia.high = Math.max(d.asia.high, bars[i].high);
      d.asia.low  = Math.min(d.asia.low,  bars[i].low);
    } else if (barInD <= LONDON_END) {
      if (!d.london) d.london = { high: -Infinity, low: Infinity };
      d.london.high = Math.max(d.london.high, bars[i].high);
      d.london.low  = Math.min(d.london.low,  bars[i].low);
    }
  }
  return days;
}

// ── الباك تست ─────────────────────────────────
function runBacktest(symbol, maxTrades = 200) {
  process.stdout.write(`\n🔄 توليد بيانات ${symbol}... `);
  const bars = generateBars(symbol, 12000);
  console.log(`✅  ${bars.length} شمعة (${Math.round(bars.length/288)} يوم)`);

  const sessions = buildSessionRanges(bars);

  const trades   = [];
  const COOLDOWN = 12; // 1 ساعة
  let inTrade    = false;
  let openTrade  = null;
  let skipUntil  = 0;

  for (let i = 300; i < bars.length - 30; i++) {
    // تقييم صفقة مفتوحة
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

    const b       = bars[i];
    const dayIdx  = Math.floor(i / 288);
    const barInD  = b.barInDay;
    const prevDay = sessions[dayIdx - 1] || {};
    const curDay  = sessions[dayIdx]     || {};

    const a = atr(bars, i);
    const r = rsi(bars, i);
    if (a === 0) continue;

    let type = null, sweepOf = null, sweepLevel = null;

    // ── London يكسح Asia (barInDay 96-150) ──────
    if (barInD >= 96 && barInD <= 150) {
      const asiaRange = curDay.asia;
      if (asiaRange && asiaRange.high > -Infinity) {
        // SHORT: sweep فوق Asia High ثم إغلاق تحته
        if (b.high > asiaRange.high
          && b.close < asiaRange.high
          && b.close < b.open
          && (b.high - Math.max(b.open, b.close)) >= a * 0.25
          && r >= 55) {
          type = 'SHORT'; sweepOf = 'Asia High'; sweepLevel = asiaRange.high;
        }
        // LONG: sweep تحت Asia Low ثم إغلاق فوقه
        else if (b.low < asiaRange.low
          && b.close > asiaRange.low
          && b.close > b.open
          && (Math.min(b.open, b.close) - b.low) >= a * 0.25
          && r <= 45) {
          type = 'LONG'; sweepOf = 'Asia Low'; sweepLevel = asiaRange.low;
        }
      }
    }

    // ── NY يكسح London (barInDay 156-220) ───────
    if (!type && barInD >= 156 && barInD <= 220) {
      const londonRange = curDay.london;
      if (londonRange && londonRange.high > -Infinity) {
        if (b.high > londonRange.high
          && b.close < londonRange.high
          && b.close < b.open
          && (b.high - Math.max(b.open, b.close)) >= a * 0.25
          && r >= 55) {
          type = 'SHORT'; sweepOf = 'London High'; sweepLevel = londonRange.high;
        } else if (b.low < londonRange.low
          && b.close > londonRange.low
          && b.close > b.open
          && (Math.min(b.open, b.close) - b.low) >= a * 0.25
          && r <= 45) {
          type = 'LONG'; sweepOf = 'London Low'; sweepLevel = londonRange.low;
        }
      }
    }

    if (!type) continue;

    const price = b.close;
    const sl    = type === 'LONG' ? b.low  - a * 0.1 : b.high + a * 0.1;
    const risk  = Math.abs(price - sl);
    if (risk <= 0 || risk > a * 5) continue;
    const tp1 = type === 'LONG' ? price + risk * 2 : price - risk * 2;

    const date = new Date(b.time * 1000).toISOString().slice(0, 16).replace('T', ' ');
    inTrade   = true;
    openTrade = {
      n: trades.length + 1, date, type, sweepOf,
      price: +price.toFixed(2), sl: +sl.toFixed(2), tp1: +tp1.toFixed(2),
      risk: +risk.toFixed(2), rsi: +r.toFixed(1),
      sig: { type, price, sl, tp1 },
    };
  }

  if (inTrade && openTrade && trades.length < maxTrades)
    trades.push({ ...openTrade, outcome: 'OPEN', pnl: 0 });

  return trades;
}

// ── التقرير ───────────────────────────────────
function report(symbol, trades) {
  const closed  = trades.filter(t => t.outcome !== 'OPEN');
  const wins    = trades.filter(t => t.outcome === 'TP1').length;
  const losses  = trades.filter(t => t.outcome === 'SL').length;
  const longs   = trades.filter(t => t.type === 'LONG').length;
  const shorts  = trades.filter(t => t.type === 'SHORT').length;
  const totPnl  = +trades.reduce((s, t) => s + t.pnl, 0).toFixed(2);
  const winRate = closed.length ? (wins / closed.length * 100).toFixed(1) : '0';
  const grossW  = trades.filter(t => t.pnl > 0).reduce((s, t) => s + t.pnl, 0);
  const grossL  = Math.abs(trades.filter(t => t.pnl < 0).reduce((s, t) => s + t.pnl, 0));
  const pf      = grossL > 0 ? (grossW / grossL).toFixed(2) : '∞';

  // breakdown by sweep type
  const sMap = {};
  for (const t of trades) {
    if (!sMap[t.sweepOf]) sMap[t.sweepOf] = { t: 0, w: 0 };
    sMap[t.sweepOf].t++;
    if (t.outcome === 'TP1') sMap[t.sweepOf].w++;
  }

  let mxW = 0, mxL = 0, cW = 0, cL = 0;
  for (const t of closed) {
    if (t.outcome === 'TP1') { cW++; cL = 0; mxW = Math.max(mxW, cW); }
    else                      { cL++; cW = 0; mxL = Math.max(mxL, cL); }
  }

  let eq = 0;
  const curve = trades.map(t => { eq += t.pnl; return eq >= 0 ? '▲' : '▼'; });

  const S = '═'.repeat(68);
  console.log(`\n${S}`);
  console.log(`  📊  ${symbol}  |  Session Sweep (Asia/London High-Low)`);
  console.log(S);
  console.log(`  ✅ TP1: ${String(wins).padStart(4)}   ❌ SL: ${String(losses).padStart(4)}   🔵 مفتوح: ${trades.filter(t=>t.outcome==='OPEN').length}`);
  console.log(`  📈 LONG: ${String(longs).padStart(3)}   📉 SHORT: ${String(shorts).padStart(3)}   مجموع: ${trades.length}`);
  console.log(`  🎯 Win Rate:      ${winRate}%  (${closed.length} صفقة)`);
  console.log(`  💰 Total PnL:     ${totPnl >= 0 ? '+' : ''}${totPnl} pts`);
  console.log(`  ⚡ Profit Factor:  ${pf}`);
  console.log(`  🔥 Max Win Streak: ${mxW}   ❄️  Max Loss Streak: ${mxL}`);
  console.log(`\n  📌 حسب الجلسة:`);
  for (const [k, v] of Object.entries(sMap))
    console.log(`     ${k.padEnd(14)} → ${v.w}/${v.t} (${(v.w/v.t*100).toFixed(0)}%)`);
  console.log(`\n  منحنى: ${curve.join('')}`);
  console.log(S);

  console.log(`\n  #   Date            Dir    السويب           RSI   دخول       SL         TP1        خطر   نتيجة  PnL`);
  console.log(`  ${'─'.repeat(102)}`);
  for (const t of trades) {
    const ic = t.outcome === 'TP1' ? '✅' : t.outcome === 'SL' ? '❌' : '🔵';
    console.log(
      `  ${String(t.n).padStart(3)} ${t.date}  ${t.type.padEnd(5)}  ${t.sweepOf.padEnd(16)} ` +
      `${String(t.rsi).padEnd(5)} ${String(t.price).padEnd(10)} ${String(t.sl).padEnd(10)} ` +
      `${String(t.tp1).padEnd(10)} ${String(t.risk).padEnd(5)} ${ic} ${t.outcome.padEnd(5)} ${t.pnl>=0?'+':''}${t.pnl}`
    );
  }

  return { wins, losses, totPnl, winRate: +winRate, pf, total: trades.length };
}

// ══ Main ══════════════════════════════════════
const S = '═'.repeat(68);
console.log(S);
console.log('  🔬  Session Sweep Backtest');
console.log('  📐  Asia H/L → London  |  London H/L → NY  |  R:R 1:2');
console.log(S);

const summary = {};
for (const sym of ['MNQ', 'MCL']) {
  const trades = runBacktest(sym, 200);
  if (!trades.length) { console.log(`\n⚠️  ${sym}: لا إشارات`); continue; }
  summary[sym] = report(sym, trades);
}

if (Object.keys(summary).length > 1) {
  console.log(`\n${S}`);
  console.log('  📋  المقارنة');
  console.log(S);
  for (const [sym, r] of Object.entries(summary)) {
    console.log(`  ${sym}:  ${r.total} صفقة  |  Win ${r.winRate}%  |  PnL ${r.totPnl>=0?'+':''}${r.totPnl}  |  PF ${r.pf}`);
  }
  console.log(S);
}
