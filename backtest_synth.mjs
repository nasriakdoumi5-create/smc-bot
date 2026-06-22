/**
 * Backtest — VWAP Bounce | بيانات اصطناعية واقعية
 * يعمل بدون إنترنت — لاختبار منطق الاستراتيجية
 */

// ── توليد بيانات OHLCV واقعية ───────────────────
function generateBars(startPrice, atrPerBar, numDays, intervalMins, seed=42) {
  let s = seed;
  const rand  = () => { s=(s*1664525+1013904223)&0xffffffff; return(s>>>0)/0xffffffff; };
  const randn = () => {
    const u1=rand(),u2=rand();
    return Math.sqrt(-2*Math.log(u1+1e-10))*Math.cos(2*Math.PI*u2);
  };

  // محاذاة لمنتصف الليل UTC
  const now       = Math.floor(Date.now()/1000);
  const todayMid  = now - (now % 86400);
  const startDay  = todayMid - numDays*86400;

  // بناء جلسات لكل يوم (تجاهل الإجازات)
  const sessions = [];
  for (let d=0; d<numDays; d++) {
    const dayStart = startDay + d*86400;
    const dow = new Date(dayStart*1000).getUTCDay(); // 0=Sun 6=Sat
    if (dow===0||dow===6) continue;
    sessions.push({ from: dayStart+7*3600,    to: dayStart+12*3600    }); // London
    sessions.push({ from: dayStart+49*60*30,  to: dayStart+55*60*30   }); // NY 13:30-15:30
  }
  // Fix: NY times
  const sessions2 = [];
  for (let d=0; d<numDays; d++) {
    const dayStart = startDay + d*86400;
    const dow = new Date(dayStart*1000).getUTCDay();
    if (dow===0||dow===6) continue;
    sessions2.push({ from: dayStart+7*3600,          to: dayStart+12*3600         });
    sessions2.push({ from: dayStart+13*3600+30*60,   to: dayStart+15*3600+30*60   });
  }

  const bars = [];
  let price = startPrice;

  // نظام اتجاه (يتغير كل 3-7 أيام)
  let trend=0, trendRemain=0;

  for (const sess of sessions2) {
    if (--trendRemain<=0) {
      const r=rand();
      trend = r<0.35?1:r<0.70?-1:0;
      trendRemain=Math.floor(rand()*5+3);
    }

    // VWAP تراكمي للجلسة
    let vNum=0,vDen=0;
    const dayVwap = price; // تقريب بداية اليوم

    let t=sess.from;
    while (t<sess.to) {
      const vwap = vDen>0 ? vNum/vDen : price;

      // سحب نحو VWAP + اتجاه + ضجيج
      const reversion = (vwap - price) * 0.06;
      const drift     = trend * atrPerBar * 0.10;
      const noise     = randn() * atrPerBar;

      const open  = price;
      const chg   = drift + noise + reversion;
      const close = open + chg;
      const wick  = Math.abs(randn()) * atrPerBar * 0.4;
      const hi    = Math.max(open,close) + wick;
      const lo    = Math.min(open,close) - wick;
      const vol   = Math.max(100, Math.floor((0.7+rand()*0.6)*4000));

      bars.push({
        time:  t,
        open:  +open.toFixed(2),
        high:  +Math.max(hi,open,close).toFixed(2),
        low:   +Math.min(lo,open,close).toFixed(2),
        close: +close.toFixed(2),
        volume: vol
      });

      const tp=(hi+lo+close)/3;
      vNum+=tp*vol; vDen+=vol;
      price=close;
      t+=intervalMins*60;
    }
  }
  return bars.sort((a,b)=>a.time-b.time);
}

// إعادة تجميع 5M → 1H
function resample1h(bars5m) {
  const map=new Map();
  for (const b of bars5m) {
    const key=Math.floor(b.time/3600)*3600;
    if (!map.has(key)) map.set(key,{time:key,open:b.open,high:b.high,low:b.low,close:b.close,volume:b.volume});
    else {
      const c=map.get(key);
      c.high=Math.max(c.high,b.high);
      c.low=Math.min(c.low,b.low);
      c.close=b.close;
      c.volume+=b.volume;
    }
  }
  return [...map.values()].sort((a,b)=>a.time-b.time);
}

