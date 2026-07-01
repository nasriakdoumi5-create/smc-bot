/**
 * Signal Engine — VWAP Bounce + Liquidity Sweep
 * ═══════════════════════════════════════════════
 * محرك الإشارات — يعمل على الشمعات المغلقة فقط
 * لا يعتمد على أي API خارجي — دوال نقية
 */

// ── مؤشرات أساسية ───────────────────────────────

export function calcATR(bars, period = 14) {
  const n = bars.length;
  if (n < period + 1) return bars[n - 1].high - bars[n - 1].low;
  let sum = 0;
  for (let i = n - period; i < n; i++) {
    sum += Math.max(
      bars[i].high - bars[i].low,
      Math.abs(bars[i].high - bars[i - 1].close),
      Math.abs(bars[i].low  - bars[i - 1].close)
    );
  }
  return sum / period;
}

export function calcRSI(bars, period = 14) {
  const n = bars.length;
  if (n < period + 2) return 50;
  let g = 0, l = 0;
  for (let i = n - period; i < n; i++) {
    const d = bars[i].close - bars[i - 1].close;
    d > 0 ? (g += d) : (l -= d);
  }
  if (l === 0) return 100;
  return 100 - 100 / (1 + g / l);
}

export function calcVWAP(bars) {
  // يُعاد حسابه من بداية اليوم (00:00 UTC)
  const n       = bars.length;
  const last    = bars[n - 1];
  const dayTs   = Math.floor(last.time / 86400) * 86400;
  let tpv = 0, count = 0;
  for (let i = n - 1; i >= 0; i--) {
    if (bars[i].time < dayTs) break;
    tpv += (bars[i].high + bars[i].low + bars[i].close) / 3;
    count++;
  }
  return count > 0 ? tpv / count : last.close;
}

export function calcPDHL(bars) {
  const n      = bars.length;
  const last   = bars[n - 1];
  const todayTs = Math.floor(last.time / 86400) * 86400;
  const yestTs  = todayTs - 86400;
  let pdh = -Infinity, pdl = Infinity;
  for (let i = n - 1; i >= 0; i--) {
    if (bars[i].time < yestTs) break;
    if (bars[i].time < todayTs) {
      pdh = Math.max(pdh, bars[i].high);
      pdl = Math.min(pdl, bars[i].low);
    }
  }
  return {
    pdh: isFinite(pdh) ? pdh : null,
    pdl: isFinite(pdl) ? pdl : null,
  };
}

export function calcSessionHL(bars) {
  // جلسة لندن + نيويورك: 07:00 UTC
  const n       = bars.length;
  const last    = bars[n - 1];
  const nowDate = new Date(last.time * 1000);
  const startH  = new Date(nowDate);
  startH.setUTCHours(7, 0, 0, 0);
  if (nowDate.getUTCHours() < 7) startH.setDate(startH.getDate() - 1);
  const startTs = startH.getTime() / 1000;
  let sh = -Infinity, sl = Infinity;
  for (let i = n - 1; i >= 0; i--) {
    if (bars[i].time < startTs) break;
    sh = Math.max(sh, bars[i].high);
    sl = Math.min(sl, bars[i].low);
  }
  return {
    sessionHigh: isFinite(sh) ? sh : null,
    sessionLow:  isFinite(sl) ? sl : null,
  };
}

// ── بناء الإشارة ─────────────────────────────────

function buildSignal({ type, reason, priority, bar, refLevel, atr, rsi, vwap, pdh, pdl }) {
  const entry = bar.close;
  const sl    = type === 'LONG'
    ? Math.min(bar.low,  refLevel) - atr * 0.15
    : Math.max(bar.high, refLevel) + atr * 0.15;
  const risk  = Math.abs(entry - sl);
  if (risk <= 0 || risk > atr * 8) return null;
  const tp1 = type === 'LONG' ? entry + risk * 2 : entry - risk * 2;
  const tp2 = type === 'LONG' ? entry + risk * 3 : entry - risk * 3;
  return {
    type, reason, priority,
    entry: +entry.toFixed(2),
    sl:    +sl.toFixed(2),
    tp1:   +tp1.toFixed(2),
    tp2:   +tp2.toFixed(2),
    risk:  +risk.toFixed(2),
    rsi:   +rsi.toFixed(1),
    atr:   +atr.toFixed(2),
    vwap:  +vwap.toFixed(2),
    pdh:   pdh ? +pdh.toFixed(2) : null,
    pdl:   pdl ? +pdl.toFixed(2) : null,
  };
}

