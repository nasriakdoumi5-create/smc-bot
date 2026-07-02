import { get5mBars, get1hBars } from './data.js';
import { analyze }             from './smc.js';
import { getDOMSnapshot, domSummaryText } from './tradovate.js';
import { analyzeOrderFlow, orderFlowText } from './orderflow.js';
import { getUpcomingHigh, isNewsTime }     from './calendar.js';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
if (!TOKEN || !CHAT_ID) { console.error('❌ TOKEN مفقود'); process.exit(1); }

const STATE_FILE = '/tmp/smc_state.json';
function loadState() {
  try { if (existsSync(STATE_FILE)) return JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch {}
  return { lastSignalKey: '', lastSignalTime: 0, lastHeartbeat: 0, lastNewsKey: '' };
}
function saveState(s) { try { writeFileSync(STATE_FILE, JSON.stringify(s)); } catch {} }

async function tg(text) {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' }),
  });
  return r.ok;
}

// ── ساعات التداول: 06:00 → 20:00 UTC فقط ───
function isTradingHours() {
  const h = new Date().getUTCHours();
  return h >= 6 && h < 20;
}

// ── نسبة النجاح من الـ score (10 شروط) ───────
function winRate(score) {
  // 5/10 = 50%، 7/10 = 70%، 10/10 = 95%
  return Math.min(95, Math.round(50 + (score - 4) * 7));
}

// ── تسمية الجلسة ─────────────────────────────
function sessionName() {
  const h = new Date().getUTCHours();
  if (h >= 6  && h < 8)  return 'Asia Close / London Pre';
  if (h >= 8  && h < 13) return 'London';
  if (h >= 13 && h < 17) return 'New York';
  if (h >= 17 && h < 20) return 'NY Late';
  return 'Off Hours';
}