// ═══════════════════════════════════════════════
// الاستراتيجية (مطابق لـ strategy_simple.js)
// ═══════════════════════════════════════════════
function calcADX(bars, period=14) {
  const n=bars.length;
  if(n<period+2) return {trend:'RANGING'};
  const trs=[],pdms=[],ndms=[];
  for(let i=1;i<n;i++){
    const b=bars[i],p=bars[i-1];
    trs.push(Math.max(b.high-b.low,Math.abs(b.high-p.close),Math.abs(b.low-p.close)));
    const up=b.high-p.high,dn=p.low-b.low;
    pdms.push(up>dn&&up>0?up:0);
    ndms.push(dn>up&&dn>0?dn:0);
  }
  const sl=arr=>arr.slice(-period).reduce((a,b)=>a+b,0);
  const trS=sl(trs),pdmS=sl(pdms),ndmS=sl(ndms);
  const pdi=trS>0?pdmS/trS*100:15;
  const ndi=trS>0?ndmS/trS*100:15;
  const adx=pdi+ndi>0?Math.abs(pdi-ndi)/(pdi+ndi)*100:20;
  return {adx:+adx.toFixed(1),trend:adx>25?(pdi>ndi?'BULL_TREND':'BEAR_TREND'):'RANGING'};
}

function ema(arr,p){
  const k=2/(p+1),o=[];
  for(let i=0;i<arr.length;i++){
    if(i<p-1){o.push(null);continue;}
    if(i===p-1){o.push(arr.slice(0,p).reduce((a,b)=>a+b,0)/p);continue;}
    o.push(arr[i]*k+o[i-1]*(1-k));
  }
  return o;
}

function atrArr(bars,p=14){
  const o=[];
  for(let i=0;i<bars.length;i++){
    const tr=i===0?bars[i].high-bars[i].low:
      Math.max(bars[i].high-bars[i].low,Math.abs(bars[i].high-bars[i-1].close),Math.abs(bars[i].low-bars[i-1].close));
    if(i<p-1){o.push(null);continue;}
    if(i===p-1){o.push(bars.slice(0,p).map((b,j)=>j===0?b.high-b.low:Math.max(b.high-b.low,Math.abs(b.high-bars[j-1].close),Math.abs(b.low-bars[j-1].close))).reduce((a,b)=>a+b,0)/p);continue;}
    o.push((o[i-1]*(p-1)+tr)/p);
  }
  return o;
}

function rsiArr(bars,p=14){
  const o=new Array(bars.length).fill(50);
  let g=0,l=0;
  for(let i=1;i<=p&&i<bars.length;i++){const d=bars[i].close-bars[i-1].close;d>0?g+=d:l-=d;}
  g/=p;l/=p;
  if(p<bars.length)o[p]=l===0?100:100-100/(1+g/l);
  for(let i=p+1;i<bars.length;i++){
    const d=bars[i].close-bars[i-1].close;
    g=(g*(p-1)+Math.max(d,0))/p;l=(l*(p-1)+Math.max(-d,0))/p;
    o[i]=l===0?100:100-100/(1+g/l);
  }
  return o;
}

function calcVWAP(bars){
  const out=[];let cumPV=0,cumV=0,curDay='';
  for(const b of bars){
    const day=new Date(b.time*1000).toISOString().slice(0,10);
    if(day!==curDay){cumPV=0;cumV=0;curDay=day;}
    const tp=(b.high+b.low+b.close)/3,v=b.volume||1;
    cumPV+=tp*v;cumV+=v;out.push(cumPV/cumV);
  }
  return out;
}

function buildHTF(bars1h){
  const c=bars1h.map(b=>b.close),e21=ema(c,21),e50=ema(c,50),map=new Map();
  for(let i=50;i<bars1h.length;i++){
    const E21=e21[i],E50=e50[i];
    map.set(bars1h[i].time,E21&&E50?(E21>E50?'BULL':E21<E50?'BEAR':null):null);
  }
  return map;
}

function getHTF(map,bars1h,t){
  let best=null;
  for(const b of bars1h){if(b.time<=t)best=b.time;else break;}
  return best?map.get(best)??null:null;
}

function inSession(t){
  const m=new Date(t*1000).getUTCHours()*60+new Date(t*1000).getUTCMinutes();
  return (m>=7*60&&m<12*60)||(m>=13*60+30&&m<15*60+30);
}

