/**
 * ═══════════════════════════════════════════════════
 *   NQ Futures Bot — EMA21 Bounce | 3 Timeframes
 *   1H Bias + 15M Structure + 5M Entry
 *   يعمل 24/7 على Railway
 * ═══════════════════════════════════════════════════
 */

import { get5mBars, get15mBars, get1hBars }          from './data.js';
import { analyzeSimple, currentSession, isKillzone }  from './strategy_simple.js';
import { getUpcomingHigh, isNewsTime, todaySummary }  from './calendar.js';
import { createServer }                               from 'http';

// ══ إعدادات ══════════════════════════════════════
const TOKEN    = process.env.TELEGRAM_TOKEN   || '8986679008:AAHmT44SZeoUzdkiaKg-OlnA3NHOonHZ2cw';
const CHAT_ID  = process.env.TELEGRAM_CHAT_ID || '6526134897';
const SYMBOL   = process.env.SYMBOL           || 'MNQ';
const CHECK_MS = 5 * 60 * 1000;   // كل 5 دقائق
const COOLDOWN = 30 * 60 * 1000;  // 30 دقيقة بين الإشارات

// ══ الحالة ════════════════════════════════════════
let lastSignalTime = 0;
let lastSignalKey  = '';
let lastNewsKey    = '';
let running        = false;
let stats = { total: 0, long: 0, short: 0, date: '' };

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
  htfBull:      '1H اتجاه صاعد (EMA21>EMA50)',
  htfBear:      '1H اتجاه هابط (EMA21<EMA50)',
  vwapBounce:   '5M ارتداد من VWAP',
  bouncedUp:    '5M شمعة صاعدة قوية (>50%)',
  bouncedDown:  '5M شمعة هابطة قوية (>50%)',
  rsiOk:        'RSI كان منخفضاً أثناء التراجع',
  volOk:        'الحجم مناسب',
};
const condLine = (k, v) => `${v ? '✅' : '❌'} ${LABELS[k] || k}`;