// ── المحرك الرئيسي ───────────────────────────────

export function detectSignal(bars) {
  if (!bars || bars.length < 50) return null;

  const bar  = bars[bars.length - 1];  // آخر شمعة مغلقة
  const atr  = calcATR(bars);
  const rsi  = calcRSI(bars);
  const vwap = calcVWAP(bars);
  const upper = vwap + atr * 1.5;
  const lower = vwap - atr * 1.5;
  const { pdh, pdl }             = calcPDHL(bars);
  const { sessionHigh, sessionLow } = calcSessionHL(bars);

  const wUp = bar.high  - Math.max(bar.open, bar.close);
  const wDn = Math.min(bar.open, bar.close) - bar.low;
  const minWick = atr * 0.12;

  // ══ ① سحب سيولة PDH — SHORT ════════════════════
  if (
    pdh &&
    bar.high > pdh &&          // اخترق أعلى أمس
    bar.close < pdh &&         // أغلق تحته (رفض)
    bar.close < bar.open &&    // شمعة حمراء
    wUp >= minWick &&          // ذيل علوي واضح
    rsi >= 54
  ) {
    return buildSignal({ type: 'SHORT', reason: '⚡ سحب سيولة PDH', priority: 5, bar, refLevel: pdh, atr, rsi, vwap, pdh, pdl });
  }

  // ══ ② سحب سيولة PDL — LONG ═════════════════════
  if (
    pdl &&
    bar.low < pdl &&           // اخترق أدنى أمس
    bar.close > pdl &&         // أغلق فوقه (رفض)
    bar.close > bar.open &&    // شمعة خضراء
    wDn >= minWick &&          // ذيل سفلي واضح
    rsi <= 46
  ) {
    return buildSignal({ type: 'LONG', reason: '⚡ سحب سيولة PDL', priority: 5, bar, refLevel: pdl, atr, rsi, vwap, pdh, pdl });
  }

  // ══ ③ سحب قمة الجلسة — SHORT ═══════════════════
  if (
    sessionHigh &&
    (!pdh || Math.abs(sessionHigh - pdh) > atr * 0.5) &&
    bar.high > sessionHigh &&
    bar.close < sessionHigh &&
    bar.close < bar.open &&
    wUp >= minWick &&
    rsi >= 56
  ) {
    return buildSignal({ type: 'SHORT', reason: '⚡ سحب قمة الجلسة', priority: 4, bar, refLevel: sessionHigh, atr, rsi, vwap, pdh, pdl });
  }

  // ══ ④ سحب قاع الجلسة — LONG ════════════════════
  if (
    sessionLow &&
    (!pdl || Math.abs(sessionLow - pdl) > atr * 0.5) &&
    bar.low < sessionLow &&
    bar.close > sessionLow &&
    bar.close > bar.open &&
    wDn >= minWick &&
    rsi <= 44
  ) {
    return buildSignal({ type: 'LONG', reason: '⚡ سحب قاع الجلسة', priority: 4, bar, refLevel: sessionLow, atr, rsi, vwap, pdh, pdl });
  }

  // ══ ⑤ VWAP Upper Band — SHORT ═══════════════════
  if (
    bar.high >= upper &&
    bar.close < upper &&
    bar.close < bar.open &&
    wUp >= minWick &&
    rsi >= 56
  ) {
    return buildSignal({ type: 'SHORT', reason: 'VWAP Upper Band', priority: 3, bar, refLevel: upper, atr, rsi, vwap, pdh, pdl });
  }

  // ══ ⑥ VWAP Lower Band — LONG ════════════════════
  if (
    bar.low <= lower &&
    bar.close > lower &&
    bar.close > bar.open &&
    wDn >= minWick &&
    rsi <= 44
  ) {
    return buildSignal({ type: 'LONG', reason: 'VWAP Lower Band', priority: 3, bar, refLevel: lower, atr, rsi, vwap, pdh, pdl });
  }

  return null;
}

// ── فحص الصفقات المفتوحة ─────────────────────────

export function checkOpenTrade(trade, bar) {
  if (trade.type === 'LONG') {
    if (bar.low  <= trade.sl)  return 'SL';
    if (bar.high >= trade.tp1) return 'TP1';
  } else {
    if (bar.high >= trade.sl)  return 'SL';
    if (bar.low  <= trade.tp1) return 'TP1';
  }
  return null;
}
