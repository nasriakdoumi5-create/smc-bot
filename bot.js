/**
 * ═══════════════════════════════════════════════════
 *   Multi-Symbol Bot — EMA21 Bounce | 3 Timeframes
 *   1H Bias + 15M Structure + 5M Entry
 *   يعمل 24/7 على Railway
 * ═══════════════════════════════════════════════════
 */

import { get5mBars, get15mBars, get1hBars }          from './data.js';
import { analyzeSimple, currentSession }              from './strategy_simple.js';
import { getUpcomingHigh, isNewsTime, todaySummary }  from './calendar.js';
import { createServer }                               from 'http';

// ══ إعدادات ══════════════════════════════════════
const TOKEN    = process.env.TELEGRAM_TOKEN   || '8986679008:AAHmT44SZeoUzdkiaKg-OlnA3NHOonHZ2cw';
const CHAT_ID  = process.env.TELEGRAM_CHAT_ID || '6526134897';
const CHECK_MS = 5 * 60 * 1000;   // كل 5 دقائق
const COOLDOWN = 30 * 60 * 1000;  // 30 دقيقة بين الإشارات

// الرموز المراقَبة (يمكن تغييرها عبر env: SYMBOLS=MNQ,MCL,MGC)
const SYMBOLS = (process.env.SYMBOLS || 'MNQ,MCL').split(',').map(s => s.trim());

// أسماء العرض
const SYMBOL_NAMES = {
  MNQ: 'Micro Nasdaq (MNQ)',
  MGC: 'Micro Gold (MGC)',
  MCL: 'Micro Crude Oil (MCL)',
  MES: 'Micro S&P 500 (MES)',
};

// ══ الحالة (لكل رمز) ══════════════════════════════
const state = {};
for (const sym of SYMBOLS) {
  state[sym] = { lastSignalTime: 0, lastSignalKey: '' };
}

let lastNewsKey = '';
let running     = false;
let stats = { total: 0, long: 0, short: 0, bySymbol: {}, date: '' };

// ══ Telegram ══════════════════════════════════════
async function tg(text) {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' }),
  }).catch(() => null);
  return r?.ok;
}

// ══ تسميات الشروط ════════════════════════════════
const LABELS = {
  htfBull:       '1H اتجاه صاعد (EMA50>EMA200)',
  htfBear:       '1H اتجاه هابط (EMA50<EMA200)',
  mtfNear:       '15M السعر قرب EMA21',
  touchedEma21:  '5M لمس خط EMA21',
  bouncedUp:     '5M ارتداد صاعد من EMA21',
  bouncedDown:   '5M ارتداد هابط من EMA21',
  rsiOk:         'RSI مناسب للدخول',
  pdlSweep:      '⚡ كسح PDL + انعكاس (بونص)',
  pdhSweep:      '⚡ كسح PDH + انعكاس (بونص)',
};
const condLine = (k, v) => `${v ? '✅' : '❌'} ${LABELS[k] || k}`;

// ══ جودة الإشارة ══════════════════════════════════
function quality(score) {
  if (score >= 5) return { stars: '⭐⭐⭐', label: 'ممتازة' };
  if (score >= 4) return { stars: '⭐⭐',   label: 'قوية'   };
  return             { stars: '⭐',     label: 'جيدة'   };
}

// ══ تحذيرات الأخبار ══════════════════════════════
async function checkNews() {
  const events = await getUpcomingHigh(15);
  for (const e of events) {
    const key = e.date + e.title;
    if (key === lastNewsKey) continue;
    lastNewsKey = key;
    const mins = Math.max(1, Math.round((new Date(e.date) - Date.now()) / 60000));
    await tg(
`⚠️ <b>خبر مهم — ${e.title}</b>
🕐 خلال <b>${mins} دقيقة</b>  |  🔴 High Impact
${e.forecast ? `📊 التوقع: ${e.forecast}` : ''}
⛔ <b>لا تدخل — انتظر انتهاء الخبر</b>`
    ).catch(() => {});
  }
}

