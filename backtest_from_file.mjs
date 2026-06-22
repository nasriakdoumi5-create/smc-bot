/**
 * Backtest من بيانات حقيقية محفوظة في data/
 * شغّل أولاً: GitHub Action "Fetch Market Data"
 * ثم: node backtest_from_file.mjs
 */
import { readFileSync, existsSync } from 'fs';

function loadData(file) {
  if (!existsSync(file)) throw new Error(`ملف غير موجود: ${file}\nشغّل GitHub Action "Fetch Market Data" أولاً`);
  return JSON.parse(readFileSync(file, 'utf8'));
}

function sliceDays(bars, days) {
  const cutoff = Date.now()/1000 - days*86400;
  return bars.filter(b => b.time >= cutoff);
}

// ═══════════════ نفس كود الاستراتيجية ═══════════════

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
    const V=vwap[i],V1=vwap[i-1],A=atr[i];
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

    const wasBelow=[p1,p2,p3].some(b=>b.low<V1*1.001);
    const tDn=Math.min(p1.low,p2.low,p3.low)<=V*1.003;
    const vL=(wasBelow||tDn)&&cur.close>=V*0.999;
    const mRsi=Math.min(rsi[i-1],rsi[i-2],rsi[i-3]);
    const rL=mRsi<48;
    const body=Math.abs(cur.close-cur.open),rng=cur.high-cur.low||0.01;
    const bL=cur.close>cur.open&&body/rng>0.50;

    const wasAbove=[p1,p2,p3].some(b=>b.high>V1*0.999);
    const tUp=Math.max(p1.high,p2.high,p3.high)>=V*0.997;
    const vS=(wasAbove||tUp)&&cur.close<=V*1.001;
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

    const d=new Date(cur.time*1000).toLocaleDateString('ar-DZ',{day:'2-digit',month:'2-digit'});
    const t2=new Date(cur.time*1000).toLocaleTimeString('ar-DZ',{hour:'2-digit',minute:'2-digit'});
    results.push({d,t:t2,type,price:+price.toFixed(1),outcome});
    lastSig=cur.time;
  }
  return{label,results,rr};
}

function print({label,results,rr}){
  const w=results.filter(r=>r.outcome==='WIN').length;
  const l=results.filter(r=>r.outcome==='LOSS').length;
  const t=results.filter(r=>r.outcome==='TIMEOUT').length;
  const dec=w+l;
  const wr=dec>0?(w/dec*100).toFixed(1):'—';
  const exp=dec>0?((w/dec*rr)-(l/dec)).toFixed(3):'0';
  const mo=Math.round(results.length/2);
  const m$=(mo*parseFloat(exp||0)*75).toFixed(0);
  const pct=parseFloat(wr||0);
  const bar='█'.repeat(Math.round(pct/10))+'░'.repeat(10-Math.round(pct/10));

  results.forEach((r,i)=>{
    const ic=r.outcome==='WIN'?'✅':r.outcome==='LOSS'?'❌':'⏳';
    console.log(`  ${String(i+1).padStart(2)}. ${ic} ${r.d} ${r.t}  ${r.type.padEnd(5)} @ ${r.price}`);
  });

  console.log(`\n┌${'─'.repeat(55)}┐`);
  console.log(`│  ${label.padEnd(53)}│`);
  console.log(`├${'─'.repeat(55)}┤`);
  console.log(`│  إجمالي : ${String(results.length).padEnd(44)}│`);
  console.log(`│  ✅ WIN  : ${String(w).padEnd(44)}│`);
  console.log(`│  ❌ LOSS : ${String(l).padEnd(44)}│`);
  console.log(`│  ⏳ TO   : ${String(t).padEnd(44)}│`);
  console.log(`│  WR     : ${(wr+'%  '+bar).padEnd(44)}│`);
  console.log(`│  Exp    : ${(exp+'R').padEnd(44)}│`);
  console.log(`│  /شهر   : ${(mo+' إشارة  |  $'+m$).padEnd(44)}│`);
  console.log(`└${'─'.repeat(55)}┘`);
  console.log(`  ${parseFloat(exp)>0?'✅':'❌'} ${wr}% WR | ${exp}R Expectancy\n`);
  return {w,l,t,n:results.length,wr,exp,mo,m$};
}

// ════════════════════════════════════════════════
// التشغيل
// ════════════════════════════════════════════════
console.log('\n'+'═'.repeat(60));
console.log('  📊 VWAP Bounce Backtest — بيانات حقيقية من Yahoo Finance');
console.log('═'.repeat(60));

