/**
 * SMC Elite Strategy Engine
 * نفس منطق Pine Script لكن بـ JavaScript خالص
 *
 * 7 شروط — الإشارة عند 5+/7
 * ① HTF Trend  ② Session  ③ Liquidity Sweep
 * ④ Order Block  ⑤ FVG  ⑥ Fibonacci OTE  ⑦ RSI
 */

// ══ EMA ══════════════════════════════════════
export function ema(bars, period, key = 'close') {
  const k = 2 / (period + 1);
  const result = [];
  let prev = null;
  for (const bar of bars) {
    const val = bar[key];
    if (prev === null) { prev = val; result.push(val); continue; }
    prev = val * k + prev * (1 - k);
    result.push(prev);
  }
  return result;
}

// ══ ATR ══════════════════════════════════════
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
  // pad front with nulls
  const pad = bars.length - result.length;
  return [...Array(pad).fill(null), ...result];
}

// ══ RSI ══════════════════════════════════════
export function rsi(bars, period = 14) {
  const result = Array(period).fill(null);
  let gains = 0, losses = 0;
  for (let i = 1; i <= period; i++) {
    const d = bars[i].close - bars[i - 1].close;
    gains += Math.max(d, 0);
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

// ══ Swing Highs/Lows ═════════════════════════
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

// ══ Session Filter ════════════════════════════
function inSession(bar) {
  const h = new Date(bar.time * 1000).getUTCHours();
  // 06:00–20:00 UTC (London pre + London + NY + NY late) — لا جلسة آسيا
  return h >= 6 && h < 20;
}

// ══ Main Analysis ════════════════════════════
export function analyze(bars5m, bars1h, dom = null, of = null) {
  if (bars5m.length < 50 || bars1h.length < 200) {
    return { error: 'not enough data' };
  }

  // ── ① HTF Trend (EMA 50/200 على 1H) ──────
  const ema50h  = ema(bars1h, 50);
  const ema200h = ema(bars1h, 200);
  const lastEma50  = ema50h[ema50h.length - 1];
  const lastEma200 = ema200h[ema200h.length - 1];
  const htfBull = lastEma50 > lastEma200;
  const htfBear = lastEma50 < lastEma200;

  // ── آخر bar ───────────────────────────────
  const n    = bars5m.length;
  const last = bars5m[n - 1];
  const prev = bars5m[n - 2];

  // ── ② Session ─────────────────────────────
  const sessionOk = inSession(last);

  // ── ATR & RSI ─────────────────────────────
  const atrArr = atr(bars5m, 14);
  const rsiArr = rsi(bars5m, 14);
  const curATR = atrArr[n - 1] || 0;
  const curRSI = rsiArr[n - 1] || 50;

  // ── Swing H/L ─────────────────────────────
  const sHighs = swingHighs(bars5m, 10);
  const sLows  = swingLows(bars5m, 10);

  let lastSH = null, lastSL = null;
  for (let i = n - 1; i >= 0; i--) {
    if (lastSH === null && sHighs[i] !== null) lastSH = sHighs[i];
    if (lastSL === null && sLows[i]  !== null) lastSL = sLows[i];
    if (lastSH && lastSL) break;
  }

  // ── ③ Liquidity Sweep ─────────────────────
  // السعر اخترق swing ثم رجع
  let recentSweepUp   = false;
  let recentSweepDown = false;
  for (let i = Math.max(0, n - 20); i < n; i++) {
    const b = bars5m[i];
    if (lastSH && b.high > lastSH && b.close < lastSH) recentSweepUp   = true;
    if (lastSL && b.low  < lastSL && b.close > lastSL) recentSweepDown = true;
  }

  // ── ④ Order Block ─────────────────────────
  let bullOB_top = null, bullOB_bot = null;
  let bearOB_top = null, bearOB_bot = null;

  for (let i = Math.max(1, n - 30); i < n - 1; i++) {
    const b    = bars5m[i];
    const next = bars5m[i + 1];
    const body = Math.abs(b.close - b.open);

    // Bull displacement: شمعة صاعدة قوية > 2× ATR
    const bullDisp = next.close > bars5m[i].high && (next.close - next.open) > curATR * 2;
    if (bullDisp && b.open > b.close) {  // شمعة هبوطية قبله = OB حقيقي
      bullOB_top = b.open;
      bullOB_bot = b.close;
    }

    // Bear displacement: شمعة هابطة قوية > 2× ATR
    const bearDisp = next.close < bars5m[i].low && (next.open - next.close) > curATR * 2;
    if (bearDisp && b.close > b.open) {  // شمعة صاعدة قبله = OB حقيقي
      bearOB_top = b.close;
      bearOB_bot = b.open;
    }
  }

  const inBullOB = bullOB_top && last.close <= bullOB_top && last.close >= bullOB_bot;
  const inBearOB = bearOB_top && last.close <= bearOB_top && last.close >= bearOB_bot;

  // ── ⑤ Fair Value Gap ──────────────────────
  let recentBullFVG = false;
  let recentBearFVG = false;
  for (let i = Math.max(2, n - 15); i < n; i++) {
    const fvgBullSize = bars5m[i].low  - bars5m[i - 2].high;
    const fvgBearSize = bars5m[i - 2].low  - bars5m[i].high;
    if (fvgBullSize > curATR * 0.5) recentBullFVG = true;
    if (fvgBearSize > curATR * 0.5) recentBearFVG = true;
  }

  // ── ⑥ Fibonacci OTE (61.8–78.6%) ─────────
  let fibOTE_bull = false;
  let fibOTE_bear = false;
  if (lastSH && lastSL) {
    const rng  = lastSH - lastSL;
    const p    = last.close;
    fibOTE_bull = p >= (lastSH - rng * 0.786) && p <= (lastSH - rng * 0.618);
    fibOTE_bear = p >= (lastSL + rng * 0.618) && p <= (lastSL + rng * 0.786);
  }

  // ── ⑦ RSI ─────────────────────────────────
  const rsiOversold   = curRSI < 40;
  const rsiOverbought = curRSI > 60;

  // ── ⑧ Order Flow — Delta ──────────────────
  const positiveDelta = of?.positiveDelta ?? false;
  const negativeDelta = of?.negativeDelta ?? false;

  // ── ⑩ Order Flow — Stacked Imbalance (Footprint) ──
  const ofBuyImbalance  = of?.stackedBuy  ?? false;
  const ofSellImbalance = of?.stackedSell ?? false;

  // ── ⑪ Delta Divergence ────────────────────
  const bullDivergence = of?.bullDivergence ?? false;
  const bearDivergence = of?.bearDivergence ?? false;

  // ── Score (10 شروط) ──────────────────────
  const scoreLong  = (htfBull        ? 1 : 0)
                   + (sessionOk       ? 1 : 0)
                   + (recentSweepDown ? 1 : 0)
                   + (inBullOB        ? 1 : 0)
                   + (recentBullFVG   ? 1 : 0)
                   + (fibOTE_bull     ? 1 : 0)
                   + (rsiOversold     ? 1 : 0)
                   + (positiveDelta   ? 1 : 0)
                   + (ofBuyImbalance  ? 1 : 0)
                   + (bullDivergence  ? 1 : 0);

  const scoreShort = (htfBear        ? 1 : 0)
                   + (sessionOk       ? 1 : 0)
                   + (recentSweepUp   ? 1 : 0)
                   + (inBearOB        ? 1 : 0)
                   + (recentBearFVG   ? 1 : 0)
                   + (fibOTE_bear     ? 1 : 0)
                   + (rsiOverbought   ? 1 : 0)
                   + (negativeDelta   ? 1 : 0)
                   + (ofSellImbalance ? 1 : 0)
                   + (bearDivergence  ? 1 : 0);

  // ── SL / TP ───────────────────────────────
  const price = last.close;
  let signal = null;

  if (scoreLong >= 4 && scoreLong > scoreShort) {
    const sl  = bullOB_bot ? bullOB_bot - curATR : price - curATR * 2;
    const risk = Math.abs(price - sl);
    signal = {
      type:   'LONG',
      score:  scoreLong,
      price,
      sl:     +sl.toFixed(2),
      tp1:    +(price + risk * 2).toFixed(2),
      tp2:    +(price + risk * 4).toFixed(2),
      rr:     '2:1',
      atr:    +curATR.toFixed(2),
      rsi:    +curRSI.toFixed(1),
      conditions: { htfBull, sessionOk, recentSweepDown, inBullOB, recentBullFVG, fibOTE_bull, rsiOversold, positiveDelta, ofBuyImbalance, bullDivergence }
    };
  } else if (scoreShort >= 4 && scoreShort > scoreLong) {
    const sl  = bearOB_top ? bearOB_top + curATR : price + curATR * 2;
    const risk = Math.abs(sl - price);
    signal = {
      type:   'SHORT',
      score:  scoreShort,
      price,
      sl:     +sl.toFixed(2),
      tp1:    +(price - risk * 2).toFixed(2),
      tp2:    +(price - risk * 4).toFixed(2),
      rr:     '2:1',
      atr:    +curATR.toFixed(2),
      rsi:    +curRSI.toFixed(1),
      conditions: { htfBear, sessionOk, recentSweepUp, inBearOB, recentBearFVG, fibOTE_bear, rsiOverbought, negativeDelta, ofSellImbalance, bearDivergence }
    };
  }

  return {
    symbol:     'NQ/MNQ',
    price:      +price.toFixed(2),
    time:       new Date(last.time * 1000).toISOString(),
    htfTrend:   htfBull ? 'BULL' : htfBear ? 'BEAR' : 'NEUTRAL',
    session:    sessionOk,
    scoreLong,
    scoreShort,
    signal,
    atr:        +curATR.toFixed(2),
    rsi:        +curRSI.toFixed(1),
  };
}