function get1HMom(bars1h,t){
  const r=bars1h.filter(b=>b.time<=t).slice(-4);
  if(r.length<3)return null;
  const l=r.slice(-3);
  return{bullish:l.filter(b=>b.close>b.open).length>=2,bearish:l.filter(b=>b.close<b.open).length>=2};
}

function runBacktest(bars5m, bars1h, label, rr=1.5, withADX=true) {
  const vwap=calcVWAP(bars5m),atr=atrArr(bars5m,14),rsi=rsiArr(bars5m,14);
  const atrEma=ema(atr.map(v=>v??0),20);
  const htfMap=buildHTF(bars1h);
  const results=[];let lastSig=0;

  for(let i=60;i<bars5m.length-25;i++){
    const cur=bars5m[i],p1=bars5m[i-1],p2=bars5m[i-2],p3=bars5m[i-3],p4=bars5m[i-4];
    const V=vwap[i],V1=vwap[i-1],A=atr[i],R=rsi[i];
    if(!V||!A)continue;
    if(!inSession(cur.time))continue;
    if(cur.time-lastSig<30*60)continue;

    const htf=getHTF(htfMap,bars1h,cur.time);
    if(!htf)continue;

    const aAvg=atrEma[i];
    if(aAvg&&A>aAvg*2.0)continue;
    if(Math.abs(p1.close-p4.close)>=A*2.5)continue;
    if(aAvg&&A<aAvg*0.55)continue;

    const mom=get1HMom(bars1h,cur.time);
    if(!mom)continue;

    let regime='RANGING';
    if(withADX){
      const h1=bars1h.filter(b=>b.time<=cur.time);
      regime=calcADX(h1,14).trend;
    }

    // LONG
    const wasBel=[p1,p2,p3].some(b=>b.low<V1*1.001);
    const tDn=Math.min(p1.low,p2.low,p3.low)<=V*1.003;
    const vL=(wasBel||tDn)&&cur.close>=V*0.999;
    const mRsi=Math.min(rsi[i-1],rsi[i-2],rsi[i-3]);
    const rL=mRsi<48;
    const body=Math.abs(cur.close-cur.open),rng=cur.high-cur.low||0.01;
    const bL=cur.close>cur.open&&body/rng>0.50;

    // SHORT
    const wasAb=[p1,p2,p3].some(b=>b.high>V1*0.999);
    const tUp=Math.max(p1.high,p2.high,p3.high)>=V*0.997;
    const vS=(wasAb||tUp)&&cur.close<=V*1.001;
    const xRsi=Math.max(rsi[i-1],rsi[i-2],rsi[i-3]);
    const rS=xRsi>52;
    const bS=cur.close<cur.open&&body/rng>0.50;

    let type=null;
    if(htf==='BULL'&&vL&&bL&&rL&&mom.bullish&&regime!=='BEAR_TREND') type='LONG';
    else if(htf==='BEAR'&&vS&&bS&&rS&&mom.bearish&&regime!=='BULL_TREND') type='SHORT';
    if(!type)continue;

    const price=cur.close;
    let sl,risk;
    if(type==='LONG'){sl=Math.min(p1.low,p2.low,p3.low,V)-A*0.3;risk=price-sl;}
    else{sl=Math.max(p1.high,p2.high,p3.high,V)+A*0.3;risk=sl-price;}
    if(risk<A*0.2||risk>A*2.0)continue;
    const tp=type==='LONG'?price+risk*rr:price-risk*rr;

    let outcome='TIMEOUT';
    for(let j=i+1;j<Math.min(i+24,bars5m.length);j++){
      const fb=bars5m[j];
      if(type==='LONG'){if(fb.low<=sl){outcome='LOSS';break;}if(fb.high>=tp){outcome='WIN';break;}}
      else{if(fb.high>=sl){outcome='LOSS';break;}if(fb.low<=tp){outcome='WIN';break;}}
    }
    results.push({type,outcome});
    lastSig=cur.time;
  }
  return{label,results,rr};
}

