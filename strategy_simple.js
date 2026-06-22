/**
 * EMA21 Bounce — 3 Timeframes
 * ══════════════════════════════════════════════
 * 1H  → الاتجاه العام  (EMA50 vs EMA200)
 * 15M → البنية الوسطى (EMA21 — هل السعر قريب؟)
 * 5M  → الدخول        (لمس + ارتداد + RSI)
 *
 * النقاط (0-5):
 * ① 15M: السعر قرب EMA21 (±0.5%)        +1
 * ② 5M:  لمس EMA21 في آخر 4 شمعات       +1
 * ③ 5M:  شمعة ارتداد قوية (جسم >38%)    +1
 * ④ 5M:  RSI مناسب (<48 شراء / >52 بيع) +1
 * ⑤ PDH/PDL: كسح مستوى أمس + انعكاس    +1 (بونص)
 *
 * إشارة عند نقاط >= 3
 * ══════════════════════════════════════════════
 */

// ── مؤشرات ─────────────────────────────────────
function ema(arr, period) {
  const k = 2 / (period + 1), out = [];
  for (let i = 0; i < arr.length; i++) {
    if (i < period - 1) { out.push(null); continue; }
    if (i === period - 1) { out.push(arr.slice(0, period).reduce((a, b) => a + b, 0) / period); continue; }
    out.push(arr[i] * k + out[i - 1] * (1 - k));
  }
  return out;
}

function atrCalc(bars, period = 14) {
  const out = [];
  for (let i = 0; i < bars.length; i++) {
    const tr = i === 0 ? bars[i].high - bars[i].low
      : Math.max(bars[i].high - bars[i].low,
          Math.abs(bars[i].high - bars[i-1].close),
          Math.abs(bars[i].low  - bars[i-1].close));
    if (i < period - 1) { out.push(null); continue; }
    if (i === period - 1) {
      const s = bars.slice(0, period).map((b, j) => j === 0 ? b.high - b.low
        : Math.max(b.high-b.low, Math.abs(b.high-bars[j-1].close), Math.abs(b.low-bars[j-1].close)));
      out.push(s.reduce((a, b) => a + b, 0) / period); continue;
    }
    out.push((out[i-1] * (period-1) + tr) / period);
  }
  return out;
}

function rsiCalc(bars, period = 14) {
  const out = new Array(bars.length).fill(50);
  let g = 0, l = 0;
  for (let i = 1; i <= period; i++) { const d = bars[i].close - bars[i-1].close; d > 0 ? (g += d) : (l -= d); }
  g /= period; l /= period;
  out[period] = l === 0 ? 100 : 100 - 100 / (1 + g / l);
  for (let i = period + 1; i < bars.length; i++) {
    const d = bars[i].close - bars[i-1].close;
    g = (g * (period-1) + Math.max(d, 0)) / period;
    l = (l * (period-1) + Math.max(-d, 0)) / period;
    out[i] = l === 0 ? 100 : 100 - 100 / (1 + g / l);
  }
  return out;
}

// ── قمة وقاع أمس من بيانات 1H ─────────────────
function getPDHL(bars1h) {
  const byDay = {};
  for (const b of bars1h) {
    const day = new Date(b.time * 1000).toISOString().slice(0, 10);
    if (!byDay[day]) byDay[day] = { high: -Infinity, low: Infinity };
    byDay[day].high = Math.max(byDay[day].high, b.high);
    byDay[day].low  = Math.min(byDay[day].low,  b.low);
  }
  const days = Object.keys(byDay).sort();
  if (days.length < 2) return null;
  const yesterday = days[days.length - 2];
  return { pdh: byDay[yesterday].high, pdl: byDay[yesterday].low };
}

// ── اسم الجلسة الحالية ─────────────────────────
export function currentSession() {
  const mins = new Date().getUTCHours() * 60 + new Date().getUTCMinutes();
  if (mins >= 7*60  && mins < 11*60)       return '🇬🇧 London';
  if (mins >= 11*60 && mins < 13*60+30)    return '🔀 London/NY';
  if (mins >= 13*60+30 && mins < 21*60)    return '🇺🇸 New York';
  if (mins >= 1*60  && mins <  4*60)       return '🌏 Asia';
  return '🌙 Off-Hours';
}

