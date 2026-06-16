/**
 * Utility functions — EMA / ATR / RSI / Swing H/L
 * (مكتبة أدوات — بدون استراتيجية)
 */

export function ema(bars, period, key = 'close') {
  const k = 2 / (period + 1);
  let prev = null;
  return bars.map(bar => {
    const val = bar[key];
    if (prev === null) { prev = val; return val; }
    prev = val * k + prev * (1 - k);
    return prev;
  });
}

export function atr(bars, period = 14) {
  const trs = bars.map((b, i) => {
    if (i === 0) return b.high - b.low;
    const prev = bars[i - 1].close;
    return Math.max(b.high - b.low, Math.abs(b.high - prev), Math.abs(b.low - prev));
  });
  const result = [];
  let avg = trs.slice(0, period).reduce((a, b) => a + b, 0) / period;
  result.push(avg);
  for (let i = period; i < trs.length; i++) {
    avg = (avg * (period - 1) + trs[i]) / period;
    result.push(avg);
  }
  return [...Array(bars.length - result.length).fill(null), ...result];
}

export function rsi(bars, period = 14) {
  const result = Array(period).fill(null);
  let gains = 0, losses = 0;
  for (let i = 1; i <= period; i++) {
    const d = bars[i].close - bars[i - 1].close;
    gains  += Math.max(d, 0);
    losses += Math.max(-d, 0);
  }
  let avgGain = gains / period;
  let avgLoss = losses / period;
  result.push(100 - 100 / (1 + avgGain / (avgLoss || 0.001)));
  for (let i = period + 1; i < bars.length; i++) {
    const d = bars[i].close - bars[i - 1].close;
    avgGain = (avgGain * (period - 1) + Math.max(d, 0)) / period;
    avgLoss = (avgLoss * (period - 1) + Math.max(-d, 0)) / period;
    result.push(100 - 100 / (1 + avgGain / (avgLoss || 0.001)));
  }
  return result;
}

export function swingHighs(bars, len = 10) {
  return bars.map((_, i) => {
    if (i < len || i >= bars.length - len) return null;
    const h = bars[i].high;
    for (let j = i - len; j <= i + len; j++) {
      if (j !== i && bars[j].high >= h) return null;
    }
    return h;
  });
}

export function swingLows(bars, len = 10) {
  return bars.map((_, i) => {
    if (i < len || i >= bars.length - len) return null;
    const l = bars[i].low;
    for (let j = i - len; j <= i + len; j++) {
      if (j !== i && bars[j].low <= l) return null;
    }
    return l;
  });
}
