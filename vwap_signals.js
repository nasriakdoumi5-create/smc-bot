/**
 * VWAP Bounce + Liquidity Sweep — محلل الإشارات اليومية
 * يجلب بيانات MNQ الحية ويحدد أفضل 3 إشارات
 */

import { get5mBars } from './data.js';

// ── مؤشرات ──────────────────────────────────────

function calcATR(bars, i, p = 14) {
  if (i < p + 1) return bars[i].high - bars[i].low;
  let s = 0;
  for (let j = i - p + 1; j <= i; j++)
    s += Math.max(
      bars[j].high - bars[j].low,
      Math.abs(bars[j].high - bars[j - 1].close),
      Math.abs(bars[j].low  - bars[j - 1].close)
    );
  return s / p;
}

function calcRSI(bars, i, p = 14) {
  if (i < p + 1) return 50;
  let g = 0, l = 0;
  for (let j = i - p + 1; j <= i; j++) {
    const d = bars[j].close - bars[j - 1].close;
    if (d > 0) g += d; else l -= d;
  }
  return l === 0 ? 100 : 100 - 100 / (1 + g / l);
}

function calcDayVWAP(bars, i) {
  const barDate  = new Date(bars[i].time * 1000);
  const dayStart = new Date(barDate);
  dayStart.setUTCHours(0, 0, 0, 0);
  const dayTs = dayStart.getTime() / 1000;

  let tpv = 0, n = 0;
  for (let j = i; j >= 0; j--) {
    if (bars[j].time < dayTs) break;
    tpv += (bars[j].high + bars[j].low + bars[j].close) / 3;
    n++;
  }
  return n > 0 ? tpv / n : bars[i].close;
}

function calcPDHL(bars, i) {
  const today = new Date(bars[i].time * 1000);
  today.setUTCHours(0, 0, 0, 0);
  const todayTs  = today.getTime() / 1000;
  const yestTs   = todayTs - 86400;

  let pdh = -Infinity, pdl = Infinity;
  for (let j = i; j >= 0; j--) {
    if (bars[j].time < yestTs) break;
    if (bars[j].time < todayTs) {
      pdh = Math.max(pdh, bars[j].high);
      pdl = Math.min(pdl, bars[j].low);
    }
  }
  return {
    pdh: isFinite(pdh) ? pdh : null,
    pdl: isFinite(pdl) ? pdl : null,
  };
}

function calcSessionHL(bars, i) {
  // جلسة لندن + نيويورك: 07:00 UTC
  const now    = new Date(bars[i].time * 1000);
  const start  = new Date(now);
  start.setUTCHours(7, 0, 0, 0);
  if (now.getUTCHours() < 7) start.setDate(start.getDate() - 1);
  const startTs = start.getTime() / 1000;

  let sh = -Infinity, sl = Infinity;
  for (let j = i; j >= 0; j--) {
    if (bars[j].time < startTs) break;
    sh = Math.max(sh, bars[j].high);
    sl = Math.min(sl, bars[j].low);
  }
  return {
    sessionHigh: isFinite(sh) ? sh : null,
    sessionLow:  isFinite(sl) ? sl : null,
  };
}

// ── بناء إشارة ──────────────────────────────────

function mkLong(reason, entry, atr, rrMult = 2, priority = 2, condition = '') {
  const sl   = entry - atr * 0.3;
  const risk = entry - sl;
  const tp   = entry + risk * rrMult;
  return { type: 'LONG', reason, entry: +entry.toFixed(2), sl: +sl.toFixed(2), tp: +tp.toFixed(2), risk: +risk.toFixed(2), rr: rrMult, priority, condition };
}

function mkShort(reason, entry, atr, rrMult = 2, priority = 2, condition = '') {
  const sl   = entry + atr * 0.3;
  const risk = sl - entry;
  const tp   = entry - risk * rrMult;
  return { type: 'SHORT', reason, entry: +entry.toFixed(2), sl: +sl.toFixed(2), tp: +tp.toFixed(2), risk: +risk.toFixed(2), rr: rrMult, priority, condition };
}

