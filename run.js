import { get5mBars } from './data.js';
import { analyzeAMD } from './amd.js';
import { analyzeOrderFlow, orderFlowText } from './orderflow.js';
import { getUpcomingHigh, isNewsTime } from './calendar.js';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

if (!TOKEN || !CHAT_ID) { console.error('❌ TOKEN مفقود'); process.exit(1); }

// ── الرموز المراقبة ───────────────────────────
const SYMBOLS = [
  { id: 'MNQ', name: 'Micro Nasdaq',     emoji: '📊' },
  { id: 'MGC', name: 'Micro Gold',       emoji: '🥇' },
  { id: 'MCL', name: 'Micro Crude Oil',  emoji: '🛢️' },
];

const STATE_FILE = '/tmp/smc_state.json';
function loadState() {
  try { if (existsSync(STATE_FILE)) return JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch {}
  return { signals: {}, lastNewsKey: '', lastHeartbeat: 0 };
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
  asiaRangeDefined:    'Asia Range محدد',
  manipulationUp:      'Manipulation فوق Asia High (Stop Hunt)',
  manipulationDown:    'Manipulation تحت Asia Low (Stop Hunt)',
  nySession:           'جلسة NY نشطة (Distribution)',
  priceBelowAsiaHigh:  'السعر عاد تحت Asia High',
  priceAboveAsiaLow:   'السعر عاد فوق Asia Low',
  sweepReverted:       'السعر انعكس بعد الـ Sweep',
};

// ── تحليل رمز واحد ────────────────────────────
async function checkSymbol(sym, state, newsActive) {
  const bars5m = await get5mBars(sym.id).catch(() => null);
  if (!bars5m) { console.log(`[${sym.id}] فشل جلب البيانات`); return; }

  const result = analyzeAMD(bars5m);
  const of     = analyzeOrderFlow(bars5m);

  if (result.error) { console.log(`[${sym.id}]`, result.error); return; }

  const { price, session, asiaHigh, asiaLow, asiaSize, manipHigh, manipLow, manipPrice, signal } = result;
  const manipTxt = manipHigh ? `🔴 Manip↑${manipPrice}` : manipLow ? `🟢 Manip↓${manipPrice}` : '⏳ لا يوجد';
  console.log(`[${sym.id}] @ ${price} | ${session} | Asia[${asiaLow}-${asiaHigh}] | ${manipTxt}`);

  if (!signal) return;
  if (newsActive) { console.log(`[${sym.id}] خبر جارٍ — تجاهل`); return; }

  // تجنب التكرار 30 دقيقة لكل رمز منفصل
  const sigKey  = `${signal.type}_${Math.round(signal.price / 10)}`;
  const sigState = state.signals[sym.id] || {};
  const nowMs   = Date.now();

  if (sigKey === sigState.lastKey && (nowMs - sigState.lastTime) < 30 * 60 * 1000) {
    console.log(`[${sym.id}] تكرار — تجاهل`);
    return;
  }

  state.signals[sym.id] = { lastKey: sigKey, lastTime: nowMs };

  const isBull  = signal.type === 'LONG';
  const risk    = Math.abs(signal.price - signal.sl);
  const rr      = risk > 0 ? (Math.abs(signal.tp1 - signal.price) / risk).toFixed(1) : '?';
  const ofBlock = orderFlowText(of);
  const condList = Object.entries(signal.conditions)
    .map(([k, v]) => `${v ? '✅' : '❌'} ${condLabels[k] || k}`)
    .join('\n');

  await tg(
`${isBull ? '📈' : '📉'} <b>AMD — ${signal.type} | ${sym.emoji} ${sym.name}</b>

━━━━━━━━━━━━━━━━
🎭 <b>المرحلة: ${signal.phase}</b>
📦 ${signal.manipulation}

━━━━━━━━━━━━━━━━
💰 الدخول:  <b>${signal.price}</b>
🛑 SL:      <b>${signal.sl}</b>  (${risk.toFixed(2)} نقطة)
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

  console.log(`✅ [${sym.id}] إشارة AMD ${signal.type} @ ${signal.price}`);
}

// ══ الدالة الرئيسية ═══════════════════════════
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

  const newsActive = await isNewsTime().catch(() => false);

  // ── Heartbeat كل ساعة ─────────────────────
  const nowMs = Date.now();
  if (nowMs - (state.lastHeartbeat || 0) > 60 * 60 * 1000) {
    state.lastHeartbeat = nowMs;

    // جلب حالة الـ 3 رموز موازياً
    const statuses = await Promise.all(SYMBOLS.map(async sym => {
      const bars = await get5mBars(sym.id).catch(() => null);
      if (!bars) return `${sym.emoji} ${sym.id}: ❌ لا بيانات`;
      const r = analyzeAMD(bars);
      if (r.error) return `${sym.emoji} ${sym.id}: ⚠️ ${r.error}`;
      const manip = r.manipHigh ? `🔴 Manip↑${r.manipPrice}` : r.manipLow ? `🟢 Manip↓${r.manipPrice}` : '⏳ لا يوجد';
      return `${sym.emoji} <b>${sym.id}</b> @ ${r.price}\n   ${r.session} | ${manip}\n   Asia: ${r.asiaLow}–${r.asiaHigh}`;
    }));

    await tg(
`🤖 <b>AMD Bot — تقرير الساعة</b>

${statuses.join('\n\n')}

${newsActive ? '⛔ خبر جارٍ الآن' : '✅ لا أخبار نشطة'}
🕐 ${new Date().toLocaleString('ar-DZ')}`
    ).catch(() => {});
  }

  // ── تحليل الـ 3 رموز موازياً ──────────────
  await Promise.all(SYMBOLS.map(sym => checkSymbol(sym, state, newsActive)));

  saveState(state);
}

check().catch(e => { console.error('[Fatal]', e.message); process.exit(1); });
