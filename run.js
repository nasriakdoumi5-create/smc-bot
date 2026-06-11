import { get5mBars, get1hBars } from './data.js';
import { analyze } from './smc.js';
import { getUpcomingHigh, isNewsTime } from './calendar.js';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const SYMBOL  = process.env.SYMBOL || 'MNQ';

if (!TOKEN || !CHAT_ID) { console.error('❌ TOKEN مفقود'); process.exit(1); }

const STATE_FILE = '/tmp/smc_state.json';
function loadState() {
  try { if (existsSync(STATE_FILE)) return JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch {}
  return { lastSignalKey: '', lastSignalTime: 0, lastNewsKey: '' };
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
  rsiOversold:'RSI مبالغ هبوط', rsiOverbought:'RSI مبالغ صعود',
};

async function check() {
  const state = loadState();
  const upcoming = await getUpcomingHigh(15).catch(() => []);
  for (const e of upcoming) {
    const key = e.date + e.title;
    if (key !== state.lastNewsKey) {
      state.lastNewsKey = key;
      const mins = Math.max(1, Math.round((new Date(e.date) - Date.now()) / 60000));
      await tg(`⚠️ <b>خبر مهم — ${e.title}</b>\n🕐 خلال <b>${mins} دقيقة</b> | 🔴 High Impact\n⛔ <b>لا تدخل الصفقة</b>`).catch(() => {});
    }
  }

  const [bars5m, bars1h] = await Promise.all([get5mBars(SYMBOL), get1hBars(SYMBOL)]);
  const result = analyze(bars5m, bars1h);
  if (result.error) { console.log('[SMC]', result.error); saveState(state); return; }

  const { price, signal, htfTrend, session, scoreLong, scoreShort, rsi } = result;
  console.log(`${SYMBOL} @ ${price} | ${htfTrend} L:${scoreLong}/7 S:${scoreShort}/7 RSI:${rsi}`);

  // إرسال حالة كل ساعة حتى يعرف المستخدم البوت شغال
  const nowH = Date.now();
  const lastHeartbeat = state.lastHeartbeat || 0;
  if (nowH - lastHeartbeat > 60 * 60 * 1000) {
    state.lastHeartbeat = nowH;
    const sessionIcon = session ? '🟢 نشطة' : '🔴 مغلقة';
    await tg(
`🤖 <b>SMC Bot — تقرير الساعة</b>

📊 ${SYMBOL} @ <b>${price}</b>
📈 HTF Trend: <b>${htfTrend}</b>
🕐 الجلسة: ${sessionIcon}
⬆️ نقاط LONG:  ${scoreLong}/7
⬇️ نقاط SHORT: ${scoreShort}/7
📉 RSI: ${rsi}

${signal ? `⚡ <b>إشارة ${signal.type} جاهزة — تحقق من الرسالة التالية</b>` : '⏳ لا توجد إشارة بعد — البوت يراقب...'}`
    ).catch(() => {});
  }

  if (!signal) { saveState(state); return; }

  const sigKey = `${signal.type}_${Math.round(signal.price / 10)}`;
  const now = Date.now();
  if (sigKey === state.lastSignalKey && (now - state.lastSignalTime) < 30 * 60 * 1000) {
    console.log(`تكرار — تجاهل`); saveState(state); return;
  }
  if (await isNewsTime()) { console.log(`خبر جارٍ — تجاهل`); saveState(state); return; }

  state.lastSignalKey = sigKey;
  state.lastSignalTime = now;

  const isBull = signal.type === 'LONG';
  const scoreBar = '●'.repeat(signal.score) + '○'.repeat(7 - signal.score);
  const risk = Math.abs(signal.price - signal.sl);
  const rr = risk > 0 ? (Math.abs(signal.tp1 - signal.price) / risk).toFixed(1) : '?';
  const condList = Object.entries(signal.conditions).map(([k,v]) => `${v?'✅':'❌'} ${condLabels[k]||k}`).join('\n');

  await tg(`${isBull?'📈':'📉'} <b>إشارة ${signal.type} — NQ Futures</b>

💰 السعر:  <b>${signal.price}</b>
🛑 SL:     <b>${signal.sl}</b>  (${risk.toFixed(0)} نقطة)
🎯 TP1:    <b>${signal.tp1}</b>
🎯 TP2:    <b>${signal.tp2}</b>
⚖️  R:R:   <b>${rr}:1</b>

⭐ الجودة: <b>${signal.score}/7</b>  ${scoreBar}
📊 RSI:    ${signal.rsi}  |  ATR: ${signal.atr}

${condList}

<i>⚠️ القرار النهائي لك</i>
🕐 ${new Date().toLocaleString('ar-DZ')}`);

  console.log(`✅ إشعار — ${signal.type} @ ${signal.price} | ${signal.score}/7`);
  saveState(state);
}

check().catch(e => { console.error('[Fatal]', e.message); process.exit(1); });
