/**
 * تشغيل الباكتست بالبيانات المحلية بدلاً من Yahoo Finance
 */
import { readFileSync } from 'fs';

const localBars = JSON.parse(readFileSync('./local_data.json', 'utf8'));

// ── EMA ──────────────────────────────────────────
function ema(data, p) {
  const k = 2/(p+1), o = [];
  for (let i = 0; i < data.length; i++) {
    if (i < p-1) { o.push(null); continue; }
    if (i === p-1) { o.push(data.slice(0,p).reduce((a,b)=>a+b,0)/p); continue; }
    o.push(data[i]*k + o[i-1]*(1-k));
  }
  return o;
}

// ── ATR ──────────────────────────────────────────
function atr(bars, p) {
  const tr = bars.map((b,i) => i===0 ? b.high-b.low :
    Math.max(b.high-b.low, Math.abs(b.high-bars[i-1].close), Math.abs(b.low-bars[i-1].close)));
  const o = [];
  for (let i = 0; i < bars.length; i++) {
    if (i < p-1) { o.push(null); continue; }
    if (i === p-1) { o.push(tr.slice(0,p).reduce((a,b)=>a+b,0)/p); continue; }
    o.push((o[i-1]*(p-1)+tr[i])/p);
  }
  return o;
}

// ── RSI ──────────────────────────────────────────
function rsi(bars, p) {
  const o = new Array(bars.length).fill(50);
  let g=0, l=0;
  for (let i=1; i<=p; i++) {
    const d = bars[i].close - bars[i-1].close;
    d>0 ? g+=d : l+=Math.abs(d);
  }
  g/=p; l/=p;
  o[p] = l===0?100:100-100/(1+g/l);
  for (let i=p+1; i<bars.length; i++) {
    const d = bars[i].close - bars[i-1].close;
    g = (g*(p-1)+Math.max(d,0))/p;
    l = (l*(p-1)+Math.max(-d,0))/p;
    o[i] = l===0?100:100-100/(1+g/l);
  }
  return o;
}

// ── Killzone ──────────────────────────────────────
function inKillzone(unixTime) {
  const d = new Date(unixTime * 1000);
  const mins = d.getUTCHours()*60 + d.getUTCMinutes();
  return (mins >= 13*60+30 && mins < 16*60) || (mins >= 7*60 && mins < 10*60);
}

// ── FVG ──────────────────────────────────────────
function detectFVG(bars, i, minSize) {
  if (i < 2) return null;
  const b0=bars[i-2], b2=bars[i];
  if (b2.low > b0.high && (b2.low - b0.high) >= minSize)
    return { type:'BULL', top: b2.low, bot: b0.high, midpoint: (b2.low+b0.high)/2, barIdx: i };
  if (b2.high < b0.low && (b0.low - b2.high) >= minSize)
    return { type:'BEAR', top: b0.low, bot: b2.high, midpoint: (b0.low+b2.high)/2, barIdx: i };
  return null;
}

// ── ICT Backtest ──────────────────────────────────
function runICT(bars, label, rrMultiple = 1.5, holdBars = 18) {
  const closes  = bars.map(b => b.close);
  const e50arr  = ema(closes, 50);
  const e200arr = ema(closes, 200);
  const e21arr  = ema(closes, 21);
  const atrArr  = atr(bars, 14);
  const rsiArr  = rsi(bars, 14);

  const results = [];
  const activeFVGs = [];
  let lastEntryBar = -8;

  for (let i = 210; i < bars.length - holdBars - 2; i++) {
    const b = bars[i];
    const E50=e50arr[i], E200=e200arr[i], E21=e21arr[i], A=atrArr[i], R=rsiArr[i];
    if (!E50||!E200||!E21||!A) continue;

    const htfBull = E50 > E200;
    const htfBear = E50 < E200;

    const fvg = detectFVG(bars, i, A * 0.3);
    if (fvg) {
      if ((fvg.type==='BULL'&&htfBull)||(fvg.type==='BEAR'&&htfBear))
        activeFVGs.push({ ...fvg, created: i });
    }
    while (activeFVGs.length > 0 && i - activeFVGs[0].created > 30) activeFVGs.shift();

    if (!inKillzone(b.time)) continue;
    if (i - lastEntryBar < 6) continue;

    for (const fvg of activeFVGs) {
      const price = b.close;
      if (price < fvg.bot || price > fvg.top) continue;

      const body  = Math.abs(b.close - b.open);
      const range = (b.high - b.low) || 0.01;
      let type = null;

      if (fvg.type==='BULL'&&htfBull) {
        const bullCandle = b.close>b.open && body/range>0.3;
        const hammer     = b.close>b.open && (b.open-b.low)>body*1.2;
        if ((bullCandle||hammer) && R<65) type='LONG';
      }
      if (fvg.type==='BEAR'&&htfBear) {
        const bearCandle = b.close<b.open && body/range>0.3;
        const shootstar  = b.close<b.open && (b.high-b.open)>body*1.2;
        if ((bearCandle||shootstar) && R>35) type='SHORT';
      }
      if (!type) continue;

      let sl;
      if (type==='LONG') { sl=fvg.bot-A*0.25; if(sl>=price) continue; }
      else               { sl=fvg.top+A*0.25; if(sl<=price) continue; }

      const risk = Math.abs(price-sl);
      if (risk<A*0.2||risk>A*4) continue;

      const tp = type==='LONG' ? price+risk*rrMultiple : price-risk*rrMultiple;

      let outcome='TIMEOUT', barsHeld=0;
      for (let j=i+1; j<Math.min(i+holdBars,bars.length); j++) {
        const fb=bars[j]; barsHeld++;
        if (type==='LONG') {
          if(fb.low<=sl){outcome='LOSS';break;}
          if(fb.high>=tp){outcome='WIN';break;}
        } else {
          if(fb.high>=sl){outcome='LOSS';break;}
          if(fb.low<=tp){outcome='WIN';break;}
        }
      }

      const d = new Date(b.time*1000).toLocaleDateString('ar-DZ',{day:'2-digit',month:'2-digit',year:'2-digit'});
      results.push({ d, type, price:+price.toFixed(1), sl:+sl.toFixed(1), tp:+tp.toFixed(1),
        risk:+risk.toFixed(1), rsi:+R.toFixed(0), outcome, barsHeld });
      lastEntryBar = i;
      break;
    }
  }
  return { label, results, rrMultiple };
}

