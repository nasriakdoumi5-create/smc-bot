/**
 * SMC Scanner — GitHub Actions Runner
 * بحث مستمر خلال جميع الجلسات — بدون استراتيجية
 */

import { get5mBars }               from './data.js';
import { getUpcomingHigh, isNewsTime } from './calendar.js';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const TOKEN   = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

if (!TOKEN || !CHAT_ID) {
  console.error('❌ TELEGRAM_TOKEN أو TELEGRAM_CHAT_ID غير موجود');
  process.exit(1);
}

const SYMBOLS = ['MNQ', 'MGC', 'MCL', 'MES'];
const SYM_NAMES = {
  MNQ: 'Nasdaq  (MNQ)',
  MGC: 'Gold    (MGC)',
  MCL: 'Crude   (MCL)',
  MES: 'S&P 500 (MES)',
};

// ══ Sessions (UTC minutes) ════════════════════
const SESSIONS = {
  ASIA:     { start: 0   * 60,      end: 4  * 60,     label: '🌏 آسيا'    },
  LONDON:   { start: 8   * 60,      end: 12 * 60,     label: '🇬🇧 لندن'   },
  NEW_YORK: { start: 13  * 60 + 30, end: 16 * 60,     label: '🇺🇸 نيويورك' },
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
const STATE_FILE = '/tmp/smc_state.json';

function loadState() {
  try {
    if (existsSync(STATE_FILE)) return JSON.parse(readFileSync(STATE_FILE, 'utf8'));
  } catch {}
  return { lastNewsKey: '', sessionOpened: {} };
}

function saveState(s) {
  try { writeFileSync(STATE_FILE, JSON.stringify(s)); } catch {}
}

// ══ Telegram ════════════════════════════════
async function tg(text) {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' }),
  });
  if (!r.ok) console.error('[TG Error]', await r.text());
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
    } catch (e) { console.error(`[${sym}]`, e.message); }
  }));
  return SYMBOLS.map(s => results.find(r => r.sym === s)).filter(Boolean);
}

// ══ Main ══════════════════════════════════════
async function main() {
  const state   = loadState();
  const session = currentSession();
  const t = new Date().toLocaleTimeString('es-ES', {
    timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit'
  });

  // ── أخبار قادمة ───────────────────────────
  const news = await getUpcomingHigh(15).catch(() => []);
  for (const e of news) {
    const key = e.date + e.title;
    if (key === state.lastNewsKey) continue;
    state.lastNewsKey = key;
    const mins    = Math.max(1, Math.round((new Date(e.date) - Date.now()) / 60000));
    const timeStr = new Date(e.date).toLocaleTimeString('es-ES', {
      timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit'
    });
    await tg(
`⚠️ <b>خبر مهم — ${e.title}</b>

🕐 خلال <b>${mins} دقيقة</b>  (${timeStr} إسبانيا)
🔴 High Impact USD
${e.forecast ? `📊 التوقع: ${e.forecast}` : ''}

⛔ <b>كن حذراً — تقلبات متوقعة</b>`
    ).catch(() => {});
  }

  // ── جلب الأسعار ───────────────────────────
  const prices = await getPrices();

  if (session) {
    const sess = SESSIONS[session];

    // تنبيه افتتاح الجلسة (مرة واحدة فقط في كل جلسة)
    const today    = new Date().toLocaleDateString('es-ES', { timeZone: 'Europe/Madrid' });
    const openKey  = `${session}_${today}`;

    if (!state.sessionOpened?.[openKey]) {
      state.sessionOpened = state.sessionOpened || {};
      state.sessionOpened[openKey] = true;

      const lines = prices.map(p => {
        const arrow = p.chg >= 0 ? '🟢' : '🔴';
        const sign  = p.chg >= 0 ? '+' : '';
        return `${arrow} ${SYM_NAMES[p.sym]}: <b>${p.price.toFixed(2)}</b>  (${sign}${p.pct}%)`;
      }).join('\n');

      await tg(
`${sess.label} <b>جلسة ${sess.label} — افتتاح</b>
━━━━━━━━━━━━━━━━━━━━

${lines}

━━━━━━━━━━━━━━━━━━━━
🕐 ${t} (إسبانيا)
🔍 البوت يراقب باستمرار`
      ).catch(() => {});

      console.log(`[${t}] 🟢 جلسة ${session} — تنبيه افتتاح أُرسل`);
    }

    // سجل الأسعار في الكونسول
    const log = prices.map(p => `${p.sym}:${p.price.toFixed(0)}(${p.chg >= 0 ? '+' : ''}${p.pct}%)`).join('  ');
    console.log(`[${t}] ${session} | ${log}`);

  } else {
    const log = prices.map(p => `${p.sym}:${p.price.toFixed(0)}`).join('  ');
    console.log(`[${t}] خارج الجلسات | ${log}`);
  }

  saveState(state);
}

main().catch(e => { console.error('[Fatal]', e.message); process.exit(1); });