// ── التحليل الرئيسي ──────────────────────────────

export async function analyzeVWAP(symbol = 'MNQ') {
  const bars = await get5mBars(symbol);
  if (!bars || bars.length < 50) return { error: 'بيانات غير كافية' };

  const i     = bars.length - 1;
  const b     = bars[i];
  const atr   = calcATR(bars, i);
  const rsi   = calcRSI(bars, i);
  const vwap  = calcDayVWAP(bars, i);
  const upper = vwap + atr * 1.5;
  const lower = vwap - atr * 1.5;
  const price = b.close;
  const { pdh, pdl }             = calcPDHL(bars, i);
  const { sessionHigh, sessionLow } = calcSessionHL(bars, i);

  const setups = [];

  // ① VWAP Upper Band — SHORT
  if (price >= upper - atr * 0.8 && price <= upper + atr * 0.5) {
    setups.push(mkShort(
      'VWAP Upper Band',
      upper, atr, 2,
      rsi >= 55 ? 3 : 2,
      `انتظر إغلاق شمعة حمراء تحت ${upper.toFixed(0)} مع RSI ≥ 58 وذيل علوي`
    ));
  }

  // ② VWAP Lower Band — LONG
  if (price <= lower + atr * 0.8 && price >= lower - atr * 0.5) {
    setups.push(mkLong(
      'VWAP Lower Band',
      lower, atr, 2,
      rsi <= 45 ? 3 : 2,
      `انتظر إغلاق شمعة خضراء فوق ${lower.toFixed(0)} مع RSI ≤ 42 وذيل سفلي`
    ));
  }

  // ③ PDH Liquidity Sweep — SHORT (الأهم)
  if (pdh) {
    const sweepEntry = pdh + atr * 0.1;
    setups.push({
      type: 'SHORT',
      reason: '⚡ سحب سيولة PDH',
      entry: +sweepEntry.toFixed(2),
      sl:    +(pdh + atr * 0.6).toFixed(2),
      tp:    +(sweepEntry - (atr * 0.5 + atr * 0.6) * 2).toFixed(2),
      risk:  +(atr * 0.5).toFixed(2),
      rr: 2, priority: 5,
      condition: `انتظر كسر ${pdh.toFixed(0)} → شمعة رجوع حمراء → ادخل SHORT بعد الإغلاق تحت PDH`,
    });
  }

  // ④ PDL Liquidity Sweep — LONG (الأهم)
  if (pdl) {
    const sweepEntry = pdl - atr * 0.1;
    setups.push({
      type: 'LONG',
      reason: '⚡ سحب سيولة PDL',
      entry: +sweepEntry.toFixed(2),
      sl:    +(pdl - atr * 0.6).toFixed(2),
      tp:    +(sweepEntry + (atr * 0.5 + atr * 0.6) * 2).toFixed(2),
      risk:  +(atr * 0.5).toFixed(2),
      rr: 2, priority: 5,
      condition: `انتظر كسر ${pdl.toFixed(0)} → شمعة رجوع خضراء → ادخل LONG بعد الإغلاق فوق PDL`,
    });
  }

  // ⑤ Session Low Sweep — LONG
  if (sessionLow && (!pdl || Math.abs(sessionLow - pdl) > atr)) {
    const sweepEntry = sessionLow - atr * 0.05;
    setups.push({
      type: 'LONG',
      reason: '⚡ سحب قاع الجلسة',
      entry: +sweepEntry.toFixed(2),
      sl:    +(sessionLow - atr * 0.5).toFixed(2),
      tp:    +(sweepEntry + atr * 0.9).toFixed(2),
      risk:  +(atr * 0.45).toFixed(2),
      rr: 2, priority: 4,
      condition: `انتظر كسر قاع الجلسة ${sessionLow.toFixed(0)} ثم شمعة خضراء للارتداد`,
    });
  }

  // ⑥ Session High Sweep — SHORT
  if (sessionHigh && (!pdh || Math.abs(sessionHigh - pdh) > atr)) {
    const sweepEntry = sessionHigh + atr * 0.05;
    setups.push({
      type: 'SHORT',
      reason: '⚡ سحب قمة الجلسة',
      entry: +sweepEntry.toFixed(2),
      sl:    +(sessionHigh + atr * 0.5).toFixed(2),
      tp:    +(sweepEntry - atr * 0.9).toFixed(2),
      risk:  +(atr * 0.45).toFixed(2),
      rr: 2, priority: 4,
      condition: `انتظر كسر قمة الجلسة ${sessionHigh.toFixed(0)} ثم شمعة حمراء للانعكاس`,
    });
  }

  // ⑦ VWAP Reversion (السعر بعيد عن VWAP) — LONG
  if (price < vwap - atr && rsi < 42) {
    setups.push(mkLong(
      'ارتداد VWAP',
      price, atr, 2, 2,
      `السعر بعيد تحت VWAP — انتظر شمعة خضراء تتجه نحو ${vwap.toFixed(0)}`
    ));
  }

  // ⑦ VWAP Reversion — SHORT
  if (price > vwap + atr && rsi > 58) {
    setups.push(mkShort(
      'ارتداد VWAP',
      price, atr, 2, 2,
      `السعر بعيد فوق VWAP — انتظر شمعة حمراء تتجه نحو ${vwap.toFixed(0)}`
    ));
  }

  // ── أفضل 3 ──────────────────────────────────────
  const top3 = setups
    .sort((a, b) => b.priority - a.priority)
    .slice(0, 3);

  return {
    symbol, price,
    vwap:        +vwap.toFixed(2),
    upper:       +upper.toFixed(2),
    lower:       +lower.toFixed(2),
    atr:         +atr.toFixed(2),
    rsi:         +rsi.toFixed(1),
    pdh:         pdh         ? +pdh.toFixed(2)         : null,
    pdl:         pdl         ? +pdl.toFixed(2)         : null,
    sessionHigh: sessionHigh ? +sessionHigh.toFixed(2) : null,
    sessionLow:  sessionLow  ? +sessionLow.toFixed(2)  : null,
    setups: top3,
    time: new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' }),
  };
}

