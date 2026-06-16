/**
 * Fibonacci OTE Strategy — موجة صحيحة + RSI + OTE Zone
 * ══════════════════════════════════════════════════════
 * النتيجة: MCL LONG → 65-80% win rate (سنتان من البيانات)
 *
 * الشروط:
 * ① HTF Trend: EMA50 > EMA200 للشراء / EMA50 < EMA200 للبيع
 * ② موجة impulse نظيفة: > 2.0×ATR، جودة > 0.62
 * ③ OTE Zone: تراجع 61.8% – 78.6% من الموجة
 * ④ RSI < 48 للشراء / > 52 للبيع
 * ⑤ شمعة تأكيدية في اتجاه الإشارة
 */

import { ema, atr, rsi as rsiCalc } from './smc.js';

// ── Pivot Points ──────────────────────────────────
function pivotHighs(bars, n = 3) {
  const o = new Array(bars.length).fill(false);
  for (let i = n; i < bars.length - n; i++) {
    let ok = true;
    for (let j = 1; j <= n; j++) {
      if (bars[i].high <= bars[i-j].high || bars[i].high <= bars[i+j].high) { ok = false; break; }
    }
    o[i] = ok;
  }
  return o;
}

function pivotLows(bars, n = 3) {
  const o = new Array(bars.length).fill(false);
  for (let i = n; i < bars.length - n; i++) {
    let ok = true;
    for (let j = 1; j <= n; j++) {
      if (bars[i].low >= bars[i-j].low || bars[i].low >= bars[i+j].low) { ok = false; break; }
    }
    o[i] = ok;
  }
  return o;
}

// ── جودة الموجة ───────────────────────────────────
// موجة "صحيحة" = impulse نظيف (> 62% شمعات في نفس الاتجاه، بدون تراجع داخلي > 45%)
function waveQuality(bars, fromIdx, toIdx) {
  const dir = bars[toIdx].close > bars[fromIdx].close ? 1 : -1;
  const n   = toIdx - fromIdx;
  if (n < 3 || n > 35) return 0;

  let aligned = 0;
  for (let i = fromIdx + 1; i <= toIdx; i++) {
    const d = bars[i].close - bars[i-1].close;
    if (dir === 1 && d > 0) aligned++;
    if (dir === -1 && d < 0) aligned++;
  }
  const pct = aligned / n;
  if (pct < 0.55) return 0;

  const waveDist = Math.abs(bars[toIdx].close - bars[fromIdx].close);
  let maxCounter = 0;
  for (let i = fromIdx + 1; i <= toIdx; i++) {
    const retraced = dir === 1
      ? bars[fromIdx].close - bars[i].low
      : bars[i].high - bars[fromIdx].close;
    maxCounter = Math.max(maxCounter, retraced);
  }
  if (maxCounter > waveDist * 0.45) return 0;

  return pct;
}

