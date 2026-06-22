/**
 * ═══════════════════════════════════════════════════
 *   NQ + ES Futures Bot — VWAP Bounce | Dual Instrument
 *   1H Bias + 5M Entry | يعمل 24/7
 *   التحسينات: حد خسارة يومي + Chop Filter + تذكير BE
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
const MAX_DAILY_LOSSES = 2;  // إيقاف بعد خسارتين في اليوم

// ══ الأدوات المتداولة ═════════════════════════════
const INSTRUMENTS = [
  { symbol: 'MNQ', name: 'NQ Futures', emoji: '📊' },
  { symbol: 'MES', name: 'ES Futures', emoji: '📈' },
];

// ══ حالة كل أداة ══════════════════════════════════
const instState = {};
for (const inst of INSTRUMENTS) {
  instState[inst.symbol] = { lastSignalTime: 0, dailySignals: 0 };
}

// ══ الحالة اليومية ════════════════════════════════
const MAX_SIGNALS_PER_INST = 3;  // حد أقصى 3 إشارات/أداة/يوم للحفاظ على الجودة
const daily = { losses: 0, wins: 0, signals: 0, halted: false, date: '' };

function resetDailyIfNeeded() {
  // UTC — متوافق مع نوافذ الجلسات
  const today = new Date().toISOString().slice(0, 10);
  if (daily.date !== today) {
    Object.assign(daily, { losses: 0, wins: 0, signals: 0, halted: false, date: today });
    for (const inst of INSTRUMENTS) instState[inst.symbol].dailySignals = 0;
  }
}

let lastNewsKey  = '';
let lastUpdateId = 0;
let running      = false;
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

// ══ استقبال الأوامر من Telegram ══════════════════
async function pollCommands() {
  try {
    const r = await fetch(
      `https://api.telegram.org/bot${TOKEN}/getUpdates?offset=${lastUpdateId+1}&timeout=0`
    );
    const j = await r.json();
    for (const u of j.result || []) {
      lastUpdateId = u.update_id;
      const text = (u.message?.text || '').trim().toLowerCase();
      resetDailyIfNeeded();

      if (text === '/loss') {
        daily.losses++;
        if (daily.losses >= MAX_DAILY_LOSSES) {
          daily.halted = true;
          await tg(
`🛑 <b>حد الخسارة اليومي</b>
${daily.losses} خسائر اليوم — تم إيقاف الإشارات حتى الغد
استرح وعُد غداً بذهن صافٍ 💪`);
        } else {
          await tg(`⚠️ خسارة #${daily.losses} — تبقّى ${MAX_DAILY_LOSSES - daily.losses} خسارة قبل الإيقاف`);
        }

      } else if (text === '/win') {
        daily.wins++;
        await tg(`✅ ربح #${daily.wins} مسجّل — استمر 💪 (خسائر اليوم: ${daily.losses})`);

      } else if (text === '/status') {
        const st = daily.halted ? '🛑 موقوف' : '✅ يعمل';
        await tg(
`📊 <b>حالة البوت</b>
${st}
✅ أرباح اليوم: ${daily.wins}
❌ خسائر اليوم: ${daily.losses}/${MAX_DAILY_LOSSES}
📡 إشارات اليوم: ${daily.signals}
🔢 إجمالي: ${stats.total} إشارة`);

      } else if (text === '/reset') {
        Object.assign(daily, { losses: 0, wins: 0, signals: 0, halted: false });
        await tg('🔄 تم إعادة تعيين العداد اليومي');

      } else if (text === '/help') {
        await tg(
`📋 <b>الأوامر المتاحة:</b>
/loss   — تسجيل خسارة
/win    — تسجيل ربح
/status — حالة البوت اليوم
/reset  — إعادة تعيين العداد
/help   — هذه القائمة`);
      }
    }
  } catch(e) {}
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

  const now = Date.now();

  // فلتر الجودة — فقط ⭐⭐ أو ⭐⭐⭐ (score >= 2)
  if (r.signal.score < 2) return;

  // cooldown زمني بحت (لا يعتمد على السعر)
  if (now - s.lastSignalTime < COOLDOWN) return;

  // حد أقصى للإشارات اليومية لكل أداة
  if (s.dailySignals >= MAX_SIGNALS_PER_INST) return;

  s.lastSignalTime = now;
  s.dailySignals++;
  stats.total++;
  daily.signals++;
  r.signal.type === 'LONG' ? stats.long++ : stats.short++;
  inst.symbol === 'MNQ' ? stats.nq++ : stats.es++;

  const sig    = r.signal;
  const isBull = sig.type === 'LONG';
  const q      = quality(sig.score);
  const risk   = Math.abs(sig.price - sig.sl);
  const pts    = (sig.tp1 - sig.price) * (isBull ? 1 : -1);
  const bePts  = (sig.be  - sig.price) * (isBull ? 1 : -1);
  const conds  = Object.entries(sig.conditions).map(([k, v]) => condLine(k, v)).join('\n');

  await tg(
`${isBull ? '📈' : '📉'} <b>${sig.type} — ${inst.name}</b>   ${q.stars} ${q.label}

💰 الدخول:  <b>${sig.price}</b>
🛑 SL:      <b>${sig.sl}</b>   (−${risk.toFixed(0)} نقطة)
🎯 TP:      <b>${sig.tp1}</b>   (+${pts.toFixed(0)} نقطة | R:R 1.5:1)
🔔 BE:      عند <b>${sig.be}</b> (+${bePts.toFixed(0)} نقطة) → حرّك SL للدخول

📊 VWAP: <b>${sig.vwap}</b>
📊 RSI: ${sig.rsi}   |   ATR: ${sig.atr}
🕐 ${session}   |   ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}

${conds}

<i>سجّل النتيجة: /win أو /loss</i>`
  );

  console.log(`  ✅ ${inst.name} — ${sig.type} @ ${sig.price} | ${q.label} (${sig.score}/4)`);
}

// ══ الفحص الرئيسي ════════════════════════════════
async function check() {
  if (running) return;
  running = true;
  const t = new Date().toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid' });

  try {
    await pollCommands();
    await checkNews();

    resetDailyIfNeeded();
    if (daily.halted) {
      console.log(`[${t}] 🛑 موقوف — ${daily.losses} خسائر اليوم`);
      return;
    }

    if (!isKillzone()) {
      console.log(`[${t}] 🌙 خارج Killzone`);
      return;
    }

    if (await isNewsTime()) {
      console.log(`[${t}] 🚫 خبر جارٍ`);
      return;
    }

    const session = currentSession();
    console.log(`[${t}] 🔍 فحص NQ + ES | ${session} | خسائر:${daily.losses}/${MAX_DAILY_LOSSES}`);

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
🔢 الإجمالي: ${stats.total} | NQ: ${stats.nq} | ES: ${stats.es}
📈 LONG: ${stats.long}   |   📉 SHORT: ${stats.short}

🤖 البوت يعمل — NQ + ES | RR 1.5:1
⏰ London 07-12 | NY 13:30-15:30 UTC
📋 أوامر: /win /loss /status`
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
console.log('  🤖  NQ + ES Bot — VWAP Bounce v3');
console.log('═'.repeat(52));
console.log(`  📊 Instruments : MNQ + MES`);
console.log(`  🎯 Target      : RR 1.5:1 | WR 61.7%`);
console.log(`  🛑 Daily limit : ${MAX_DAILY_LOSSES} losses → halt`);
console.log(`  📋 Commands    : /win /loss /status /reset`);
console.log(`  ⏰ Sessions    : London 07-12 | NY 13:30-15:30 UTC`);
console.log('═'.repeat(52));

tg(`🚀 <b>NQ + ES Bot v3 يعمل</b>

📊 <b>الأدوات:</b> NQ + ES Futures
🎯 <b>الهدف:</b> TP = 1.5R | WR 61.7%
🔔 <b>Breakeven:</b> تذكير تلقائي عند 0.7R
🛑 <b>حد الخسارة:</b> ${MAX_DAILY_LOSSES} خسائر/يوم ثم توقف تلقائي
⏰ <b>جلسات:</b> London 07-12 | NY 13:30-15:30

<b>الأوامر:</b>
/win — تسجيل ربح
/loss — تسجيل خسارة
/status — الحالة الحالية
/reset — إعادة تعيين
/help — قائمة الأوامر`).catch(() => {});

scheduleDailySummary();
check();
setInterval(check, CHECK_MS);

// ══ Health check server ═══════════════════════════
createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status:      daily.halted ? 'halted' : 'running',
    instruments: ['MNQ', 'MES'],
    session:     currentSession(),
    daily,
    signals:     stats,
    uptime:      Math.round(process.uptime()),
    time:        new Date().toISOString(),
  }));
}).listen(process.env.PORT || 3000, () => {
  console.log(`  🌐 Health check: port ${process.env.PORT || 3000}`);
});