try {
  const nq5m = loadData('data/nq_5m.json');
  const nq1h = loadData('data/nq_1h.json');
  const es5m = loadData('data/es_5m.json');
  const es1h = loadData('data/es_1h.json');

  const fetched = existsSync('data/fetched_at.txt')
    ? readFileSync('data/fetched_at.txt','utf8') : '—';

  const nq5m_30 = sliceDays(nq5m, 30);
  const es5m_30 = sliceDays(es5m, 30);

  console.log(`✅ البيانات من: ${fetched}`);
  console.log(`✅ NQ: ${nq5m.length} شمعة 5M | ${nq1h.length} شمعة 1H`);
  console.log(`✅ ES: ${es5m.length} شمعة 5M | ${es1h.length} شمعة 1H\n`);

  // ══ 60 يوم — بدون ADX ══
  console.log('─'.repeat(60));
  console.log('  📌 بدون ADX Filter');
  console.log('─'.repeat(60));
  const nq60_no = runBacktest(nq5m,    nq1h, 'NQ | 60 يوم | بدون ADX', 1.5, false);
  const es60_no = runBacktest(es5m,    es1h, 'ES | 60 يوم | بدون ADX', 1.5, false);
  const s_nq60_no = print(nq60_no);
  const s_es60_no = print(es60_no);

  // ══ 60 يوم — مع ADX ══
  console.log('─'.repeat(60));
  console.log('  🎯 مع ADX Filter (النسخة الجديدة)');
  console.log('─'.repeat(60));
  const nq60 = runBacktest(nq5m,    nq1h, 'NQ | 60 يوم | مع ADX', 1.5, true);
  const es60 = runBacktest(es5m,    es1h, 'ES | 60 يوم | مع ADX', 1.5, true);
  const s_nq60 = print(nq60);
  const s_es60 = print(es60);

  // ══ 30 يوم ══
  console.log('─'.repeat(60));
  console.log('  📅 30 يوم الأخيرة — مع ADX');
  console.log('─'.repeat(60));
  const nq30 = runBacktest(nq5m_30, nq1h, 'NQ | 30 يوم | مع ADX', 1.5, true);
  const es30 = runBacktest(es5m_30, es1h, 'ES | 30 يوم | مع ADX', 1.5, true);
  const s_nq30 = print(nq30);
  const s_es30 = print(es30);

  // ══ جدول الملخص النهائي ══
  const c60_no  = [...nq60_no.results, ...es60_no.results];
  const c60_adx = [...nq60.results,    ...es60.results];
  const c30_adx = [...nq30.results,    ...es30.results];

  function qs(results,rr) {
    const w=results.filter(r=>r.outcome==='WIN').length;
    const l=results.filter(r=>r.outcome==='LOSS').length;
    const dec=w+l;
    const wr=dec>0?(w/dec*100).toFixed(1):'—';
    const exp=dec>0?((w/dec*rr)-(l/dec)).toFixed(3):'0';
    const mo=Math.round(results.length/2);
    return {wr,exp,mo,m$:(mo*parseFloat(exp||0)*75).toFixed(0),n:results.length};
  }

  const q60_no  = qs(c60_no,  1.5);
  const q60_adx = qs(c60_adx, 1.5);
  const q30_adx = qs(c30_adx, 1.5);

  console.log('\n'+'═'.repeat(60));
  console.log('  🏆 الملخص النهائي');
  console.log('═'.repeat(60));
  console.log('');
  console.log(`  ${''.padEnd(22)}│ ${'WR'.padEnd(8)}│ ${'إشارات'.padEnd(8)}│ Exp    │ $/شهر`);
  console.log('  '+'─'.repeat(58));

  function row(lbl,s) {
    console.log(`  ${lbl.padEnd(22)}│ ${(s.wr+'%').padEnd(8)}│ ${String(s.n).padEnd(8)}│ ${(s.exp+'R').padEnd(7)}│ $${s.m$}`);
  }

  row('NQ (60ي) بدون ADX',   qs(nq60_no.results,1.5));
  row('ES (60ي) بدون ADX',   qs(es60_no.results,1.5));
  row('NQ+ES   بدون ADX',    q60_no);
  console.log('  '+'─'.repeat(58));
  row('NQ (60ي) مع ADX ✨',  qs(nq60.results,1.5));
  row('ES (60ي) مع ADX ✨',  qs(es60.results,1.5));
  row('NQ+ES   مع ADX ✨',   q60_adx);
  console.log('  '+'─'.repeat(58));
  row('NQ (30ي) مع ADX',     qs(nq30.results,1.5));
  row('ES (30ي) مع ADX',     qs(es30.results,1.5));
  row('NQ+ES 30ي مع ADX',    q30_adx);

  const diff=Math.abs(parseFloat(q60_adx.wr||0)-parseFloat(q30_adx.wr||0));
  const stable=diff<10;
  console.log('\n  '+'─'.repeat(58));
  console.log(`  ثبات: 60ي=${q60_adx.wr}% vs 30ي=${q30_adx.wr}% → فرق ${diff.toFixed(1)}% ${stable?'✅ مستقرة':'⚠️  تذبذب'}`);
  console.log(`  💰 ربح شهري متوقع (NQ+ES+ADX): $${q60_adx.m$}  (${q60_adx.mo} إشارة × $75)`);
  console.log('═'.repeat(60)+'\n');

} catch(e) {
  console.error('\n❌', e.message);
  process.exit(1);
}