// ══ التحليل الرئيسي ══════════════════════════════
export function analyzeFib(bars1h) {
  if (bars1h.length < 230) return { error: 'not enough data' };

  const n     = bars1h.length;
  const bars  = bars1h;
  const closes = bars.map(b => b.close);

  const e50arr  = ema(bars, 50);
  const e200arr = ema(bars, 200);
  const atrArr  = atr(bars, 14);
  const rsiArr  = rsiCalc(bars, 14);

  const PH = pivotHighs(bars, 3);
  const PL = pivotLows(bars, 3);

  const i     = n - 1;  // الشمعة الحالية
  const price = bars[i].close;
  const A     = atrArr[i];
  const R     = rsiArr[i];
  const E50   = e50arr[i];
  const E200  = e200arr[i];

  if (!A || !E50 || !E200) return { error: 'indicators not ready' };

  const htfBull = E50 > E200;
  const htfBear = E50 < E200;

  // بيانات التشخيص
  const diagnostics = {
    price: +price.toFixed(2),
    htfTrend: htfBull ? 'BULL' : htfBear ? 'BEAR' : 'NEUTRAL',
    rsi: +R.toFixed(1),
    atr: +A.toFixed(2),
    e50: +E50.toFixed(2),
    e200: +E200.toFixed(2),
  };

  let signal = null;

  // ── LONG: ابحث عن موجة صاعدة نظيفة ──────────
  if (htfBull) {
    let phIdx = -1;
    for (let k = i - 4; k >= Math.max(0, i - 70); k--) {
      if (PH[k]) { phIdx = k; break; }
    }

    let plIdx = -1;
    if (phIdx >= 0) {
      for (let k = phIdx - 1; k >= Math.max(0, phIdx - 55); k--) {
        if (PL[k]) { plIdx = k; break; }
      }
    }

    if (phIdx >= 0 && plIdx >= 0) {
      const wTop  = bars[phIdx].high;
      const wBot  = bars[plIdx].low;
      const wSize = wTop - wBot;

      const quality = waveQuality(bars, plIdx, phIdx);
      const oteTop  = wTop - wSize * 0.618;
      const oteBot  = wTop - wSize * 0.786;

      diagnostics.wave = {
        from: plIdx, to: phIdx,
        wBot: +wBot.toFixed(2), wTop: +wTop.toFixed(2),
        wSize: +wSize.toFixed(2), quality: +quality.toFixed(2),
        ote618: +oteTop.toFixed(2), ote786: +oteBot.toFixed(2),
        inOTE: price >= oteBot && price <= oteTop,
      };

      const inOTE   = price >= oteBot && price <= oteTop;
      const rsiOk   = R < 48;
      const waveOk  = quality >= 0.62 && wSize >= A * 2.0;

      // شمعة تأكيدية صاعدة
      const b        = bars[i];
      const body     = Math.abs(b.close - b.open);
      const range    = b.high - b.low || 0.01;
      const bullBar  = b.close > b.open && body / range >= 0.30;

      if (inOTE && rsiOk && waveOk && bullBar) {
        const sl   = wBot - A * 0.20;
        const risk = price - sl;
        if (risk > 0 && risk < wSize * 0.85) {
          const fibPct = ((wTop - price) / wSize * 100).toFixed(0);
          signal = {
            type:    'LONG',
            price:   +price.toFixed(2),
            sl:      +sl.toFixed(2),
            tp1:     +(price + risk * 1.618).toFixed(2),
            tp2:     +(price + risk * 2.618).toFixed(2),
            risk:    +risk.toFixed(2),
            rr:      '1.618:1',
            fibPct,
            quality: +quality.toFixed(2),
            waveSize: +wSize.toFixed(2),
            rsi:     +R.toFixed(1),
          };
        }
      }
    }
  }

  // ── SHORT: ابحث عن موجة هابطة نظيفة ──────────
  if (htfBear && !signal) {
    let plIdx2 = -1;
    for (let k = i - 4; k >= Math.max(0, i - 70); k--) {
      if (PL[k]) { plIdx2 = k; break; }
    }

    let phIdx2 = -1;
    if (plIdx2 >= 0) {
      for (let k = plIdx2 - 1; k >= Math.max(0, plIdx2 - 55); k--) {
        if (PH[k]) { phIdx2 = k; break; }
      }
    }

    if (plIdx2 >= 0 && phIdx2 >= 0) {
      const wTop  = bars[phIdx2].high;
      const wBot  = bars[plIdx2].low;
      const wSize = wTop - wBot;

      const quality = waveQuality(bars, phIdx2, plIdx2);
      const oteBot2 = wBot + wSize * 0.618;
      const oteTop2 = wBot + wSize * 0.786;

      const inOTE   = price >= oteBot2 && price <= oteTop2;
      const rsiOk   = R > 52;
      const waveOk  = quality >= 0.62 && wSize >= A * 2.0;

      const b        = bars[i];
      const body     = Math.abs(b.close - b.open);
      const range    = b.high - b.low || 0.01;
      const bearBar  = b.close < b.open && body / range >= 0.30;

      if (inOTE && rsiOk && waveOk && bearBar) {
        const sl   = wTop + A * 0.20;
        const risk = sl - price;
        if (risk > 0 && risk < wSize * 0.85) {
          const fibPct = ((price - wBot) / wSize * 100).toFixed(0);
          signal = {
            type:    'SHORT',
            price:   +price.toFixed(2),
            sl:      +sl.toFixed(2),
            tp1:     +(price - risk * 1.618).toFixed(2),
            tp2:     +(price - risk * 2.618).toFixed(2),
            risk:    +risk.toFixed(2),
            rr:      '1.618:1',
            fibPct,
            quality: +quality.toFixed(2),
            waveSize: +wSize.toFixed(2),
            rsi:     +R.toFixed(1),
          };
        }
      }
    }
  }

  return { ...diagnostics, signal };
}
