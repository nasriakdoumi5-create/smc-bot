/**
 * SMC Scanner Bot — 24/7 Cloud (Railway)
 * بحث مستمر على جميع الجلسات — بدون استراتيجية
 */

import { get5mBars }                              from './data.js';
import { getUpcomingHigh, isNewsTime, todaySummary } from './calendar.js';
import { createServer }                            from 'http';

const TOKEN    = process.env.TELEGRAM_TOKEN   || '8986679008:AAHmT44SZeoUzdkiaKg-OlnA3NHOonHZ2cw';
const CHAT_ID  = process.env.TELEGRAM_CHAT_ID || '6526134897';
const CHECK_MS = 5 * 60 * 1000;

const SYMBOLS = ['MNQ', 'MGC', 'MCL', 'MES'];
const SYM_NAMES = {
  MNQ: '📊 Nasdaq  (MNQ)',
  MGC: '🥇 Gold    (MGC)',
  MCL: '🛢 Crude   (MCL)',
  MES: '📉 S&P 500 (MES)',
};

// ══ Session Detection (UTC) ═══════════════════
const SESSIONS = {
  ASIA:     { start: 0   * 60,       end: 4   * 60,      label: '🌏 آسيا',     flag: '' },
  LONDON:   { start: 8   * 60,       end: 12  * 60,      label: '🇬🇧 لندن',    flag: '' },
  NEW_YORK: { start: 13  * 60 + 30,  end: 16  * 60,      label: '🇺🇸 نيويورك', flag: '' },
};

function currentSession() {
  const now  = new Date();
  const mins = now.getUTCHours() * 60 + now.getUTCMinutes();
  for (const [name, s] of Object.entries(SESSIONS)) {
    if (mins >= s.start && mins < s.end) return name;
  }
  return null;
}

// ══ State ════════════════════════════════════
let activeSession = null;
let lastNewsKey   = '';
let running       = false;

// ══ Telegram ═════════════════════════════════
async function tg(text) {
  try {
    const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' }),
    });
    if (!r.ok) console.error('[TG]', await r.text());
  } catch (e) { console.error('[TG]', e.message); }
}

// ══ Prices ════════════════════════════════════
async function getPrices() {
  const results = [];
  await Promise.all(SYMBOLS.map(async sym => {
    try {
      const bars = await get5mBars(sym);
      if (!bars?.length) return;
      const last = bars[bars.length - 1];
      const prev = bars[bars.length - 2];
      const chg  = +(last.close - prev.close).toFixed(2);
      const pct  = +((chg / prev.close) * 100).toFixed(2);
      results.push({ sym, price: last.close, chg, pct });
    } catch {}
  }));
  // حفظ ترتيب SYMBOLS
  return SYMBOLS.map(s => results.find(r => r.sym === s)).filter(Boolean);
}

function priceLines(prices) {
  return prices.map(p => {
    const arrow = p.chg >= 0 ? '🟢' : '🔴';
    const sign  = p.chg >= 0 ? '+' : '';
    return `${arrow} ${SYM_NAMES[p.sym] || p.sym}: <b>${p.price.toFixed(2)}</b>  (${sign}${p.pct}%)`;
  }).join('\n');
}

// ══ News Alerts ═══════════════════════════════
async function checkNews() {
  const events = await getUpcomingHigh(15).catch(() => []);
  for (const e of events) {
    const key = e.date + e.title;
    if (key === lastNewsKey) continue;
    lastNewsKey = key;
    const mins    = Math.max(1, Math.round((new Date(e.date) - Date.now()) / 60000));
    const timeStr = new Date(e.date).toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });
    await tg(
`⚠️ <b>خبر مهم — ${e.title}</b>

🕐 خلال <b>${mins} دقيقة</b>  (${timeStr} إسبانيا)
🔴 High Impact USD
${e.forecast ? `📊 التوقع: ${e.forecast}` : ''}

⛔ <b>كن حذراً — تقلبات متوقعة</b>`
    );
  }
}

