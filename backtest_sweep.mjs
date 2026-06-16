/**
 * Liquidity Sweep Backtest — PDH/PDL + NY Open
 * ──────────────────────────────────────────────
 * المنطق:
 * ① السعر يكسح قمة أمس (PDH) أو قاع أمس (PDL)
 * ② ثم ينعكس بقوة (إغلاق رجوع داخل النطاق)
 * ③ فقط في NY Open: 13:30-15:30 UTC
 * ④ HTF trend aligned (EMA50 vs EMA200)
 * ⑤ RR 1.5:1
 */

async function fetchBars(symbol, range) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=60m&range=${range}&includePrePost=true`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const j = await r.json();
  const res = j.chart?.result?.[0];
  const ts = res.timestamp, q = res.indicators.quote[0];
  return ts.map((t,i) => ({
    time:t, open:q.open[i], high:q.high[i], low:q.low[i], close:q.close[i]
  })).filter(b => b.close!=null);
}

function ema(data, p) {
  const k=2/(p+1), o=[];
  for(let i=0;i<data.length;i++) {
    if(i<p-1){o.push(null);continue;}
    if(i===p-1){o.push(data.slice(0,p).reduce((a,b)=>a+b,0)/p);continue;}
    o.push(data[i]*k+o[i-1]*(1-k));
  }
  return o;
}
function atr(bars,p) {
  const tr=bars.map((b,i)=>i===0?b.high-b.low:Math.max(b.high-b.low,Math.abs(b.high-bars[i-1].close),Math.abs(b.low-bars[i-1].close)));
  const o=[];
  for(let i=0;i<bars.length;i++){
    if(i<p-1){o.push(null);continue;}
    if(i===p-1){o.push(tr.slice(0,p).reduce((a,b)=>a+b,0)/p);continue;}
    o.push((o[i-1]*(p-1)+tr[i])/p);
  }
  return o;
}

function inNYOpen(unixTime) {
  const d = new Date(unixTime*1000);
  const mins = d.getUTCHours()*60+d.getUTCMinutes();
  return mins >= 13*60+30 && mins < 15*60+30;
}

function getDayKey(unixTime) {
  return new Date(unixTime*1000).toISOString().slice(0,10);
}

async function backtest(symbol, ticker, rr=1.5) {
  console.log(`\n► ${symbol} — جاري التحليل...`);
  const bars = await fetchBars(ticker, '730d');

  const closes=bars.map(b=>b.close);
  const e50=ema(closes,50), e200=ema(closes,200), atrArr=atr(bars,14);

  // بناء قاموس PDH/PDL لكل يوم
  const dailyMap = {}; // key=YYYY-MM-DD → {high, low}
  for(const b of bars) {
    const key = getDayKey(b.time);
    if(!dailyMap[key]) dailyMap[key] = { high:-Infinity, low:Infinity };
    dailyMap[key].high = Math.max(dailyMap[key].high, b.high);
    dailyMap[key].low  = Math.min(dailyMap[key].low,  b.low);
  }
  const days = Object.keys(dailyMap).sort();

  const results = [];
  let lastDay = '';

  for(let i=210; i<bars.length-10; i++) {
    const b = bars[i];
    if(!inNYOpen(b.time)) continue;

    const today = getDayKey(b.time);
    if(today === lastDay) continue; // صفقة واحدة يومياً فقط

    // قاع أمس وقمة أمس
    const todayIdx = days.indexOf(today);
    if(todayIdx < 1) continue;
    const yesterday = days[todayIdx-1];
    const pdh = dailyMap[yesterday]?.high;
    const pdl = dailyMap[yesterday]?.low;
    if(!pdh || !pdl) continue;

    const E50=e50[i], E200=e200[i], A=atrArr[i];
    if(!E50||!E200||!A) continue;

    const htfBull = E50 > E200;
    const htfBear = E50 < E200;

    const price = b.close;
    const body = Math.abs(b.close - b.open);
    const range = b.high - b.low || 0.01;
    const bodyPct = body/range;

    let type = null;

    // ── SHORT setup: كسح PDH ثم انعكاس ──────────
    // السعر لامس/تجاوز PDH ثم أغلق تحتها (bearish rejection)
    if(b.high > pdh &&           // لمس/تجاوز PDH
       b.close < pdh &&          // أغلق تحت PDH (انعكاس)
       b.close < b.open &&       // شمعة هابطة
       bodyPct > 0.35) {         // جسم قوي
      // لا يشترط htfBear — كسح السيولة يعمل حتى في اتجاه صاعد
      type = 'SHORT';
    }

    // ── LONG setup: كسح PDL ثم انعكاس ───────────
    if(b.low < pdl &&            // لمس/تجاوز PDL
       b.close > pdl &&          // أغلق فوق PDL (انعكاس)
       b.close > b.open &&       // شمعة صاعدة
       bodyPct > 0.35) {         // جسم قوي
      type = 'LONG';
    }

    if(!type) continue;

    // SL: فوق high الشمعة (+ATR*0.2) لـ SHORT، تحت low لـ LONG
    let sl;
    if(type === 'SHORT') sl = b.high + A*0.15;
    else                  sl = b.low  - A*0.15;

    const risk = Math.abs(price - sl);
    if(risk < A*0.1 || risk > A*5) continue;

    const tp = type==='SHORT' ? price - risk*rr : price + risk*rr;

    // محاكاة: 16 شمعة = ~16 ساعة
    let outcome='TIMEOUT';
    for(let j=i+1;j<Math.min(i+16,bars.length);j++){
      const fb=bars[j];
      if(type==='SHORT'){if(fb.high>=sl){outcome='LOSS';break;}if(fb.low<=tp){outcome='WIN';break;}}
      else              {if(fb.low<=sl) {outcome='LOSS';break;}if(fb.high>=tp){outcome='WIN';break;}}
    }

    lastDay = today;

    const d=new Date(b.time*1000).toLocaleDateString('es-ES',{timeZone:'Europe/Madrid',day:'2-digit',month:'2-digit',year:'2-digit'});
    results.push({ d, type, price:+price.toFixed(2), sl:+sl.toFixed(2), tp:+tp.toFixed(2),
      risk:+risk.toFixed(2), pdh:+pdh.toFixed(2), pdl:+pdl.toFixed(2), outcome });
  }

  const w=results.filter(r=>r.outcome==='WIN').length;
  const l=results.filter(r=>r.outcome==='LOSS').length;
  const t=results.filter(r=>r.outcome==='TIMEOUT').length;
  const wr=w+l>0?(w/(w+l)*100).toFixed(1):0;
  const pnl=(w*rr-l*1).toFixed(1);

  console.log(`\n${'═'.repeat(62)}`);
  console.log(`  ${symbol} — Liquidity Sweep (PDH/PDL) + NY Open`);
  console.log(`${'═'.repeat(62)}`);

  results.forEach((r,i) => {
    const icon=r.outcome==='WIN'?'✅':r.outcome==='LOSS'?'❌':'⏳';
    const ref=r.type==='SHORT'?`PDH:${r.pdh}`:`PDL:${r.pdl}`;
    console.log(`${String(i+1).padStart(3)}. ${icon} ${r.d} ${r.type.padEnd(5)} @ ${String(r.price).padStart(8)} SL:${r.sl} TP:${r.tp} | ${ref}`);
  });

  console.log(`\n┌${'─'.repeat(44)}┐`);
  console.log(`│  إجمالي:     ${String(results.length).padEnd(30)}│`);
  console.log(`│  ✅ رابح:    ${String(w).padEnd(31)}│`);
  console.log(`│  ❌ خاسر:    ${String(l).padEnd(31)}│`);
  console.log(`│  ⏳ Timeout: ${String(t).padEnd(31)}│`);
  console.log(`│  نسبة النجاح:  ${(wr+'%').padEnd(28)}│`);
  console.log(`│  P&L (${rr}:1): ${(pnl+'R').padEnd(29)}│`);
  const flag = parseFloat(wr)>=60?'✅ نعم!':'❌ '+wr+'%';
  console.log(`│  الهدف 60%? ${flag.padEnd(32)}│`);
  console.log(`└${'─'.repeat(44)}┘`);

  const Ls=results.filter(r=>r.type==='LONG'),  Ss=results.filter(r=>r.type==='SHORT');
  const lw=Ls.filter(r=>r.outcome==='WIN').length, ll=Ls.filter(r=>r.outcome==='LOSS').length;
  const sw=Ss.filter(r=>r.outcome==='WIN').length, sl2=Ss.filter(r=>r.outcome==='LOSS').length;
  console.log(`\n  LONG:  ${Ls.length} صفقة | ${lw}W/${ll}L | ${lw+ll>0?(lw/(lw+ll)*100).toFixed(1):0}% نجاح`);
  console.log(`  SHORT: ${Ss.length} صفقة | ${sw}W/${sl2}L | ${sw+sl2>0?(sw/(sw+sl2)*100).toFixed(1):0}% نجاح`);

  return { symbol, total:results.length, w, l, wr:parseFloat(wr), pnl:parseFloat(pnl) };
}

const r1 = await backtest('MNQ', 'NQ=F', 1.5);
const r2 = await backtest('MCL', 'CL=F', 1.5);

console.log(`\n${'═'.repeat(62)}`);
const tw=r1.w+r2.w, tl=r1.l+r2.l;
console.log(`  نهائي: MNQ ${r1.wr}% | MCL ${r2.wr}% | مجموع: ${(tw/(tw+tl)*100).toFixed(1)}%`);
console.log(`  P&L: MNQ ${r1.pnl}R | MCL ${r2.pnl}R | مجموع: ${(r1.pnl+r2.pnl).toFixed(1)}R`);
