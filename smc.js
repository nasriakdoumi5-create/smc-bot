/**
 * SMC Elite Strategy Engine v3 — High Probability
 * ════════════════════════════════════════════════
 * الهدف: 65%+ نسبة نجاح بتشديد جميع الشروط
 *
 * MANDATORY (يجب كلها):
 *   ① HTF Trend قوي: EMA21 > EMA50 > EMA200
 *   ② Killzone حقيقية: London 07-10 | NY 13:30-15:30
 *   ③ Liquidity Sweep حديث (آخر 20 شمعة)
 *
 * SCORED — يجب 4 من 6:
 *   ④ Order Block (displacement > 1.0×ATR)
 *   ⑤ Fair Value Gap (آخر 8 شمعات)
 *   ⑥ Fibonacci OTE 61.8-78.6%
 *   ⑦ RSI ذروة حقيقية < 35 أو > 65
 *   ⑧ حجم تداول حقيقي > 1.3× المتوسط
 *   ⑨ رفض قوي: جسم > 65% من النطاق
 */

// ══ EMA ══════════════════════════════════════════
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

// ══ ATR ══════════════════════════════════════════
export function atr(bars, period = 14) {
  const trs = bars.map((b, i) => {
    if (i === 0) return b.high - b.low;
    const p = bars[i - 1].close;
    return Math.max(b.high - b.low, Math.abs(b.high - p), Math.abs(b.low - p));
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

// ══ RSI ══════════════════════════════════════════
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

// ══ Swing Highs/Lows (lookup = 10 شمعة) ══════════
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

// ══ ① Killzone — London Open + NY Open فقط ═══════
function inKillzone() {
  const now  = new Date();
  const mins = now.getUTCHours() * 60 + now.getUTCMinutes();
  const londonOpen = mins >= 7 * 60  && mins < 10 * 60;      // 07:00-10:00 UTC
  const nyOpen     = mins >= 13 * 60 + 30 && mins < 15 * 60 + 30; // 13:30-15:30 UTC
  return londonOpen || nyOpen;
}

// ══ ⑧ حجم تداول — صارم، بدون auto-pass ═══════════
function volumeCheck(bars, n, lookback = 20) {
  const vols = bars.slice(Math.max(0, n - lookback), n).map(b => b.volume || 0);
  const avgVol = vols.reduce((s, v) => s + v, 0) / vols.length;
  const curVol = bars[n - 1].volume || 0;
  if (avgVol < 10) return { ok: false, ratio: 0, noData: true }; // futures بدون volume حقيقي
  return { ok: curVol > avgVol * 1.3, ratio: +(curVol / avgVol).toFixed(1), noData: false };
}

// ══ ⑨ رفض قوي — جسم > 65% ═══════════════════════
function strongRejection(bars, n, curATR) {
  const last = bars[n - 1];
  const prev = bars[n - 2];
  const body     = Math.abs(last.close - last.open);
  const bodyPrev = Math.abs(prev.close - prev.open);
  const range    = last.high - last.low || 0.01;

  const bearRej = last.close < last.open
    && body / range > 0.65
    && body > curATR * 0.5
    && prev.close > prev.open;

  const bullRej = last.close > last.open
    && body / range > 0.65
    && body > curATR * 0.5
    && prev.close < prev.open;

  return { bearRej, bullRej };
}

// ══ 1M Confirmation ══════════════════════════════
export function confirm1m(bars1m, direction) {
  if (!bars1m || bars1m.length < 5) return { confirmed: false, reason: 'لا بيانات 1M' };
  const last  = bars1m[bars1m.length - 1];
  const body  = Math.abs(last.close - last.open);
  const range = last.high - last.low || 0.01;

  if (direction === 'LONG') {
    const ok = last.close > last.open && body / range > 0.45
      && last.close > (last.high + last.low) / 2;
    return { confirmed: ok, reason: ok ? '1M شمعة صاعدة قوية ✅' : '1M لا تأكيد بعد ⏳' };
  } else {
    const ok = last.close < last.open && body / range > 0.45
      && last.close < (last.high + last.low) / 2;
    return { confirmed: ok, reason: ok ? '1M شمعة هابطة قوية ✅' : '1M لا تأكيد بعد ⏳' };
  }
}

// ══ التحليل الرئيسي ══════════════════════════════
export function analyze(bars5m, bars1h) {
  if (bars5m.length < 50 || bars1h.length < 200) {
    return { error: 'not enough data' };
  }

  // ════════════════════════════════════════════════
  // ① HTF TREND — يجب EMA21 > EMA50 > EMA200 (قوي)
  // ════════════════════════════════════════════════
  const ema21h  = ema(bars1h, 21);
  const ema50h  = ema(bars1h, 50);
  const ema200h = ema(bars1h, 200);
  const E21  = ema21h[ema21h.length - 1];
  const E50  = ema50h[ema50h.length - 1];
  const E200 = ema200h[ema200h.length - 1];

  // اتجاه قوي: 3 EMAs مرتبة
  const htfBull       = E50 > E200;
  const htfBear       = E50 < E200;
  const htfBullStrong = E21 > E50 && E50 > E200;  // ← إلزامي للـ LONG
  const htfBearStrong = E21 < E50 && E50 < E200;  // ← إلزامي للـ SHORT

  // ════════════════════════════════════════════════
  // ② KILLZONE — إلزامي
  // ════════════════════════════════════════════════
  const sessionOk = inKillzone();

  // ── آخر شمعة ─────────────────────────────────
  const n    = bars5m.length;
  const last = bars5m[n - 1];

  // ── ATR و RSI ──────────────────────────────────
  const atrArr   = atr(bars5m, 14);
  const atr1hArr = atr(bars1h, 14);
  const rsiArr   = rsi(bars5m, 14);
  const curATR   = atrArr[n - 1] || 1;
  const atr1h    = atr1hArr[atr1hArr.length - 1] || curATR * 3;
  const curRSI   = rsiArr[n - 1] || 50;

  // ── Swing H/L ──────────────────────────────────
  const sHighs = swingHighs(bars5m, 10);
  const sLows  = swingLows(bars5m, 10);

  let lastSH = null, lastSL = null, lastSHIdx = -1, lastSLIdx = -1;
  for (let i = n - 1; i >= 0; i--) {
    if (lastSH === null && sHighs[i] !== null) { lastSH = sHighs[i]; lastSHIdx = i; }
    if (lastSL === null && sLows[i]  !== null) { lastSL = sLows[i];  lastSLIdx = i; }
    if (lastSH && lastSL) break;
  }

  // ════════════════════════════════════════════════
  // ③ LIQUIDITY SWEEP — إلزامي (آخر 20 شمعة)
  // ════════════════════════════════════════════════
  let recentSweepUp   = false;
  let recentSweepDown = false;
  for (let i = Math.max(0, n - 20); i < n; i++) {
    const b = bars5m[i];
    if (lastSH && b.high > lastSH && b.close < lastSH) recentSweepUp   = true;
    if (lastSL && b.low  < lastSL && b.close > lastSL) recentSweepDown = true;
  }

  // ════════════════════════════════════════════════
  // ④ ORDER BLOCK — displacement إلزامي > 1.0×ATR
  // ════════════════════════════════════════════════
  let bullOB_top = null, bullOB_bot = null;
  let bearOB_top = null, bearOB_bot = null;
  let swingLowForSL = null, swingHighForSL = null;

  for (let i = Math.max(1, n - 20); i < n - 1; i++) {
    const b    = bars5m[i];
    const next = bars5m[i + 1];
    const bullDisp = (next.close - next.open) > curATR * 1.0 && next.close > b.high;
    if (bullDisp && b.open > b.close) {
      bullOB_top = b.open; bullOB_bot = b.close;
      swingLowForSL = Math.min(b.low, next.low);
    }
    const bearDisp = (next.open - next.close) > curATR * 1.0 && next.close < b.low;
    if (bearDisp && b.close > b.open) {
      bearOB_top = b.close; bearOB_bot = b.open;
      swingHighForSL = Math.max(b.high, next.high);
    }
  }

  const inBullOB = !!(bullOB_top && last.close <= bullOB_top && last.close >= bullOB_bot);
  const inBearOB = !!(bearOB_top && last.close <= bearOB_top && last.close >= bearOB_bot);

  // ════════════════════════════════════════════════
  // ⑤ FAIR VALUE GAP — آخر 8 شمعات فقط
  // ════════════════════════════════════════════════
  let recentBullFVG = false;
  let recentBearFVG = false;
  for (let i = Math.max(2, n - 8); i < n; i++) {
    const gap = bars5m[i].low - bars5m[i - 2].high;
    const gap2 = bars5m[i - 2].low - bars5m[i].high;
    if (gap > curATR * 0.3)  recentBullFVG = true;
    if (gap2 > curATR * 0.3) recentBearFVG = true;
  }

  // ════════════════════════════════════════════════
  // ⑥ FIBONACCI OTE 61.8-78.6%
  // ════════════════════════════════════════════════
  let fibOTE_bull = false, fibOTE_bear = false;
  if (lastSH && lastSL) {
    const rng = lastSH - lastSL;
    const p   = last.close;
    fibOTE_bull = p >= (lastSH - rng * 0.786) && p <= (lastSH - rng * 0.618);
    fibOTE_bear = p >= (lastSL + rng * 0.618) && p <= (lastSL + rng * 0.786);
  }

  // ════════════════════════════════════════════════
  // ⑦ RSI — ذروة حقيقية (< 35 أو > 65)
  // ════════════════════════════════════════════════
  const rsiOversold   = curRSI < 35;   // أكثر صرامة من 40
  const rsiOverbought = curRSI > 65;   // أكثر صرامة من 60

  // ════════════════════════════════════════════════
  // ⑧ VOLUME — حقيقي فقط
  // ════════════════════════════════════════════════
  const volData  = volumeCheck(bars5m, n);
  const volSpike = volData.ok && !volData.noData;

  // ════════════════════════════════════════════════
  // ⑨ STRONG REJECTION — جسم > 65%
  // ════════════════════════════════════════════════
  const rejection = strongRejection(bars5m, n, curATR);
  const bullMomentum = rejection.bullRej;
  const bearMomentum = rejection.bearRej;

  // ════════════════════════════════════════════════
  // SCORE (6 شروط اختيارية)
  // ════════════════════════════════════════════════
  const scoreLong  = (inBullOB      ? 1 : 0)
                   + (recentBullFVG ? 1 : 0)
                   + (fibOTE_bull   ? 1 : 0)
                   + (rsiOversold   ? 1 : 0)
                   + (volSpike      ? 1 : 0)
                   + (bullMomentum  ? 1 : 0);

  const scoreShort = (inBearOB      ? 1 : 0)
                   + (recentBearFVG ? 1 : 0)
                   + (fibOTE_bear   ? 1 : 0)
                   + (rsiOverbought ? 1 : 0)
                   + (volSpike      ? 1 : 0)
                   + (bearMomentum  ? 1 : 0);

  // ════════════════════════════════════════════════
  // SIGNAL — المندتوري + 4 من 6 اختياري
  // ════════════════════════════════════════════════
  const price = last.close;
  let signal  = null;

  const mandatoryLong  = htfBullStrong && sessionOk && recentSweepDown;
  const mandatoryShort = htfBearStrong && sessionOk && recentSweepUp;

  if (mandatoryLong && scoreLong >= 4) {
    const sl   = swingLowForSL
      ? swingLowForSL - curATR * 0.3
      : (bullOB_bot ? bullOB_bot - atr1h * 0.3 : price - atr1h);
    const risk = Math.abs(price - sl);
    signal = {
      type: 'LONG', score: scoreLong, maxScore: 6, price,
      sl:   +sl.toFixed(2),
      tp1:  +(price + risk * 2).toFixed(2),
      tp2:  +(price + risk * 3.5).toFixed(2),
      tp3:  +(price + risk * 5).toFixed(2),
      rr: '2:1 / 3.5:1',
      atr: +curATR.toFixed(2), atr1h: +atr1h.toFixed(2),
      rsi: +curRSI.toFixed(1),
      volRatio: volData.noData ? 'N/A' : volData.ratio,
      conditions: {
        htfBull: htfBullStrong, sessionOk, recentSweepDown,
        inBullOB, recentBullFVG, fibOTE_bull,
        rsiOversold, volSpike, bullMomentum,
      },
    };
  } else if (mandatoryShort && scoreShort >= 4) {
    const sl   = swingHighForSL
      ? swingHighForSL + curATR * 0.3
      : (bearOB_top ? bearOB_top + atr1h * 0.3 : price + atr1h);
    const risk = Math.abs(sl - price);
    signal = {
      type: 'SHORT', score: scoreShort, maxScore: 6, price,
      sl:   +sl.toFixed(2),
      tp1:  +(price - risk * 2).toFixed(2),
      tp2:  +(price - risk * 3.5).toFixed(2),
      tp3:  +(price - risk * 5).toFixed(2),
      rr: '2:1 / 3.5:1',
      atr: +curATR.toFixed(2), atr1h: +atr1h.toFixed(2),
      rsi: +curRSI.toFixed(1),
      volRatio: volData.noData ? 'N/A' : volData.ratio,
      conditions: {
        htfBear: htfBearStrong, sessionOk, recentSweepUp,
        inBearOB, recentBearFVG, fibOTE_bear,
        rsiOverbought, volSpike, bearMomentum,
      },
    };
  }

  return {
    symbol: 'NQ/MNQ',
    price:  +price.toFixed(2),
    time:   new Date(last.time * 1000).toLocaleString('es-ES', { timeZone: 'Europe/Madrid' }),
    htfTrend: htfBullStrong ? 'BULL↑↑' : htfBull ? 'BULL' : htfBearStrong ? 'BEAR↓↓' : htfBear ? 'BEAR' : 'NEUTRAL',
    session:  sessionOk,
    mandatory: { htfBullStrong, htfBearStrong, sessionOk, recentSweepDown, recentSweepUp },
    scoreLong, scoreShort,
    signal,
    atr:  +curATR.toFixed(2),
    rsi:  +curRSI.toFixed(1),
  };
}