// ══ التحليل الرئيسي ════════════════════════════
export function analyzeSimple(bars5m, bars15m, bars1h) {
  if (!bars5m  || bars5m.length  < 50)  return { error: 'بيانات 5M غير كافية'  };
  if (!bars15m || bars15m.length < 30)  return { error: 'بيانات 15M غير كافية' };
  if (!bars1h  || bars1h.length  < 210) return { error: 'بيانات 1H غير كافية'  };

  // ══ ① HTF Bias — 1H ════════════════════════
  const c1h   = bars1h.map(b => b.close);
  const e50h  = ema(c1h, 50);
  const e200h = ema(c1h, 200);
  const n1h   = bars1h.length - 1;
  const E50   = e50h[n1h], E200 = e200h[n1h];
  if (!E50 || !E200) return { error: 'EMA 1H لم تكتمل' };

  const htfBull = E50 > E200;
  const htfBear = E50 < E200;
  const htfGap  = Math.abs(E50 - E200);
  const htfTrend = htfBull ? (htfGap / E200 > 0.005 ? 'BULL↑↑' : 'BULL') :
                   htfBear ? (htfGap / E200 > 0.005 ? 'BEAR↓↓' : 'BEAR') : 'NEUTRAL';

  if (!htfBull && !htfBear) return { error: null, htfTrend: 'NEUTRAL', signal: null,
    debug: { reason: 'السوق محايد — EMA50 ≈ EMA200' } };

  // PDH / PDL
  const pdhl = getPDHL(bars1h);

  // ══ ② MTF Structure — 15M ════════════════════
  const c15m      = bars15m.map(b => b.close);
  const e21_15arr = ema(c15m, 21);
  const e50_15arr = ema(c15m, 50);
  const n15       = bars15m.length - 1;
  const E21_15    = e21_15arr[n15];
  const E50_15    = e50_15arr[n15];
  const price15   = bars15m[n15].close;

  // السعر في منطقة التصحيح: بين EMA21 و EMA50 على 15M
  const mtfNear = E21_15 && E50_15 && Math.abs(price15 - E21_15) / E21_15 < 0.004;
  const mtfPullback = E21_15 && (
    (htfBull && price15 >= E21_15 * 0.998 && price15 <= E50_15 * 1.01) ||
    (htfBear && price15 <= E21_15 * 1.002 && price15 >= E50_15 * 0.99)
  );

  // ══ ③ LTF Entry — 5M ════════════════════════
  const c5m     = bars5m.map(b => b.close);
  const e21_5arr = ema(c5m, 21);
  const atr5arr  = atrCalc(bars5m, 14);
  const rsi5arr  = rsiCalc(bars5m, 14);

  const n5  = bars5m.length - 1;
  const cur = bars5m[n5];
  const p1  = bars5m[n5 - 1];
  const p2  = bars5m[n5 - 2];
  const p3  = bars5m[n5 - 3];
  const p4  = bars5m[n5 - 4];

  const E21_5 = e21_5arr[n5];
  const A     = atr5arr[n5];
  const R     = rsi5arr[n5];
  if (!E21_5 || !A) return { error: 'مؤشرات 5M لم تكتمل' };

  const price = cur.close;

  // ① فلتر Spike — لا ندخل بعد حركة مفاجئة كبيرة
  const recentMove  = Math.abs(p1.close - p3.close);
  const noSpike     = recentMove < A * 2.0;

  // ② لمس EMA21 حقيقي — الشمعة يجب أن تكون لمست أو تقاطعت مع EMA21
  const touchedBull = [p1, p2, p3].some((b, j) => {
    const e = e21_5arr[n5-1-j] ?? E21_5;
    return b.low <= e * 1.001; // لمس حقيقي من الأعلى
  });
  const touchedBear = [p1, p2, p3].some((b, j) => {
    const e = e21_5arr[n5-1-j] ?? E21_5;
    return b.high >= e * 0.999; // لمس حقيقي من الأسفل
  });

  // ③ شمعة ارتداد قوية — جسم > 50% + إغلاق قوي
  const body      = Math.abs(cur.close - cur.open);
  const range     = cur.high - cur.low || 0.01;
  const strongBody = body / range > 0.50;
  const bouncedBull = cur.close > cur.open && strongBody && cur.close > E21_5;
  const bouncedBear = cur.close < cur.open && strongBody && cur.close < E21_5;

  // ④ RSI — ضعف حقيقي قبل الارتداد
  const rsiLong  = R < 50; // ذروة البيع على 5M
  const rsiShort = R > 50; // ذروة الشراء على 5M

  // ⑤ PDH/PDL sweep — بونص عالي الجودة
  let pdhSweep = false, pdlSweep = false;
  if (pdhl) {
    pdlSweep = [p1, p2, p3].some(b => b.low < pdhl.pdl) && cur.close > pdhl.pdl;
    pdhSweep = [p1, p2, p3].some(b => b.high > pdhl.pdh) && cur.close < pdhl.pdh;
  }

  // ══ النقاط (5 شروط) ══════════════════════════
  const scoreLong  = (mtfNear||mtfPullback?1:0) + (touchedBull?1:0) + (bouncedBull?1:0) + (rsiLong?1:0)  + (pdlSweep?1:0);
  const scoreShort = (mtfNear||mtfPullback?1:0) + (touchedBear?1:0) + (bouncedBear?1:0) + (rsiShort?1:0) + (pdhSweep?1:0);

  // الحد الأدنى 4/5 + لا Spike
  const longOk  = htfBull && scoreLong  >= 4 && noSpike;
  const shortOk = htfBear && scoreShort >= 4 && noSpike;

  // ══ بناء الإشارة ════════════════════════════
  let signal = null;

  if (longOk && (!shortOk || scoreLong >= scoreShort)) {
    const recentLow = Math.min(p1.low, p2.low, p3.low);
    const sl   = Math.min(recentLow, E21_5) - A * 0.25;
    const risk = price - sl;
    // نسبة خطر معقولة: 0.5 إلى 3× ATR
    if (risk > A * 0.5 && risk < A * 3) {
      signal = {
        type:     'LONG',
        score:    scoreLong,
        maxScore: 5,
        price:    +price.toFixed(2),
        sl:       +sl.toFixed(2),
        tp1:      +(price + risk * 2).toFixed(2),
        tp2:      +(price + risk * 3.5).toFixed(2),
        risk:     +risk.toFixed(2),
        rsi:      +R.toFixed(1),
        atr:      +A.toFixed(2),
        e21_5m:   +E21_5.toFixed(2),
        e21_15m:  E21_15 ? +E21_15.toFixed(2) : null,
        pdh:      pdhl?.pdh ? +pdhl.pdh.toFixed(2) : null,
        pdl:      pdhl?.pdl ? +pdhl.pdl.toFixed(2) : null,
        conditions: { htfBull, mtfNear: mtfNear||mtfPullback, touchedEma21: touchedBull, bouncedUp: bouncedBull, rsiOk: rsiLong, pdlSweep },
      };
    }
  } else if (shortOk) {
    const recentHigh = Math.max(p1.high, p2.high, p3.high);
    const sl   = Math.max(recentHigh, E21_5) + A * 0.25;
    const risk = sl - price;
    if (risk > A * 0.5 && risk < A * 3) {
      signal = {
        type:     'SHORT',
        score:    scoreShort,
        maxScore: 5,
        price:    +price.toFixed(2),
        sl:       +sl.toFixed(2),
        tp1:      +(price - risk * 2).toFixed(2),
        tp2:      +(price - risk * 3.5).toFixed(2),
        risk:     +risk.toFixed(2),
        rsi:      +R.toFixed(1),
        atr:      +A.toFixed(2),
        e21_5m:   +E21_5.toFixed(2),
        e21_15m:  E21_15 ? +E21_15.toFixed(2) : null,
        pdh:      pdhl?.pdh ? +pdhl.pdh.toFixed(2) : null,
        pdl:      pdhl?.pdl ? +pdhl.pdl.toFixed(2) : null,
        conditions: { htfBear, mtfNear: mtfNear||mtfPullback, touchedEma21: touchedBear, bouncedDown: bouncedBear, rsiOk: rsiShort, pdhSweep },
      };
    }
  }

  const reason = !htfBull && !htfBear         ? 'لا اتجاه HTF'
    : !noSpike                                 ? `فلتر Spike — حركة مفاجئة ${recentMove.toFixed(0)} نقطة`
    : !(touchedBull || touchedBear)            ? `لم يلمس EMA21 (${E21_5?.toFixed(0)})`
    : !(bouncedBull || bouncedBear)            ? 'جسم الشمعة ضعيف (<50%)'
    : !(rsiLong || rsiShort)                   ? `RSI محايد (${R.toFixed(0)}) — يحتاج <50 أو >50`
    : (scoreLong < 4 && scoreShort < 4)        ? `النقاط غير كافية (L:${scoreLong} S:${scoreShort}/5)`
    : 'جميع الشروط متحققة';

  return {
    price:    +price.toFixed(2),
    htfTrend,
    e21_5m:   +E21_5.toFixed(2),
    e21_15m:  E21_15 ? +E21_15.toFixed(2) : null,
    rsi:      +R.toFixed(1),
    atr:      +A.toFixed(2),
    scoreLong, scoreShort,
    pdh: pdhl?.pdh ? +pdhl.pdh.toFixed(2) : null,
    pdl: pdhl?.pdl ? +pdhl.pdl.toFixed(2) : null,
    signal,
    debug: { htfBull, htfBear, mtfNear, touchedBull, touchedBear,
             bouncedBull, bouncedBear, rsiLong, rsiShort, strongBody,
             noSpike, pdlSweep, pdhSweep, reason },
  };
}
