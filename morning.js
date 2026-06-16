/**
 * تقرير صباحي — 09:00 إسبانيا
 * أسعار السوق + أخبار اليوم
 */

import { get5mBars }    from './data.js';
import { fetchCalendar } from './calendar.js';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const TZ      = 'Europe/Madrid';

if (!TOKEN || !CHAT_ID) process.exit(1);

const SYMBOLS = ['MNQ', 'MGC', 'MCL', 'MES'];
const SYM_NAMES = {
  MNQ: '📊 Nasdaq  (MNQ)',
  MGC: '🥇 Gold    (MGC)',
  MCL: '🛢 Crude   (MCL)',
  MES: '📉 S&P 500 (MES)',
};

async function tg(text) {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' }),
  });
  if (!r.ok) console.error('[TG]', await r.text());
}

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
  return SYMBOLS.map(s => results.find(r => r.sym === s)).filter(Boolean);
}

async function main() {
  const now     = new Date();
  const today   = now.toLocaleDateString('es-ES', { timeZone: TZ, weekday: 'long', day: 'numeric', month: 'long' });
  const todayStr = now.toLocaleDateString('es-ES', { timeZone: TZ });

  // ── أسعار ─────────────────────────────────
  const prices = await getPrices();
  const priceLines = prices.map(p => {
    const arrow = p.chg >= 0 ? '🟢' : '🔴';
    const sign  = p.chg >= 0 ? '+' : '';
    return `${arrow} ${SYM_NAMES[p.sym]}: <b>${p.price.toFixed(2)}</b>  (${sign}${p.pct}%)`;
  }).join('\n');

  // ── أخبار ─────────────────────────────────
  const events = await fetchCalendar().catch(() => []);
  const usd    = events
    .filter(e => new Date(e.date).toLocaleDateString('es-ES', { timeZone: TZ }) === todayStr && e.country === 'USD')
    .sort((a, b) => new Date(a.date) - new Date(b.date));

  let newsSection = usd.length === 0
    ? '✅ لا توجد أخبار USD مهمة اليوم\n'
    : usd.map(e => {
        const t    = new Date(e.date).toLocaleTimeString('es-ES', { timeZone: TZ, hour: '2-digit', minute: '2-digit' });
        const icon = e.impact === 'High' ? '🔴' : e.impact === 'Medium' ? '🟡' : '⚪';
        return `${icon} ${t} — ${e.title}`;
      }).join('\n');

  const highCount = usd.filter(e => e.impact === 'High').length;
  const warning   = highCount > 0
    ? `\n⚠️ <b>${highCount} خبر أحمر اليوم — انتبه للتقلبات</b>`
    : '';

  await tg(
`🌅 <b>صباح الخير — ${today}</b>
━━━━━━━━━━━━━━━━━━━━

${priceLines}

━━━━━━━━━━━━━━━━━━━━
📰 <b>أخبار USD اليوم</b>
${newsSection}
━━━━━━━━━━━━━━━━━━━━
🕐 <b>مواعيد الجلسات (إسبانيا)</b>
🌏 آسيا:     02:00 – 06:00
🇬🇧 لندن:    10:00 – 14:00
🇺🇸 نيويورك: 15:30 – 19:00
${warning}

🤖 البوت يراقب باستمرار ✅`
  );

  console.log('✅ تقرير صباحي أُرسل');
}

main().catch(e => console.error('[Fatal]', e.message));
