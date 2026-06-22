/**
 * Backtest v3 — توازن بين الجودة والكمية
 * Yahoo Finance: آخر 60 يوم 5M + 1H
 *
 * v1: RSI<50, 4/4 → 44 إشارة، 30.8% (كثير وضعيف)
 * v2: RSI<45, 5/5 → 0 إشارات (صارم جداً)
 * v3: RSI<48, 4/5 + EMA trend + killzone موسّع → هدف 15-20 إشارة بجودة أعلى
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
    low:  q.low[i], close: q.close[i], volume: q.volume[i] || 0
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

// London كامل + NY open (بدون آخر الجلسة)
function inSession(unixTime) {
  const mins = new Date(unixTime*1000).getUTCHours()*60 + new Date(unixTime*1000).getUTCMinutes();
  const london = mins >= 7*60    && mins < 12*60;   // 07:00-12:00 UTC
  const nyOpen  = mins >= 13*60+30 && mins < 17*60; // 13:30-17:00 UTC (فقط الفتح)
  return london || nyOpen;
}

function getHTFBias(bars1h, targetTime) {
  const relevant = bars1h.filter(b => b.time <= targetTime);
  if (relevant.length < 200) return null;
  const closes = relevant.map(b => b.close);
  const e50  = ema(closes, 50);
  const e200 = ema(closes, 200);
  const n = e50.length - 1;
  if (!e50[n] || !e200[n]) return null;
  const gap = Math.abs(e50[n] - e200[n]) / e200[n];
  if (gap < 0.001) return null; // تقاطع هامشي — تجاهل
  return { bull: e50[n] > e200[n], bear: e50[n] < e200[n], gap };
}

function runBacktest(bars5m, bars1h, label, rrMultiple=2.0, holdBars=36) {
  const closes = bars5m.map(b => b.close);
  const atr5   = atrArr(bars5m, 14);
  const rsi5   = rsiArr(bars5m, 14);
  const e21_5  = ema(closes, 21);
  const e50_5  = ema(closes, 50);

  const results = [];
  let lastEntryBar = -12;

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

    if (!inSession(cur.time)) continue;
    if (i - lastEntryBar < 10) continue;

    const htf = getHTFBias(bars1h, cur.time);
    if (!htf) continue;

    // فلتر Spike
    const recentMove = Math.abs(p1.close - p4.close);
    if (recentMove >= A * 2.5) continue;

    // ① EMA trend على 5M — الأهم
    const emaTrendLong  = E21 > E50;
    const emaTrendShort = E21 < E50;

    // ② لمس EMA21
    const touchedBull = [p1,p2,p3,p4].some((b,j) => b.low  <= (e21_5[i-1-j]??E21) * 1.001);
    const touchedBear = [p1,p2,p3,p4].some((b,j) => b.high >= (e21_5[i-1-j]??E21) * 0.999);

    // ③ شمعة ارتداد — جسم > 55%
    const body       = Math.abs(cur.close - cur.open);
    const range      = cur.high - cur.low || 0.01;
    const strongBody  = body / range > 0.55;
    const bouncedBull = cur.close > cur.open && strongBody && cur.close > E21;
    const bouncedBear = cur.close < cur.open && strongBody && cur.close < E21;

    // ④ RSI — 48/52 (توازن بين 50 و45)
    const rsiLong  = R < 48;
    const rsiShort = R > 52;

    // ⑤ HTF قوي
    const htfOk = htf.gap > 0.003; // فارق > 0.3%

    // النقاط (5 شروط)
    const scoreLong  = (emaTrendLong?1:0)  + (touchedBull?1:0) + (bouncedBull?1:0) + (rsiLong?1:0)  + (htfOk?1:0);
    const scoreShort = (emaTrendShort?1:0) + (touchedBear?1:0) + (bouncedBear?1:0) + (rsiShort?1:0) + (htfOk?1:0);

    // 4/5 — يكفي 4 شروط من 5
    let type = null;
    if (htf.bull && emaTrendLong  && scoreLong  >= 4) type = 'LONG';
    else if (htf.bear && emaTrendShort && scoreShort >= 4) type = 'SHORT';
    if (!type) continue;

    const score = type==='LONG' ? scoreLong : scoreShort;

    const price = cur.close;
    let sl, risk;
    if (type === 'LONG') {
      const recentLow  = Math.min(p1.low, p2.low, p3.low, p4.low);
      sl   = Math.min(recentLow, E21) - A * 0.3;
      risk = price - sl;
    } else {
      const recentHigh = Math.max(p1.high, p2.high, p3.high, p4.high);
      sl   = Math.max(recentHigh, E21) + A * 0.3;
      risk = sl - price;
    }

    if (risk < A * 0.4 || risk > A * 2.5) continue;
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
      risk:+risk.toFixed(1), rsi:+R.toFixed(0), score, outcome, barsHeld });
    lastEntryBar = i;
  }

  return { label, results, rrMultiple };
}

function print({ label, results, rrMultiple }) {
  const wins    = results.filter(r=>r.outcome==='WIN').length;
  const losses  = results.filter(r=>r.outcome==='LOSS').length;
  const timeout = results.filter(r=>r.outcome==='TIMEOUT').length;
  const decided = wins + losses;
  const wr      = decided>0 ? (wins/decided*100).toFixed(1) : '0';
  const pnl     = (wins*rrMultiple - losses).toFixed(1);
  const exp     = decided>0 ? ((wins/decided*rrMultiple)-(losses/decided)).toFixed(3) : '0';
  const perWeek = (results.length / (60/7)).toFixed(1);

  console.log(`\n${'═'.repeat(62)}`);
  console.log(`  ${label}`);
  console.log(`${'═'.repeat(62)}`);

  results.forEach((r,idx) => {
    const icon = r.outcome==='WIN'?'✅':r.outcome==='LOSS'?'❌':'⏳';
    console.log(`  ${String(idx+1).padStart(2)}. ${icon} ${r.d} ${r.t} ${r.type.padEnd(5)} @ ${String(r.price).padStart(8)} SL:${r.sl} RSI:${r.rsi} [${r.score}/5]`);
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

  const perTrade_risk = 75;
  const monthlySignals = results.length / 2;
  const monthly$ = (monthlySignals * parseFloat(exp) * perTrade_risk).toFixed(0);

  console.log(`│${'─'.repeat(46)}│`);
  console.log(`│  بمخاطرة $75/صفقة:                           │`);
  console.log(`│  إشارات/شهر تقريباً: ${String(Math.round(monthlySignals)).padEnd(26)}│`);
  console.log(`│  ربح شهري متوقع    : ${('$'+monthly$).padEnd(26)}│`);
  console.log(`└${'─'.repeat(46)}┘`);

  const pass = parseFloat(wr) >= 50;
  console.log(`\n  ${pass ? '✅ مربحة' : '❌ تحتاج تحسين'} — نجاح ${wr}%`);

  if (results.length === 0) {
    console.log('\n  ⚠️  لا إشارات — السوق كان في range أو الشروط لا تتطابق مع هذه الفترة');
  }
}

// ── تشغيل ─────────────────────────────────────────
console.log('\n🔍 جاري جلب بيانات NQ الحقيقية من Yahoo Finance...');

try {
  const [bars5m, bars1h] = await Promise.all([
    fetchYahoo('NQ=F', '5m',  '60d'),
    fetchYahoo('NQ=F', '60m', '60d'),
  ]);

  const from = new Date(bars5m[0].time*1000).toLocaleDateString('ar-DZ');
  const to   = new Date(bars5m[bars5m.length-1].time*1000).toLocaleDateString('ar-DZ');
  console.log(`✅ ${bars5m.length} شمعة 5M | ${bars1h.length} شمعة 1H | ${from} → ${to}\n`);

  print(runBacktest(bars5m, bars1h, 'v3 — RSI 48/52 | EMA trend | 4/5 | RR 2:1',   2.0, 36));
  print(runBacktest(bars5m, bars1h, 'v3 — RSI 48/52 | EMA trend | 4/5 | RR 2.5:1', 2.5, 36));

} catch(e) {
  console.error('\n❌ خطأ:', e.message);
  console.log('   تأكد من اتصال الإنترنت وأنك في: C:\\Users\\nasri\\smc-bot\\smc-bot');
}
