/**
 * Backtest v4 — إعادة بناء كاملة
 *
 * المشكلة المكتشفة في v1-v3:
 * ① HTF (EMA50/200 على 1H) بطيء جداً — يقول "bull" حتى بعد أسابيع من الانهيار
 * ② RSI كان اختيارياً فجاء LONG بـ RSI:65 (ذروة شراء)
 * ③ 139 إشارة في 60 يوم = كمية بلا جودة
 *
 * الحل v4:
 * ① HTF سريع: السعر > EMA21(1H) + EMA21(1H) > EMA50(1H) معاً
 *    → لو نزل السعر تحت EMA21 على 1H، نوقف LONG فوراً
 * ② RSI مطلوب دائماً: < 50 للشراء / > 50 للبيع (ليس اختيارياً)
 * ③ Cooldown زمني: 45 دقيقة حقيقية (ليس عد شمعات)
 * ④ حد أقصى: إشارة واحدة فقط كل 2 ساعة
 * ⑤ 4 شروط إلزامية كلها (ليس 4 من 5)
 */

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
    low:  q.low[i], close: q.close[i], volume: q.volume[i]||0
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
    Math.max(b.high-b.low,Math.abs(b.high-bars[i-1].close),Math.abs(b.low-bars[i-1].close)));
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
  const london = mins >= 7*60    && mins < 12*60;
  const nyOpen  = mins >= 13*60+30 && mins < 17*60;
  return london || nyOpen;
}

// ── HTF سريع: يوقف LONG فوراً لو السعر نزل تحت EMA21(1H) ──
function buildHTFCache(bars1h) {
  const closes = bars1h.map(b => b.close);
  const e21    = ema(closes, 21);
  const e50    = ema(closes, 50);
  // نبني خريطة timestamp → bias
  const map = new Map();
  for (let i = 50; i < bars1h.length; i++) {
    const price = bars1h[i].close;
    const E21   = e21[i], E50 = e50[i];
    if (!E21 || !E50) { map.set(bars1h[i].time, null); continue; }
    const bull = price > E21 && E21 > E50;  // سعر فوق EMA21، وEMA21 فوق EMA50
    const bear = price < E21 && E21 < E50;  // سعر تحت EMA21، وEMA21 تحت EMA50
    map.set(bars1h[i].time, bull ? 'BULL' : bear ? 'BEAR' : null);
  }
  return map;
}

function getHTFBias(htfMap, bars1h, targetTime) {
  // نأخذ آخر 1H bar قبل وقت الإشارة
  let best = null;
  for (const b of bars1h) {
    if (b.time <= targetTime) best = b.time;
    else break;
  }
  return best ? (htfMap.get(best) ?? null) : null;
}

function runBacktest(bars5m, bars1h, label, rrMultiple=2.0, holdBars=36) {
  const closes = bars5m.map(b => b.close);
  const atr5   = atrArr(bars5m, 14);
  const rsi5   = rsiArr(bars5m, 14);
  const e21_5  = ema(closes, 21);
  const e50_5  = ema(closes, 50);

  const htfMap = buildHTFCache(bars1h);

  const results = [];
  let lastSignalTime = 0;  // timestamp حقيقي للـ cooldown
  const COOLDOWN_SEC = 45 * 60; // 45 دقيقة

  for (let i = 55; i < bars5m.length - holdBars - 2; i++) {
    const cur = bars5m[i];
    const p1  = bars5m[i-1];
    const p2  = bars5m[i-2];
    const p3  = bars5m[i-3];
    const p4  = bars5m[i-4];

    const E21 = e21_5[i];
    const E50 = e50_5[i];
    const A   = atr5[i];
    const R   = rsi5[i];
    if (!E21 || !E50 || !A) continue;

    // ① جلسة
    if (!inSession(cur.time)) continue;

    // ② Cooldown زمني (45 دقيقة)
    if (cur.time - lastSignalTime < COOLDOWN_SEC) continue;

    // ③ HTF سريع
    const htf = getHTFBias(htfMap, bars1h, cur.time);
    if (!htf) continue;

    // ④ فلتر Spike
    const recentMove = Math.abs(p1.close - p4.close);
    if (recentMove >= A * 2.5) continue;

    // ── شروط LONG (كلها إلزامية) ──
    const emaTrendLong  = E21 > E50;
    const touchedBull   = [p1,p2,p3,p4].some((b,j) => b.low  <= (e21_5[i-1-j]??E21)*1.001);
    const body_r        = cur.high - cur.low || 0.01;
    const body_b        = Math.abs(cur.close - cur.open);
    const bouncedBull   = cur.close > cur.open && body_b/body_r > 0.55 && cur.close > E21;
    const rsiLong       = R < 50; // إلزامي

    // ── شروط SHORT (كلها إلزامية) ──
    const emaTrendShort = E21 < E50;
    const touchedBear   = [p1,p2,p3,p4].some((b,j) => b.high >= (e21_5[i-1-j]??E21)*0.999);
    const bouncedBear   = cur.close < cur.open && body_b/body_r > 0.55 && cur.close < E21;
    const rsiShort      = R > 50;

    // كل الشروط مطلوبة
    let type = null;
    if (htf==='BULL' && emaTrendLong  && touchedBull  && bouncedBull  && rsiLong)  type = 'LONG';
    else if (htf==='BEAR' && emaTrendShort && touchedBear  && bouncedBear  && rsiShort) type = 'SHORT';
    if (!type) continue;

    const price = cur.close;
    let sl, risk;
    if (type==='LONG') {
      const recentLow  = Math.min(p1.low,p2.low,p3.low,p4.low);
      sl   = Math.min(recentLow, E21) - A*0.3;
      risk = price - sl;
    } else {
      const recentHigh = Math.max(p1.high,p2.high,p3.high,p4.high);
      sl   = Math.max(recentHigh, E21) + A*0.3;
      risk = sl - price;
    }

    if (risk < A*0.4 || risk > A*2.5) continue;
    const tp = type==='LONG' ? price+risk*rrMultiple : price-risk*rrMultiple;

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
    lastSignalTime = cur.time;
  }

  return { label, results, rrMultiple };
}

