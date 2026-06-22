/**
 * ═══════════════════════════════════════════════════
 *   NQ + ES Futures Bot — VWAP Bounce | Dual Instrument
 *   1H Bias + 5M Entry | يعمل 24/7
 *   التحسينات: حد خسارة يومي + Chop Filter + تذكير BE
 * ═══════════════════════════════════════════════════
 */

import { get5mBars, get15mBars, get1hBars }          from './data_tradovate.js';
import { executeSignal }                              from './tradovate.js';
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

// ══ الصفقات المفتوحة حالياً ═══════════════════════
const activeTrades = new Map(); // symbol → { entry, sl, tp, be, type, openTime, beNotified }

// ══ الحالة اليومية ════════════════════════════════
const MAX_SIGNALS_PER_INST = 3;
const daily = { losses: 0, wins: 0, signals: 0, halted: false, date: '' };

// ══ إحصائيات الجلسة الحالية ══════════════════════
const session = { name: '', wins: 0, losses: 0, timeouts: 0, signals: 0 };

function resetSession(name) {
  Object.assign(session, { name, wins: 0, losses: 0, timeouts: 0, signals: 0 });
}

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
        const activeList = activeTrades.size === 0 ? 'لا يوجد' :
          [...activeTrades.values()].map(t => {
            const mins = Math.round((Date.now()-t.openTime)/60000);
            return `• ${t.name} ${t.type} @ ${t.entry} (${mins}د)`;
          }).join('\n');
        await tg(
`📊 <b>حالة البوت</b>
${st}
✅ أرباح اليوم: ${daily.wins}
❌ خسائر اليوم: ${daily.losses}/${MAX_DAILY_LOSSES}
📡 إشارات اليوم: ${daily.signals}
🔄 صفقات مفتوحة: ${activeTrades.size}
${activeList !== 'لا يوجد' ? activeList + '\n' : ''}🔢 إجمالي: ${stats.total} إشارة`);

      } else if (text === '/reset') {
        Object.assign(daily, { losses: 0, wins: 0, signals: 0, halted: false });
        await tg('🔄 تم إعادة تعيين العداد اليومي');

      } else if (text === '/trades') {
        if (activeTrades.size === 0) {
          await tg('📭 لا توجد صفقات مفتوحة حالياً');
        } else {
          const lines = [...activeTrades.values()].map(t => {
            const mins = Math.round((Date.now()-t.openTime)/60000);
            return `${t.type==='LONG'?'📈':'📉'} <b>${t.name}</b> ${t.type}\n💰 ${t.entry} | 🛑 ${t.sl} | 🎯 ${t.tp}\n⏱ منذ ${mins} دقيقة`;
          }).join('\n─────\n');
          await tg(`🔄 <b>الصفقات المفتوحة (${activeTrades.size})</b>\n─────\n${lines}`);
        }

      } else if (text === '/help') {
        await tg(
`📋 <b>الأوامر المتاحة:</b>
/status  — حالة البوت اليوم
/trades  — الصفقات المفتوحة
/reset   — إعادة تعيين العداد
/win     — تسجيل ربح يدوي
/loss    — تسجيل خسارة يدوي
/help    — هذه القائمة

🤖 البوت يتابع الصفقات تلقائياً`);
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

// ══ متابعة الصفقات المفتوحة تلقائياً ════════════
async function checkActiveTrades() {
  if (activeTrades.size === 0) return;

  for (const [symbol, trade] of activeTrades) {
    try {
      const bars = await get5mBars(symbol);
      if (!bars || bars.length === 0) continue;

      const openTimeSec = trade.openTime / 1000;
      const newBars = bars.filter(b => b.time > openTimeSec);
      if (newBars.length === 0) continue;

      let result = null;
      let resultPrice = null;

      // timeout بعد ساعتين
      if (Date.now() - trade.openTime > 2 * 60 * 60 * 1000) {
        result = 'TIMEOUT';
        resultPrice = bars[bars.length - 1].close;
      } else {
        for (const bar of newBars) {
          if (trade.type === 'LONG') {
            if (bar.low  <= trade.sl) { result = 'LOSS'; resultPrice = trade.sl; break; }
            if (bar.high >= trade.tp) { result = 'WIN';  resultPrice = trade.tp; break; }
            if (!trade.beNotified && bar.high >= trade.be) {
              trade.beNotified = true;
              await tg(`🔔 <b>حرّك SL للدخول — ${trade.name}</b>\nالسعر وصل BE: <b>${trade.be}</b> ✅`);
            }
          } else {
            if (bar.high >= trade.sl) { result = 'LOSS'; resultPrice = trade.sl; break; }
            if (bar.low  <= trade.tp) { result = 'WIN';  resultPrice = trade.tp; break; }
            if (!trade.beNotified && bar.low <= trade.be) {
              trade.beNotified = true;
              await tg(`🔔 <b>حرّك SL للدخول — ${trade.name}</b>\nالسعر وصل BE: <b>${trade.be}</b> ✅`);
            }
          }
        }
      }

      if (!result) continue;
      activeTrades.delete(symbol);

      const mins = Math.round((Date.now() - trade.openTime) / 60000);

      if (result === 'WIN') {
        daily.wins++;
        session.wins++;
        await tg(
`✅ <b>ربح تلقائي — ${trade.name}</b>
🎯 TP وصل: <b>${resultPrice}</b>
📈 الدخول: ${trade.entry} → +${Math.abs(resultPrice-trade.entry).toFixed(0)} نقطة
⏱ المدة: ${mins} دقيقة
─────────────────
✅ أرباح اليوم: ${daily.wins} | ❌ خسائر: ${daily.losses}`);

      } else if (result === 'LOSS') {
        daily.losses++;
        session.losses++;
        if (daily.losses >= MAX_DAILY_LOSSES) {
          daily.halted = true;
          await tg(
`❌ <b>خسارة تلقائية — ${trade.name}</b>
🛑 SL وصل: <b>${resultPrice}</b>
⏱ المدة: ${mins} دقيقة
─────────────────
🛑 <b>حد الخسارة اليومي — ${daily.losses} خسائر</b>
إيقاف الإشارات حتى الغد 💪`);
        } else {
          await tg(
`❌ <b>خسارة تلقائية — ${trade.name}</b>
🛑 SL وصل: <b>${resultPrice}</b>
⏱ المدة: ${mins} دقيقة
⚠️ خسارة #${daily.losses} — تبقّى ${MAX_DAILY_LOSSES-daily.losses} قبل الإيقاف`);
        }

      } else {
        session.timeouts++;
        await tg(
`⏳ <b>انتهاء الوقت — ${trade.name}</b>
لم يصل TP أو SL خلال ساعتين
السعر الحالي: <b>${resultPrice}</b> | الدخول: ${trade.entry}
<i>أغلق الصفقة يدوياً إذا كانت مفتوحة</i>`);
      }

      console.log(`  [AutoTrack] ${symbol} → ${result} @ ${resultPrice}`);
    } catch(e) {
      console.error(`[AutoTrack] ${symbol}:`, e.message);
    }
  }
}

// ══ معالجة إشارة أداة واحدة ══════════════════════
async function processInstrument(inst, session) {
  const s = instState[inst.symbol];

  // لا تفتح صفقة جديدة إذا هناك صفقة مفتوحة لنفس الأداة
  if (activeTrades.has(inst.symbol)) return;

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
  session.signals++;
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

🤖 <i>البوت يتابع الصفقة تلقائياً</i>`
  );

  // حفظ الصفقة للمتابعة التلقائية
  activeTrades.set(inst.symbol, {
    symbol:      inst.symbol,
    name:        inst.name,
    type:        sig.type,
    entry:       sig.price,
    sl:          sig.sl,
    tp:          sig.tp1,
    be:          sig.be,
    openTime:    Date.now(),
    beNotified:  false,
  });

  console.log(`  ✅ ${inst.name} — ${sig.type} @ ${sig.price} | ${q.label} (${sig.score}/4)`);

  // تنفيذ تلقائي على حساب Tradovate Demo
  if (process.env.TRADOVATE_USERNAME) {
    try {
      await executeSignal(sig, inst.symbol);
      console.log(`  [Tradovate] ✅ أمر مُنفَّذ: ${inst.symbol} ${sig.type}`);
    } catch (err) {
      console.error(`  [Tradovate] ❌ فشل التنفيذ:`, err.message);
      await tg(`⚠️ <b>Tradovate: فشل التنفيذ</b>\n${err.message}`).catch(() => {});
    }
  }
}

// ══ الفحص الرئيسي ════════════════════════════════
async function check() {
  if (running) return;
  running = true;
  const t = new Date().toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid' });

  try {
    await pollCommands();
    await checkNews();
    await checkActiveTrades(); // متابعة الصفقات المفتوحة في كل دورة

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

// ══ تقرير نهاية الجلسة ════════════════════════════
async function sendSessionSummary(sessionName) {
  if (session.signals === 0) return; // لا إشارات → لا تقرير
  const total  = session.wins + session.losses + session.timeouts;
  const wr     = total > 0 ? Math.round(session.wins / total * 100) : 0;
  const bars   = '█'.repeat(Math.round(wr/10)) + '░'.repeat(10-Math.round(wr/10));
  const status = wr >= 60 ? '✅ جلسة ممتازة' : wr >= 50 ? '⚖️ جلسة متعادلة' : '⚠️ جلسة صعبة';

  await tg(
`📋 <b>تقرير جلسة ${sessionName}</b>
─────────────────────
📊 الإشارات: ${session.signals}
✅ أرباح:   ${session.wins}
❌ خسائر:   ${session.losses}
⏳ Timeout: ${session.timeouts}
─────────────────────
📈 WR: ${wr}%  ${bars}
${status}
─────────────────────
📅 اليوم: ✅ ${daily.wins} ربح | ❌ ${daily.losses} خسارة`
  ).catch(() => {});
}

function scheduleSessionSummaries() {
  // نهاية London: 12:00 UTC | نهاية NY: 15:30 UTC
  const sessions = [
    { name: '🇬🇧 London (07-12 UTC)', endH: 12, endM: 0  },
    { name: '🇺🇸 NY Open (13:30-15:30 UTC)', endH: 15, endM: 30 },
  ];

  for (const s of sessions) {
    (function schedule(sess) {
      function msUntilEnd() {
        const now  = new Date();
        const next = new Date();
        next.setUTCHours(sess.endH, sess.endM, 0, 0);
        if (next <= now) next.setUTCDate(next.getUTCDate() + 1);
        return next - now;
      }
      setTimeout(async function fire() {
        await sendSessionSummary(sess.name);
        resetSession(sess.name);
        setTimeout(fire, msUntilEnd());
      }, msUntilEnd());
    })(s);
  }

  // إعادة تعيين جلسة London عند بدايتها 07:00 UTC
  (function scheduleReset() {
    function msUntil7() {
      const now = new Date(), next = new Date();
      next.setUTCHours(7, 0, 0, 0);
      if (next <= now) next.setUTCDate(next.getUTCDate() + 1);
      return next - now;
    }
    setTimeout(function fire() {
      resetSession('🇬🇧 London');
      setTimeout(fire, msUntil7());
    }, msUntil7());
  })();
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
console.log('  🤖  NQ + ES Bot — VWAP Bounce v5');
console.log('═'.repeat(52));
console.log(`  📊 Instruments : MNQ + MES`);
console.log(`  🎯 Target      : RR 1.5:1 | WR 63%+`);
console.log(`  🛑 Daily limit : ${MAX_DAILY_LOSSES} losses → halt`);
console.log(`  🤖 Auto-track  : WIN/LOSS يُسجَّل تلقائياً`);
console.log(`  📡 Data        : Tradovate (real-time)`);
console.log(`  🔌 Execution   : ${process.env.TRADOVATE_USERNAME ? 'Tradovate Demo' : 'إشارات فقط'}`);
console.log(`  📋 Commands    : /status /trades /reset`);
console.log(`  ⏰ Sessions    : London 07-12 | NY 13:30-15:30 UTC`);
console.log('═'.repeat(52));

// اختبار اتصال Tradovate عند البدء
import('./tradovate.js').then(({ tradovate }) => {
  if (!process.env.TRADOVATE_USERNAME) return;
  tradovate.ensureToken()
    .then(() => tradovate.getAccount())
    .then(acc => {
      console.log(`  [Tradovate] ✅ متصل — ${acc.name} (${process.env.TRADOVATE_ENV || 'demo'})`);
      tg(`✅ <b>Tradovate متصل</b>\n📋 الحساب: <b>${acc.name}</b>\n🌐 البيئة: ${(process.env.TRADOVATE_ENV || 'demo').toUpperCase()}\n📡 البيانات: لحظية (real-time)`).catch(() => {});
    })
    .catch(err => {
      console.error(`  [Tradovate] ❌ فشل الاتصال:`, err.message);
      tg(`⚠️ <b>Tradovate: فشل الاتصال</b>\n${err.message}`).catch(() => {});
    });
}).catch(() => {});

tg(`🚀 <b>NQ + ES Bot v5 يعمل</b>

📊 <b>الأدوات:</b> NQ + ES Futures
🎯 <b>الهدف:</b> TP = 1.5R | WR 63%+
📡 <b>البيانات:</b> Tradovate (لحظية — لا تأخير)
🤖 <b>تتبع تلقائي:</b> البوت يسجّل WIN/LOSS وحده
🔔 <b>Breakeven:</b> تنبيه تلقائي عند 0.7R
🛑 <b>حد الخسارة:</b> ${MAX_DAILY_LOSSES} خسائر/يوم ثم توقف تلقائي
⏰ <b>جلسات:</b> London 07-12 | NY 13:30-15:30

<b>الأوامر:</b>
/status — الحالة الحالية
/trades — الصفقات المفتوحة
/reset  — إعادة تعيين
/help   — قائمة الأوامر`).catch(() => {});

scheduleSessionSummaries();
scheduleDailySummary();
check();
setInterval(check, CHECK_MS);

// ══ Health check server ═══════════════════════════
createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status:       daily.halted ? 'halted' : 'running',
    instruments:  ['MNQ', 'MES'],
    session:      currentSession(),
    daily,
    signals:      stats,
    activeTrades: Object.fromEntries(activeTrades),
    uptime:       Math.round(process.uptime()),
    time:         new Date().toISOString(),
  }));
}).listen(process.env.PORT || 3000, () => {
  console.log(`  🌐 Health check: port ${process.env.PORT || 3000}`);
});
