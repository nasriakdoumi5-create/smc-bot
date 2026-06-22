/**
 * VWAP Bounce Scalping — NQ Futures
 * ══════════════════════════════════════════════
 * HTF (1H): EMA21 vs EMA50 — الاتجاه العام
 * LTF (5M): VWAP Bounce — الدخول
 *
 * المنطق:
 * السوق يرتد دائماً نحو VWAP (المؤسسات تستخدمه كمرجع)
 * → LONG: السعر نزل تحت VWAP ثم ارتد للأعلى + RSI كان < 45
 * → SHORT: السعر صعد فوق VWAP ثم ارتد للأسفل + RSI كان > 55
 *
 * SL: أدنى/أعلى الشمعات الأخيرة - 0.3 ATR
 * TP1: 1.5× risk | TP2: 2.5× risk (حد أقصى ساعتان)
 * ══════════════════════════════════════════════
 */

// ── مؤشرات ─────────────────────────────────────
// ADX: يقيس قوة الاتجاه (لا اتجاهه)
// ADX > 25 = اتجاه قوي | ADX < 20 = سوق متذبذب
function calcADX(bars, period=14) {
  const n = bars.length;
  if (n < period+2) return { adx:20, pdi:15, ndi:15, trend:'RANGING' };
  const trs=[],pdms=[],ndms=[];
  for (let i=1;i<n;i++) {
    const b=bars[i],p=bars[i-1];
    trs.push(Math.max(b.high-b.low,Math.abs(b.high-p.close),Math.abs(b.low-p.close)));
    const up=b.high-p.high, dn=p.low-b.low;
    pdms.push(up>dn&&up>0?up:0);
    ndms.push(dn>up&&dn>0?dn:0);
  }
  const sum=(arr)=>arr.slice(-period).reduce((a,b)=>a+b,0);
  const trS=sum(trs),pdmS=sum(pdms),ndmS=sum(ndms);
  const pdi=trS>0?pdmS/trS*100:15;
  const ndi=trS>0?ndmS/trS*100:15;
  const adx=pdi+ndi>0?Math.abs(pdi-ndi)/(pdi+ndi)*100:20;
  const trend=adx>25?(pdi>ndi?'BULL_TREND':'BEAR_TREND'):'RANGING';
  return { adx:+adx.toFixed(1), pdi:+pdi.toFixed(1), ndi:+ndi.toFixed(1), trend };
}

function ema(arr, period) {
  const k = 2/(period+1), out = [];
  for (let i = 0; i < arr.length; i++) {
    if (i < period-1) { out.push(null); continue; }
    if (i === period-1) { out.push(arr.slice(0,period).reduce((a,b)=>a+b,0)/period); continue; }
    out.push(arr[i]*k + out[i-1]*(1-k));
  }
  return out;
}

function atrCalc(bars, period=14) {
  const out = [];
  for (let i = 0; i < bars.length; i++) {
    const tr = i===0 ? bars[i].high-bars[i].low
      : Math.max(bars[i].high-bars[i].low,
          Math.abs(bars[i].high-bars[i-1].close),
          Math.abs(bars[i].low -bars[i-1].close));
    if (i < period-1) { out.push(null); continue; }
    if (i === period-1) {
      const s = bars.slice(0,period).map((b,j)=> j===0 ? b.high-b.low
        : Math.max(b.high-b.low,Math.abs(b.high-bars[j-1].close),Math.abs(b.low-bars[j-1].close)));
      out.push(s.reduce((a,b)=>a+b,0)/period); continue;
    }
    out.push((out[i-1]*(period-1)+tr)/period);
  }
  return out;
}