function st(results,rr){
  const w=results.filter(r=>r.outcome==='WIN').length;
  const l=results.filter(r=>r.outcome==='LOSS').length;
  const t=results.filter(r=>r.outcome==='TIMEOUT').length;
  const dec=w+l;
  const wr=dec>0?(w/dec*100).toFixed(1):'—';
  const exp=dec>0?((w/dec*rr)-(l/dec)).toFixed(3):'0';
  const mo=Math.round(results.length/2);
  const m$=(mo*parseFloat(exp||0)*75).toFixed(0);
  return{w,l,t,n:results.length,wr,exp,mo,m$,dec};
}

// ── طباعة نتيجة واحدة ────────────────────────────
function pr({label,results,rr}){
  const {w,l,t,n,wr,exp,mo,m$}=st(results,rr);
  const pct=parseFloat(wr||0);
  const bar=Math.round(pct/10);
  const fill='█'.repeat(bar)+'░'.repeat(10-bar);
  console.log(`\n┌${'─'.repeat(58)}┐`);
  console.log(`│  ${label.padEnd(56)}│`);
  console.log(`├${'─'.repeat(58)}┤`);
  console.log(`│  إجمالي : ${String(n).padEnd(47)}│`);
  console.log(`│  ✅ WIN  : ${String(w).padEnd(47)}│`);
  console.log(`│  ❌ LOSS : ${String(l).padEnd(47)}│`);
  console.log(`│  ⏳ TO   : ${String(t).padEnd(47)}│`);
  console.log(`│  WR     : ${(wr+'%  '+fill).padEnd(47)}│`);
  console.log(`│  Exp    : ${(exp+'R').padEnd(47)}│`);
  console.log(`│  /شهر   : ${(mo+' إشارة | $'+m$).padEnd(47)}│`);
  console.log(`└${'─'.repeat(58)}┘`);
  console.log(`  ${parseFloat(exp)>0?'✅':'❌'} ${label} — WR:${wr}%`);
}

// ── جدول المقارنة ─────────────────────────────────
function cmpRow(lbl, r1, r2, rr) {
  const s1=st(r1.results,rr), s2=st(r2.results,rr);
  const d=(parseFloat(s2.wr||0)-parseFloat(s1.wr||0)).toFixed(1);
  const arr=parseFloat(d)>=0?'▲':'▼';
  return `  ${lbl.padEnd(18)}│ ${('WR:'+s1.wr+'% ('+s1.n+'إش)').padEnd(18)}│ ${('WR:'+s2.wr+'% ('+s2.n+'إش)').padEnd(18)}│ ${arr}${d}%`;
}

// ════════════════════════════════════════════════════
// تشغيل
// ════════════════════════════════════════════════════
console.log('\n'+'═'.repeat(62));
console.log('  📊 VWAP Bounce Backtest — NQ + ES | ADX Filter Test');
console.log('  ⚡ بيانات اصطناعية واقعية | 60 يوم');
console.log('═'.repeat(62));

// توليد البيانات (3 سيناريوهات)
// NQ: ~21000، ATR/5M ~20 نقطة
// ES: ~5900،  ATR/5M ~7 نقطة
const NQ5m_A = generateBars(21000, 20, 60, 5, 42);   // سيناريو عادي
const ES5m_A = generateBars(5900,  7,  60, 5, 99);
const NQ5m_B = generateBars(19500, 25, 60, 5, 17);   // سيناريو متقلب
const ES5m_B = generateBars(5700,  9,  60, 5, 55);

const NQ1h_A = resample1h(NQ5m_A);
const ES1h_A = resample1h(ES5m_A);
const NQ1h_B = resample1h(NQ5m_B);
const ES1h_B = resample1h(ES5m_B);

const now60 = Date.now()/1000;
const NQ5m_A30 = NQ5m_A.filter(b=>b.time>=now60-30*86400);
const ES5m_A30 = ES5m_A.filter(b=>b.time>=now60-30*86400);

console.log(`\n✅ NQ-A: ${NQ5m_A.length} شمعة 5M (${NQ1h_A.length} × 1H)`);
console.log(`✅ ES-A: ${ES5m_A.length} شمعة 5M (${ES1h_A.length} × 1H)`);
console.log(`✅ NQ-B: ${NQ5m_B.length} شمعة 5M (${NQ1h_B.length} × 1H)\n`);

