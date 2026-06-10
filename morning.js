/**
 * تقرير صباحي يومي — يُرسل 09:00 إسبانيا
 * أخبار اليوم + حالة السوق + تحذيرات
 */

import { get1hBars }       from './data.js';
import { ema }             from './smc.js';
import { fetchCalendar }   from './calendar.js';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const TZ      = 'Europe/Madrid';

if (!TOKEN || !CHAT_ID) process.exit(1);

async function tg(text) {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' })
  });
  if (!r.ok) console.error('[TG]', await r.text());
}

async function marketBias(symbol) {
  const bars = await get1hBars(symbol).catch(() => []);
  if (bars.length < 200) return '❓';
  const ema50  = ema(bars, 50);
  const ema200 = ema(bars, 200);
  const e50    = ema50[ema50.length - 1];
  const e200   = ema200[ema200.length - 1];
  const price  = bars[bars.length - 1].close;
  if (e50 > e200 && price > e50)  return '🟢 صاعد';
  if (e50 < e200 && price < e50)  return '🔴 هابط';
  return '🟡 محايد';
}

async function main() {
  const now   = new Date();
  const today = now.toLocaleDateString('es-ES', { timeZone: TZ, weekday: 'long', day: 'numeric', month: 'long' });

  // ── أخبار اليوم ──────────────────────────
  const events  = await fetchCalendar().catch(() => []);
  const todayStr = now.toLocaleDateString('es-ES', { timeZone: TZ });
  const usd = events
    .filter(e => new Date(e.date).toLocaleDateString('es-ES', { timeZone: TZ }) === todayStr && e.country === 'USD')
    .sort((a, b) => new Date(a.date) - new Date(b.date));

  const highNews   = usd.filter(e => e.impact === 'High');
  const medNews    = usd.filter(e => e.impact === 'Medium');

  let newsSection = '';
  if (usd.length === 0) {
    newsSection = '✅ لا توجد أخبار USD مهمة اليوم\n';
  } else {
    for (const e of usd) {
      const t    = new Date(e.date).toLocaleTimeString('es-ES', { timeZone: TZ, hour: '2-digit', minute: '2-digit' });
      const icon = e.impact === 'High' ? '🔴' : e.impact === 'Medium' ? '🟡' : '⚪';
      newsSection += `${icon} ${t} — ${e.title}\n`;
    }
  }

  // ── حالة السوق ───────────────────────────
  const [mnqBias, mgcBias, mclBias] = await Promise.all([
    marketBias('MNQ'),
    marketBias('MGC'),
    marketBias('MCL'),
  ]);

  // ── تحذير أخبار حمراء ────────────────────
  const warning = highNews.length > 0
    ? `\n⚠️ <b>تحذير: ${highNews.length} خبر أحمر اليوم — انتبه للتقلبات</b>\n`
    : '';

  await tg(
`🌅 <b>صباح الخير — تقرير يوم ${today}</b>
━━━━━━━━━━━━━━━━━━━━

📊 <b>حالة السوق (1H)</b>
MNQ (Nasdaq):  ${mnqBias}
MGC (Gold):    ${mgcBias}
MCL (Oil):     ${mclBias}

━━━━━━━━━━━━━━━━━━━━
📰 <b>أخبار USD اليوم</b>
${newsSection}
━━━━━━━━━━━━━━━━━━━━
🕐 <b>مواعيد الجلسات (إسبانيا)</b>
🇬🇧 لندن:    09:00 – 13:00
🇺🇸 نيويورك: 14:30 – 18:00
${warning}
🤖 البوت يراقب الثلاثة كل دقيقة ✅`
  );

  console.log('✅ تقرير صباحي أُرسل');
}

main().catch(e => console.error('[Fatal]', e.message));
