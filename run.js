/**
 * SMC Elite — GitHub Actions Runner
 * يفحص MNQ + MGC + MCL في كل دورة
 */

import { get5mBars, get1hBars }                    from './data.js';
import { analyze }                                  from './smc.js';
import { getUpcomingHigh, isNewsTime }              from './calendar.js';
import { readFileSync, writeFileSync, existsSync }  from 'fs';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const SYMBOLS = ['MNQ', 'MGC', 'MCL'];

if (!TOKEN || !CHAT_ID) {
  console.error('❌ TELEGRAM_TOKEN أو TELEGRAM_CHAT_ID غير موجود');
  process.exit(1);
}

const STATE_FILE = '/tmp/smc_state.json';

function loadState() {
  try {
    if (existsSync(STATE_FILE)) return JSON.parse(readFileSync(STATE_FILE, 'utf8'));
  } catch {}
  return { signals: {}, lastNewsKey: '' };
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
  MNQ: 'Micro Nasdaq',
  MGC: 'Micro Gold',
  MCL: 'Micro Crude Oil',
};

const condLabels = {
  htfBull:'HTF Trend صاعد', htfBear:'HTF Trend هابط',
  sessionOk:'جلسة نشطة',
  recentSweepDown:'Liquidity Sweep هبوطي', recentSweepUp:'Liquidity Sweep صاعد',
  inBullOB:'Order Block صاعد', inBearOB:'Order Block هابط',
  recentBullFVG:'Fair Value Gap صاعد', recentBearFVG:'Fair Value Gap هابط',
  fibOTE_bull:'Fibonacci OTE (61-78%)', fibOTE_bear:'Fibonacci OTE (61-78%)',
  rsiOversold:'RSI مبالغ هبوط', rsiOverbought:'RSI مبالغ صعود',
};

async function checkSymbol(symbol, state) {
  const [bars5m, bars1h] = await Promise.all([
    get5mBars(symbol),
    get1hBars(symbol)
  ]);

  const result = analyze(bars5m, bars1h);
  if (result.error) { console.log(`[${symbol}]`, result.error); return; }

  const { price, signal, htfTrend, session, scoreLong, scoreShort, rsi } = result;
  const t = new Date().toLocaleTimeString('ar-DZ');
  console.log(`[${t}] ${symbol} @ ${price} | ${htfTrend} L:${scoreLong}/7 S:${scoreShort}/7 RSI:${rsi}`);

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

  if (await isNewsTime()) {
    console.log(`[${symbol}] خبر جارٍ — تجاهل`);
    return;
  }

  state.signals[symbol] = { key: sigKey, time: now };

  const isBull   = signal.type === 'LONG';
  const scoreBar = '●'.repeat(signal.score) + '○'.repeat(7 - signal.score);
  const risk     = Math.abs(signal.price - signal.sl);
  const rr       = risk > 0 ? (Math.abs(signal.tp1 - signal.price) / risk).toFixed(1) : '?';
  const condList = Object.entries(signal.conditions)
    .map(([k, v]) => `${v ? '✅' : '❌'} ${condLabels[k] || k}`)
    .join('\n');

  await tg(
`${isBull ? '📈' : '📉'} <b>إشارة ${signal.type} — ${symbolNames[symbol] || symbol}</b>

💰 السعر:  <b>${signal.price}</b>
🛑 SL:     <b>${signal.sl}</b>  (${risk.toFixed(0)} نقطة)
🎯 TP1:    <b>${signal.tp1}</b>  (+${Math.abs(signal.tp1 - signal.price).toFixed(0)} نقطة)
🎯 TP2:    <b>${signal.tp2}</b>  (+${Math.abs(signal.tp2 - signal.price).toFixed(0)} نقطة)
🎯 TP3:    <b>${signal.tp3}</b>  (+${Math.abs(signal.tp3 - signal.price).toFixed(0)} نقطة)
⚖️  R:R:   <b>${rr}</b>

⭐ الجودة: <b>${signal.score}/7</b>  ${scoreBar}
📊 RSI:    ${signal.rsi}  |  ATR: ${signal.atr}

${condList}

<i>⚠️ القرار النهائي لك</i>
🕐 ${new Date().toLocaleString('ar-DZ')}`
  );

  console.log(`[${t}] ✅ إشعار ${symbol} — ${signal.type} @ ${signal.price} | ${signal.score}/7`);
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
      await tg(
`⚠️ <b>خبر مهم — ${e.title}</b>
🕐 خلال <b>${mins} دقيقة</b>  |  🔴 High Impact
⛔ <b>لا تدخل الصفقة — انتظر الخبر</b>`
      ).catch(() => {});
    }
  }

  // فحص الثلاثة بالتوازي
  await Promise.all(SYMBOLS.map(s => checkSymbol(s, state).catch(e => console.error(`[${s}]`, e.message))));

  saveState(state);
}

main().catch(e => { console.error('[Fatal]', e.message); process.exit(1); });