// ── تنسيق رسالة Telegram ─────────────────────────

export function formatSignalsMsg(r) {
  if (r.error) return `⚠️ خطأ في التحليل: ${r.error}`;

  const dir  = p => p > 3 ? '🔴🔴' : p > 2 ? '🔴' : '🟡';
  const icon = t => t === 'LONG' ? '📈' : '📉';

  let msg =
`📊 <b>تحليل VWAP — ${r.symbol}   ${r.time}</b>

💵 السعر:  <b>${r.price}</b>
〰️ VWAP:   <b>${r.vwap}</b>   |   RSI: <b>${r.rsi}</b>
🔴 Upper:  <b>${r.upper}</b>   |   ATR: ${r.atr}
🟢 Lower:  <b>${r.lower}</b>
${r.pdh ? `📌 PDH: <b>${r.pdh}</b>   |   PDL: <b>${r.pdl}</b>` : ''}
${r.sessionHigh ? `📍 قمة الجلسة: <b>${r.sessionHigh}</b>   |   قاع: <b>${r.sessionLow}</b>` : ''}

─────────────────────────────
`;

  r.setups.forEach((s, idx) => {
    const riskPts = s.risk.toFixed(0);
    const profPts = (s.risk * s.rr).toFixed(0);
    msg +=
`${idx + 1}. ${icon(s.type)} <b>${s.type}</b>  ${dir(s.priority)}  <i>${s.reason}</i>
   دخول: <b>${s.entry}</b>   SL: <b>${s.sl}</b>   TP: <b>${s.tp}</b>
   خطر: ${riskPts} نقطة → ربح: ${profPts} نقطة (R:R 1:${s.rr})
   📋 <i>${s.condition}</i>

`;
  });

  msg += `<i>⚠️ انتظر تأكيد الشمعة قبل الدخول — لا تخاطر أكثر من 1-2%</i>`;
  return msg;
}