// ── EMA Bounce Backtest (استراتيجيتك الرئيسية) ────
function runEMABounce(bars, label, rrMultiple = 1.5, holdBars = 16) {
  const closes  = bars.map(b => b.close);
  const e50arr  = ema(closes, 50);
  const e200arr = ema(closes, 200);
  const e21arr  = ema(closes, 21);
  const atrArr  = atr(bars, 14);
  const rsiArr  = rsi(bars, 14);

  const results = [];
  let lastEntryBar = -8;

  for (let i = 210; i < bars.length - holdBars - 2; i++) {
    const b    = bars[i];
    const E50  = e50arr[i], E200=e200arr[i], E21=e21arr[i];
    const A    = atrArr[i], R=rsiArr[i];
    if (!E50||!E200||!E21||!A) continue;
    if (i - lastEntryBar < 6) continue;

    const htfBull = E50 > E200;
    const htfBear = E50 < E200;
    const nearEMA = Math.abs(b.close - E21) < A * 0.5;
    if (!nearEMA) continue;

    const body  = Math.abs(b.close - b.open);
    const range = (b.high - b.low) || 0.01;
    let type = null;

    if (htfBull && b.close > b.open && body/range > 0.35 && R < 60) type = 'LONG';
    if (htfBear && b.close < b.open && body/range > 0.35 && R > 40) type = 'SHORT';
    if (!type) continue;

    const sl = type==='LONG' ? E21 - A*0.5 : E21 + A*0.5;
    if (type==='LONG' && sl >= b.close) continue;
    if (type==='SHORT' && sl <= b.close) continue;

    const risk = Math.abs(b.close - sl);
    if (risk < A*0.1 || risk > A*3) continue;

    const tp = type==='LONG' ? b.close+risk*rrMultiple : b.close-risk*rrMultiple;

    let outcome='TIMEOUT', barsHeld=0;
    for (let j=i+1; j<Math.min(i+holdBars,bars.length); j++) {
      const fb=bars[j]; barsHeld++;
      if (type==='LONG') {
        if(fb.low<=sl){outcome='LOSS';break;}
        if(fb.high>=tp){outcome='WIN';break;}
      } else {
        if(fb.high>=sl){outcome='LOSS';break;}
        if(fb.low<=tp){outcome='WIN';break;}
      }
    }
    const d = new Date(b.time*1000).toLocaleDateString('ar-DZ',{day:'2-digit',month:'2-digit',year:'2-digit'});
    results.push({ d, type, price:+b.close.toFixed(1), sl:+sl.toFixed(1), tp:+tp.toFixed(1),
      risk:+risk.toFixed(1), rsi:+R.toFixed(0), outcome, barsHeld });
    lastEntryBar = i;
  }
  return { label, results, rrMultiple };
}