function print({ label, results, rrMultiple }) {
  const wins    = results.filter(r=>r.outcome==='WIN').length;
  const losses  = results.filter(r=>r.outcome==='LOSS').length;
  const timeout = results.filter(r=>r.outcome==='TIMEOUT').length;
  const decided = wins+losses;
  const wr      = decided>0 ? (wins/decided*100).toFixed(1) : '0';
  const pnl     = (wins*rrMultiple - losses).toFixed(1);
  const exp     = decided>0 ? ((wins/decided*rrMultiple)-(losses/decided)).toFixed(3) : '0';
  const perWeek = (results.length/(60/7)).toFixed(1);

  console.log(`\n${'═'.repeat(64)}`);
  console.log(`  ${label}`);
  console.log(`${'═'.repeat(64)}`);

  results.forEach((r,idx) => {
    const icon = r.outcome==='WIN'?'✅':r.outcome==='LOSS'?'❌':'⏳';
    console.log(`  ${String(idx+1).padStart(2)}. ${icon} ${r.d} ${r.t} ${r.type.padEnd(5)} @ ${String(r.price).padStart(8)} SL:${r.sl} RSI:${r.rsi}`);
  });

  console.log(`\n┌${'─'.repeat(46)}┐`);
  console.log(`│  إجمالي الإشارات (60 يوم): ${String(results.length).padEnd(20)}│`);
  console.log(`│  متوسط/أسبوع             : ${(perWeek+' إشارة').padEnd(20)}│`);
  console.log(`│  ✅ رابحة                 : ${String(wins).padEnd(20)}│`);
  console.log(`│  ❌ خاسرة                 : ${String(losses).padEnd(20)}│`);
  console.log(`│  ⏳ Timeout               : ${String(timeout).padEnd(20)}│`);
  console.log(`│  نسبة النجاح              : ${(wr+'%').padEnd(20)}│`);
  console.log(`│  P&L الكلي                : ${(pnl+'R').padEnd(20)}│`);
  console.log(`│  Expectancy/صفقة          : ${(exp+'R').padEnd(20)}│`);

  const monthlySignals = results.length/2;
  const monthly$ = (monthlySignals * parseFloat(exp) * 75).toFixed(0);
  console.log(`│${'─'.repeat(46)}│`);
  console.log(`│  بمخاطرة $75/صفقة:                           │`);
  console.log(`│  إشارات/شهر تقريباً: ${String(Math.round(monthlySignals)).padEnd(26)}│`);
  console.log(`│  ربح شهري متوقع    : ${('$'+monthly$).padEnd(26)}│`);
  console.log(`└${'─'.repeat(46)}┘`);

  const pass = parseFloat(wr) >= 50;
  console.log(`\n  ${pass?'✅ مربحة':'❌ تحتاج تحسين'} — نجاح ${wr}%\n`);

  if (results.length===0) {
    console.log('  ⚠️  لا إشارات — النزول الحاد أوقف كل الـ LONG، والسوق لم يكن في bear كاف للـ SHORT');
  }
}

console.log('\n🔍 جاري جلب بيانات NQ الحقيقية...\n');

try {
  const [bars5m, bars1h] = await Promise.all([
    fetchYahoo('NQ=F','5m','60d'),
    fetchYahoo('NQ=F','60m','60d'),
  ]);

  const from = new Date(bars5m[0].time*1000).toLocaleDateString('ar-DZ');
  const to   = new Date(bars5m[bars5m.length-1].time*1000).toLocaleDateString('ar-DZ');
  console.log(`✅ ${bars5m.length} شمعة 5M | ${bars1h.length} شمعة 1H | ${from} → ${to}\n`);

  print(runBacktest(bars5m, bars1h, 'v4 — HTF سريع | شروط إلزامية | Cooldown 45min | RR 2:1',   2.0, 36));
  print(runBacktest(bars5m, bars1h, 'v4 — HTF سريع | شروط إلزامية | Cooldown 45min | RR 2.5:1', 2.5, 36));

} catch(e) {
  console.error('\n❌ خطأ:', e.message);
  console.log('   في مجلد: C:\\Users\\nasri\\smc-bot\\smc-bot');
}
