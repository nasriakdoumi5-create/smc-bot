/**
 * ICT Backtest — 730 يوم من 1H NQ
 * الاستراتيجية: FVG + HTF Bias + Killzone + Confirmation
 */

// ── جلب البيانات ─────────────────────────────────
async function fetchBars(symbol, range) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=60m&range=${range}&includePrePost=true`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const j = await r.json();
  const res = j.chart?.result?.[0];
  if (!res) throw new Error('No data');
  const ts = res.timestamp;
  const q  = res.indicators.quote[0];
  return ts.map((t,i) => ({
    time: t, open: q.open[i], high: q.high[i],
    low: q.low[i], close: q.close[i], volume: q.volume[i]
  })).filter(b => b.close != null && b.high != null && b.low != null);
}

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

// ── Killzone: NY 13:30-16:00 UTC أو London 07:00-10:00 UTC ──
function inKillzone(unixTime) {
  const d = new Date(unixTime * 1000);
  const mins = d.getUTCHours()*60 + d.getUTCMinutes();
  const ny     = mins >= 13*60+30 && mins < 16*60;
  const london = mins >= 7*60     && mins < 10*60;
  return ny || london;
}

// ── FVG: Fair Value Gap ───────────────────────────
// Bull FVG: [i-2].high < [i].low
// Bear FVG: [i-2].low  > [i].high
function detectFVG(bars, i, minSize) {
  if (i < 2) return null;
  const b0=bars[i-2], b2=bars[i];
  // Bull FVG
  if (b2.low > b0.high && (b2.low - b0.high) >= minSize) {
    return { type:'BULL', top: b2.low, bot: b0.high, midpoint: (b2.low+b0.high)/2, barIdx: i };
  }
  // Bear FVG
  if (b2.high < b0.low && (b0.low - b2.high) >= minSize) {
    return { type:'BEAR', top: b0.low, bot: b2.high, midpoint: (b0.low+b2.high)/2, barIdx: i };
  }
  return null;
}

// ── الخوارزمية الرئيسية ───────────────────────────
async function backtest(symbol, tickerYahoo, rrMultiple = 1.5, holdBars = 16) {
  console.log(`\n► جاري تحميل بيانات ${symbol}...`);
  const bars = await fetchBars(tickerYahoo, '730d');
  console.log(`  ${bars.length} شمعة — ${new Date(bars[0].time*1000).toLocaleDateString('es-ES',{timeZone:'Europe/Madrid'})} → ${new Date(bars[bars.length-1].time*1000).toLocaleDateString('es-ES',{timeZone:'Europe/Madrid'})}`);

  const closes = bars.map(b => b.close);
  const e50arr = ema(closes, 50);
  const e200arr= ema(closes, 200);
  const e21arr = ema(closes, 21);
  const atrArr = atr(bars, 14);
  const rsiArr = rsi(bars, 14);

  const results = [];
  const activeFVGs = []; // FVGs نشطة تنتظر الدخول
  let lastEntryBar = -8;

  for (let i = 210; i < bars.length - holdBars - 2; i++) {
    const b = bars[i];
    const E50  = e50arr[i],  E200 = e200arr[i];
    const E21  = e21arr[i];
    const A    = atrArr[i],  R = rsiArr[i];

    if (!E50 || !E200 || !E21 || !A) continue;

    const htfBull = E50 > E200;
    const htfBear = E50 < E200;

    // 1) كشف FVG جديد وإضافته للقائمة
    const fvg = detectFVG(bars, i, A * 0.3);
    if (fvg) {
      // فقط FVGs في اتجاه HTF
      if ((fvg.type === 'BULL' && htfBull) || (fvg.type === 'BEAR' && htfBear)) {
        activeFVGs.push({ ...fvg, created: i });
      }
    }

    // تنظيف FVGs القديمة (أكثر من 30 شمعة)
    while (activeFVGs.length > 0 && i - activeFVGs[0].created > 30) {
      activeFVGs.shift();
    }

    // 2) هل نحن في Killzone؟
    if (!inKillzone(b.time)) continue;

    // 3) تجنب الدخول المتكرر
    if (i - lastEntryBar < 6) continue;

    // 4) البحث عن دخول داخل FVG + تأكيد
    for (const fvg of activeFVGs) {
      const price = b.close;

      // السعر يدخل داخل FVG
      if (price < fvg.bot || price > fvg.top) continue;

      const body = Math.abs(b.close - b.open);
      const range = (b.high - b.low) || 0.01;

      let type = null;

      if (fvg.type === 'BULL' && htfBull) {
        // دخول شراء داخل FVG صاعد
        // تأكيد: شمعة صاعدة أو hammer
        const bullCandle = b.close > b.open && body/range > 0.3;
        const hammer     = b.close > b.open && (b.open - b.low) > body * 1.2;
        if ((bullCandle || hammer) && R < 65) type = 'LONG';
      }

      if (fvg.type === 'BEAR' && htfBear) {
        // دخول بيع داخل FVG هابط
        const bearCandle = b.close < b.open && body/range > 0.3;
        const shootstar  = b.close < b.open && (b.high - b.open) > body * 1.2;
        if ((bearCandle || shootstar) && R > 35) type = 'SHORT';
      }

      if (!type) continue;

      // SL: خارج FVG بمسافة 0.25×ATR
      let sl, tp;
      if (type === 'LONG') {
        sl = fvg.bot - A * 0.25;
        if (sl >= price) continue;
      } else {
        sl = fvg.top + A * 0.25;
        if (sl <= price) continue;
      }

      const risk = Math.abs(price - sl);
      if (risk < A * 0.2 || risk > A * 4) continue;

      tp = type === 'LONG' ? price + risk * rrMultiple : price - risk * rrMultiple;

      // محاكاة الصفقة
      let outcome = 'TIMEOUT', barsHeld = 0;
      for (let j = i+1; j < Math.min(i+holdBars, bars.length); j++) {
        const fb = bars[j];
        barsHeld++;
        if (type === 'LONG') {
          if (fb.low  <= sl) { outcome = 'LOSS'; break; }
          if (fb.high >= tp) { outcome = 'WIN';  break; }
        } else {
          if (fb.high >= sl) { outcome = 'LOSS'; break; }
          if (fb.low  <= tp) { outcome = 'WIN';  break; }
        }
      }

      const d = new Date(b.time*1000).toLocaleDateString('es-ES',{
        timeZone:'Europe/Madrid', day:'2-digit', month:'2-digit', year:'2-digit'
      });

      results.push({ d, type, price: +price.toFixed(1), sl: +sl.toFixed(1), tp: +tp.toFixed(1),
        risk: +risk.toFixed(1), rsi: +R.toFixed(0), fvgType: fvg.type, outcome, barsHeld });

      lastEntryBar = i;
      break; // صفقة واحدة لكل شمعة
    }
  }

  // ── إحصائيات ─────────────────────────────────
  const wins    = results.filter(r => r.outcome === 'WIN').length;
  const losses  = results.filter(r => r.outcome === 'LOSS').length;
  const timeout = results.filter(r => r.outcome === 'TIMEOUT').length;
  const decided = wins + losses;
  const wr      = decided > 0 ? (wins/decided*100).toFixed(1) : 0;
  const pnl     = (wins*rrMultiple - losses).toFixed(1);
  const expectancy = decided > 0 ? ((wins/decided*rrMultiple) - (losses/decided)).toFixed(2) : 0;

  console.log(`\n${'═'.repeat(60)}`);
  console.log(`  ${symbol} — ICT FVG Backtest | RR ${rrMultiple}:1`);
  console.log(`${'═'.repeat(60)}`);
  results.slice(-50).forEach((r,i) => {
    const icon = r.outcome==='WIN'?'✅':r.outcome==='LOSS'?'❌':'⏳';
    console.log(`${String(results.length-50+i+1).padStart(3)}. ${icon} ${r.d} ${r.type.padEnd(5)} @ ${String(r.price).padStart(8)} SL:${r.sl} TP:${r.tp} RSI:${r.rsi}`);
  });

  console.log(`\n┌${'─'.repeat(42)}┐`);
  console.log(`│  إجمالي الإشارات:  ${String(results.length).padEnd(22)}│`);
  console.log(`│  ✅ رابح:    ${String(wins).padEnd(29)}│`);
  console.log(`│  ❌ خاسر:    ${String(losses).padEnd(29)}│`);
  console.log(`│  ⏳ Timeout: ${String(timeout).padEnd(29)}│`);
  console.log(`│  نسبة النجاح:  ${(wr+'%').padEnd(26)}│`);
  console.log(`│  P&L: ${(pnl+'R').padEnd(35)}│`);
  console.log(`│  Expectancy/صفقة: ${(expectancy+'R').padEnd(23)}│`);
  console.log(`│  الهدف 60%? ${parseFloat(wr)>=60?'✅ نعم!':'❌ لا — '+wr+'%'}${' '.repeat(parseFloat(wr)>=60?27:22)}│`);
  console.log(`└${'─'.repeat(42)}┘`);

  // تحليل حسب النوع
  const L = results.filter(r=>r.type==='LONG');
  const S = results.filter(r=>r.type==='SHORT');
  const lw = L.filter(r=>r.outcome==='WIN').length, ll = L.filter(r=>r.outcome==='LOSS').length;
  const sw = S.filter(r=>r.outcome==='WIN').length, sl2 = S.filter(r=>r.outcome==='LOSS').length;
  console.log(`\n  LONG:  ${L.length} صفقة | ${lw}W/${ll}L | ${(lw+ll>0?(lw/(lw+ll)*100).toFixed(1):0)}%`);
  console.log(`  SHORT: ${S.length} صفقة | ${sw}W/${sl2}L | ${(sw+sl2>0?(sw/(sw+sl2)*100).toFixed(1):0)}%`);

  return { symbol, total: results.length, wins, losses, wr: parseFloat(wr), pnl: parseFloat(pnl), expectancy: parseFloat(expectancy) };
}

// ── تشغيل الاختبار ────────────────────────────────
const rMNQ = await backtest('MNQ', 'NQ=F',  1.5, 18);
const rMCL = await backtest('MCL', 'CL=F',  1.5, 18);

console.log(`\n${'═'.repeat(60)}`);
console.log(`  ملخص نهائي — اختبار 2 سنة`);
console.log(`${'═'.repeat(60)}`);
console.log(`MNQ: ${rMNQ.total} إشارة | نجاح: ${rMNQ.wr}% | P&L: ${rMNQ.pnl}R | Exp: ${rMNQ.expectancy}R`);
console.log(`MCL: ${rMCL.total} إشارة | نجاح: ${rMCL.wr}% | P&L: ${rMCL.pnl}R | Exp: ${rMCL.expectancy}R`);
const totalW = rMNQ.wins + rMCL.wins, totalL = rMNQ.losses + rMCL.losses;
console.log(`الإجمالي: نجاح ${(totalW/(totalW+totalL)*100).toFixed(1)}% | ${totalW}W/${totalL}L`);
