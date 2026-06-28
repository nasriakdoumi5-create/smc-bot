/**
 * SMC Elite — GitHub Actions Runner
 * يفحص MNQ + MGC + MCL في كل دورة
 * يحسب عدد العقود تلقائياً بناءً على الـ SL
 */

import { get5mBars, get1hBars, get1mBars }          from './data.js';
import { analyze, confirm1m }                       from './smc.js';
import { analyzeFib }                               from './fib_ote.js';
import { getUpcomingHigh, isNewsTime }              from './calendar.js';
import { readFileSync, writeFileSync, existsSync }  from 'fs';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const SYMBOLS = ['MNQ', 'MCL']; // MGC/MES موقف مؤقتاً — نسبة نجاح ضعيفة في الـ Backtest

// ══ إعدادات إدارة المال ══════════════════════
const ACCOUNT_BALANCE  = 50_000;   // حجم الحساب الممول
const CURRENT_BALANCE  = 49_400;   // الرصيد الحالي (بعد خسارة $600)
const RISK_PER_TRADE   = 75;       // 🔴 مرحلة التعافي — $75/صفقة
const MAX_DRAWDOWN     = 1_500;    // الحد الأقصى للخسارة الإجمالية
const DAILY_STOP_LOSS  = 300;      // وقف يومي عند $300 (4 صفقات فاشلة)
const REMAINING_BUDGET = 900;      // المتبقي قبل الحرق ($1500 - $600)

// قيمة النقطة لكل رمز (بالدولار)
const POINT_VALUE = {
  MNQ: 2,    // Micro Nasdaq  — $2 / نقطة
  MGC: 10,   // Micro Gold    — $10 / نقطة
  MCL: 100,  // Micro Crude   — $100 / نقطة
  MES: 5,    // Micro S&P 500 — $5 / نقطة
};

// الحد الأقصى للعقود لكل رمز
const MAX_CONTRACTS = {
  MNQ: 5,
  MGC: 3,
  MCL: 2,
  MES: 5,
};

/**
 * حساب عدد العقود بناءً على المخاطرة والـ SL
 * contracts = RISK / (SL_points × point_value)
 */
function calcContracts(symbol, entryPrice, slPrice) {
  const slPoints        = Math.abs(entryPrice - slPrice);
  const pointVal        = POINT_VALUE[symbol] || 2;
  const riskPerContract = slPoints * pointVal;
  if (riskPerContract <= 0) return { contracts: 1, actualRisk: RISK_PER_TRADE, warning: false };

  const contracts  = Math.floor(RISK_PER_TRADE / riskPerContract);
  const maxC       = MAX_CONTRACTS[symbol] || 3;
  const final      = Math.max(1, Math.min(contracts, maxC));
  const actualRisk = +(final * riskPerContract).toFixed(0);
  // تحذير إذا الخطر الفعلي يتجاوز الميزانية بأكثر من 50%
  const warning    = actualRisk > RISK_PER_TRADE * 1.5;
  return { contracts: final, actualRisk, warning };
}

// ══════════════════════════════════════════════

if (!TOKEN || !CHAT_ID) {
  console.error('❌ TELEGRAM_TOKEN أو TELEGRAM_CHAT_ID غير موجود');
  process.exit(1);
}

const STATE_FILE = '/tmp/smc_state.json';

function loadState() {
  try {
    if (existsSync(STATE_FILE)) return JSON.parse(readFileSync(STATE_FILE, 'utf8'));
  } catch {}
  return { signals: {}, lastNewsKey: '', dailyLoss: 0, dailyDate: '', tradesLeft: 12 };
}

function checkDailyReset(state) {
  const today = new Date().toLocaleDateString('es-ES', { timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit' });
  if (state.dailyDate !== today) {
    state.dailyDate  = today;
    state.dailyLoss  = 0;
  }
}

function saveState(s) {
  try { writeFileSync(STATE_FILE, JSON.stringify(s)); } catch {}
}

async function tg(text) {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' })
  });
  if (!r.ok) console.error('[TG Error]', await r.text());
  return r.ok;
}

const symbolNames = {
  MNQ: 'Micro Nasdaq (MNQ)',
  MGC: 'Micro Gold (MGC)',
  MCL: 'Micro Crude Oil (MCL)',
  MES: 'Micro S&P 500 (MES)',
};

const condLabels = {
  htfBull:'HTF قوي ↑↑ (EMA21>50>200)', htfBear:'HTF قوي ↓↓ (EMA21<50<200)',
  sessionOk:'Killzone (London/NY Open)',
  recentSweepDown:'Liquidity Sweep ↓ ✓', recentSweepUp:'Liquidity Sweep ↑ ✓',
  inBullOB:'Order Block صاعد',    inBearOB:'Order Block هابط',
  recentBullFVG:'FVG صاعد',       recentBearFVG:'FVG هابط',
  fibOTE_bull:'Fibonacci OTE 61.8-78.6%', fibOTE_bear:'Fibonacci OTE 61.8-78.6%',
  rsiOversold:'RSI ذروة بيع < 35',  rsiOverbought:'RSI ذروة شراء > 65',
  volSpike:'حجم تداول حقيقي > 1.3×',
  bullMomentum:'رفض صاعد قوي > 65%', bearMomentum:'رفض هابط قوي > 65%',
};

