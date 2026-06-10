/**
 * ════════════════════════════════════════════════
 *   SMC Elite Bot — مستقل 100% بدون TradingView
 *   يعمل 24/7 على السحابة المجانية (Railway)
 * ════════════════════════════════════════════════
 */

import { get5mBars, get1hBars }                    from './data.js';
import { analyze }                                  from './smc.js';
import { getUpcomingHigh, isNewsTime, todaySummary } from './calendar.js';

// ══ إعدادات ══════════════════════════════════
const TOKEN   = process.env.TELEGRAM_TOKEN   || '8986679008:AAHmT44SZeoUzdkiaKg-OlnA3NHOonHZ2cw';
const CHAT_ID = process.env.TELEGRAM_CHAT_ID || '6526134897';
const SYMBOL  = process.env.SYMBOL           || 'MNQ';
const CHECK_MS = 5 * 60 * 1000;   // فحص كل 5 دقائق (= شمعة 5m جديدة)

// ══ State ════════════════════════════════════
let lastSignalKey = '';   // type+price لتجنب التكرار
let lastNewsKey   = '';
let totalToday    = 0;
let running       = false;

// ══ Telegram ══════════════════════════════════
async function tg(text) {
  await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' })
  });
}

// ══ تحذيرات الأخبار ═══════════════════════════
async function checkNews() {
  const upcoming = await getUpcomingHigh(15);
  for (const e of upcoming) {
    const key = e.date + e.title;
    if (key === lastNewsKey) continue;
    lastNewsKey = key;
    const mins = Math.max(1, Math.round((new Date(e.date) - Date.now()) / 60000));
    await tg(
`⚠️ <b>خبر مهم — ${e.title}</b>
🕐 خلال <b>${mins} دقيقة</b>  |  🔴 High Impact
${e.forecast ? `📊 التوقع: ${e.forecast}` : ''}
⛔ <b>لا تدخل الصفقة — انتظر الخبر</b>`
    ).catch(() => {});
  }
}

// ══ الفحص الرئيسي ════════════════════════════
async function check() {
  if (running) return;
  running = true;

  try {
    await checkNews();

    // جلب البيانات
    const [bars5m, bars1h] = await Promise.all([
      get5mBars(SYMBOL),
      get1hBars(SYMBOL)
    ]);

    const result = analyze(bars5m, bars1h);
    if (result.error) { console.log('[SMC]', result.error); return; }

    const { price, signal, htfTrend, session, scoreLong, scoreShort, rsi } = result;
    const t = new Date().toLocaleTimeString('ar-DZ');
    console.log(`[${t}] ${SYMBOL} @ ${price} | Trend:${htfTrend} Session:${session} L:${scoreLong}/7 S:${scoreShort}/7 RSI:${rsi}`);

    if (!signal) return;

    // تجنب التكرار — مفتاح فريد لكل إشارة
    const sigKey = `${signal.type}_${Math.round(signal.price / 10)}`;
    if (sigKey === lastSignalKey) return;

    // لا إشارات وقت الأخبار
    if (await isNewsTime()) {
      console.log(`[${t}] 🚫 إشارة ${signal.type} — خبر جارٍ، تجاهل`);
      return;
    }

    lastSignalKey = sigKey;
    totalToday++;

    const isBull  = signal.type === 'LONG';
    const scoreBar = '●'.repeat(signal.score) + '○'.repeat(7 - signal.score);
    const risk     = Math.abs(signal.price - signal.sl);
    const rrActual = risk > 0 ? (Math.abs(signal.tp1 - signal.price) / risk).toFixed(1) : '?';

    // الشروط المتحققة
    const cond = signal.conditions;
    const condList = Object.entries(cond)
      .map(([k, v]) => `${v ? '✅' : '❌'} ${condLabel(k)}`)
      .join('\n');

    await tg(
`${isBull ? '📈' : '📉'} <b>إشارة ${signal.type} — NQ Futures</b>

💰 السعر:  <b>${signal.price}</b>
🛑 SL:     <b>${signal.sl}</b>  (${risk.toFixed(0)} نقطة)
🎯 TP1:    <b>${signal.tp1}</b>
🎯 TP2:    <b>${signal.tp2}</b>
⚖️  R:R:   <b>${rrActual}:1</b>

⭐ الجودة: <b>${signal.score}/7</b>  ${scoreBar}
📊 RSI:    ${signal.rsi}  |  ATR: ${signal.atr}

${condList}

<i>⚠️ القرار النهائي لك</i>
🕐 ${new Date().toLocaleString('ar-DZ')}`
    );

    console.log(`[${t}] ✅ إشعار #${totalToday} — ${signal.type} @ ${signal.price} | ${signal.score}/7`);

  } catch (err) {
    console.error('[Error]', err.message);
  } finally {
    running = false;
  }
}

