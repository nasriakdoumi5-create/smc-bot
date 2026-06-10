/**
 * SMC Elite — GitHub Actions Runner
 * يفحص MNQ + MGC + MCL في كل دورة
 * يحسب عدد العقود تلقائياً بناءً على الـ SL
 */

import { get5mBars, get1hBars }                    from './data.js';
import { analyze }                                  from './smc.js';
import { getUpcomingHigh, isNewsTime }              from './calendar.js';
import { readFileSync, writeFileSync, existsSync }  from 'fs';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const SYMBOLS = ['MNQ', 'MGC', 'MCL'];

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
  MGC: 10,   // Micro Gold    — $10 / نقطة (1 نقطة = $1/oz × 10 oz)
  MCL: 100,  // Micro Crude   — $100 / نقطة (1$ = 0.01 تغيير × 100 = $1... في الواقع $1/0.01=$100)
};

// الحد الأقصى للعقود لكل رمز
const MAX_CONTRACTS = {
  MNQ: 5,
  MGC: 3,
  MCL: 2,
};

/**
 * حساب عدد العقود بناءً على المخاطرة والـ SL
 * contracts = RISK / (SL_points × point_value)
 */
function calcContracts(symbol, entryPrice, slPrice) {
  const slPoints  = Math.abs(entryPrice - slPrice);
  const pointVal  = POINT_VALUE[symbol] || 2;
  const riskPerContract = slPoints * pointVal;
  if (riskPerContract <= 0) return 1;

  const contracts = Math.floor(RISK_PER_TRADE / riskPerContract);
  const maxC      = MAX_CONTRACTS[symbol] || 3;
  return Math.max(1, Math.min(contracts, maxC));
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
};

const condLabels = {
  htfBull:'HTF Trend صاعد',       htfBear:'HTF Trend هابط',
  sessionOk:'جلسة نشطة',
  recentSweepDown:'Liquidity Sweep ↓', recentSweepUp:'Liquidity Sweep ↑',
  inBullOB:'Order Block صاعد',    inBearOB:'Order Block هابط',
  recentBullFVG:'FVG صاعد',       recentBearFVG:'FVG هابط',
  fibOTE_bull:'Fibonacci OTE',    fibOTE_bear:'Fibonacci OTE',
  rsiOversold:'RSI ذروة بيع',     rsiOverbought:'RSI ذروة شراء',
  volSpike:'حجم تداول مرتفع',
  bullMomentum:'رفض صاعد قوي',    bearMomentum:'رفض هابط قوي',
};

async function checkSymbol(symbol, state) {
  const [bars5m, bars1h] = await Promise.all([
    get5mBars(symbol),
    get1hBars(symbol)
  ]);

  const result = analyze(bars5m, bars1h);
  if (result.error) { console.log(`[${symbol}]`, result.error); return; }

  const { price, signal, htfTrend, session, scoreLong, scoreShort, rsi } = result;
  const t = new Date().toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });
  console.log(`[${t}] ${symbol} @ ${price} | ${htfTrend} L:${scoreLong}/9 S:${scoreShort}/9 RSI:${rsi}`);

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

  state.signals[symbol] = { key: sigKey, time: now };
  state.dailyLoss  = (state.dailyLoss  || 0) + RISK_PER_TRADE;
  state.tradesLeft = (state.tradesLeft ?? 12) - 1;

  // ── حساب العقود ──────────────────────────
  const contracts  = calcContracts(symbol, signal.price, signal.sl);
  const pointVal   = POINT_VALUE[symbol] || 2;
  const slPoints   = Math.abs(signal.price - signal.sl);
  const riskDollar = +(contracts * slPoints * pointVal).toFixed(0);
  const tp1Dollar  = +(contracts * Math.abs(signal.tp1 - signal.price) * pointVal).toFixed(0);
  const tp2Dollar  = +(contracts * Math.abs(signal.tp2 - signal.price) * pointVal).toFixed(0);
  const tp3Dollar  = +(contracts * Math.abs(signal.tp3 - signal.price) * pointVal).toFixed(0);

  const isBull    = signal.type === 'LONG';
  const scoreBar  = '●'.repeat(signal.score) + '○'.repeat(9 - signal.score);
  const risk      = Math.abs(signal.price - signal.sl);
  const rr        = risk > 0 ? (Math.abs(signal.tp1 - signal.price) / risk).toFixed(1) : '?';
  const condList  = Object.entries(signal.conditions)
    .map(([k, v]) => `${v ? '✅' : '❌'} ${condLabels[k] || k}`)
    .join('\n');

  const dir = isBull ? 'BUY' : 'SELL';

  await tg(
`${isBull ? '📈' : '📉'} <b>إشارة ${signal.type} — ${symbolNames[symbol] || symbol}</b>

━━━━━━━━━━━━━━━━━━━━
📌 <b>أمر التنفيذ</b>
${isBull ? '🟢' : '🔴'} الاتجاه: <b>${dir}</b>
📦 العقود: <b>${contracts}</b> عقد
💵 السعر:  <b>${signal.price}</b>
🛑 SL:     <b>${signal.sl}</b>  (${slPoints.toFixed(0)} نقطة)

🎯 <b>الأهداف</b>
TP1: <b>${signal.tp1}</b>  ← +$${tp1Dollar} (R:R ${rr})
TP2: <b>${signal.tp2}</b>  ← +$${tp2Dollar}
TP3: <b>${signal.tp3}</b>  ← +$${tp3Dollar}

━━━━━━━━━━━━━━━━━━━━
💸 <b>إدارة المال</b>
خطر:    <b>$${riskDollar}</b> من $${ACCOUNT_BALANCE.toLocaleString()}
نقطة:   <b>$${pointVal} / عقد</b>
━━━━━━━━━━━━━━━━━━━━

⭐ الجودة: <b>${signal.score}/9</b>  ${scoreBar}
📊 RSI: ${signal.rsi}  |  ATR: ${signal.atr}  |  Vol: ${signal.volRatio}x

${condList}

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
