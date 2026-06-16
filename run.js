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
  { id: 'NQ', name: 'Nasdaq Futures', emoji: '📊' },
  { id: 'NG', name: 'Natural Gas',    emoji: '🔥' },
];

// مفتاح اليوم بتوقيت مدريد (YYYY-MM-DD)
function todayMadrid() {
  return new Date().toLocaleDateString('sv-SE', { timeZone: 'Europe/Madrid' });
}

const STATE_FILE = '/tmp/smc_state.json';
function loadState() {
  try { if (existsSync(STATE_FILE)) return JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch {}
  return { dailySignals: {}, lastNewsKey: '', lastHeartbeat: 0 };
}
function saveState(s) { try { writeFileSync(STATE_FILE, JSON.stringify(s)); } catch {} }

async function tg(text) {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' })
  });
  return r.ok;
}

// ── تحليل رمز واحد ────────────────────────────
async function checkSymbol(sym, state, newsActive) {
  const bars = await get5mBars(sym.id).catch(() => null);
  if (!bars) { console.log(`[${sym.id}] فشل جلب البيانات`); return; }

  const result = analyzeAMD(bars);
  const of     = analyzeOrderFlow(bars);

  if (result.error) { console.log(`[${sym.id}]`, result.error); return; }

  const {
    price, session, asiaHigh, asiaLow, asiaSize,
    mUp, mDn, mUpClosed, mDnClosed, manipPrice,
    dispBull, dispBear, htfBias, longScore, shortScore, signal,
  } = result;

  const manipTxt = mUp
    ? `🔴 Hunt↑${manipPrice ?? asiaHigh}`
    : mDn ? `🟢 Hunt↓${manipPrice ?? asiaLow}` : '⏳ لا يوجد';

  console.log(`[${sym.id}] @ ${price} | ${session} | Asia[${asiaLow}–${asiaHigh}] | ${manipTxt} | L:${longScore} S:${shortScore}`);

  if (!signal) return;
  if (newsActive) { console.log(`[${sym.id}] خبر جارٍ — تجاهل`); return; }

  // إشارة واحدة فقط يومياً لكل رمز
  const today = todayMadrid();
  if (!state.dailySignals) state.dailySignals = {};
  const symDay = state.dailySignals[sym.id];

  if (symDay && symDay.date === today) {
    console.log(`[${sym.id}] إشارة اليوم أُرسلت مسبقاً (${symDay.type} @ ${symDay.price}) — تجاهل`);
    return;
  }

  // تسجيل الإشارة
  state.dailySignals[sym.id] = { date: today, type: signal.type, price: signal.price };

  const isBull  = signal.type === 'LONG';
  const risk    = Math.abs(signal.price - signal.sl);
  const rr      = risk > 0 ? (Math.abs(signal.tp1 - signal.price) / risk).toFixed(1) : '?';
  const ofBlock = orderFlowText(of);

  const htfLine  = htfBias === 'bull' ? '📈 HTF: صاعد ✅' : htfBias === 'bear' ? '📉 HTF: هابط ✅' : '📊 HTF: محايد';
  const dispLine = isBull
    ? `${dispBull ? '✅' : '❌'} Displacement صعودي`
    : `${dispBear ? '✅' : '❌'} Displacement هبوطي`;
  const huntLine = isBull
    ? `${mDn && mDnClosed ? '✅' : '❌'} Hunt DN + إغلاق داخل النطاق`
    : `${mUp && mUpClosed ? '✅' : '❌'} Hunt UP + إغلاق داخل النطاق`;

  await tg(
`${isBull ? '📈' : '📉'} <b>AMD SNIPER — ${signal.type} | ${sym.emoji} ${sym.name}</b>

━━━━━━━━━━━━━━━━
🎭 <b>المرحلة: ${signal.phase}</b>
📦 ${signal.manipulation}

━━━━━━━━━━━━━━━━
💰 الدخول:  <b>${signal.price}</b>
🛑 SL:      <b>${signal.sl}</b>  (${risk.toFixed(4)} نقطة)
🎯 TP1:     <b>${signal.tp1}</b>  (1.5:1)
🎯 TP2:     <b>${signal.tp2}</b>  (3:1)
⚖️  R:R:    <b>${rr}:1</b>

━━━━━━━━━━━━━━━━
📊 Asia Range: ${asiaLow} – ${asiaHigh}  (${asiaSize} نقطة)
🏆 Score: <b>${signal.score}</b>

${htfLine}
${huntLine}
${dispLine}${ofBlock ? '\n\n' + ofBlock : ''}

<i>⚠️ إشارة واحدة يومياً — القرار النهائي لك</i>
🕐 ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}`
  );

  console.log(`✅ [${sym.id}] إشارة AMD SNIPER ${signal.type} @ ${signal.price} | Score: ${signal.score}`);
}

// ══ الدالة الرئيسية ═══════════════════════════
async function check() {
  const state = loadState();

  // ── أخبار ─────────────────────────────────
  const upcoming = await getUpcomingHigh(15).catch(() => []);
  for (const e of upcoming) {
    const key = e.date + e.title;
    if (key !== state.lastNewsKey) {
      state.lastNewsKey = key;
      const mins = Math.max(1, Math.round((new Date(e.date) - Date.now()) / 60000));
      await tg(
        `⚠️ <b>خبر مهم — ${e.title}</b>\n🕐 خلال <b>${mins} دقيقة</b> | 🔴 High Impact\n⛔ <b>لا تدخل الصفقة</b>`
      ).catch(() => {});
    }
  }

  const newsActive = await isNewsTime().catch(() => false);

  // ── Heartbeat كل ساعة ──────────────────────
  const nowMs = Date.now();
  if (nowMs - (state.lastHeartbeat || 0) > 60 * 60 * 1000) {
    state.lastHeartbeat = nowMs;

    const statuses = await Promise.all(SYMBOLS.map(async sym => {
      const bars = await get5mBars(sym.id).catch(() => null);
      if (!bars) return `${sym.emoji} ${sym.id}: ❌ لا بيانات`;
      const r = analyzeAMD(bars);
      if (r.error) return `${sym.emoji} ${sym.id}: ⚠️ ${r.error}`;
      const manip = r.mUp
        ? `🔴 Hunt↑${r.manipPrice ?? r.asiaHigh}`
        : r.mDn ? `🟢 Hunt↓${r.manipPrice ?? r.asiaLow}` : '⏳ لا يوجد';
      const today = todayMadrid();
      const sent  = state.dailySignals?.[sym.id]?.date === today
        ? `📨 إشارة أُرسلت: ${state.dailySignals[sym.id].type}`
        : '⏳ لا إشارة بعد';
      return `${sym.emoji} <b>${sym.id}</b> @ ${r.price}\n   ${r.session} | ${manip}\n   Asia: ${r.asiaLow}–${r.asiaHigh} | L:${r.longScore} S:${r.shortScore}\n   ${sent}`;
    }));

    await tg(
`🤖 <b>AMD SNIPER Bot — تقرير الساعة</b>

${statuses.join('\n\n')}

${newsActive ? '⛔ خبر جارٍ الآن' : '✅ لا أخبار نشطة'}
🕐 ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}`
    ).catch(() => {});
  }

  // ── تحليل الرموز الثلاثة موازياً ───────────
  await Promise.all(SYMBOLS.map(sym => checkSymbol(sym, state, newsActive)));

  saveState(state);
}

check().catch(e => { console.error('[Fatal]', e.message); process.exit(1); });