function condLabel(key) {
  const labels = {
    htfBull: 'HTF Trend صاعد', htfBear: 'HTF Trend هابط',
    sessionOk: 'جلسة نشطة',
    recentSweepDown: 'Liquidity Sweep هبوطي', recentSweepUp: 'Liquidity Sweep صاعد',
    inBullOB: 'داخل Order Block صاعد', inBearOB: 'داخل Order Block هابط',
    recentBullFVG: 'Fair Value Gap صاعد', recentBearFVG: 'Fair Value Gap هابط',
    fibOTE_bull: 'Fibonacci OTE (61-78%)', fibOTE_bear: 'Fibonacci OTE (61-78%)',
    rsiOversold: 'RSI مبالغ هبوط', rsiOverbought: 'RSI مبالغ صعود',
  };
  return labels[key] || key;
}

// ══ ملخص يومي الساعة 8 صباحاً ════════════════
async function dailySummary() {
  try {
    const summary = await todaySummary();
    await tg(
`📅 <b>صباح الخير — أخبار USD اليوم</b>

${summary}

─────────────────
🤖 البوت يعمل — فحص كل 5 دقائق
📊 إشارات أمس: ${totalToday}`
    );
    totalToday = 0;
  } catch (e) { console.error('[Daily]', e.message); }
}

function scheduleDailySummary() {
  const now  = new Date();
  const next = new Date();
  next.setHours(8, 0, 0, 0);
  if (next <= now) next.setDate(next.getDate() + 1);
  setTimeout(() => { dailySummary(); setInterval(dailySummary, 86400000); }, next - now);
}

// ══ بدء التشغيل ═══════════════════════════════
console.log('═'.repeat(50));
console.log('  🤖  SMC Elite Bot — Cloud Mode');
console.log('═'.repeat(50));
console.log(`  📊 Symbol:  ${SYMBOL} (NQ Futures)`);
console.log(`  ⏱️  Check:   every 5 minutes`);
console.log(`  📱 Chat ID: ${CHAT_ID}`);
console.log('═'.repeat(50));

tg(`🚀 <b>SMC Elite Bot يعمل على السحابة</b>

✅ بدون TradingView Desktop
📊 بيانات: Yahoo Finance (NQ Futures)
⏱️ فحص كل 5 دقائق
📰 تقويم اقتصادي مدمج

<i>الإشارات تصل هنا مباشرة 24/7</i>`).catch(() => {});

dailySummary();
scheduleDailySummary();

check();
setInterval(check, CHECK_MS);

// ── Keep-alive للـ Railway (منع النوم) ──────
import { createServer } from 'http';
createServer((req, res) => {
  res.writeHead(200);
  res.end(JSON.stringify({ status: 'running', symbol: SYMBOL, totalToday, time: new Date().toISOString() }));
}).listen(process.env.PORT || 3000, () => {
  console.log(`  🌐 HTTP server on port ${process.env.PORT || 3000}`);
});