function rsiCalc(bars, period=14) {
  const out = new Array(bars.length).fill(50);
  let g=0, l=0;
  for (let i=1; i<=period; i++) { const d=bars[i].close-bars[i-1].close; d>0?(g+=d):(l-=d); }
  g/=period; l/=period;
  out[period] = l===0?100:100-100/(1+g/l);
  for (let i=period+1; i<bars.length; i++) {
    const d=bars[i].close-bars[i-1].close;
    g=(g*(period-1)+Math.max(d,0))/period;
    l=(l*(period-1)+Math.max(-d,0))/period;
    out[i]=l===0?100:100-100/(1+g/l);
  }
  return out;
}

// ── VWAP يومي (يُعاد حسابه كل يوم) ────────────
function calcVWAP(bars) {
  const out = [];
  let cumPV=0, cumV=0, curDay='';
  for (const b of bars) {
    const day = new Date(b.time*1000).toISOString().slice(0,10);
    if (day !== curDay) { cumPV=0; cumV=0; curDay=day; }
    const tp = (b.high+b.low+b.close)/3;
    const v  = b.volume || 1;
    cumPV += tp*v; cumV += v;
    out.push(cumPV/cumV);
  }
  return out;
}

// ── اسم الجلسة الحالية ─────────────────────────
export function currentSession() {
  const mins = new Date().getUTCHours()*60 + new Date().getUTCMinutes();
  if (mins >= 9*60  && mins < 11*60+30)  return '🇬🇧 London KZ';
  if (mins >= 11*60+30 && mins < 13*60+30) return '🔀 London/NY';
  if (mins >= 13*60+30 && mins < 15*60+30) return '🇺🇸 NY Open KZ';
  if (mins >= 7*60 && mins < 9*60)       return '🇬🇧 London Early';
  if (mins >= 1*60  && mins <  4*60)     return '🌏 Asia';
  return '🌙 Off-Hours';
}

// ── فلتر الجلسة — London + NY Open (بدون المساء المتأخر) ─
export function isKillzone() {
  const mins = new Date().getUTCHours()*60 + new Date().getUTCMinutes();
  const london = mins >= 7*60 && mins < 12*60;
  const ny     = mins >= 13*60+30 && mins < 15*60+30;
  return london || ny;
}

