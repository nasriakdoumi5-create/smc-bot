import { get5mBars } from './data.js';
import { analyzeAMD } from './amd.js';
import { analyzeOrderFlow, orderFlowText } from './orderflow.js';
import { getUpcomingHigh, isNewsTime } from './calendar.js';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const SYMBOL  = process.env.SYMBOL || 'MNQ';

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

  // ── جلب البيانات ──────────────────────────
  const bars5m = await get5mBars(SYMBOL);
  const result = analyzeAMD(bars5m);
  const of     = analyzeOrderFlow(bars5m);

  if (result.error) {
    console.log('[AMD]', result.error);
    saveState(state); return;
  }

  const { price, session, asiaHigh, asiaLow, asiaSize, manipHigh, manipLow, manipPrice, inDistribution, signal } = result;

  // ── log ───────────────────────────────────
  const manipTxt = manipHigh ? `🔴 Manip↑${manipPrice}` : manipLow ? `🟢 Manip↓${manipPrice}` : '⏳ لا يوجد';
  console.log(`${SYMBOL} @ ${price} | ${session} | Asia[${asiaLow}-${asiaHigh}] | ${manipTxt}`);

  // ── Heartbeat كل ساعة ─────────────────────
  const nowMs = Date.now();
  if (nowMs - (state.lastHeartbeat || 0) > 60 * 60 * 1000) {
    state.lastHeartbeat = nowMs;
    await tg(
`🤖 <b>AMD Bot — تقرير الساعة</b>

💰 ${SYMBOL} @ <b>${price}</b>
🕐 الجلسة: <b>${session}</b>

📦 Asia Range:
   High: <b>${asiaHigh}</b>
   Low:  <b>${asiaLow}</b>
   Size: ${asiaSize} نقطة

🎭 Manipulation:
${manipHigh ? `   🔴 Stop Hunt فوق Asia High @ ${manipPrice}` : ''}${manipLow ? `   🟢 Stop Hunt تحت Asia Low  @ ${manipPrice}` : ''}${!manipHigh && !manipLow ? '   ⏳ لم يحدث بعد — انتظار London' : ''}

${inDistribution && signal ? '⚡ <b>إشارة جاهزة — تحقق من الرسالة التالية</b>' : inDistribution ? '🔍 NY نشطة — لا توجد إشارة بعد' : '⏳ انتظار جلسة NY للدخول'}`
    ).catch(() => {});
  }

  if (!signal) { saveState(state); return; }

  // ── تجنب التكرار (30 دقيقة) ───────────────
  const sigKey = `${signal.type}_${Math.round(signal.price / 10)}`;
  if (sigKey === state.lastSignalKey && (nowMs - state.lastSignalTime) < 30 * 60 * 1000) {
    console.log('تكرار — تجاهل'); saveState(state); return;
  }
  if (await isNewsTime()) { console.log('خبر جارٍ — تجاهل'); saveState(state); return; }

  state.lastSignalKey  = sigKey;
  state.lastSignalTime = nowMs;

  // ── إرسال الإشارة ─────────────────────────
  const isBull = signal.type === 'LONG';
  const risk   = Math.abs(signal.price - signal.sl);
  const rr     = risk > 0 ? (Math.abs(signal.tp1 - signal.price) / risk).toFixed(1) : '?';
  const ofBlock = orderFlowText(of);

  const condList = Object.entries(signal.conditions)
    .map(([k, v]) => `${v ? '✅' : '❌'} ${condLabels[k] || k}`)
    .join('\n');

  await tg(
`${isBull ? '📈' : '📉'} <b>AMD — إشارة ${signal.type} | NQ Futures</b>

━━━━━━━━━━━━━━━━
🎭 <b>المرحلة: ${signal.phase}</b>
📦 ${signal.manipulation}

━━━━━━━━━━━━━━━━
💰 الدخول:  <b>${signal.price}</b>
🛑 SL:      <b>${signal.sl}</b>  (${risk.toFixed(0)} نقطة)
🎯 TP1:     <b>${signal.tp1}</b>
🎯 TP2:     <b>${signal.tp2}</b>  ← ${isBull ? 'Asia High' : 'Asia Low'}
⚖️  R:R:    <b>${rr}:1</b>

━━━━━━━━━━━━━━━━
📊 Asia Range: ${asiaLow} – ${asiaHigh} (${asiaSize} نقطة)

${condList}
${ofBlock ? '\n' + ofBlock : ''}

<i>⚠️ القرار النهائي لك</i>
🕐 ${new Date().toLocaleString('ar-DZ')}`
  );

  console.log(`✅ إشارة AMD ${signal.type} @ ${signal.price}`);
  saveState(state);
}

const condLabels = {
  asiaRangeDefined:    'Asia Range محدد',
  manipulationUp:      'Manipulation فوق Asia High (Stop Hunt صاعد)',
  manipulationDown:    'Manipulation تحت Asia Low (Stop Hunt هابط)',
  nySession:           'جلسة NY نشطة (Distribution)',
  priceBelowAsiaHigh:  'السعر عاد تحت Asia High',
  priceAboveAsiaLow:   'السعر عاد فوق Asia Low',
  sweepReverted:       'السعر انعكس بعد الـ Sweep',
};

check().catch(e => { console.error('[Fatal]', e.message); process.exit(1); });