// ══ فحص رمز واحد ══════════════════════════════════
async function checkSymbol(symbol, t) {
  const [bars5m, bars15m, bars1h] = await Promise.all([
    get5mBars(symbol),
    get15mBars(symbol),
    get1hBars(symbol),
  ]);

  const r = analyzeSimple(bars5m, bars15m, bars1h);

  if (r.error) {
    console.log(`[${t}] ${symbol} ⚠️  ${r.error}`);
    return;
  }

  const session = currentSession();
  console.log(
    `[${t}] ${symbol} @ ${r.price} | ${r.htfTrend} | ${session} | ` +
    `L:${r.scoreLong}/5 S:${r.scoreShort}/5 | RSI:${r.rsi} | ` +
    (r.debug?.reason ? r.debug.reason : '') +
    (r.signal ? ` → 🚨 ${r.signal.type} ${r.signal.score}/5` : '')
  );

  if (!r.signal) return;

  // Cooldown لكل رمز على حدة
  const now    = Date.now();
  const sym    = state[symbol];
  const sigKey = `${r.signal.type}_${Math.round(r.signal.price / 20)}`;
  if (sigKey === sym.lastSignalKey && now - sym.lastSignalTime < COOLDOWN) {
    console.log(`[${t}] ${symbol} ⏳ Cooldown (${Math.round((COOLDOWN - (now - sym.lastSignalTime)) / 60000)} دقيقة باقية)`);
    return;
  }

  if (await isNewsTime()) {
    console.log(`[${t}] ${symbol} 🚫 خبر جارٍ — تجاهل الإشارة`);
    return;
  }

  sym.lastSignalKey  = sigKey;
  sym.lastSignalTime = now;
  stats.total++;
  r.signal.type === 'LONG' ? stats.long++ : stats.short++;
  stats.bySymbol[symbol] = (stats.bySymbol[symbol] || 0) + 1;

  // ══ رسالة Telegram ══════════════════════════
  const sig     = r.signal;
  const isBull  = sig.type === 'LONG';
  const q       = quality(sig.score);
  const risk    = Math.abs(sig.price - sig.sl);
  const rr      = risk > 0 ? (Math.abs(sig.tp1 - sig.price) / risk).toFixed(1) : '?';
  const conds   = Object.entries(sig.conditions).map(([k, v]) => condLine(k, v)).join('\n');
  const name    = SYMBOL_NAMES[symbol] || symbol;

  const pdhLine = sig.pdh ? `📌 PDH: <b>${sig.pdh}</b>  |  PDL: <b>${sig.pdl}</b>` : '';
  const e21Line = sig.e21_15m
    ? `📉 EMA21 → 5M: ${sig.e21_5m}  |  15M: ${sig.e21_15m}`
    : `📉 EMA21 (5M): ${sig.e21_5m}`;

  await tg(
`${isBull ? '📈' : '📉'} <b>${sig.type} — ${name}</b>   ${q.stars} ${q.label}

💰 الدخول:  <b>${sig.price}</b>
🛑 SL:      <b>${sig.sl}</b>   (−${risk.toFixed(0)} نقطة)
🎯 TP1:     <b>${sig.tp1}</b>   (R:R ${rr}:1)
🎯 TP2:     <b>${sig.tp2}</b>   (R:R ${(risk > 0 ? Math.abs(sig.tp2 - sig.price)/risk : 0).toFixed(1)}:1)

${e21Line}
${pdhLine}
📊 RSI: ${sig.rsi}   |   ATR: ${sig.atr}
🕐 ${session}   |   ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}

${conds}

<i>⚠️ إدارة المخاطر: لا تخاطر بأكثر من 1-2% من رأس المال</i>`
  );

  console.log(`[${t}] ✅ إشارة #${stats.total} — ${symbol} ${sig.type} @ ${sig.price} | ${q.label} (${sig.score}/5)`);
}

