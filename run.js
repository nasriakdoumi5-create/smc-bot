import { get5mBars, get1hBars } from './data.js';
import { analyze } from './smc.js';
import { getUpcomingHigh, isNewsTime } from './calendar.js';
import { analyzeOrderFlow, orderFlowText } from './orderflow.js';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const SYMBOL  = process.env.SYMBOL || 'MNQ';

// رمز Tradovate للـ NQ — يتغير حسب الشهر
const TV_SYMBOL = process.env.TRADOVATE_SYMBOL || 'NQM6';

if (!TOKEN || !CHAT_ID) { console.error('❌ TOKEN مفقود'); process.exit(1); }

const STATE_FILE = '/tmp/smc_state.json';
function loadState() {
  try { if (existsSync(STATE_FILE)) return JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch {}
  return { lastSignalKey: '', lastSignalTime: 0, lastNewsKey: '', lastHeartbeat: 0 };
}
function saveState(s) { try { writeFileSync(STATE_FILE, JSON.stringify(s)); } catch {} }

async function tg(text) {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' })
  });
  return r.ok;
}

const condLabels = {
  htfBull:'HTF Trend صاعد', htfBear:'HTF Trend هابط', sessionOk:'جلسة نشطة',
  recentSweepDown:'Liquidity Sweep هبوطي', recentSweepUp:'Liquidity Sweep صاعد',
  inBullOB:'Order Block صاعد', inBearOB:'Order Block هابط',
  recentBullFVG:'Fair Value Gap صاعد', recentBearFVG:'Fair Value Gap هابط',
  fibOTE_bull:'Fibonacci OTE (61-78%)', fibOTE_bear:'Fibonacci OTE (61-78%)',
  rsiOversold:'RSI تحت 50', rsiOverbought:'RSI فوق 50',
  positiveDelta:'Order Flow — Delta إيجابي ↑',
  negativeDelta:'Order Flow — Delta سلبي ↓',
  ofBuyImbalance:'Order Flow — Stacked Buy Imbalance ✦',
  ofSellImbalance:'Order Flow — Stacked Sell Imbalance ✦',
  bullDivergence:'Delta Divergence صاعد ⚠️',
  bearDivergence:'Delta Divergence هابط ⚠️',
};

async function check() {
  const state = loadState();

  // ── أخبار ────────────────────────────────
  const upcoming = await getUpcomingHigh(15).catch(() => []);
  for (const e of upcoming) {
    const key = e.date + e.title;
    if (key !== state.lastNewsKey) {
      state.lastNewsKey = key;
      const mins = Math.max(1, Math.round((new Date(e.date) - Date.now()) / 60000));
      await tg(`⚠️ <b>خبر مهم — ${e.title}</b>\n🕐 خلال <b>${mins} دقيقة</b> | 🔴 High Impact\n⛔ <b>لا تدخل الصفقة</b>`).catch(() => {});
    }
  }

  // ── جلب البيانات (Yahoo Finance فقط — مجاني 100%) ──
  const [bars5m, bars1h] = await Promise.all([
    get5mBars(SYMBOL),
    get1hBars(SYMBOL),
  ]);

  // Order Flow يُحسب من نفس بيانات Yahoo — لا يحتاج API إضافي
  const of = analyzeOrderFlow(bars5m);

  const result = analyze(bars5m, bars1h, null, of);
  if (result.error) { console.log('[SMC]', result.error); saveState(state); return; }

  const { price, signal, htfTrend, session, scoreLong, scoreShort, rsi } = result;

  const ofInfo = of
    ? `⚡ OF: Delta ${of.lastDelta >= 0 ? '+' : ''}${of.lastDelta} | Cum.Δ ${of.cumDelta >= 0 ? '+' : ''}${of.cumDelta}${of.stackedSell ? ' 🔴 SI' : ''}${of.stackedBuy ? ' 🟢 SI' : ''}${of.bearDivergence ? ' ⚠️DIV' : ''}`
    : '⚡ OF: -';

  console.log(`${SYMBOL} @ ${price} | ${htfTrend} L:${scoreLong}/11 S:${scoreShort}/11 RSI:${rsi} | ${ofInfo}`);

  // ── Heartbeat كل ساعة ─────────────────────
  const nowMs = Date.now();
  if (nowMs - (state.lastHeartbeat || 0) > 60 * 60 * 1000) {
    state.lastHeartbeat = nowMs;
    await tg(
`🤖 <b>SMC Bot — تقرير الساعة</b>

📊 ${SYMBOL} @ <b>${price}</b>
📈 HTF Trend: <b>${htfTrend}</b>
🕐 الجلسة: ${session ? '🟢 نشطة' : '🔴 مغلقة'}
⬆️ نقاط LONG:  ${scoreLong}/11
⬇️ نقاط SHORT: ${scoreShort}/11
📉 RSI: ${rsi}
${domInfo}

${signal ? `⚡ <b>إشارة ${signal.type} جاهزة</b>` : '⏳ لا توجد إشارة — البوت يراقب...'}`
    ).catch(() => {});
  }

  if (!signal) { saveState(state); return; }

  // ── تجنب التكرار ──────────────────────────
  const sigKey = `${signal.type}_${Math.round(signal.price / 10)}`;
  if (sigKey === state.lastSignalKey && (nowMs - state.lastSignalTime) < 30 * 60 * 1000) {
    console.log(`تكرار — تجاهل`); saveState(state); return;
  }
  if (await isNewsTime()) { console.log(`خبر جارٍ — تجاهل`); saveState(state); return; }

  state.lastSignalKey  = sigKey;
  state.lastSignalTime = nowMs;

  const isBull   = signal.type === 'LONG';
  const total    = Object.keys(signal.conditions).length;
  const scoreBar = '●'.repeat(signal.score) + '○'.repeat(total - signal.score);
  const risk     = Math.abs(signal.price - signal.sl);
  const rr       = risk > 0 ? (Math.abs(signal.tp1 - signal.price) / risk).toFixed(1) : '?';
  const condList = Object.entries(signal.conditions)
    .map(([k, v]) => `${v ? '✅' : '❌'} ${condLabels[k] || k}`)
    .join('\n');

  const ofBlock = orderFlowText(of);

  await tg(
`${isBull ? '📈' : '📉'} <b>إشارة ${signal.type} — NQ Futures</b>

💰 السعر:  <b>${signal.price}</b>
🛑 SL:     <b>${signal.sl}</b>  (${risk.toFixed(0)} نقطة)
🎯 TP1:    <b>${signal.tp1}</b>
🎯 TP2:    <b>${signal.tp2}</b>
⚖️  R:R:   <b>${rr}:1</b>

⭐ الجودة: <b>${signal.score}/${total}</b>  ${scoreBar}
📊 RSI: ${signal.rsi}  |  ATR: ${signal.atr}

${condList}
${ofBlock ? '\n' + ofBlock : ''}

<i>⚠️ القرار النهائي لك</i>
🕐 ${new Date().toLocaleString('ar-DZ')}`
  );

  console.log(`✅ إشعار — ${signal.type} @ ${signal.price} | ${signal.score}/${total}`);
  saveState(state);
}

check().catch(e => { console.error('[Fatal]', e.message); process.exit(1); });
