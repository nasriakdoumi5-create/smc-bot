/**
 * ═══════════════════════════════════════════════════
 *   NQ + ES Futures Bot — VWAP Bounce | Dual Instrument
 *   1H Bias + 5M Entry | يعمل 24/7
 * ═══════════════════════════════════════════════════
 */

import { get5mBars, get15mBars, get1hBars }          from './data.js';
import { analyzeSimple, currentSession, isKillzone }  from './strategy_simple.js';
import { getUpcomingHigh, isNewsTime, todaySummary }  from './calendar.js';
import { createServer }                               from 'http';

// ══ إعدادات ══════════════════════════════════════
const TOKEN    = process.env.TELEGRAM_TOKEN   || '8986679008:AAHmT44SZeoUzdkiaKg-OlnA3NHOonHZ2cw';
const CHAT_ID  = process.env.TELEGRAM_CHAT_ID || '6526134897';
const CHECK_MS = 5 * 60 * 1000;
const COOLDOWN = 30 * 60 * 1000;

// ══ الأدوات المتداولة ═════════════════════════════
const INSTRUMENTS = [
  { symbol: 'MNQ', name: 'NQ Futures',  emoji: '📊' },
  { symbol: 'MES', name: 'ES Futures',  emoji: '📈' },
];

// ══ حالة كل أداة منفصلة ══════════════════════════
const instState = {};
for (const inst of INSTRUMENTS) {
  instState[inst.symbol] = { lastSignalTime: 0, lastSignalKey: '' };
}

let lastNewsKey = '';
let running     = false;
let stats = { total: 0, long: 0, short: 0, nq: 0, es: 0, date: '' };

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

// ══ معالجة إشارة أداة واحدة ══════════════════════
async function processInstrument(inst, session) {
  const s = instState[inst.symbol];

  const [bars5m, bars15m, bars1h] = await Promise.all([
    get5mBars(inst.symbol),
    get15mBars(inst.symbol),
    get1hBars(inst.symbol),
  ]);

  const r = analyzeSimple(bars5m, bars15m, bars1h);
  if (r.error || !r.signal) return;

  const now    = Date.now();
  const sigKey = `${r.signal.type}_${Math.round(r.signal.price / 20)}`;
  if (sigKey === s.lastSignalKey && now - s.lastSignalTime < COOLDOWN) return;

  s.lastSignalKey  = sigKey;
  s.lastSignalTime = now;
  stats.total++;
  r.signal.type === 'LONG' ? stats.long++ : stats.short++;
  inst.symbol === 'MNQ' ? stats.nq++ : stats.es++;

  const sig    = r.signal;
  const isBull = sig.type === 'LONG';
  const q      = quality(sig.score);
  const risk   = Math.abs(sig.price - sig.sl);
  const rr     = risk > 0 ? (Math.abs(sig.tp1 - sig.price) / risk).toFixed(1) : '?';
  const conds  = Object.entries(sig.conditions).map(([k, v]) => condLine(k, v)).join('\n');

  await tg(
`${isBull ? '📈' : '📉'} <b>${sig.type} — ${inst.name}</b>   ${q.stars} ${q.label}

💰 الدخول:  <b>${sig.price}</b>
🛑 SL:      <b>${sig.sl}</b>   (−${risk.toFixed(0)} نقطة)
🎯 TP1:     <b>${sig.tp1}</b>   (R:R ${rr}:1)
🎯 TP2:     <b>${sig.tp2}</b>   (R:R ${(risk > 0 ? Math.abs(sig.tp2 - sig.price)/risk : 0).toFixed(1)}:1)

📊 VWAP: <b>${sig.vwap}</b>
📊 RSI: ${sig.rsi}   |   ATR: ${sig.atr}
🕐 ${session}   |   ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}

${conds}

<i>⚠️ إدارة المخاطر: لا تخاطر بأكثر من 1-2% من رأس المال</i>`
  );

  console.log(`  ✅ ${inst.name} — ${sig.type} @ ${sig.price} | ${q.label} (${sig.score}/4)`);
}