// ══ Session Open Alert ════════════════════════
async function onSessionOpen(name) {
  const s      = SESSIONS[name];
  const prices = await getPrices();
  const t      = new Date().toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });

  await tg(
`${s.label} <b>جلسة ${s.label} — افتتاح</b>
━━━━━━━━━━━━━━━━━━━━

${priceLines(prices)}

━━━━━━━━━━━━━━━━━━━━
🕐 ${t} (إسبانيا)
🔍 البوت يراقب السوق باستمرار`
  );
}

// ══ Main Scan Loop ════════════════════════════
async function check() {
  if (running) return;
  running = true;
  try {
    await checkNews();

    const session = currentSession();
    const t = new Date().toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });

    // كشف افتتاح الجلسة
    if (session && session !== activeSession) {
      activeSession = session;
      console.log(`[${t}] 🟢 جلسة ${session} افتُتحت`);
      await onSessionOpen(session);
    } else if (!session && activeSession) {
      activeSession = null;
      console.log(`[${t}] ⚫ خارج الجلسات`);
    }

    // سجل حالة كل 5 دقائق
    const prices = await getPrices();
    const log = prices.map(p => `${p.sym}:${p.price.toFixed(0)}`).join(' ');
    console.log(`[${t}] Session:${session || 'OFF'} | ${log}`);

  } catch (err) {
    console.error('[Error]', err.message);
  } finally {
    running = false;
  }
}

// ══ Daily Morning Summary ════════════════════
async function dailySummary() {
  try {
    const prices = await getPrices();
    const summary = await todaySummary();
    const today   = new Date().toLocaleDateString('es-ES', {
      timeZone: 'Europe/Madrid', weekday: 'long', day: 'numeric', month: 'long'
    });

    await tg(
`☀️ <b>صباح الخير — ${today}</b>
━━━━━━━━━━━━━━━━━━━━

${priceLines(prices)}

━━━━━━━━━━━━━━━━━━━━
📰 <b>أخبار USD اليوم</b>
${summary}

━━━━━━━━━━━━━━━━━━━━
🕐 <b>مواعيد الجلسات (إسبانيا)</b>
🌏 آسيا:     02:00 – 06:00
🇬🇧 لندن:    10:00 – 14:00
🇺🇸 نيويورك: 15:30 – 19:00

🤖 البوت يراقب باستمرار ✅`
    );
  } catch (e) { console.error('[Daily]', e.message); }
}

function scheduleDailySummary() {
  const now  = new Date();
  const next = new Date();
  next.setHours(8, 0, 0, 0);
  if (next <= now) next.setDate(next.getDate() + 1);
  setTimeout(() => {
    dailySummary();
    setInterval(dailySummary, 86_400_000);
  }, next - now);
}

// ══ Start ════════════════════════════════════
console.log('═'.repeat(50));
console.log('  🤖  SMC Scanner Bot — All Sessions');
console.log(`  📊  ${SYMBOLS.join(' • ')}`);
console.log('  ⏱️   فحص كل 5 دقائق — بلا توقف');
console.log('═'.repeat(50));

tg(
`🚀 <b>SMC Scanner يعمل على السحابة</b>

📊 يراقب: ${SYMBOLS.join(' • ')}
⏱️ فحص كل 5 دقائق
🌏 آسيا  |  🇬🇧 لندن  |  🇺🇸 نيويورك
📰 تنبيهات أخبار مدمجة`
).catch(() => {});

dailySummary();
scheduleDailySummary();
check();
setInterval(check, CHECK_MS);

// Keep-alive for Railway
createServer((req, res) => {
  res.writeHead(200);
  res.end(JSON.stringify({
    status:  'running',
    symbols: SYMBOLS,
    session: currentSession(),
    time:    new Date().toISOString(),
  }));
}).listen(process.env.PORT || 3000, () => {
  console.log(`  🌐 HTTP on port ${process.env.PORT || 3000}`);
});