async function check() {
  const state = loadState();
  const now   = Date.now();

  // ── أخبار مهمة ───────────────────────────────
  const upcoming = await getUpcomingHigh(15).catch(() => []);
  for (const e of upcoming) {
    const key = e.date + e.title;
    if (key !== state.lastNewsKey) {
      state.lastNewsKey = key;
      const mins = Math.max(1, Math.round((new Date(e.date) - now) / 60000));
      await tg(`⚠️ <b>خبر مهم — ${e.title}</b>\n🕐 خلال <b>${mins} دقيقة</b>\n⛔ لا تدخل الصفقة`).catch(() => {});
    }
  }

  // ── خارج ساعات التداول ───────────────────────
  if (!isTradingHours()) {
    console.log('[MNQ] خارج ساعات التداول (06:00-20:00 UTC)');
    saveState(state);
    return;
  }

  // ── جلب البيانات ─────────────────────────────
  const [bars5m, bars1h] = await Promise.all([
    get5mBars('MNQ').catch(() => null),
    get1hBars('MNQ').catch(() => null),
  ]);

  if (!bars5m || !bars1h) {
    console.log('[MNQ] فشل جلب البيانات');
    saveState(state);
    return;
  }

  // ── Order Flow & DOM ─────────────────────────
  const of  = analyzeOrderFlow(bars5m);
  const dom = await getDOMSnapshot(process.env.TRADOVATE_SYMBOL || 'NQM6').catch(() => null);

  // ── تحليل SMC / ICT ──────────────────────────
  const result = analyze(bars5m, bars1h, dom, of);
  if (result.error) { console.log('[MNQ]', result.error); saveState(state); return; }

  const { price, htfTrend, scoreLong, scoreShort, signal, atr, rsi } = result;
  console.log(`[MNQ] @ ${price} | ${htfTrend} | Long:${scoreLong}/10 Short:${scoreShort}/10 | RSI:${rsi}`);

  // ── Heartbeat كل ساعة ────────────────────────
  if (now - (state.lastHeartbeat || 0) > 60 * 60 * 1000) {
    state.lastHeartbeat = now;
    const domTxt = domSummaryText(dom);
    const ofTxt  = orderFlowText(of);
    await tg(
`🤖 <b>MNQ Council — تقرير ${sessionName()}</b>

💹 السعر: <b>${price}</b>
📈 HTF: <b>${htfTrend}</b>
📊 Long Score: ${scoreLong}/10 | Short Score: ${scoreShort}/10
⚡ ATR: ${atr} | RSI: ${rsi}
${domTxt ? '\n' + domTxt : ''}${ofTxt ? '\n' + ofTxt : ''}

🕐 ${new Date().toUTCString()}`
    ).catch(() => {});
  }

  // ── إشارة فقط ≥ 70% ─────────────────────────
  if (!signal) { console.log('[MNQ] لا إشارة كافية'); saveState(state); return; }

  const newsActive = await isNewsTime().catch(() => false);
  if (newsActive) { console.log('[MNQ] خبر جارٍ — تجاهل'); saveState(state); return; }

  const wr  = winRate(signal.score);
  if (wr < 70) { console.log(`[MNQ] نسبة نجاح ${wr}% — دون 70%`); saveState(state); return; }

  // ── تجنب التكرار (30 دقيقة) ──────────────────
  const sigKey = `${signal.type}_${Math.round(signal.price / 5)}`;
  if (sigKey === state.lastSignalKey && (now - state.lastSignalTime) < 30 * 60 * 1000) {
    console.log('[MNQ] تكرار — تجاهل');
    saveState(state);
    return;
  }
  state.lastSignalKey  = sigKey;
  state.lastSignalTime = now;

  const isBull  = signal.type === 'LONG';
  const risk    = Math.abs(signal.price - signal.sl);
  const domText = domSummaryText(dom);
  const ofText  = orderFlowText(of);

  // ── قائمة الشروط المحققة ──────────────────────
  const condNames = {
    htfBull: 'HTF صاعد', htfBear: 'HTF هابط',
    sessionOk: 'الجلسة نشطة',
    recentSweepDown: 'سحب سيولة ↓', recentSweepUp: 'سحب سيولة ↑',
    inBullOB: 'Order Block صاعد', inBearOB: 'Order Block هابط',
    recentBullFVG: 'FVG صاعد', recentBearFVG: 'FVG هابط',
    fibOTE_bull: 'Fibonacci OTE ↑', fibOTE_bear: 'Fibonacci OTE ↓',
    rsiOversold: 'RSI مبالغ هبوطه', rsiOverbought: 'RSI مبالغ صعوده',
    positiveDelta: 'Delta إيجابي', negativeDelta: 'Delta سلبي',
    ofBuyImbalance: 'Stacked Buy', ofSellImbalance: 'Stacked Sell',
    bullDivergence: 'Divergence صاعد', bearDivergence: 'Divergence هابط',
  };
  const condList = Object.entries(signal.conditions)
    .map(([k, v]) => `${v ? '✅' : '❌'} ${condNames[k] || k}`)
    .join('\n');

  await tg(
`${isBull ? '🟢' : '🔴'} <b>${signal.type} — MNQ</b>  |  ${sessionName()}

━━━━━━━━━━━━━━━━
💰 الدخول:  <b>${signal.price}</b>
🛑 SL:      <b>${signal.sl}</b>
🎯 TP1:     <b>${signal.tp1}</b>  (+$${Math.round(risk * 2 * 2)})
🎯 TP2:     <b>${signal.tp2}</b>  (+$${Math.round(risk * 4 * 2)})
⚖️  RR:     <b>2:1</b>
📊 نجاح:    <b>${wr}%</b>  (${signal.score}/10 شروط)

━━━━━━━━━━━━━━━━
${condList}
${domText ? '\n' + domText : ''}${ofText ? '\n' + ofText : ''}

⚡ ATR: ${atr} | RSI: ${rsi}
<i>⚠️ القرار النهائي لك — المجلس يقترح فقط</i>
🕐 ${new Date().toUTCString()}`
  );

  console.log(`✅ [MNQ] إشارة ${signal.type} @ ${signal.price} | ${wr}% | ${signal.score}/10`);
  saveState(state);
}

check().catch(e => { console.error('[Fatal]', e.message); process.exit(1); });
