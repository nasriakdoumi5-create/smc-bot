/**
 * 14:00 UTC Reversal — Last Wave
 * MNQ 5M | صفقة واحدة يومياً
 */

export function analyze1400(bars5m, lookback = 11, rrRatio = 1.5) {
  const n = bars5m.length;
  if (n < lookback + 3) return { signal: null, error: 'بيانات غير كافية' };

  const refBar      = bars5m[n - 2];            // close[1]        ≈ 13:55
  const lookbackBar = bars5m[n - 2 - lookback]; // close[lookback] ≈ 13:00
  const entryPrice  = bars5m[n - 1].close;      // سعر الدخول

  const lastWaveUp   = refBar.close > lookbackBar.close;
  const lastWaveDown = refBar.close < lookbackBar.close;
  const waveSize     = Math.abs(refBar.close - lookbackBar.close);

  if (waveSize <= 5) return { signal: null, reason: `موجة صغيرة: ${waveSize.toFixed(1)}` };

  const recentBars = bars5m.slice(n - lookback - 1);
  const swingHigh  = Math.max(...recentBars.map(b => b.high));
  const swingLow   = Math.min(...recentBars.map(b => b.low));

  if (lastWaveUp) {
    const tpDist = entryPrice - swingLow;
    if (tpDist <= 0) return { signal: null, reason: 'TP سالب' };
    const slDist = tpDist / rrRatio;
    return {
      signal: {
        type:     'SHORT',
        price:    +entryPrice.toFixed(2),
        sl:       +(entryPrice + slDist).toFixed(2),
        tp:       +(entryPrice - tpDist).toFixed(2),
        waveSize: Math.round(waveSize),
        rr:       rrRatio,
      }
    };
  }

  if (lastWaveDown) {
    const tpDist = swingHigh - entryPrice;
    if (tpDist <= 0) return { signal: null, reason: 'TP سالب' };
    const slDist = tpDist / rrRatio;
    return {
      signal: {
        type:     'LONG',
        price:    +entryPrice.toFixed(2),
        sl:       +(entryPrice - slDist).toFixed(2),
        tp:       +(entryPrice + tpDist).toFixed(2),
        waveSize: Math.round(waveSize),
        rr:       rrRatio,
      }
    };
  }

  return { signal: null, reason: 'لا موجة واضحة' };
}