// ── طباعة النتائج ─────────────────────────────────
function printResults({ label, results, rrMultiple }) {
  const wins    = results.filter(r=>r.outcome==='WIN').length;
  const losses  = results.filter(r=>r.outcome==='LOSS').length;
  const timeout = results.filter(r=>r.outcome==='TIMEOUT').length;
  const decided = wins + losses;
  const wr      = decided>0 ? (wins/decided*100).toFixed(1) : 0;
  const pnl     = (wins*rrMultiple - losses).toFixed(1);
  const exp     = decided>0 ? ((wins/decided*rrMultiple) - (losses/decided)).toFixed(3) : 0;

  const L  = results.filter(r=>r.type==='LONG');
  const S  = results.filter(r=>r.type==='SHORT');
  const lw = L.filter(r=>r.outcome==='WIN').length;
  const ll = L.filter(r=>r.outcome==='LOSS').length;
  const sw = S.filter(r=>r.outcome==='WIN').length;
  const sl2= S.filter(r=>r.outcome==='LOSS').length;

  console.log(`\n${'═'.repeat(55)}`);
  console.log(`  ${label} | RR ${rrMultiple}:1 | ${results.length} إشارة`);
  console.log(`${'═'.repeat(55)}`);

  // آخر 30 صفقة
  const show = results.slice(-30);
  show.forEach((r,idx) => {
    const icon = r.outcome==='WIN'?'✅':r.outcome==='LOSS'?'❌':'⏳';
    console.log(`  ${icon} ${r.d} ${r.type.padEnd(5)} @ ${String(r.price).padStart(7)} | R:${r.rsi} | ${r.outcome}`);
  });

  console.log(`\n┌${'─'.repeat(40)}┐`);
  console.log(`│  إجمالي الإشارات : ${String(results.length).padEnd(21)}│`);
  console.log(`│  ✅ رابح          : ${String(wins).padEnd(21)}│`);
  console.log(`│  ❌ خاسر          : ${String(losses).padEnd(21)}│`);
  console.log(`│  ⏳ Timeout       : ${String(timeout).padEnd(21)}│`);
  console.log(`│  نسبة النجاح      : ${(wr+'%').padEnd(21)}│`);
  console.log(`│  P&L (R)         : ${pnl.padEnd(21)}│`);
  console.log(`│  Expectancy/صفقة : ${(exp+'R').padEnd(21)}│`);
  const pass = parseFloat(wr) >= 55;
  console.log(`│  هل تجتاز 55%؟   : ${(pass?'✅ نعم!':'❌ لا — '+wr+'%').padEnd(21)}│`);
  console.log(`└${'─'.repeat(40)}┘`);
  console.log(`  LONG : ${L.length} | ${lw}W/${ll}L → ${lw+ll>0?(lw/(lw+ll)*100).toFixed(1):0}%`);
  console.log(`  SHORT: ${S.length} | ${sw}W/${sl2}L → ${sw+sl2>0?(sw/(sw+sl2)*100).toFixed(1):0}%`);

  return { wins, losses, decided, wr: parseFloat(wr), pnl: parseFloat(pnl), exp: parseFloat(exp) };
}

// ── تشغيل الكل ────────────────────────────────────
console.log(`\n🔍 باكتست محلي — بيانات MNQ محاكاة (730 يوم، 1H)`);
console.log(`   ${localBars.length} شمعة | من ${new Date(localBars[0].time*1000).toLocaleDateString('ar-DZ')} → ${new Date(localBars[localBars.length-1].time*1000).toLocaleDateString('ar-DZ')}`);

const r1 = printResults(runICT(localBars,       'ICT FVG Strategy'));
const r2 = printResults(runEMABounce(localBars, 'EMA21 Bounce Strategy'));

console.log(`\n${'═'.repeat(55)}`);
console.log(`  ملخص المقارنة`);
console.log(`${'═'.repeat(55)}`);
console.log(`  ICT FVG     : ${r1.wr}% نجاح | P&L: ${r1.pnl}R | Exp: ${r1.exp}R/صفقة`);
console.log(`  EMA Bounce  : ${r2.wr}% نجاح | P&L: ${r2.pnl}R | Exp: ${r2.exp}R/صفقة`);

const best = r1.exp >= r2.exp ? 'ICT FVG' : 'EMA21 Bounce';
console.log(`\n  ► الاستراتيجية الأفضل: ${best}`);
console.log(`  ► رأس مال 1000$ + خطر 1%/صفقة:`);
const expBest = Math.max(r1.exp, r2.exp);
const tradesBest = Math.max(r1.decided, r2.decided);
const monthlyR = (tradesBest / 24) * expBest; // صفقات شهرية
console.log(`    متوسط صفقات/شهر : ${(tradesBest/24).toFixed(0)}`);
console.log(`    ربح شهري متوقع  : ${(monthlyR * 10).toFixed(1)}$ (بمخاطرة 10$/صفقة)`);
console.log(`    ربح شهري متوقع  : ${(monthlyR * 50).toFixed(0)}$ (بمخاطرة 50$/صفقة)`);