// ══ الفحص الرئيسي ════════════════════════════════
async function check() {
  if (running) return;
  running = true;
  const t = new Date().toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid' });

  try {
    await checkNews();

    if (!isKillzone()) {
      console.log(`[${t}] 🌙 خارج Killzone — لا فحص`);
      return;
    }

    if (await isNewsTime()) {
      console.log(`[${t}] 🚫 خبر جارٍ — تجاهل`);
      return;
    }

    const session = currentSession();
    console.log(`[${t}] 🔍 فحص NQ + ES | ${session}`);

    // فحص كلا الأداتين بالتوازي
    await Promise.allSettled(
      INSTRUMENTS.map(inst => processInstrument(inst, session))
    );

  } catch (err) {
    console.error(`[${t}] ❌ Error:`, err.message);
  } finally {
    running = false;
  }
}

// ══ ملخص يومي الساعة 8:00 صباحاً ══════════════
async function dailySummary() {
  try {
    const today = new Date().toLocaleDateString('es-ES', { timeZone: 'Europe/Madrid' });
    if (stats.date !== today) { stats = { total: 0, long: 0, short: 0, nq: 0, es: 0, date: today }; }

    const calSummary = await todaySummary();
    await tg(
`🌅 <b>صباح الخير — ملخص اليوم</b>
📅 ${today}

<b>📰 أخبار USD اليوم:</b>
${calSummary}

─────────────────
<b>📊 إشارات أمس:</b>
🔢 الإجمالي: ${stats.total}
📊 NQ: ${stats.nq}   |   📈 ES: ${stats.es}
📈 LONG: ${stats.long}   |   📉 SHORT: ${stats.short}

🤖 البوت يعمل — NQ + ES
⏰ London 07-12 UTC | NY Open 13:30-15:30 UTC`
    );
    stats = { total: 0, long: 0, short: 0, nq: 0, es: 0, date: today };
  } catch (e) { console.error('[Daily]', e.message); }
}

function scheduleDailySummary() {
  function nextMorning() {
    const now = new Date(), next = new Date();
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
console.log('  🤖  NQ + ES Futures Bot — VWAP Bounce');
console.log('═'.repeat(52));
console.log(`  📊 Instruments: MNQ (NQ) + MES (ES)`);
console.log(`  ⏱️  Check  : every 5 minutes`);
console.log(`  ⏸️  Cooldown: 30 minutes per instrument`);
console.log(`  📐 Strategy: VWAP Bounce (1H Bias + 5M Entry)`);
console.log(`  📱 Chat ID : ${CHAT_ID}`);
console.log('═'.repeat(52));

tg(`🚀 <b>NQ + ES Bot يعمل الآن</b>

📊 <b>الأدوات:</b> NQ Futures + ES Futures
📐 <b>الاستراتيجية:</b> VWAP Bounce Scalping
⏱ <b>Timeframes:</b> 1H Bias + 5M Entry
🎯 <b>الهدف:</b> TP1=1.5R | TP2=2.5R
🔍 <b>فحص:</b> كل 5 دقائق (كلا الأداتين)
⏸ <b>Cooldown:</b> 30 دقيقة لكل أداة بشكل مستقل
⏰ <b>جلسات:</b> London 07-12 | NY Open 13:30-15:30

<i>~38 إشارة/شهر — ضعف الفرص بنفس مستوى الأمان ⭐</i>`).catch(() => {});

scheduleDailySummary();
check();
setInterval(check, CHECK_MS);

// ══ Health check server ═══════════════════════════
createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status:      'running',
    instruments: ['MNQ', 'MES'],
    session:     currentSession(),
    signals:     stats,
    uptime:      Math.round(process.uptime()),
    time:        new Date().toISOString(),
  }));
}).listen(process.env.PORT || 3000, () => {
  console.log(`  🌐 Health check: port ${process.env.PORT || 3000}`);
});
