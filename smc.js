/**
 * SMC Elite Strategy Engine v2
 * 9 شروط — الإشارة عند 6+/9
 * ① HTF Trend  ② Session  ③ Liquidity Sweep
 * ④ Order Block  ⑤ FVG  ⑥ Fibonacci OTE  ⑦ RSI
 * ⑧ Volume Spike  ⑨ Momentum Rejection
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
  const d = new Date(bar.time * 1000);
  const h = d.getUTCHours();
  const m = d.getUTCMinutes();
  const mins = h * 60 + m;
  const london = mins >= 8 * 60  && mins < 12 * 60;
  const ny     = mins >= 13 * 60 + 30 && mins < 16 * 60;
  return london || ny;
}

// ══ Volume Spike ══════════════════════════════
function volumeSpike(bars, n, lookback = 20) {
  const recent = bars.slice(Math.max(0, n - lookback), n);
  const avgVol = recent.reduce((s, b) => s + (b.volume || 0), 0) / recent.length;
  const curVol = bars[n - 1].volume || 0;
  // إذا لا توجد بيانات حجم (Futures على Yahoo) — نعتبره محايداً true
  if (avgVol === 0) return { spike: true, ratio: 1, noData: true };
  return { spike: curVol > avgVol * 1.5, ratio: +(curVol / avgVol).toFixed(1), noData: false };
}

// ══ Momentum Rejection ═══════════════════════
// شمعة هابطة/صاعدة قوية بعد لمس مستوى = رفض
function momentumRejection(bars, n, curATR) {
  const last = bars[n - 1];
  const prev = bars[n - 2];
  const body     = Math.abs(last.close - last.open);
  const bodyPrev = Math.abs(prev.close - prev.open);

  // رفض هبوطي: شمعة هابطة بعد صعود — جسم كبير
  const bearRej = last.close < last.open && body > curATR * 0.6 && prev.close > prev.open;
  // رفض صاعدي: شمعة صاعدة بعد هبوط — جسم كبير
  const bullRej = last.close > last.open && body > curATR * 0.6 && prev.close < prev.open;

  return { bearRej, bullRej };
}

// ══ Resistance/Support Touch ═════════════════
// هل السعر لمس مستوى مقاومة/دعم مهم
function nearLevel(price, level, atrVal) {
  return Math.abs(price - level) < atrVal * 0.5;
}

// ══ 1M Entry Confirmation ═════════════════════
// تأكيد الدخول على الدقيقة: شمعة رفض + اتجاه متوافق
export function confirm1m(bars1m, direction) {
  if (!bars1m || bars1m.length < 5) return { confirmed: true, reason: 'no 1m data' };
  const n    = bars1m.length;
  const last = bars1m[n - 1];
  const prev = bars1m[n - 2];
  const body = Math.abs(last.close - last.open);
  const range = last.high - last.low || 1;

  if (direction === 'LONG') {
    // شمعة صاعدة + جسم > 40% من النطاق + إغلاق فوق المنتصف
    const bullCandle = last.close > last.open;
    const strongBody = body / range > 0.4;
    const aboveMid   = last.close > (last.high + last.low) / 2;
    const confirmed  = bullCandle && strongBody && aboveMid;
    return { confirmed, reason: confirmed ? '1M شمعة صاعدة قوية' : '1M لا تأكيد صاعد بعد' };
  } else {
    // شمعة هابطة + جسم > 40% + إغلاق تحت المنتصف
    const bearCandle = last.close < last.open;
    const strongBody = body / range > 0.4;
    const belowMid   = last.close < (last.high + last.low) / 2;
    const confirmed  = bearCandle && strongBody && belowMid;
    return { confirmed, reason: confirmed ? '1M شمعة هابطة قوية' : '1M لا تأكيد هابط بعد' };
  }
}

// ══ Main Analysis ════════════════════════════
export function analyze(bars5m, bars1h) {
  if (bars5m.length < 50 || bars1h.length < 200) {
    return { error: 'not enough data' };
  }

  // ── ① HTF Trend ───────────────────────────
  const ema50h  = ema(bars1h, 50);
  const ema200h = ema(bars1h, 200);
  const ema21h  = ema(bars1h, 21);
  const lastEma50  = ema50h[ema50h.length - 1];
  const lastEma200 = ema200h[ema200h.length - 1];
  const lastEma21  = ema21h[ema21h.length - 1];
  const htfBull = lastEma50 > lastEma200;
  const htfBear = lastEma50 < lastEma200;
  // تأكيد إضافي: EMA21 يؤكد الاتجاه
  const htfBullStrong = htfBull && lastEma21 > lastEma50;
  const htfBearStrong = htfBear && lastEma21 < lastEma50;

  // ── آخر bar ───────────────────────────────
  const n    = bars5m.length;
  const last = bars5m[n - 1];
  const prev = bars5m[n - 2];

  // ── ② Session ─────────────────────────────
  const sessionOk = inSession(last);

  // ── ATR و RSI ─────────────────────────────
  const atrArr   = atr(bars5m, 14);
  const atr1hArr = atr(bars1h, 14);
  const rsiArr   = rsi(bars5m, 14);
  const curATR   = atrArr[n - 1] || 0;
  const atr1h    = atr1hArr[atr1hArr.length - 1] || curATR * 3;
  const curRSI   = rsiArr[n - 1] || 50;

  // ── Swing H/L ─────────────────────────────
  const sHighs = swingHighs(bars5m, 10);
  const sLows  = swingLows(bars5m, 10);

  let lastSH = null, lastSL = null;
  let lastSHIdx = -1, lastSLIdx = -1;
  for (let i = n - 1; i >= 0; i--) {
    if (lastSH === null && sHighs[i] !== null) { lastSH = sHighs[i]; lastSHIdx = i; }
    if (lastSL === null && sLows[i]  !== null) { lastSL = sLows[i];  lastSLIdx = i; }
    if (lastSH && lastSL) break;
  }

  // ── ③ Liquidity Sweep ─────────────────────
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
    const bullDisp = next.close > bars5m[i].high && (next.close - next.open) > curATR * 1.5;
    if (bullDisp && b.open > b.close) { bullOB_top = b.open; bullOB_bot = b.close; }
    const bearDisp = next.close < bars5m[i].low && (next.open - next.close) > curATR * 1.5;
    if (bearDisp && b.close > b.open) { bearOB_top = b.close; bearOB_bot = b.open; }
  }

  const inBullOB = bullOB_top && last.close <= bullOB_top && last.close >= bullOB_bot;
  const inBearOB = bearOB_top && last.close <= bearOB_top && last.close >= bearOB_bot;

  // ── ⑤ Fair Value Gap ──────────────────────
  let recentBullFVG = false;
  let recentBearFVG = false;
  for (let i = Math.max(2, n - 15); i < n; i++) {
    if (bars5m[i].low  > bars5m[i - 2].high) recentBullFVG = true;
    if (bars5m[i].high < bars5m[i - 2].low)  recentBearFVG = true;
  }

  // ── ⑥ Fibonacci OTE ───────────────────────
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

  // ── ⑧ Volume Spike ────────────────────────
  const volData = volumeSpike(bars5m, n);
  const volSpike = volData.spike;

  // ── ⑨ Momentum Rejection ──────────────────
  const momentum = momentumRejection(bars5m, n, curATR);
  const bullMomentum = momentum.bullRej;
  const bearMomentum = momentum.bearRej;

  // ── Score (9 شروط) ────────────────────────
  const scoreLong  = (htfBull          ? 1 : 0)
                   + (sessionOk         ? 1 : 0)
                   + (recentSweepDown   ? 1 : 0)
                   + (inBullOB          ? 1 : 0)
                   + (recentBullFVG     ? 1 : 0)
                   + (fibOTE_bull       ? 1 : 0)
                   + (rsiOversold       ? 1 : 0)
                   + (volSpike          ? 1 : 0)
                   + (bullMomentum      ? 1 : 0);

  const scoreShort = (htfBear           ? 1 : 0)
                   + (sessionOk          ? 1 : 0)
                   + (recentSweepUp      ? 1 : 0)
                   + (inBearOB           ? 1 : 0)
                   + (recentBearFVG      ? 1 : 0)
                   + (fibOTE_bear        ? 1 : 0)
                   + (rsiOverbought      ? 1 : 0)
                   + (volSpike           ? 1 : 0)
                   + (bearMomentum       ? 1 : 0);

  // ── SL / TP ───────────────────────────────
  const price = last.close;
  let signal = null;

  if (scoreLong >= 6 && scoreLong > scoreShort) {
    const sl   = bullOB_bot ? bullOB_bot - atr1h * 0.5 : price - atr1h;
    const risk = Math.abs(price - sl);
    signal = {
      type:  'LONG', score: scoreLong, maxScore: 9, price,
      sl:    +sl.toFixed(2),
      tp1:   +(price + risk * 2).toFixed(2),
      tp2:   +(price + risk * 4).toFixed(2),
      tp3:   +(price + risk * 6).toFixed(2),
      rr:    '2:1 / 4:1',
      atr:   +curATR.toFixed(2),
      atr1h: +atr1h.toFixed(2),
      rsi:   +curRSI.toFixed(1),
      volRatio: +volData.ratio.toFixed(1),
      conditions: {
        htfBull, sessionOk, recentSweepDown, inBullOB,
        recentBullFVG, fibOTE_bull, rsiOversold, volSpike, bullMomentum
      }
    };
  } else if (scoreShort >= 6 && scoreShort > scoreLong) {
    const sl   = bearOB_top ? bearOB_top + atr1h * 0.5 : price + atr1h;
    const risk = Math.abs(sl - price);
    signal = {
      type:  'SHORT', score: scoreShort, maxScore: 9, price,
      sl:    +sl.toFixed(2),
      tp1:   +(price - risk * 2).toFixed(2),
      tp2:   +(price - risk * 4).toFixed(2),
      tp3:   +(price - risk * 6).toFixed(2),
      rr:    '2:1 / 4:1',
      atr:   +curATR.toFixed(2),
      atr1h: +atr1h.toFixed(2),
      rsi:   +curRSI.toFixed(1),
      volRatio: +volData.ratio.toFixed(1),
      conditions: {
        htfBear, sessionOk, recentSweepUp, inBearOB,
        recentBearFVG, fibOTE_bear, rsiOverbought, volSpike, bearMomentum
      }
    };
  }

  return {
    symbol:    'NQ/MNQ',
    price:     +price.toFixed(2),
    time:      new Date(last.time * 1000).toLocaleString('es-ES', { timeZone: 'Europe/Madrid' }),
    htfTrend:  htfBullStrong ? 'BULL↑' : htfBull ? 'BULL' : htfBearStrong ? 'BEAR↓' : htfBear ? 'BEAR' : 'NEUTRAL',
    session:   sessionOk,
    scoreLong, scoreShort,
    signal,
    atr:       +curATR.toFixed(2),
    rsi:       +curRSI.toFixed(1),
    volRatio:  +volData.ratio.toFixed(1),
  };
}
