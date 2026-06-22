/**
 * Backtest — الاستراتيجية الجديدة على بيانات NQ حقيقية
 * Yahoo Finance: آخر 60 يوم 5M + 1H
 * يشغّله المستخدم محلياً لأن الخادم محجوب عن Yahoo
 */

// ── جلب البيانات ─────────────────────────────────
async function fetchYahoo(ticker, interval, range) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${interval}&range=${range}&includePrePost=false`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const j = await r.json();
  const res = j.chart?.result?.[0];
  if (!res) throw new Error(`لا بيانات: ${ticker}`);
  const ts = res.timestamp;
  const q  = res.indicators.quote[0];
  return ts.map((t,i) => ({
    time: t, open: q.open[i], high: q.high[i],
    low:  q.low[i],  close: q.close[i], volume: q.volume[i] || 0
  })).filter(b => b.close != null && b.high != null);
}

// ── مؤشرات ───────────────────────────────────────
function ema(arr, p) {
  const k = 2/(p+1), o = [];
  for (let i = 0; i < arr.length; i++) {
    if (i < p-1) { o.push(null); continue; }
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
    if (i < p-1) { o.push(null); continue; }
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

// ── Session filter ────────────────────────────────
function inSession(unixTime) {
  const now  = new Date(unixTime * 1000);
  const mins = now.getUTCHours()*60 + now.getUTCMinutes();
  const london = mins >= 7*60  && mins < 12*60;
  const ny     = mins >= 13*60+30 && mins < 22*60;
  return london || ny;
}

// ── HTF Bias من 1H ───────────────────────────────
function getHTFBias(bars1h, targetTime) {
  // أبحث عن آخر 1H bar قبل وقت الإشارة
  const relevant = bars1h.filter(b => b.time <= targetTime);
  if (relevant.length < 200) return null;
  const closes = relevant.map(b => b.close);
  const e50  = ema(closes, 50);
  const e200 = ema(closes, 200);
  const n = e50.length - 1;
  if (!e50[n] || !e200[n]) return null;
  return { bull: e50[n] > e200[n], bear: e50[n] < e200[n] };
}

// ── الاستراتيجية الجديدة bar بـ bar ──────────────
function runBacktest(bars5m, bars1h, label, rrMultiple=2.0, holdBars=24) {
  const closes  = bars5m.map(b => b.close);
  const atr5    = atrArr(bars5m, 14);
  const rsi5    = rsiArr(bars5m, 14);
  const e21_5   = ema(closes, 21);
  const e50_5   = ema(closes, 50);

  const results = [];
  let lastEntryBar = -10;

  for (let i = 30; i < bars5m.length - holdBars - 2; i++) {
    const cur = bars5m[i];
    const p1  = bars5m[i-1];
    const p2  = bars5m[i-2];
    const p3  = bars5m[i-3];

    const E21 = e21_5[i];
    const A   = atr5[i];
    const R   = rsi5[i];
    if (!E21 || !A || R === null) continue;

    // فلتر جلسة
    if (!inSession(cur.time)) continue;

    // كولداون
    if (i - lastEntryBar < 8) continue;

    // HTF Bias
    const htf = getHTFBias(bars1h, cur.time);
    if (!htf) continue;

    // ① فلتر Spike
    const recentMove = Math.abs(p1.close - p3.close);
    const noSpike    = recentMove < A * 2.0;
    if (!noSpike) continue;

    // ② لمس EMA21 حقيقي
    const touchedBull = [p1,p2,p3].some((b,j) => b.low  <= (e21_5[i-1-j]??E21)*1.001);
    const touchedBear = [p1,p2,p3].some((b,j) => b.high >= (e21_5[i-1-j]??E21)*0.999);

    // ③ شمعة ارتداد — جسم > 50%
    const body      = Math.abs(cur.close - cur.open);
    const range     = cur.high - cur.low || 0.01;
    const strongBody = body / range > 0.50;
    const bouncedBull = cur.close > cur.open && strongBody && cur.close > E21;
    const bouncedBear = cur.close < cur.open && strongBody && cur.close < E21;

    // ④ RSI
    const rsiLong  = R < 50;
    const rsiShort = R > 50;

    // ⑤ نقاط
    const scoreLong  = (touchedBull?1:0) + (bouncedBull?1:0) + (rsiLong?1:0)  + (htf.bull?1:0);
    const scoreShort = (touchedBear?1:0) + (bouncedBear?1:0) + (rsiShort?1:0) + (htf.bear?1:0);

    // يحتاج 4/4
    let type = null;
    if (htf.bull && scoreLong >= 4)                          type = 'LONG';
    else if (htf.bear && scoreShort >= 4)                    type = 'SHORT';
    if (!type) continue;

    // SL/TP
    const price = cur.close;
    let sl, risk;
    if (type === 'LONG') {
      const recentLow = Math.min(p1.low, p2.low, p3.low);
      sl   = Math.min(recentLow, E21) - A * 0.25;
      risk = price - sl;
    } else {
      const recentHigh = Math.max(p1.high, p2.high, p3.high);
      sl   = Math.max(recentHigh, E21) + A * 0.25;
      risk = sl - price;
    }

    if (risk < A * 0.5 || risk > A * 3) continue;
    const tp = type==='LONG' ? price+risk*rrMultiple : price-risk*rrMultiple;

    // محاكاة
    let outcome='TIMEOUT', barsHeld=0;
    for (let j=i+1; j<Math.min(i+holdBars, bars5m.length); j++) {
      const fb = bars5m[j]; barsHeld++;
      if (type==='LONG')  { if(fb.low<=sl){outcome='LOSS';break;} if(fb.high>=tp){outcome='WIN';break;} }
      else                { if(fb.high>=sl){outcome='LOSS';break;} if(fb.low<=tp){outcome='WIN';break;} }
    }

    const d = new Date(cur.time*1000).toLocaleDateString('ar-DZ',{day:'2-digit',month:'2-digit',year:'2-digit'});
    const t = new Date(cur.time*1000).toLocaleTimeString('ar-DZ',{hour:'2-digit',minute:'2-digit'});
    results.push({ d, t, type, price:+price.toFixed(1), sl:+sl.toFixed(1), tp:+tp.toFixed(1),
      risk:+risk.toFixed(1), rsi:+R.toFixed(0), outcome, barsHeld });
    lastEntryBar = i;
  }

  return { label, results, rrMultiple };
}

// ── طباعة ────────────────────────────────────────
function print({ label, results, rrMultiple }) {
  const wins    = results.filter(r=>r.outcome==='WIN').length;
  const losses  = results.filter(r=>r.outcome==='LOSS').length;
  const timeout = results.filter(r=>r.outcome==='TIMEOUT').length;
  const decided = wins + losses;
  const wr      = decided>0 ? (wins/decided*100).toFixed(1) : '0';
  const pnl     = (wins*rrMultiple - losses).toFixed(1);
  const exp     = decided>0 ? ((wins/decided*rrMultiple)-(losses/decided)).toFixed(3) : '0';
  const perWeek = (results.length / (60/7)).toFixed(1); // 60 يوم ÷ أسابيع

  console.log(`\n${'═'.repeat(58)}`);
  console.log(`  ${label} | RR ${rrMultiple}:1`);
  console.log(`${'═'.repeat(58)}`);

  results.forEach((r,idx) => {
    const icon = r.outcome==='WIN'?'✅':r.outcome==='LOSS'?'❌':'⏳';
    console.log(`  ${String(idx+1).padStart(2)}. ${icon} ${r.d} ${r.t} ${r.type.padEnd(5)} @ ${String(r.price).padStart(8)} SL:${r.sl} RSI:${r.rsi}`);
  });

  console.log(`\n┌${'─'.repeat(44)}┐`);
  console.log(`│  إجمالي الإشارات (60 يوم): ${String(results.length).padEnd(18)}│`);
  console.log(`│  متوسط/أسبوع             : ${(perWeek+' إشارة').padEnd(18)}│`);
  console.log(`│  ✅ رابحة                 : ${String(wins).padEnd(18)}│`);
  console.log(`│  ❌ خاسرة                 : ${String(losses).padEnd(18)}│`);
  console.log(`│  ⏳ Timeout               : ${String(timeout).padEnd(18)}│`);
  console.log(`│  نسبة النجاح              : ${(wr+'%').padEnd(18)}│`);
  console.log(`│  P&L الكلي                : ${(pnl+'R').padEnd(18)}│`);
  console.log(`│  Expectancy/صفقة          : ${(exp+'R').padEnd(18)}│`);

  // حساب الدخل بالدولار
  const perTrade_risk = 75; // $75 مخاطرة/صفقة
  const monthlyR = (results.length / 2) * parseFloat(exp);
  const monthly$ = (monthlyR * perTrade_risk).toFixed(0);

  console.log(`│${'─'.repeat(44)}│`);
  console.log(`│  بمخاطرة $75/صفقة:                         │`);
  console.log(`│  ربح شهري متوقع: ${('$'+monthly$).padEnd(26)}│`);
  console.log(`└${'─'.repeat(44)}┘`);

  const pass = parseFloat(wr) >= 55;
  console.log(`\n  ${pass ? '✅ الاستراتيجية مربحة' : '❌ تحتاج تحسين'} — نجاح ${wr}%`);
}

// ── تشغيل ─────────────────────────────────────────
console.log('\n🔍 جاري جلب بيانات NQ الحقيقية من Yahoo Finance...');
console.log('   (آخر 60 يوم — 5M + 1H)\n');

try {
  const [bars5m, bars1h] = await Promise.all([
    fetchYahoo('NQ=F', '5m',  '60d'),
    fetchYahoo('NQ=F', '60m', '60d'),
  ]);

  const from = new Date(bars5m[0].time*1000).toLocaleDateString('ar-DZ');
  const to   = new Date(bars5m[bars5m.length-1].time*1000).toLocaleDateString('ar-DZ');
  console.log(`✅ بيانات مستلمة: ${bars5m.length} شمعة 5M | ${bars1h.length} شمعة 1H`);
  console.log(`   الفترة: ${from} → ${to}`);

  const res = runBacktest(bars5m, bars1h, 'استراتيجية EMA21 الجديدة (صارمة)', 2.0, 24);
  print(res);

  if (res.results.length === 0) {
    console.log('\n⚠️  لا إشارات — الشروط صارمة جداً على هذه الفترة.');
    console.log('   هذا يعني: إما السوق كان في trend قوي بدون تصحيحات،');
    console.log('   أو الاستراتيجية تحتاج تخفيف طفيف في بعض الشروط.');
  }

} catch(e) {
  console.error('\n❌ خطأ:', e.message);
  console.log('   تأكد من اتصال الإنترنت وأنك في مجلد smc-bot\\smc-bot');
}