async function checkSymbol(symbol, state) {
  const [bars5m, bars1h, bars1m] = await Promise.all([
    get5mBars(symbol),
    get1hBars(symbol),
    get1mBars(symbol)
  ]);

  const result    = analyze(bars5m, bars1h);
  const fibResult = analyzeFib(bars1h);
  if (result.error) { console.log(`[${symbol}]`, result.error); return; }

  const { price, htfTrend, session, scoreLong, scoreShort, rsi, mandatory } = result;
  const t = new Date().toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });

  // ── فلتر Mandatory: إذا لم تكتمل الشروط الإلزامية → تجاهل ──
  const mLong  = mandatory?.htfBullStrong && mandatory?.sessionOk && mandatory?.recentSweepDown;
  const mShort = mandatory?.htfBearStrong && mandatory?.sessionOk && mandatory?.recentSweepUp;
  if (!mLong && !mShort && !fibResult?.signal) {
    console.log(`[${t}] ${symbol} — لا mandatory | HTF:${htfTrend} KZ:${session?'✅':'❌'}`);
    return;
  }

  // ── الفيبو يأخذ الأولوية إذا أعطى إشارة ──────
  let signal = fibResult?.signal || result.signal;
  let isFibSignal = !!(fibResult?.signal);

  const fibDiag = fibResult?.wave
    ? ` | FIB OTE:${fibResult.wave.inOTE?'✅':'❌'}(${fibResult.wave.ote618?.toFixed(0)}-${fibResult.wave.ote786?.toFixed(0)}) Q:${fibResult.wave.quality}`
    : '';
  console.log(`[${t}] ${symbol} @ ${price} | ${htfTrend} L:${scoreLong}/9 S:${scoreShort}/9 RSI:${rsi}${fibDiag}`);

  if (!signal) return;

  // تجنب التكرار لكل رمز بشكل مستقل
  if (!state.signals) state.signals = {};
  const sigKey = `${signal.type}_${Math.round(signal.price / 10)}`;
  const now    = Date.now();
  const last   = state.signals[symbol] || {};

  if (last.key === sigKey && (now - last.time) < 30 * 60 * 1000) {
    console.log(`[${symbol}] تكرار — تجاهل`);
    return;
  }

  // وقف يومي
  checkDailyReset(state);
  if (state.dailyLoss >= DAILY_STOP_LOSS) {
    console.log(`[${symbol}] ⛔ وقف يومي — خسارة اليوم $${state.dailyLoss}`);
    return;
  }

  // عدد الصفقات المتبقية
  if ((state.tradesLeft ?? 12) <= 0) {
    console.log(`[${symbol}] ⛔ انتهت الصفقات المتاحة للحساب`);
    await tg('🚨 <b>تحذير: انتهت الصفقات المتاحة</b>\nالحساب وصل لحد الخسارة الأقصى — لا تفتح صفقات جديدة').catch(() => {});
    return;
  }

  if (await isNewsTime()) {
    console.log(`[${symbol}] خبر جارٍ — تجاهل`);
    return;
  }

  // تأكيد 1M قبل الإشارة
  const entry1m = confirm1m(bars1m, signal.type);

  state.signals[symbol] = { key: sigKey, time: now };
  state.dailyLoss  = (state.dailyLoss  || 0) + RISK_PER_TRADE;
  state.tradesLeft = (state.tradesLeft ?? 12) - 1;

  // ── حساب العقود ──────────────────────────
  const calc       = calcContracts(symbol, signal.price, signal.sl);
  const contracts  = calc.contracts;
  const riskDollar = calc.actualRisk;
  const riskWarn   = calc.warning;
  const pointVal   = POINT_VALUE[symbol] || 2;
  const tp1Dollar  = +(contracts * Math.abs(signal.tp1 - signal.price) * pointVal).toFixed(0);
  const tp2Dollar  = +(contracts * Math.abs(signal.tp2 - signal.price) * pointVal).toFixed(0);
  const isBull     = signal.type === 'LONG';
  const risk       = Math.abs(signal.price - signal.sl);
  const rr         = risk > 0 ? (Math.abs(signal.tp1 - signal.price) / risk).toFixed(1) : '?';
  const dir        = isBull ? 'BUY' : 'SELL';

  // ── رسالة مختلفة حسب نوع الإشارة ────────────
  let msgBody;

  if (isFibSignal) {
    // إشارة الفيبو: أوضح وأبسط (win rate أعلى)
    const fibLabel = '📐 <b>إشارة Fibonacci OTE — نسبة نجاح 65-80%</b>';
    msgBody =
`${isBull ? '📈' : '📉'} ${fibLabel}
<b>${symbolNames[symbol] || symbol}</b>

━━━━━━━━━━━━━━━━━━━━
📌 <b>الدخول</b>
${isBull ? '🟢' : '🔴'} الاتجاه: <b>${dir}</b>
📦 العقود: <b>${contracts}</b> عقد
💵 السعر:  <b>${signal.price}</b>
🛑 SL:     <b>${signal.sl}</b>

🎯 <b>الأهداف</b>
TP1: <b>${signal.tp1}</b>  ← +$${tp1Dollar} (R:R ${rr})
TP2: <b>${signal.tp2}</b>  ← +$${tp2Dollar}

━━━━━━━━━━━━━━━━━━━━
📐 <b>تحليل الفيبو</b>
مستوى الدخول: <b>Fib ${signal.fibPct}%</b> من الموجة
منطقة OTE:    61.8% – 78.6% ✅
جودة الموجة: <b>${signal.quality}</b>/1.0
حجم الموجة:  <b>${signal.waveSize}</b>

📊 RSI: ${signal.rsi} | R:R ${signal.rr}
🕯 1M: ${entry1m.confirmed ? '✅' : '⚠️'} ${entry1m.reason}`;
  } else {
    // إشارة SMC الاعتيادية
    const isStrong = signal.score >= 5;
    const scoreBar = '●'.repeat(signal.score) + '○'.repeat(6 - Math.min(signal.score, 6));
    const tp3Dollar = +(contracts * Math.abs((signal.tp3||signal.tp2) - signal.price) * pointVal).toFixed(0);
    const condList  = Object.entries(signal.conditions || {})
      .map(([k, v]) => `${v ? '✅' : '❌'} ${condLabels[k] || k}`)
      .join('\n');
    const qualLabel = isStrong ? '🔥 إشارة عالية الجودة (5-6/6)' : '⚡ إشارة جيدة (4/6) — تحقق من الشارت';
    const slPoints  = risk;

    msgBody =
`${isBull ? '📈' : '📉'} <b>${qualLabel} — ${symbolNames[symbol] || symbol}</b>

━━━━━━━━━━━━━━━━━━━━
📌 <b>أمر التنفيذ</b>
${isBull ? '🟢' : '🔴'} الاتجاه: <b>${dir}</b>
📦 العقود: <b>${contracts}</b> عقد
💵 السعر:  <b>${signal.price}</b>
🛑 SL:     <b>${signal.sl}</b>  (${slPoints.toFixed(0)} نقطة)

🎯 <b>الأهداف</b>
TP1: <b>${signal.tp1}</b>  ← +$${tp1Dollar} (R:R ${rr})
TP2: <b>${signal.tp2}</b>  ← +$${tp2Dollar}
TP3: <b>${signal.tp3 || signal.tp2}</b>  ← +$${tp3Dollar}

━━━━━━━━━━━━━━━━━━━━
⭐ الجودة: <b>${signal.score}/6</b>  ${scoreBar}
🔒 Mandatory: HTF قوي ✅ | Killzone ✅ | Sweep ✅
📊 RSI: ${signal.rsi}  |  ATR: ${signal.atr}
🕯 1M: ${entry1m.confirmed ? '✅' : '⚠️'} ${entry1m.reason}

${condList}`;
  }

  await tg(
`${msgBody}

━━━━━━━━━━━━━━━━━━━━
💸 <b>إدارة المال</b>
خطر:    <b>$${riskDollar}</b>${riskWarn ? '  ⚠️' : ' ✅'}
نقطة:   <b>$${pointVal} / عقد</b>
━━━━━━━━━━━━━━━━━━━━
📋 <b>حالة الحساب</b>
صفقات اليوم: خسارة $${state.dailyLoss} / $${DAILY_STOP_LOSS}
متبقي كلياً: <b>${state.tradesLeft} صفقة</b> قبل الحد الأقصى

⚠️ <i>القرار النهائي لك — تحقق من الشارت قبل الدخول</i>
🕐 ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' })} (إسبانيا)`
  );

  console.log(`[${t}] ✅ إشعار ${symbol} — ${signal.type} @ ${signal.price} | ${signal.score}/9 | ${contracts} عقود`);
}

async function main() {
  const state = loadState();

  // أخبار قادمة
  const upcoming = await getUpcomingHigh(15).catch(() => []);
  for (const e of upcoming) {
    const key = e.date + e.title;
    if (key !== state.lastNewsKey) {
      state.lastNewsKey = key;
      const mins = Math.max(1, Math.round((new Date(e.date) - Date.now()) / 60000));
      const newsTime = new Date(e.date).toLocaleString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });
      await tg(
`⚠️ <b>خبر مهم — ${e.title}</b>
🕐 خلال <b>${mins} دقيقة</b> (${newsTime} إسبانيا)  |  🔴 High Impact
⛔ <b>لا تدخل الصفقة — انتظر الخبر</b>`
      ).catch(() => {});
    }
  }

  // فحص الثلاثة بالتوازي
  await Promise.all(SYMBOLS.map(s => checkSymbol(s, state).catch(e => console.error(`[${s}]`, e.message))));

  saveState(state);
}

main().catch(e => { console.error('[Fatal]', e.message); process.exit(1); });