// ══ الفحص الرئيسي (كل الرموز) ════════════════════
async function check() {
  if (running) return;
  running = true;
  const t = new Date().toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid' });

  try {
    await checkNews();
    // فحص جميع الرموز بالتتابع (لتجنب حظر Yahoo Finance)
    for (const symbol of SYMBOLS) {
      await checkSymbol(symbol, t).catch(err =>
        console.error(`[${t}] ${symbol} ❌ Error:`, err.message)
      );
    }
  } finally {
    running = false;
  }
}

// ══ ملخص يومي الساعة 8:00 صباحاً (توقيت مدريد) ══
async function dailySummary() {
  try {
    const today = new Date().toLocaleDateString('es-ES', { timeZone: 'Europe/Madrid' });
    if (stats.date !== today) { stats = { total: 0, long: 0, short: 0, bySymbol: {}, date: today }; }

    const calSummary = await todaySummary();
    const bySymLine  = Object.entries(stats.bySymbol)
      .map(([s, n]) => `   ${s}: ${n}`).join('\n') || '   لا يوجد';

    await tg(
`🌅 <b>صباح الخير — ملخص اليوم</b>
📅 ${today}

<b>📰 أخبار USD اليوم:</b>
${calSummary}

─────────────────
<b>📊 إشارات أمس:</b>
🔢 الإجمالي: ${stats.total}
📈 LONG:  ${stats.long}   |   📉 SHORT: ${stats.short}
${bySymLine}

🤖 البوت يعمل — فحص كل 5 دقائق
📊 الرموز: ${SYMBOLS.join(', ')}
⏰ 1H Bias + 15M Structure + 5M Entry`
    );
    stats = { total: 0, long: 0, short: 0, bySymbol: {}, date: today };
  } catch (e) { console.error('[Daily]', e.message); }
}

function scheduleDailySummary() {
  const now  = new Date();
  const next = new Date();
  next.setHours(8, 0, 0, 0);
  if (next <= now) next.setDate(next.getDate() + 1);
  setTimeout(() => {
    dailySummary();
    setInterval(dailySummary, 86400000);
  }, next - now);
}

// ══ بدء التشغيل ══════════════════════════════════
console.log('═'.repeat(52));
console.log('  🤖  Multi-Symbol Bot — EMA21 Bounce 3TF');
console.log('═'.repeat(52));
console.log(`  📊 Symbols : ${SYMBOLS.join(', ')}`);
console.log(`  ⏱️  Check   : every 5 minutes`);
console.log(`  ⏸️  Cooldown : 30 minutes per symbol`);
console.log(`  📐 Strategy : 1H Bias + 15M + 5M Entry`);
console.log(`  📱 Chat ID  : ${CHAT_ID}`);
console.log('═'.repeat(52));

tg(`🚀 <b>Trading Bot يعمل الآن</b>

📊 <b>الرموز:</b> ${SYMBOLS.map(s => SYMBOL_NAMES[s] || s).join('\n         ')}
📐 <b>الاستراتيجية:</b> EMA21 Bounce
⏱ <b>3 Timeframes:</b> 1H + 15M + 5M
🔍 <b>فحص:</b> كل 5 دقائق لكل رمز
⏸ <b>Cooldown:</b> 30 دقيقة بين إشارات كل رمز
📰 تقويم اقتصادي مدمج (تجنب الأخبار تلقائياً)

<i>الإشارات تصل هنا مع تقييم الجودة ⭐</i>`).catch(() => {});

dailySummary();
scheduleDailySummary();
check();
setInterval(check, CHECK_MS);

// ══ Health check server (Railway) ════════════════
createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status:   'running',
    symbols:  SYMBOLS,
    session:  currentSession(),
    signals:  stats,
    uptime:   Math.round(process.uptime()),
    time:     new Date().toISOString(),
  }));
}).listen(process.env.PORT || 3000, () => {
  console.log(`  🌐 Health check: port ${process.env.PORT || 3000}`);
});