// ══ التحليل الرئيسي ════════════════════════════
export function analyzeSimple(bars5m, _bars15m, bars1h) {
  if (!bars5m || bars5m.length < 50) return { error: 'بيانات 5M غير كافية' };
  if (!bars1h  || bars1h.length < 50) return { error: 'بيانات 1H غير كافية' };

  // ══ HTF Bias — 1H (EMA21 vs EMA50) ════════════
  const c1h  = bars1h.map(b=>b.close);
  const e21h = ema(c1h,21);
  const e50h = ema(c1h,50);
  const n1h  = bars1h.length-1;
  const E21h = e21h[n1h], E50h = e50h[n1h];
  if (!E21h || !E50h) return { error: 'EMA 1H لم تكتمل' };

  const htfBull  = E21h > E50h;
  const htfBear  = E21h < E50h;
  const htfTrend = htfBull ? 'BULL↑' : htfBear ? 'BEAR↓' : 'NEUTRAL';
  if (!htfBull && !htfBear) return { htfTrend:'NEUTRAL', signal:null,
    debug:{ reason:'السوق محايد — لا اتجاه واضح على 1H' } };

  // ══ LTF — 5M ════════════════════════════════
  const c5m   = bars5m.map(b=>b.close);
  const vwap5 = calcVWAP(bars5m);
  const atr5  = atrCalc(bars5m,14);
  const rsi5  = rsiCalc(bars5m,14);
  const volArr= bars5m.map(b=>b.volume||0);
  const volEma= ema(volArr,20);

  const n5  = bars5m.length-1;
  const cur = bars5m[n5];
  const p1  = bars5m[n5-1];
  const p2  = bars5m[n5-2];
  const p3  = bars5m[n5-3];
  const p4  = bars5m[n5-4];

  const VWAP   = vwap5[n5];
  const VWAP_1 = vwap5[n5-1];
  const A      = atr5[n5];
  const R      = rsi5[n5];
  const VOL    = volArr[n5];
  const VOLAVG = volEma[n5];

  if (!VWAP || !A) return { error: 'VWAP أو ATR لم يكتمل' };

  const price = cur.close;

  // فلتر Spike
  const recentMove = Math.abs(p1.close-p4.close);
  const noSpike    = recentMove < A*2.5;

  // فلتر تذبذب شديد (أخبار كبيرة)
  const atrAvgVal = ema(atr5.map(v=>v??0),20)[n5];
  const normalATR  = !atrAvgVal || A < atrAvgVal*2.0;

  // فلتر Chop: السوق عرضي إذا ATR أقل من 55% من المتوسط
  const notChoppy  = !atrAvgVal || A > atrAvgVal*0.55;

  // ── Market Regime (ADX على 1H) ──────────────────
  // RANGING: ADX<20 → VWAP Bounce ممتاز (كلا الاتجاهين)
  // BULL_TREND: ADX>25 + PDI>NDI → فقط LONG
  // BEAR_TREND: ADX>25 + NDI>PDI → فقط SHORT
  const regime  = calcADX(bars1h, 14);
  const noCounterTrendLong  = regime.trend !== 'BEAR_TREND'; // لا LONG في bear قوي
  const noCounterTrendShort = regime.trend !== 'BULL_TREND'; // لا SHORT في bull قوي

  // ── زخم 1H: آخر 3 شمعات 1H ──────────────────
  const last3h    = bars1h.slice(-4, -1); // آخر 3 شمعات مكتملة
  const bull1h    = last3h.filter(b=>b.close>b.open).length >= 2;
  const bear1h    = last3h.filter(b=>b.close<b.open).length >= 2;

  // ── VWAP Bounce LONG ──
  // يجب أن يكون السعر قد تجاوز VWAP للأسفل فعلاً (لا مجرد اقتراب)
  const wasBelow    = [p1,p2,p3].some(b => b.low  < VWAP_1);      // تجاوز حقيقي لأسفل
  const touchedDown = Math.min(p1.low,p2.low,p3.low) <= VWAP;     // لمس VWAP بالضبط
  const vwapLong    = (wasBelow || touchedDown) && cur.close > VWAP; // الإغلاق فوق VWAP

  // ── VWAP Bounce SHORT ──
  const wasAbove    = [p1,p2,p3].some(b => b.high > VWAP_1);      // تجاوز حقيقي لأعلى
  const touchedUp   = Math.max(p1.high,p2.high,p3.high) >= VWAP;  // لمس VWAP بالضبط
  const vwapShort   = (wasAbove || touchedUp) && cur.close < VWAP; // الإغلاق تحت VWAP

  // ── شمعة ارتداد قوية — 60% حد أدنى (أعلى من 50%) ──
  const body       = Math.abs(cur.close-cur.open);
  const range      = cur.high-cur.low||0.01;
  const strongBody  = body/range > 0.60;
  const bouncedBull = cur.close>cur.open && strongBody;
  const bouncedBear = cur.close<cur.open && strongBody;

  // ── RSI أكثر صرامة على شمعات التراجع ──
  const minRsi = Math.min(rsi5[n5-1],rsi5[n5-2],rsi5[n5-3]);
  const maxRsi = Math.max(rsi5[n5-1],rsi5[n5-2],rsi5[n5-3]);
  const rsiLong  = minRsi < 45; // كان منخفضاً (أكثر صرامة من 48)
  const rsiShort = maxRsi > 55; // كان مرتفعاً (أكثر صرامة من 52)

  // ── حجم أعلى من المتوسط (تأكيد اهتمام المؤسسات) ──
  const volOk = !VOLAVG || VOL >= VOLAVG*0.85;

  // ══ قرار الدخول ═══════════════════════════════
  // زخم 1H إلزامي: لا LONG إذا 3 شمعات 1H هابطة
  const longOk  = htfBull && vwapLong  && bouncedBull && rsiLong  && noSpike && normalATR && notChoppy && bull1h && noCounterTrendLong;
  const shortOk = htfBear && vwapShort && bouncedBear && rsiShort && noSpike && normalATR && notChoppy && bear1h && noCounterTrendShort;

  let signal = null;

  if (longOk) {
    const recentLow = Math.min(p1.low,p2.low,p3.low);
    const sl   = Math.min(recentLow,VWAP) - A*0.3;
    const risk = price-sl;
    if (risk > A*0.3 && risk < A*2.5) {
      signal = {
        type:   'LONG',
        price:  +price.toFixed(2),
        sl:     +sl.toFixed(2),
        tp1:    +(price+risk*1.5).toFixed(2),
        tp2:    +(price+risk*2.5).toFixed(2),
        risk:   +risk.toFixed(2),
        be:     +(price+risk*0.7).toFixed(2),  // نقطة تحريك SL للدخول
        rsi:    +R.toFixed(1),
        atr:    +A.toFixed(2),
        vwap:   +VWAP.toFixed(2),
        score:  [volOk, body/range>0.70, minRsi<40, regime.trend==='RANGING'].filter(Boolean).length + 1,
        maxScore: 4,
        regime: regime.trend,
        adx:    regime.adx,
        conditions: { htfBull, vwapBounce:vwapLong, bouncedUp:bouncedBull, rsiOk:rsiLong, volOk },
      };
    }
  } else if (shortOk) {
    const recentHigh = Math.max(p1.high,p2.high,p3.high);
    const sl   = Math.max(recentHigh,VWAP) + A*0.3;
    const risk = sl-price;
    if (risk > A*0.3 && risk < A*2.5) {
      signal = {
        type:   'SHORT',
        price:  +price.toFixed(2),
        sl:     +sl.toFixed(2),
        tp1:    +(price-risk*1.5).toFixed(2),
        tp2:    +(price-risk*2.5).toFixed(2),
        risk:   +risk.toFixed(2),
        be:     +(price-risk*0.7).toFixed(2),  // نقطة تحريك SL للدخول
        rsi:    +R.toFixed(1),
        atr:    +A.toFixed(2),
        vwap:   +VWAP.toFixed(2),
        score:  [volOk, body/range>0.70, maxRsi>60, regime.trend==='RANGING'].filter(Boolean).length + 1,
        maxScore: 4,
        regime: regime.trend,
        adx:    regime.adx,
        conditions: { htfBear, vwapBounce:vwapShort, bouncedDown:bouncedBear, rsiOk:rsiShort, volOk },
      };
    }
  }

  const reason = !noSpike                         ? `فلتر Spike — حركة ${recentMove.toFixed(0)} نقطة`
    : !normalATR                                  ? 'تذبذب شديد — خبر كبير محتمل'
    : !notChoppy                                  ? `سوق عرضي — ATR منخفض`
    : !noCounterTrendLong && !noCounterTrendShort ? `ADX ${regime.adx} — ضد الاتجاه القوي`
    : !(vwapLong||vwapShort)                      ? `السعر بعيد عن VWAP (${VWAP.toFixed(0)})`
    : !(bouncedBull||bouncedBear)                 ? 'جسم الشمعة ضعيف (<50%)'
    : !(rsiLong||rsiShort)                        ? `RSI محايد (${minRsi.toFixed(0)}-${maxRsi.toFixed(0)})`
    : 'جميع الشروط متحققة ✅';

  return {
    price:    +price.toFixed(2),
    htfTrend,
    vwap:     +VWAP.toFixed(2),
    rsi:      +R.toFixed(1),
    atr:      +A.toFixed(2),
    signal,
    debug: { htfBull, htfBear, vwapLong, vwapShort, bouncedBull, bouncedBear,
             rsiLong, rsiShort, noSpike, normalATR, minRsi:+minRsi.toFixed(0),
             maxRsi:+maxRsi.toFixed(0), reason },
  };
}