// ══ سيناريو A: بدون ADX vs مع ADX ══
console.log('─'.repeat(62));
console.log('  🔵 سيناريو A — بدون ADX Filter');
console.log('─'.repeat(62));
const nqA_no = runBacktest(NQ5m_A, NQ1h_A, 'NQ | 60 يوم | بدون ADX', 1.5, false);
const esA_no = runBacktest(ES5m_A, ES1h_A, 'ES | 60 يوم | بدون ADX', 1.5, false);
pr(nqA_no); pr(esA_no);

console.log('\n'+'─'.repeat(62));
console.log('  🟢 سيناريو A — مع ADX Filter');
console.log('─'.repeat(62));
const nqA_adx = runBacktest(NQ5m_A, NQ1h_A, 'NQ | 60 يوم | مع ADX', 1.5, true);
const esA_adx = runBacktest(ES5m_A, ES1h_A, 'ES | 60 يوم | مع ADX', 1.5, true);
pr(nqA_adx); pr(esA_adx);

// ══ سيناريو B (متقلب) ══
console.log('\n'+'─'.repeat(62));
console.log('  🟠 سيناريو B (متقلب) — مع ADX Filter');
console.log('─'.repeat(62));
const nqB_no  = runBacktest(NQ5m_B, NQ1h_B, 'NQ | متقلب | بدون ADX', 1.5, false);
const nqB_adx = runBacktest(NQ5m_B, NQ1h_B, 'NQ | متقلب | مع ADX',   1.5, true);
pr(nqB_no); pr(nqB_adx);

// ══ 60 vs 30 يوم ══
console.log('\n'+'─'.repeat(62));
console.log('  📅 30 يوم vs 60 يوم (ثبات الاستراتيجية)');
console.log('─'.repeat(62));
const nqA30_adx = runBacktest(NQ5m_A30, NQ1h_A, 'NQ | 30 يوم | مع ADX', 1.5, true);
const esA30_adx = runBacktest(ES5m_A30, ES1h_A, 'ES | 30 يوم | مع ADX', 1.5, true);
pr(nqA30_adx); pr(esA30_adx);

// ══ جدول ملخص ══
const comb60_no  = [...nqA_no.results,  ...esA_no.results];
const comb60_adx = [...nqA_adx.results, ...esA_adx.results];
const comb30_adx = [...nqA30_adx.results,...esA30_adx.results];

console.log('\n'+'═'.repeat(62));
console.log('  🏆 جدول المقارنة النهائي');
console.log('═'.repeat(62));
console.log(`  ${'الأداة'.padEnd(18)}│ ${'بدون ADX'.padEnd(18)}│ ${'مع ADX'.padEnd(18)}│ التغيير`);
console.log('  '+'─'.repeat(60));
console.log(cmpRow('NQ (60 يوم)',  nqA_no, nqA_adx, 1.5));
console.log(cmpRow('ES (60 يوم)',  esA_no, esA_adx, 1.5));
console.log(cmpRow('NQ متقلب',    nqB_no, nqB_adx, 1.5));

const c60no ={results:comb60_no,  rr:1.5};
const c60adx={results:comb60_adx, rr:1.5};
console.log(cmpRow('NQ+ES مجمع',  c60no,  c60adx,  1.5));

console.log('  '+'─'.repeat(60));

// ثبات 60 vs 30 يوم
const s60=st(comb60_adx,1.5), s30=st(comb30_adx,1.5);
const diff=Math.abs(parseFloat(s60.wr||0)-parseFloat(s30.wr||0));
const stable=diff<10;

console.log(`\n  ثبات 60 يوم vs 30 يوم:`);
console.log(`  60 يوم: WR ${s60.wr}% (${s60.n} إشارة)`);
console.log(`  30 يوم: WR ${s30.wr}% (${s30.n} إشارة)`);
console.log(`  الفرق: ${diff.toFixed(1)}% → ${stable?'✅ مستقرة':'⚠️  متذبذبة'}`);

console.log(`\n  💰 الربح الشهري المتوقع (NQ+ES مع ADX):`);
console.log(`     ${s60.mo} إشارة/شهر × Exp ${s60.exp}R × $75 = $${s60.m$}`);

console.log('\n'+'═'.repeat(62));
console.log('  ⚠️  بيانات اصطناعية — للاختبار الحقيقي شغّل:');
console.log('  node backtest_new_strategy.mjs    (على جهازك)');
console.log('═'.repeat(62)+'\n');
