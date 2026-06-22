/**
 * Backtest — VWAP Bounce Scalping على NQ حقيقي
 * Yahoo Finance: آخر 60 يوم 5M + 1H
 *
 * المنطق: السوق يرتد نحو VWAP — المؤسسات تستخدمه
 * LONG: السعر نزل تحت VWAP + RSI منخفض + ارتداد صاعد
 * SHORT: السعر صعد فوق VWAP + RSI مرتفع + ارتداد هابط
 */

async function fetchYahoo(ticker, interval, range) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${interval}&range=${range}&includePrePost=false`;
  const r = await fetch(url, { headers:{'User-Agent':'Mozilla/5.0'} });
  const j = await r.json();
  const res = j.chart?.result?.[0];
  if (!res) throw new Error(`لا بيانات: ${ticker}`);
  const ts=res.timestamp, q=res.indicators.quote[0];
  return ts.map((t,i)=>({
    time:t, open:q.open[i], high:q.high[i], low:q.low[i],
    close:q.close[i], volume:q.volume[i]||0
  })).filter(b=>b.close!=null&&b.high!=null);
}

function ema(arr, p) {
  const k=2/(p+1), o=[];
  for (let i=0;i<arr.length;i++) {
    if (i<p-1) {o.push(null);continue;}
    if (i===p-1) {o.push(arr.slice(0,p).reduce((a,b)=>a+b,0)/p);continue;}
    o.push(arr[i]*k+o[i-1]*(1-k));
  }
  return o;
}

function atrArr(bars,p=14) {
  const tr=bars.map((b,i)=>i===0?b.high-b.low:
    Math.max(b.high-b.low,Math.abs(b.high-bars[i-1].close),Math.abs(b.low-bars[i-1].close)));
  const o=[];
  for (let i=0;i<bars.length;i++) {
    if (i<p-1) {o.push(null);continue;}
    if (i===p-1) {o.push(tr.slice(0,p).reduce((a,b)=>a+b,0)/p);continue;}
    o.push((o[i-1]*(p-1)+tr[i])/p);
  }
  return o;
}

function rsiArr(bars,p=14) {
  const o=new Array(bars.length).fill(50);
  let g=0,l=0;
  for (let i=1;i<=p;i++){const d=bars[i].close-bars[i-1].close;d>0?g+=d:l-=d;}
  g/=p;l/=p;
  o[p]=l===0?100:100-100/(1+g/l);
  for (let i=p+1;i<bars.length;i++){
    const d=bars[i].close-bars[i-1].close;
    g=(g*(p-1)+Math.max(d,0))/p;l=(l*(p-1)+Math.max(-d,0))/p;
    o[i]=l===0?100:100-100/(1+g/l);
  }
  return o;
}

// VWAP يومي — يُعاد حسابه كل يوم
function calcVWAP(bars) {
  const out=[];
  let cumPV=0,cumV=0,curDay='';
  for (const b of bars) {
    const day=new Date(b.time*1000).toISOString().slice(0,10);
    if (day!==curDay){cumPV=0;cumV=0;curDay=day;}
    const tp=(b.high+b.low+b.close)/3, v=b.volume||1;
    cumPV+=tp*v; cumV+=v;
    out.push(cumPV/cumV);
  }
  return out;
}

// HTF من 1H
function buildHTF(bars1h) {
  const closes=bars1h.map(b=>b.close);
  const e21=ema(closes,21),e50=ema(closes,50);
  const map=new Map();
  for (let i=50;i<bars1h.length;i++) {
    const E21=e21[i],E50=e50[i];
    if (!E21||!E50){map.set(bars1h[i].time,null);continue;}
    map.set(bars1h[i].time, E21>E50?'BULL':E21<E50?'BEAR':null);
  }
  return map;
}

function getHTF(map,bars1h,t) {
  let best=null;
  for (const b of bars1h){if(b.time<=t)best=b.time;else break;}
  return best?(map.get(best)??null):null;
}

function inSession(t) {
  const m=new Date(t*1000).getUTCHours()*60+new Date(t*1000).getUTCMinutes();
  // London: 07:00-12:00 UTC (كامل جلسة لندن)
  const london = m>=7*60 && m<12*60;
  // NY Open: 13:30-15:30 UTC (أقوى ساعتين — نوقف قبل تراجع الحجم)
  const ny = m>=13*60+30 && m<15*60+30;
  return london || ny;
}

// زخم 1H: آخر 3 شمعات 1H — هل الزخم يوافق الاتجاه؟
function get1HMomentum(bars1h, targetTime) {
  const recent = bars1h.filter(b=>b.time<=targetTime).slice(-4);
  if (recent.length < 3) return null;
  const last3  = recent.slice(-3);
  const bullBars = last3.filter(b=>b.close>b.open).length;
  const bearBars = last3.filter(b=>b.close<b.open).length;
  return { bullish: bullBars >= 2, bearish: bearBars >= 2 };
}

function runBacktest(bars5m, bars1h, label, rr=1.5, hold=24) {
  const vwap5 = calcVWAP(bars5m);
  const atr5  = atrArr(bars5m,14);
  const rsi5  = rsiArr(bars5m,14);
  const atrEma= ema(atr5.map(v=>v??0),20);
  const htfMap= buildHTF(bars1h);

  const results=[];
  let lastSigTime=0;

  for (let i=60;i<bars5m.length-hold-2;i++) {
    const cur=bars5m[i],p1=bars5m[i-1],p2=bars5m[i-2],p3=bars5m[i-3],p4=bars5m[i-4];
    const VWAP=vwap5[i], VWAP1=vwap5[i-1];
    const A=atr5[i], R=rsi5[i];
    if (!VWAP||!A) continue;
    if (!inSession(cur.time)) continue;
    if (cur.time-lastSigTime < 30*60) continue;

    const htf=getHTF(htfMap,bars1h,cur.time);
    if (!htf) continue;

    // فلتر تذبذب شديد
    const atrAvg=atrEma[i];
    if (atrAvg&&A>atrAvg*2.0) continue;

    // فلتر Spike
    if (Math.abs(p1.close-p4.close)>=A*2.5) continue;

    // زخم 1H — لا LONG إذا آخر 3 شمعات 1H هابطة (والعكس)
    const mom=get1HMomentum(bars1h,cur.time);
    if (!mom) continue;

    // ── شروط LONG ──
    const wasBelow  = [p1,p2,p3].some(b=>b.low<VWAP1*1.001);
    const touchedDn = Math.min(p1.low,p2.low,p3.low)<=VWAP*1.003;
    const vwapL     = (wasBelow||touchedDn) && cur.close>=VWAP*0.999;
    const minRsi    = Math.min(rsi5[i-1],rsi5[i-2],rsi5[i-3]);
    const rsiL      = minRsi < 48;
    const body      = Math.abs(cur.close-cur.open), range=cur.high-cur.low||0.01;
    const bounceL   = cur.close>cur.open && body/range>0.50;
    const momentumL = mom.bullish; // آخر 3 شمعات 1H صاعدة (2 من 3)

    // ── شروط SHORT ──
    const wasAbove  = [p1,p2,p3].some(b=>b.high>VWAP1*0.999);
    const touchedUp = Math.max(p1.high,p2.high,p3.high)>=VWAP*0.997;
    const vwapS     = (wasAbove||touchedUp) && cur.close<=VWAP*1.001;
    const maxRsi    = Math.max(rsi5[i-1],rsi5[i-2],rsi5[i-3]);
    const rsiS      = maxRsi > 52;
    const bounceS   = cur.close<cur.open && body/range>0.50;
    const momentumS = mom.bearish; // آخر 3 شمعات 1H هابطة (2 من 3)

    let type=null;
    if (htf==='BULL'&&vwapL&&bounceL&&rsiL&&momentumL) type='LONG';
    else if (htf==='BEAR'&&vwapS&&bounceS&&rsiS&&momentumS) type='SHORT';
    if (!type) continue;

    const price=cur.close;
    let sl,risk;
    if (type==='LONG') {
      sl=Math.min(p1.low,p2.low,p3.low,VWAP)-A*0.3;
      risk=price-sl;
    } else {
      sl=Math.max(p1.high,p2.high,p3.high,VWAP)+A*0.3;
      risk=sl-price;
    }
    if (risk<A*0.2||risk>A*2.0) continue;
    const tp=type==='LONG'?price+risk*rr:price-risk*rr;

    let outcome='TIMEOUT',barsHeld=0;
    for (let j=i+1;j<Math.min(i+hold,bars5m.length);j++) {
      const fb=bars5m[j];barsHeld++;
      if (type==='LONG') {if(fb.low<=sl){outcome='LOSS';break;}if(fb.high>=tp){outcome='WIN';break;}}
      else               {if(fb.high>=sl){outcome='LOSS';break;}if(fb.low<=tp){outcome='WIN';break;}}
    }

    const d=new Date(cur.time*1000).toLocaleDateString('ar-DZ',{day:'2-digit',month:'2-digit',year:'2-digit'});
    const t2=new Date(cur.time*1000).toLocaleTimeString('ar-DZ',{hour:'2-digit',minute:'2-digit'});
    const rsiDisp=type==='LONG'?minRsi:maxRsi;
    results.push({d,t:t2,type,price:+price.toFixed(1),sl:+sl.toFixed(1),tp:+tp.toFixed(1),
      vwap:+VWAP.toFixed(1),risk:+risk.toFixed(1),rsi:+rsiDisp.toFixed(0),outcome,barsHeld});
    lastSigTime=cur.time;
  }
  return {label,results,rr};
}

function print({label,results,rr}) {
  const wins  =results.filter(r=>r.outcome==='WIN').length;
  const losses=results.filter(r=>r.outcome==='LOSS').length;
  const to    =results.filter(r=>r.outcome==='TIMEOUT').length;
  const dec   =wins+losses;
  const wr    =dec>0?(wins/dec*100).toFixed(1):'0';
  const pnl   =(wins*rr-losses).toFixed(1);
  const exp   =dec>0?((wins/dec*rr)-(losses/dec)).toFixed(3):'0';
  const pw    =(results.length/(60/7)).toFixed(1);

  console.log(`\n${'═'.repeat(64)}`);
  console.log(`  ${label}`);
  console.log(`${'═'.repeat(64)}`);
  results.forEach((r,i)=>{
    const ic=r.outcome==='WIN'?'✅':r.outcome==='LOSS'?'❌':'⏳';
    console.log(`  ${String(i+1).padStart(2)}. ${ic} ${r.d} ${r.t} ${r.type.padEnd(5)} @ ${String(r.price).padStart(8)} VWAP:${r.vwap} RSI:${r.rsi}`);
  });
  console.log(`\n┌${'─'.repeat(46)}┐`);
  console.log(`│  إجمالي (60 يوم) : ${String(results.length).padEnd(27)}│`);
  console.log(`│  متوسط/أسبوع    : ${(pw+' إشارة').padEnd(27)}│`);
  console.log(`│  ✅ رابحة        : ${String(wins).padEnd(27)}│`);
  console.log(`│  ❌ خاسرة        : ${String(losses).padEnd(27)}│`);
  console.log(`│  ⏳ Timeout      : ${String(to).padEnd(27)}│`);
  console.log(`│  نسبة النجاح    : ${(wr+'%').padEnd(27)}│`);
  console.log(`│  P&L             : ${(pnl+'R').padEnd(27)}│`);
  console.log(`│  Expectancy      : ${(exp+'R').padEnd(27)}│`);
  const mo=Math.round(results.length/2);
  const m$=(mo*parseFloat(exp)*75).toFixed(0);
  console.log(`│${'─'.repeat(46)}│`);
  console.log(`│  إشارات/شهر: ${String(mo).padEnd(33)}│`);
  console.log(`│  ربح شهري ($75/صفقة): $${m$.padEnd(21)}│`);
  console.log(`└${'─'.repeat(46)}┘`);
  // مربحة إذا Expectancy > 0 (مع RR 2:1 يكفي 34% win rate)
  const ok = parseFloat(exp) > 0;
  console.log(`\n  ${ok?'✅ مربحة':'❌ خاسرة'} — WR:${wr}% | Expectancy:${exp}R\n`);
  if (!results.length) console.log('  ⚠️  لا إشارات في هذه الفترة\n');
}

console.log('\n📊 VWAP Bounce Backtest — NQ Futures\n');
try {
  const [bars5m,bars1h]=await Promise.all([
    fetchYahoo('NQ=F','5m','60d'),
    fetchYahoo('NQ=F','60m','60d'),
  ]);
  const from=new Date(bars5m[0].time*1000).toLocaleDateString('ar-DZ');
  const to  =new Date(bars5m[bars5m.length-1].time*1000).toLocaleDateString('ar-DZ');
  console.log(`✅ ${bars5m.length} شمعة 5M | ${bars1h.length} شمعة 1H | ${from} → ${to}\n`);

  print(runBacktest(bars5m,bars1h,'VWAP Bounce | RR 1.5:1 | Hold 2h',  1.5,24));
  print(runBacktest(bars5m,bars1h,'VWAP Bounce | RR 2.0:1 | Hold 2h',  2.0,24));

} catch(e) {
  console.error('\n❌ خطأ:',e.message);
  console.log('   مجلد: C:\\Users\\nasri\\smc-bot\\smc-bot');
}
