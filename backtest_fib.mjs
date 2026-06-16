/**
 * Fibonacci OTE + RSI Backtest
 * ════════════════════════════════════════════════════════
 * المبدأ:
 *   ① كشف موجة impulse حقيقية (نظيفة، قوية، واضحة)
 *   ② انتظار التراجع إلى OTE Zone: 61.8% – 78.6%
 *   ③ RSI تأكيد: < 45 للشراء (oversold في التراجع)
 *                  > 55 للبيع  (overbought في التراجع)
 *   ④ شمعة انعكاس عند المستوى
 *   ⑤ SL: تحت/فوق نقطة بداية الموجة
 *   ⑥ TP: مستوى 100% (قمة/قاع الموجة) أو امتداد 127.2%
 *
 * "الموجات الصحيحة" = impulse قوي:
 *   - حجم الموجة >= 2.5 × ATR
 *   - اتجاه واضح (> 60% من الشمعات في نفس اتجاه الموجة)
 *   - ليس بطيئاً جداً (< 30 شمعة)
 *   - ليس سريعاً جداً (> 3 شمعات)
 * ════════════════════════════════════════════════════════
 */

async function fetchBars(symbol, range) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=60m&range=${range}&includePrePost=true`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const j = await r.json();
  const res = j.chart?.result?.[0];
  const ts = res.timestamp, q = res.indicators.quote[0];
  return ts.map((t,i) => ({
    time:t, open:q.open[i], high:q.high[i],
    low:q.low[i], close:q.close[i]
  })).filter(b => b.close != null && b.high != null);
}

function ema(data, p) {
  const k=2/(p+1), o=[];
  for(let i=0;i<data.length;i++){
    if(i<p-1){o.push(null);continue;}
    if(i===p-1){o.push(data.slice(0,p).reduce((a,b)=>a+b,0)/p);continue;}
    o.push(data[i]*k+o[i-1]*(1-k));
  }
  return o;
}
function atr(bars,p) {
  const tr=bars.map((b,i)=>i===0?b.high-b.low:
    Math.max(b.high-b.low,Math.abs(b.high-bars[i-1].close),Math.abs(b.low-bars[i-1].close)));
  const o=[];
  for(let i=0;i<bars.length;i++){
    if(i<p-1){o.push(null);continue;}
    if(i===p-1){o.push(tr.slice(0,p).reduce((a,b)=>a+b,0)/p);continue;}
    o.push((o[i-1]*(p-1)+tr[i])/p);
  }
  return o;
}
function rsiCalc(bars,p) {
  const o=new Array(bars.length).fill(50);
  let g=0,l=0;
  for(let i=1;i<=p;i++){const d=bars[i].close-bars[i-1].close;d>0?g+=d:l+=Math.abs(d);}
  g/=p;l/=p;
  o[p]=l===0?100:100-100/(1+g/l);
  for(let i=p+1;i<bars.length;i++){
    const d=bars[i].close-bars[i-1].close;
    g=(g*(p-1)+Math.max(d,0))/p;l=(l*(p-1)+Math.max(-d,0))/p;
    o[i]=l===0?100:100-100/(1+g/l);
  }
  return o;
}

// ── pivot high/low (N شمعات على كل جانب) ────────
function pivotHighs(bars, n=3) {
  const o=new Array(bars.length).fill(false);
  for(let i=n;i<bars.length-n;i++){
    let isPH=true;
    for(let j=1;j<=n;j++) if(bars[i].high<=bars[i-j].high||bars[i].high<=bars[i+j].high){isPH=false;break;}
    o[i]=isPH;
  }
  return o;
}
function pivotLows(bars, n=3) {
  const o=new Array(bars.length).fill(false);
  for(let i=n;i<bars.length-n;i++){
    let isPL=true;
    for(let j=1;j<=n;j++) if(bars[i].low>=bars[i-j].low||bars[i].low>=bars[i+j].low){isPL=false;break;}
    o[i]=isPL;
  }
  return o;
}

// ══ قياس جودة الموجة ════════════════════════════
// موجة "صحيحة" = impulse نظيف
function waveQuality(bars, fromIdx, toIdx) {
  const dir = bars[toIdx].close > bars[fromIdx].close ? 1 : -1;
  const n   = toIdx - fromIdx;
  if (n < 3 || n > 35) return 0;  // قصيرة جداً أو طويلة جداً

  let aligned = 0;
  for (let i = fromIdx+1; i <= toIdx; i++) {
    const chg = bars[i].close - bars[i-1].close;
    if (dir === 1 && chg > 0) aligned++;
    if (dir === -1 && chg < 0) aligned++;
  }
  const alignPct = aligned / n;  // % شمعات في اتجاه الموجة
  if (alignPct < 0.55) return 0;  // موجة مضطربة — ليست impulse

  // تحقق أن الموجة لا تتداخل مع نقطة البداية (لا تعود لأكثر من 50%)
  const waveDist = Math.abs(bars[toIdx].close - bars[fromIdx].close);
  let maxCounter = 0;
  for (let i = fromIdx+1; i <= toIdx; i++) {
    const retraced = dir===1
      ? bars[fromIdx].close - bars[i].low
      : bars[i].high - bars[fromIdx].close;
    maxCounter = Math.max(maxCounter, retraced);
  }
  if (maxCounter > waveDist * 0.5) return 0;  // تراجع داخلي كبير = ليست impulse

  return alignPct;  // جودة الموجة (0.55 – 1.0)
}

// ══ Fibonacci Levels ════════════════════════════
function fibLevel(start, end, pct) {
  return end + (start - end) * pct;
}

// ══ الخوارزمية الرئيسية ═════════════════════════
async function backtest(symbol, ticker, rrMultiple=1.618) {
  console.log(`\n► ${symbol} — جاري التحميل...`);
  const bars = await fetchBars(ticker, '730d');
  console.log(`  ${bars.length} شمعة — ${new Date(bars[0].time*1000).toLocaleDateString('es-ES',{timeZone:'Europe/Madrid'})} → ${new Date(bars[bars.length-1].time*1000).toLocaleDateString('es-ES',{timeZone:'Europe/Madrid'})}`);

  const closes = bars.map(b=>b.close);
  const e50arr = ema(closes,50), e200arr = ema(closes,200);
  const atrArr = atr(bars,14);
  const rsiArr = rsiCalc(bars,14);
  const PH     = pivotHighs(bars,3);
  const PL     = pivotLows(bars,3);

  const results = [];
  let lastEntryBar = -10;

  // نبحث عن كل pivot — ثم نبحث عن موجة نظيفة قبله
  for (let i = 220; i < bars.length - 12; i++) {
    if (i - lastEntryBar < 5) continue;

    const A    = atrArr[i];
    const R    = rsiArr[i];
    const E50  = e50arr[i], E200 = e200arr[i];
    if (!A || !E50 || !E200) continue;

    const htfBull = E50 > E200;
    const htfBear = E50 < E200;

    // ── LONG: ابحث عن موجة صاعدة نظيفة قبل 60 شمعة ──
    if (htfBull) {
      // ابحث عن آخر pivot high ثم pivot low قبله
      let phIdx = -1;
      for (let k = i-4; k >= Math.max(0,i-60); k--) {
        if (PH[k]) { phIdx = k; break; }
      }
      if (phIdx < 0) continue;

      let plIdx = -1;
      for (let k = phIdx-1; k >= Math.max(0,phIdx-50); k--) {
        if (PL[k]) { plIdx = k; break; }
      }
      if (plIdx < 0) continue;

      // الموجة الصاعدة: من pivot low إلى pivot high
      const waveStart = plIdx;
      const waveEnd   = phIdx;
      const waveBot   = bars[waveStart].low;
      const waveTop   = bars[waveEnd].high;
      const waveSize  = waveTop - waveBot;

      // فلتر الجودة
      if (waveSize < A * 2.5) continue;                   // موجة صغيرة
      const quality = waveQuality(bars, waveStart, waveEnd);
      if (quality < 0.55) continue;                       // موجة مضطربة

      // Fibonacci OTE Zone: 61.8% – 78.6% (تراجع)
      const fib618  = fibLevel(waveTop, waveBot, 0.382);  // = waveBot + 61.8% من الارتفاع
      const fib786  = fibLevel(waveTop, waveBot, 0.214);  // = waveBot + 78.6% من الارتفاع
      // بعبارة أخرى: السعر تراجع 61.8-78.6% من الموجة الصاعدة
      const oteTop  = waveTop - waveSize * 0.618;
      const oteBot  = waveTop - waveSize * 0.786;

      const price = bars[i].close;

      // السعر داخل OTE zone
      if (price < oteBot || price > oteTop) continue;

      // RSI تأكيد: oversold نسبياً في التراجع
      if (R > 50) continue;  // RSI يجب أن يكون < 50 (فضاء للارتداد)

      // شمعة صاعدة تأكيدية
      const b = bars[i];
      const body = Math.abs(b.close - b.open);
      const range = b.high - b.low || 0.01;
      if (b.close <= b.open) continue;          // يجب شمعة صاعدة
      if (body/range < 0.30) continue;          // جسم قوي

      // SL: تحت bott الموجة + هامش
      const sl  = waveBot - A * 0.25;
      const risk = price - sl;
      if (risk <= 0 || risk > waveSize * 0.9) continue;

      // TP: 100% (قمة الموجة السابقة) أو امتداد 127.2%
      const tp  = Math.min(waveTop + waveSize * 0.272, price + risk * rrMultiple);

      let outcome = 'TIMEOUT';
      for(let j=i+1; j<Math.min(i+24,bars.length); j++) {
        const fb=bars[j];
        if(fb.low<=sl){outcome='LOSS';break;}
        if(fb.high>=tp){outcome='WIN';break;}
      }

      const d=new Date(b.time*1000).toLocaleDateString('es-ES',{timeZone:'Europe/Madrid',day:'2-digit',month:'2-digit',year:'2-digit'});
      const fib618pct = ((waveTop-price)/waveSize*100).toFixed(0);
      results.push({d,type:'LONG',price:+price.toFixed(1),sl:+sl.toFixed(1),tp:+tp.toFixed(1),
        risk:+risk.toFixed(1),rsi:+R.toFixed(0),fibPct:fib618pct,quality:+quality.toFixed(2),
        waveSize:+waveSize.toFixed(1),outcome});
      lastEntryBar = i;
    }

    // ── SHORT: ابحث عن موجة هابطة نظيفة ─────────
    if (htfBear) {
      let plIdx2 = -1;
      for (let k = i-4; k >= Math.max(0,i-60); k--) {
        if (PL[k]) { plIdx2 = k; break; }
      }
      if (plIdx2 < 0) continue;

      let phIdx2 = -1;
      for (let k = plIdx2-1; k >= Math.max(0,plIdx2-50); k--) {
        if (PH[k]) { phIdx2 = k; break; }
      }
      if (phIdx2 < 0) continue;

      const waveStart = phIdx2;
      const waveEnd   = plIdx2;
      const waveTop   = bars[waveStart].high;
      const waveBot   = bars[waveEnd].low;
      const waveSize  = waveTop - waveBot;

      if (waveSize < A * 2.5) continue;
      const quality = waveQuality(bars, waveStart, waveEnd);
      if (quality < 0.55) continue;

      // OTE Zone: 61.8% – 78.6% من الموجة الهابطة (ارتداد)
      const oteBot2  = waveBot + waveSize * 0.618;
      const oteTop2  = waveBot + waveSize * 0.786;

      const price = bars[i].close;
      if (price < oteBot2 || price > oteTop2) continue;

      if (R < 50) continue;  // RSI يجب > 50 للبيع

      const b = bars[i];
      const body = Math.abs(b.close - b.open);
      const range = b.high - b.low || 0.01;
      if (b.close >= b.open) continue;
      if (body/range < 0.30) continue;

      const sl  = waveTop + A * 0.25;
      const risk = sl - price;
      if (risk <= 0 || risk > waveSize * 0.9) continue;

      const tp  = Math.max(waveBot - waveSize * 0.272, price - risk * rrMultiple);

      let outcome = 'TIMEOUT';
      for(let j=i+1; j<Math.min(i+24,bars.length); j++) {
        const fb=bars[j];
        if(fb.high>=sl){outcome='LOSS';break;}
        if(fb.low<=tp){outcome='WIN';break;}
      }

      const d=new Date(bars[i].time*1000).toLocaleDateString('es-ES',{timeZone:'Europe/Madrid',day:'2-digit',month:'2-digit',year:'2-digit'});
      const fibPct = ((price-waveBot)/waveSize*100).toFixed(0);
      results.push({d,type:'SHORT',price:+price.toFixed(1),sl:+sl.toFixed(1),tp:+tp.toFixed(1),
        risk:+risk.toFixed(1),rsi:+R.toFixed(0),fibPct,quality:+quality.toFixed(2),
        waveSize:+waveSize.toFixed(1),outcome});
      lastEntryBar = i;
    }
  }

  // ── إحصائيات ─────────────────────────────────
  const w=results.filter(r=>r.outcome==='WIN').length;
  const l=results.filter(r=>r.outcome==='LOSS').length;
  const t=results.filter(r=>r.outcome==='TIMEOUT').length;
  const wr = w+l>0 ? (w/(w+l)*100).toFixed(1) : 0;
  const pnl= (w*rrMultiple - l).toFixed(1);
  const expectancy = w+l>0 ? ((w/(w+l))*rrMultiple - (l/(w+l))).toFixed(2) : 0;

  console.log(`\n${'═'.repeat(65)}`);
  console.log(`  ${symbol} — Fibonacci OTE (61.8-78.6%) + RSI | RR ${rrMultiple}:1`);
  console.log(`${'═'.repeat(65)}`);

  results.forEach((r,idx) => {
    const icon=r.outcome==='WIN'?'✅':r.outcome==='LOSS'?'❌':'⏳';
    console.log(`${String(idx+1).padStart(3)}. ${icon} ${r.d} ${r.type.padEnd(5)} @ ${String(r.price).padStart(8)} | Fib:${r.fibPct}% RSI:${r.rsi} Q:${r.quality} | SL:${r.sl} TP:${r.tp}`);
  });

  console.log(`\n┌${'─'.repeat(48)}┐`);
  console.log(`│  إجمالي الإشارات:  ${String(results.length).padEnd(28)}│`);
  console.log(`│  ✅ رابح:    ${String(w).padEnd(35)}│`);
  console.log(`│  ❌ خاسر:    ${String(l).padEnd(35)}│`);
  console.log(`│  ⏳ Timeout: ${String(t).padEnd(35)}│`);
  console.log(`│  نسبة النجاح:  ${(wr+'%').padEnd(32)}│`);
  console.log(`│  P&L (${rrMultiple}:1): ${(pnl+'R').padEnd(33)}│`);
  console.log(`│  Expectancy:  ${(expectancy+'R / صفقة').padEnd(33)}│`);
  const goal = parseFloat(wr)>=60 ? '✅ فوق 60%!' : parseFloat(wr)>=50 ? '⚡ مربح (50%+)' : '❌ '+wr+'%';
  console.log(`│  النتيجة:   ${goal.padEnd(36)}│`);
  console.log(`└${'─'.repeat(48)}┘`);

  const Ls=results.filter(r=>r.type==='LONG'), Ss=results.filter(r=>r.type==='SHORT');
  const lw=Ls.filter(r=>r.outcome==='WIN').length, ll=Ls.filter(r=>r.outcome==='LOSS').length;
  const sw=Ss.filter(r=>r.outcome==='WIN').length, sl2=Ss.filter(r=>r.outcome==='LOSS').length;
  console.log(`\n  LONG:  ${Ls.length} | ${lw}W/${ll}L | ${lw+ll>0?(lw/(lw+ll)*100).toFixed(1):0}% نجاح`);
  console.log(`  SHORT: ${Ss.length} | ${sw}W/${sl2}L | ${sw+sl2>0?(sw/(sw+sl2)*100).toFixed(1):0}% نجاح`);

  return {symbol,total:results.length,w,l,t,wr:parseFloat(wr),pnl:parseFloat(pnl),expectancy:parseFloat(expectancy)};
}

const r1 = await backtest('MNQ', 'NQ=F', 1.618);
const r2 = await backtest('MCL', 'CL=F', 1.618);

const tw=r1.w+r2.w, tl=r1.l+r2.l;
console.log(`\n${'═'.repeat(65)}`);
console.log(`  ملخص 2 سنة — Fibonacci OTE Strategy`);
console.log(`${'═'.repeat(65)}`);
console.log(`  MNQ: ${r1.total} إشارة | نجاح: ${r1.wr}% | P&L: +${r1.pnl}R | Exp: ${r1.expectancy}R`);
console.log(`  MCL: ${r2.total} إشارة | نجاح: ${r2.wr}% | P&L: +${r2.pnl}R | Exp: ${r2.expectancy}R`);
console.log(`  الإجمالي: ${tw+tl} صفقة | نجاح: ${(tw/(tw+tl)*100).toFixed(1)}% | ${tw}W/${tl}L`);
