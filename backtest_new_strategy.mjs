/**
 * Backtest v6 — الإصلاح الجوهري
 *
 * المشكلة المكتشفة: RSI يُفحص على شمعة الارتداد
 * → بحلول الارتداد يكون RSI قد تعافى إلى 52-55 فيفشل الشرط
 * الحل: افحص RSI على شمعات التراجع (p1,p2,p3) لا الارتداد
 * + فلتر تذبذب: إذا ATR أعلى 2× معدله → سوق متقلب → لا دخول
 */

async function fetchYahoo(ticker, interval, range) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${interval}&range=${range}&includePrePost=false`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const j = await r.json();
  const res = j.chart?.result?.[0];
  if (!res) throw new Error(`لا بيانات: ${ticker}`);
  const ts = res.timestamp, q = res.indicators.quote[0];
  return ts.map((t,i) => ({
    time:t, open:q.open[i], high:q.high[i], low:q.low[i], close:q.close[i], volume:q.volume[i]||0
  })).filter(b => b.close != null && b.high != null);
}

function ema(arr, p) {
  const k = 2/(p+1), o = [];
  for (let i = 0; i < arr.length; i++) {
    if (i < p-1)   { o.push(null); continue; }
    if (i === p-1) { o.push(arr.slice(0,p).reduce((a,b)=>a+b,0)/p); continue; }
    o.push(arr[i]*k + o[i-1]*(1-k));
  }
  return o;
}

function atrArr(bars, p=14) {
  const tr = bars.map((b,i) => i===0 ? b.high-b.low :
    Math.max(b.high-b.low, Math.abs(b.high-bars[i-1].close), Math.abs(b.low-bars[i-1].close)));
  const o = [];
  for (let i = 0; i < bars.length; i++) {
    if (i < p-1)   { o.push(null); continue; }
    if (i === p-1) { o.push(tr.slice(0,p).reduce((a,b)=>a+b,0)/p); continue; }
    o.push((o[i-1]*(p-1)+tr[i])/p);
  }
  return o;
}

function rsiArr(bars, p=14) {
  const o = new Array(bars.length).fill(50);
  let g=0, l=0;
  for (let i=1; i<=p; i++) { const d=bars[i].close-bars[i-1].close; d>0?g+=d:l-=d; }
  g/=p; l/=p;
  o[p] = l===0?100:100-100/(1+g/l);
  for (let i=p+1; i<bars.length; i++) {
    const d=bars[i].close-bars[i-1].close;
    g=(g*(p-1)+Math.max(d,0))/p; l=(l*(p-1)+Math.max(-d,0))/p;
    o[i]=l===0?100:100-100/(1+g/l);
  }
  return o;
}

function inSession(unixTime) {
  const mins = new Date(unixTime*1000).getUTCHours()*60 + new Date(unixTime*1000).getUTCMinutes();
  return (mins >= 7*60 && mins < 12*60) || (mins >= 13*60+30 && mins < 17*60);
}

function buildHTFCache(bars1h) {
  const closes = bars1h.map(b=>b.close);
  const e21 = ema(closes,21), e50 = ema(closes,50);
  const map = new Map();
  for (let i=50; i<bars1h.length; i++) {
    const E21=e21[i], E50=e50[i];
    if (!E21||!E50) { map.set(bars1h[i].time,null); continue; }
    map.set(bars1h[i].time, E21>E50?'BULL':E21<E50?'BEAR':null);
  }
  return map;
}

function getHTF(htfMap, bars1h, t) {
  let best=null;
  for (const b of bars1h) { if(b.time<=t) best=b.time; else break; }
  return best ? (htfMap.get(best)??null) : null;
}

function runBacktest(bars5m, bars1h, label, rrMultiple=2.0, holdBars=36) {
  const closes = bars5m.map(b=>b.close);
  const atr5   = atrArr(bars5m,14);
  const rsi5   = rsiArr(bars5m,14);
  const e21_5  = ema(closes,21);
  const e50_5  = ema(closes,50);
  // معدل ATR لآخر 20 شمعة (لكشف التقلب الشديد)
  const atrEma = ema(atr5.map(v=>v??0), 20);
  const htfMap = buildHTFCache(bars1h);

  const results=[];
  let lastSigTime=0;

  for (let i=60; i<bars5m.length-holdBars-2; i++) {
    const cur=bars5m[i], p1=bars5m[i-1], p2=bars5m[i-2], p3=bars5m[i-3], p4=bars5m[i-4];
    const E21=e21_5[i], E50=e50_5[i], A=atr5[i];
    if (!E21||!E50||!A) continue;

    if (!inSession(cur.time)) continue;
    if (cur.time - lastSigTime < 30*60) continue; // 30 دقيقة

    const htf = getHTF(htfMap, bars1h, cur.time);
    if (!htf) continue;

    // ① فلتر التقلب الشديد — لا دخول في أيام الأخبار الكبيرة
    const atrAvg = atrEma[i];
    if (atrAvg && A > atrAvg*2.0) continue;

    // ② Spike في آخر 4 شمعات
    if (Math.abs(p1.close-p4.close) >= A*2.5) continue;

    // ③ الاتجاه على 5M
    const emaTrendL = E21>E50, emaTrendS = E21<E50;

    // ④ لمس EMA21
    const touchL = [p1,p2,p3,p4].some((b,j)=>b.low  <=(e21_5[i-1-j]??E21)*1.001);
    const touchS = [p1,p2,p3,p4].some((b,j)=>b.high >=(e21_5[i-1-j]??E21)*0.999);

    // ⑤ شمعة ارتداد
    const body=Math.abs(cur.close-cur.open), range=cur.high-cur.low||0.01;
    const bounceL = cur.close>cur.open && body/range>0.55 && cur.close>E21;
    const bounceS = cur.close<cur.open && body/range>0.55 && cur.close<E21;

    // ⑥ RSI — يُفحص على شمعات التراجع (p1,p2,p3) لا الارتداد
    const minRsi3 = Math.min(rsi5[i-1],rsi5[i-2],rsi5[i-3]);
    const maxRsi3 = Math.max(rsi5[i-1],rsi5[i-2],rsi5[i-3]);
    const rsiL = minRsi3 < 52; // كان RSI منخفضاً أثناء التراجع
    const rsiS = maxRsi3 > 48; // كان RSI مرتفعاً أثناء الصعود

    let type=null;
    if (htf==='BULL' && emaTrendL && touchL && bounceL && rsiL) type='LONG';
    else if (htf==='BEAR' && emaTrendS && touchS && bounceS && rsiS) type='SHORT';
    if (!type) continue;

    const price=cur.close;
    let sl, risk;
    if (type==='LONG') {
      sl   = Math.min(p1.low,p2.low,p3.low,p4.low, E21)-A*0.3;
      risk = price-sl;
    } else {
      sl   = Math.max(p1.high,p2.high,p3.high,p4.high, E21)+A*0.3;
      risk = sl-price;
    }
    if (risk<A*0.4||risk>A*2.5) continue;
    const tp = type==='LONG' ? price+risk*rrMultiple : price-risk*rrMultiple;

    let outcome='TIMEOUT', barsHeld=0;
    for (let j=i+1; j<Math.min(i+holdBars,bars5m.length); j++) {
      const fb=bars5m[j]; barsHeld++;
      if (type==='LONG')  { if(fb.low<=sl){outcome='LOSS';break;} if(fb.high>=tp){outcome='WIN';break;} }
      else                { if(fb.high>=sl){outcome='LOSS';break;} if(fb.low<=tp){outcome='WIN';break;} }
    }

    const d=new Date(cur.time*1000).toLocaleDateString('ar-DZ',{day:'2-digit',month:'2-digit',year:'2-digit'});
    const t=new Date(cur.time*1000).toLocaleTimeString('ar-DZ',{hour:'2-digit',minute:'2-digit'});
    results.push({d,t,type,price:+price.toFixed(1),sl:+sl.toFixed(1),tp:+tp.toFixed(1),
      risk:+risk.toFixed(1),rsi:+minRsi3.toFixed(0),outcome,barsHeld});
    lastSigTime=cur.time;
  }
  return {label,results,rrMultiple};
}

function print({label,results,rrMultiple}) {
  const wins=results.filter(r=>r.outcome==='WIN').length;
  const losses=results.filter(r=>r.outcome==='LOSS').length;
  const timeout=results.filter(r=>r.outcome==='TIMEOUT').length;
  const decided=wins+losses;
  const wr=decided>0?(wins/decided*100).toFixed(1):'0';
  const pnl=(wins*rrMultiple-losses).toFixed(1);
  const exp=decided>0?((wins/decided*rrMultiple)-(losses/decided)).toFixed(3):'0';
  const pw=(results.length/(60/7)).toFixed(1);

  console.log(`\n${'═'.repeat(60)}`);
  console.log(`  ${label}`);
  console.log(`${'═'.repeat(60)}`);
  results.forEach((r,i)=>{
    const icon=r.outcome==='WIN'?'✅':r.outcome==='LOSS'?'❌':'⏳';
    console.log(`  ${String(i+1).padStart(2)}. ${icon} ${r.d} ${r.t} ${r.type.padEnd(5)} @ ${String(r.price).padStart(8)} SL:${r.sl} minRSI:${r.rsi}`);
  });
  console.log(`\n┌${'─'.repeat(44)}┐`);
  console.log(`│  إجمالي (60 يوم) : ${String(results.length).padEnd(25)}│`);
  console.log(`│  متوسط/أسبوع    : ${(pw+' إشارة').padEnd(25)}│`);
  console.log(`│  ✅ رابحة        : ${String(wins).padEnd(25)}│`);
  console.log(`│  ❌ خاسرة        : ${String(losses).padEnd(25)}│`);
  console.log(`│  ⏳ Timeout      : ${String(timeout).padEnd(25)}│`);
  console.log(`│  نسبة النجاح    : ${(wr+'%').padEnd(25)}│`);
  console.log(`│  P&L             : ${(pnl+'R').padEnd(25)}│`);
  console.log(`│  Expectancy      : ${(exp+'R').padEnd(25)}│`);
  const m$=(Math.round(results.length/2)*parseFloat(exp)*75).toFixed(0);
  console.log(`│  ربح شهري ($75)  : $${m$.padEnd(23)}│`);
  console.log(`└${'─'.repeat(44)}┘`);
  console.log(`\n  ${parseFloat(wr)>=50?'✅ مربحة':'❌ تحتاج تحسين'} — نجاح ${wr}%\n`);
  if (!results.length) console.log('  ⚠️  لا إشارات في هذه الفترة\n');
}

console.log('\n🔍 جاري جلب بيانات NQ...\n');
try {
  const [bars5m,bars1h] = await Promise.all([
    fetchYahoo('NQ=F','5m','60d'),
    fetchYahoo('NQ=F','60m','60d'),
  ]);
  const from=new Date(bars5m[0].time*1000).toLocaleDateString('ar-DZ');
  const to  =new Date(bars5m[bars5m.length-1].time*1000).toLocaleDateString('ar-DZ');
  console.log(`✅ ${bars5m.length} شمعة 5M | ${bars1h.length} شمعة 1H | ${from} → ${to}\n`);

  print(runBacktest(bars5m,bars1h,'v6 | RSI على التراجع | فلتر تذبذب | RR 2:1',  2.0,36));
  print(runBacktest(bars5m,bars1h,'v6 | RSI على التراجع | فلتر تذبذب | RR 2.5:1',2.5,36));

} catch(e) {
  console.error('\n❌ خطأ:',e.message);
  console.log('   مجلد: C:\\Users\\nasri\\smc-bot\\smc-bot');
}