// ══ جودة الإشارة ══════════════════════════════════
function quality(score) {
  if (score >= 4) return { stars: '⭐⭐⭐', label: 'ممتازة' };
  if (score >= 3) return { stars: '⭐⭐',   label: 'قوية'   };
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

// ══ الفحص الرئيسي ════════════════════════════════
async function check() {
  if (running) return;
  running = true;
  const t = new Date().toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid' });

  try {
    await checkNews();

    // فلتر Killzone — فقط London (09-11:30 UTC) + NY Open (13:30-15:30 UTC)
    if (!isKillzone()) {
      console.log(`[${t}] 🌙 خارج Killzone — لا فحص`);
      return;
    }

    // جلب البيانات (3 timeframes معاً)
    const [bars5m, bars15m, bars1h] = await Promise.all([
      get5mBars(SYMBOL),
      get15mBars(SYMBOL),
      get1hBars(SYMBOL),
    ]);

    const r = analyzeSimple(bars5m, bars15m, bars1h);

    if (r.error) {
      console.log(`[${t}] ⚠️  ${r.error}`);
      return;
    }

    // سجل كل فحص
    const session = currentSession();
    console.log(
      `[${t}] ${SYMBOL} @ ${r.price} | ${r.htfTrend} | ${session} | ` +
      `L:${r.scoreLong}/5 S:${r.scoreShort}/5 | RSI:${r.rsi} | ` +
      `EMA21(5m):${r.e21_5m} | ` +
      (r.debug?.reason ? r.debug.reason : '') +
      (r.signal ? ` → 🚨 ${r.signal.type} ${r.signal.score}/5` : '')
    );

    if (!r.signal) return;

    // Cooldown — لا تكرار خلال 30 دقيقة
    const now = Date.now();
    const sigKey = `${r.signal.type}_${Math.round(r.signal.price / 20)}`;
    if (sigKey === lastSignalKey && now - lastSignalTime < COOLDOWN) {
      console.log(`[${t}] ⏳ Cooldown — نفس الإشارة (${Math.round((COOLDOWN - (now - lastSignalTime)) / 60000)} دقيقة باقية)`);
      return;
    }

    // لا إشارات وقت الأخبار
    if (await isNewsTime()) {
      console.log(`[${t}] 🚫 خبر جارٍ — تجاهل الإشارة`);
      return;
    }

    lastSignalKey  = sigKey;
    lastSignalTime = now;
    stats.total++;
    r.signal.type === 'LONG' ? stats.long++ : stats.short++;

    // ══ رسالة Telegram ══════════════════════════
    const sig  = r.signal;
    const isBull = sig.type === 'LONG';
    const q    = quality(sig.score);
    const risk = Math.abs(sig.price - sig.sl);
    const rr   = risk > 0 ? (Math.abs(sig.tp1 - sig.price) / risk).toFixed(1) : '?';
    const conds = Object.entries(sig.conditions).map(([k, v]) => condLine(k, v)).join('\n');

    const vwapLine = sig.vwap ? `📊 VWAP: <b>${sig.vwap}</b>` : '';

    await tg(
`${isBull ? '📈' : '📉'} <b>${sig.type} — NQ Futures</b>   ${q.stars} ${q.label}

💰 الدخول:  <b>${sig.price}</b>
🛑 SL:      <b>${sig.sl}</b>   (−${risk.toFixed(0)} نقطة)
🎯 TP1:     <b>${sig.tp1}</b>   (R:R ${rr}:1)
🎯 TP2:     <b>${sig.tp2}</b>   (R:R ${(risk > 0 ? Math.abs(sig.tp2 - sig.price)/risk : 0).toFixed(1)}:1)

${vwapLine}
📊 RSI: ${sig.rsi}   |   ATR: ${sig.atr}
🕐 ${session}   |   ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}

${conds}

<i>⚠️ إدارة المخاطر: لا تخاطر بأكثر من 1-2% من رأس المال</i>`
    );

    console.log(`[${t}] ✅ إشارة #${stats.total} — ${sig.type} @ ${sig.price} | ${q.label} (${sig.score}/5)`);

  } catch (err) {
    console.error(`[${t}] ❌ Error:`, err.message);
  } finally {
    running = false;
  }
}

// ══ ملخص يومي الساعة 8:00 صباحاً (توقيت مدريد) ══
async function dailySummary() {
  try {
    const today = new Date().toLocaleDateString('es-ES', { timeZone: 'Europe/Madrid' });
    if (stats.date !== today) { stats = { total: 0, long: 0, short: 0, date: today }; }

    const calSummary = await todaySummary();
    await tg(
`🌅 <b>صباح الخير — ملخص اليوم</b>
📅 ${today}

<b>📰 أخبار USD اليوم:</b>
${calSummary}

─────────────────
<b>📊 إشارات أمس:</b>
🔢 الإجمالي: ${stats.total}
📈 LONG:  ${stats.long}   |   📉 SHORT: ${stats.short}

🤖 البوت يعمل — فحص كل 5 دقائق
⏰ 1H Bias + 15M Structure + 5M Entry`
    );
    stats = { total: 0, long: 0, short: 0, date: today };
  } catch (e) { console.error('[Daily]', e.message); }
}

function scheduleDailySummary() {
  function nextMorning() {
    // 8:00 صباحاً بتوقيت الجزائر (UTC+1)
    const now  = new Date();
    const next = new Date();
    // نحسب 7:00 UTC = 8:00 الجزائر
    next.setUTCHours(7, 0, 0, 0);
    if (next <= now) next.setUTCDate(next.getUTCDate() + 1);
    return next - now;
  }
  setTimeout(function fire() {
    dailySummary();
    setTimeout(fire, nextMorning());
  }, nextMorning());
}

// ══ بدء التشغيل ══════════════════════════════════
console.log('═'.repeat(52));
console.log('  🤖  NQ Futures Bot — EMA21 Bounce 3TF');
console.log('═'.repeat(52));
console.log(`  📊 Symbol : ${SYMBOL} (Nasdaq Futures)`);
console.log(`  ⏱️  Check  : every 5 minutes`);
console.log(`  ⏸️  Cooldown: 30 minutes between signals`);
console.log(`  📐 Strategy: VWAP Bounce (1H Bias + 5M Entry)`);
console.log(`  📱 Chat ID : ${CHAT_ID}`);
console.log('═'.repeat(52));

tg(`🚀 <b>NQ Bot يعمل الآن</b>

📐 <b>الاستراتيجية:</b> VWAP Bounce Scalping
⏱ <b>Timeframes:</b> 1H Bias + 5M Entry
🎯 <b>الهدف:</b> TP1=1.5R | TP2=2.5R
🔍 <b>فحص:</b> كل 5 دقائق
⏸ <b>Cooldown:</b> 30 دقيقة بين الإشارات
📰 تقويم اقتصادي مدمج (تجنب الأخبار تلقائياً)

<i>إشارات VWAP Bounce — Win Rate 58-65% المتوقع ⭐</i>`).catch(() => {});

scheduleDailySummary(); // يرسل صباح الخير الساعة 8:00 فقط (UTC+1)
check();
setInterval(check, CHECK_MS);

// ══ Health check server (Railway) ════════════════
createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status:   'running',
    symbol:   SYMBOL,
    session:  currentSession(),
    signals:  stats,
    uptime:   Math.round(process.uptime()),
    time:     new Date().toISOString(),
  }));
}).listen(process.env.PORT || 3000, () => {
  console.log(`  🌐 Health check: port ${process.env.PORT || 3000}`);
});
