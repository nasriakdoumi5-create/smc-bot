/**
 * ═══════════════════════════════════════════════════
 *   SMC Trading Bot v3.0 — Channel Business Edition
 *   TradingView Pine Script → JSON webhook → Telegram
 *   ─────────────────────────────────────────────────
 *   Indicators: VWAP Bounce Pro + Kill Zone Sweep Pro
 *   Broadcast:  Owner DM  +  Telegram Channel
 *   Commands:   /start  /status  /help
 * ═══════════════════════════════════════════════════
 */

import { createServer }   from 'http';
import { currentSession } from './strategy_simple.js';

const TOKEN      = process.env.TELEGRAM_TOKEN   || '8986679008:AAHmT44SZeoUzdkiaKg-OlnA3NHOonHZ2cw';
const OWNER_ID   = process.env.TELEGRAM_CHAT_ID || '6526134897';
const CHANNEL_ID = process.env.CHANNEL_ID       || '';   // -100xxxx or @channame
const PORT       = process.env.PORT             || 3000;

// ── Daily stats ─────────────────────────────────────
let stats = { date: '', total: 0, long: 0, short: 0, bySource: {} };

// ── Cooldown — prevent duplicate signals (15 min) ───
const lastSig  = {};
const COOLDOWN = 15 * 60 * 1000;

// ── Telegram ─────────────────────────────────────────
async function tgSend(chatId, text) {
  if (!TOKEN) { console.log(`[TG → ${chatId}]`, text); return true; }
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({
      chat_id:                  chatId,
      text,
      parse_mode:               'HTML',
      disable_web_page_preview: true,
    }),
  }).catch(() => null);
  if (r && !r.ok) {
    const err = await r.text().catch(() => '');
    console.error(`[TG → ${chatId}] FAILED:`, err.slice(0, 150));
  }
  return r?.ok ?? false;
}

async function broadcast(text) {
  await tgSend(OWNER_ID, text);
  if (CHANNEL_ID) await tgSend(CHANNEL_ID, text).catch(() => {});
}

// ── Source labels ────────────────────────────────────
function srcLabel(src) {
  if (!src) return '📡 TradingView';
  if (src === 'vwap_lower')  return '📊 VWAP Lower Band';
  if (src === 'vwap_upper')  return '📊 VWAP Upper Band';
  if (src.startsWith('kz_')) return `⚡ Kill Zone — ${src.slice(3)}`;
  return `📡 ${src}`;
}

// ── Quality stars (q = "1"|"2"|"3" from Pine Script) ─
function stars(q) {
  return '⭐'.repeat(Math.min(3, Math.max(1, parseInt(q) || 2)));
}

// ── Format one signal into a Telegram message ────────
function formatSignal(d) {
  const isBull = d.t === 'LONG';
  const sym    = d.s  || '?';
  const price  = parseFloat(d.p);
  const sl     = parseFloat(d.sl);
  const tp1    = parseFloat(d.tp1);
  const tp2    = parseFloat(d.tp2);

  const risk = Math.abs(price - sl);
  const rr1  = risk > 0 ? (Math.abs(tp1 - price) / risk).toFixed(1) : '?';
  const rr2  = risk > 0 ? (Math.abs(tp2 - price) / risk).toFixed(1) : '?';

  const slPts = risk > 0 ? risk.toFixed(0) : '?';
  const slDir = isBull ? `−${slPts}` : `+${slPts}`;

  const session  = currentSession();
  const timeCEST = new Date().toLocaleTimeString('es-ES', {
    timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit',
  });

  const src = d.src || '';
  const q   = d.q   != null ? d.q : (src.startsWith('kz_') ? 3 : 2);

  const lines = [
    `${isBull ? '📈' : '📉'} <b>${d.t} — ${sym}</b>   ${stars(q)}`,
    ``,
    `💰 <b>الدخول:  ${price.toFixed(2)}</b>`,
    `🛑 SL:      ${sl.toFixed(2)}   (${slDir} pts)`,
    `🎯 TP1:     ${tp1.toFixed(2)}   (R:R 1:${rr1})`,
    `🎯 TP2:     ${tp2.toFixed(2)}   (R:R 1:${rr2})`,
    ``,
  ];

  if (d.r  != null) lines.push(`📊 RSI: ${parseFloat(d.r).toFixed(1)}${d.a != null ? `   |   ATR: ${parseFloat(d.a).toFixed(2)}` : ''}`);
  if (d.v  != null) lines.push(`📈 VWAP: ${parseFloat(d.v).toFixed(2)}`);
  if (d.pts != null) lines.push(`🏆 النقاط: ${d.pts}/6`);

  lines.push(`🕐 ${session}   |   ${timeCEST} CEST`);
  lines.push(`📡 ${srcLabel(src)}`);
  lines.push(``);
  lines.push(`<i>⚠️ لا تخاطر بأكثر من 1-2% من رأس المال في صفقة واحدة</i>`);

  return lines.join('\n');
}

// ── Handle TradingView webhook ────────────────────────
async function handleWebhook(rawBody) {
  let d;
  try { d = JSON.parse(rawBody); } catch {
    console.error('[Webhook] JSON parse error:', rawBody.slice(0, 200));
    return false;
  }

  console.log('[Webhook]', JSON.stringify(d));

  // Support legacy field names {symbol,type,price} alongside {s,t,p}
  d.s = d.s || d.symbol;
  d.t = d.t || d.type;
  d.p = d.p || d.price;

  if (!d.t || !d.p) {
    console.log('[Webhook] Missing required fields (t, p)');
    return false;
  }

  const sym = d.s || 'UNK';
  const key = `${sym}_${d.t}`;
  const now = Date.now();

  if (lastSig[key] && now - lastSig[key] < COOLDOWN) {
    const rem = Math.round((COOLDOWN - (now - lastSig[key])) / 60000);
    console.log(`[Webhook] ⏳ Cooldown ${key} — ${rem} min remaining`);
    return true;
  }
  lastSig[key] = now;

  // Update daily stats
  const today = new Date().toISOString().slice(0, 10);
  if (stats.date !== today) stats = { date: today, total: 0, long: 0, short: 0, bySource: {} };
  stats.total++;
  d.t === 'LONG' ? stats.long++ : stats.short++;
  const sk = d.src || 'other';
  stats.bySource[sk] = (stats.bySource[sk] || 0) + 1;

  const msg = formatSignal(d);
  await broadcast(msg);
  console.log(`[Webhook] ✅ Signal #${stats.total} — ${sym} ${d.t} @ ${d.p}  src:${d.src}`);
  return true;
}

// ── Telegram long-polling ─────────────────────────────
let tgOffset = 0;

async function pollTelegram() {
  try {
    const r = await fetch(
      `https://api.telegram.org/bot${TOKEN}/getUpdates?offset=${tgOffset + 1}&timeout=30&limit=20`,
      { signal: AbortSignal.timeout(35_000) }
    );
    if (r.ok) {
      const data = await r.json();
      for (const upd of (data.result || [])) {
        tgOffset = upd.update_id;
        handleTgUpdate(upd).catch(e => console.error('[TG]', e.message));
      }
    }
  } catch (e) {
    if (!e.message?.includes('timeout') && !e.message?.includes('abort')) {
      console.error('[Poll]', e.message);
    }
  }
  setTimeout(pollTelegram, 3_000);
}

// ── Telegram command handler ──────────────────────────
async function handleTgUpdate(upd) {
  const msg = upd.message || upd.channel_post;
  if (!msg?.text) return;

  const chat    = String(msg.chat.id);
  const text    = msg.text.trim().split(' ')[0].split('@')[0];  // strip bot name + args
  const isOwner = chat === String(OWNER_ID);

  if (text === '/start') {
    await tgSend(chat,
`🤖 <b>SMC Trading Bot — مرحباً!</b>

أنا بوت يستقبل إشارات من TradingView تلقائياً ويرسلها إليك.

<b>📊 المؤشرات المتصلة:</b>
• VWAP Bounce Pro — ارتداد من نطاقات VWAP
• Kill Zone Sweep Pro — كسح السيولة في جلسات لندن ونيويورك

<b>الأوامر:</b>
/status — إحصائيات اليوم وحالة البوت
/help   — دليل قراءة الإشارات
${isOwner ? '\n🔐 <b>أنت المالك — صلاحيات كاملة</b>' : ''}`
    );
    return;
  }

  if (text === '/status') {
    const session  = currentSession();
    const today    = new Date().toISOString().slice(0, 10);
    const srcLines = Object.entries(stats.bySource)
      .map(([k, v]) => `   ${srcLabel(k)}: ${v}`)
      .join('\n') || '   لا يوجد بعد';

    await tgSend(chat,
`📊 <b>حالة البوت</b>

🟢 يعمل بشكل طبيعي
🕐 ${session}
📅 ${stats.date || today}

<b>إشارات اليوم:</b>
🔢 الإجمالي: ${stats.total}
📈 LONG:  ${stats.long}   |   📉 SHORT: ${stats.short}

<b>حسب المصدر:</b>
${srcLines}

⏱ Uptime: ${Math.round(process.uptime() / 60)} دقيقة
📡 Webhook: <code>POST /webhook</code>
📺 Channel: ${CHANNEL_ID ? '✅ مفعّل' : '❌ غير مفعّل'}`
    );
    return;
  }

  if (text === '/help') {
    await tgSend(chat,
`❓ <b>دليل قراءة الإشارات</b>

<b>مثال إشارة LONG:</b>
📈 <b>LONG — MNQ</b>   ⭐⭐⭐
💰 الدخول:  21,055.00
🛑 SL:      21,020.00   (−35 pts)
🎯 TP1:     21,125.00   (R:R 1:2)
🎯 TP2:     21,160.00   (R:R 1:3)

<b>شرح الحقول:</b>
• 💰 الدخول — سعر الدخول (فتح الشمعة التالية)
• 🛑 SL — وقف الخسارة (تحت/فوق شمعة الإشارة)
• 🎯 TP1 — هدف أول بعائد 2× المخاطرة
• 🎯 TP2 — هدف ثاني بعائد 3× المخاطرة
• ⭐ النجوم — جودة الإشارة (1-3 نجوم)

<b>المصادر:</b>
📊 VWAP Bounce — ارتداد من نطاق VWAP ± 1.5 ATR
⚡ Kill Zone — كسح PDH/PDL في مناطق الجلسات

<b>أوقات أفضل الإشارات (UTC):</b>
⭐ 07:00–11:00 — جلسة لندن
⭐ 13:30–17:00 — جلسة نيويورك

⚠️ <i>لا تخاطر بأكثر من 1-2% من رأس المال في صفقة واحدة</i>`
    );
    return;
  }
}

// ── Morning briefing (07:00 UTC daily) ───────────────
async function morningBriefing() {
  const dayAr = new Date().toLocaleDateString('ar-EG', {
    timeZone: 'UTC', weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  });
  await broadcast(
`🌅 <b>صباح الخير — جلسة جديدة</b>
📅 ${dayAr}

<b>🕐 جلسات اليوم (UTC):</b>
🇬🇧 لندن:      07:00 – 11:00
🔀 لندن/NY:   11:00 – 13:30
🇺🇸 نيويورك:  13:30 – 17:00

<b>⭐ أوقات أفضل الإشارات:</b>
• 07:00–09:00 UTC  (فتح لندن — Kill Zone)
• 13:30–15:30 UTC  (فتح نيويورك — Kill Zone)
• طوال اليوم  07:00–20:00  (VWAP Bounce)

🤖 البوت يعمل — ينتظر إشارات TradingView
<i>تأكد أن تنبيهات TradingView مفعّلة على المؤشرَين</i>`
  );
}

// ── Daily scheduler ───────────────────────────────────
function scheduleAt(utcH, utcM, fn) {
  const now  = new Date();
  const fire = new Date();
  fire.setUTCHours(utcH, utcM, 0, 0);
  if (fire <= now) fire.setUTCDate(fire.getUTCDate() + 1);
  setTimeout(() => { fn(); setInterval(fn, 86_400_000); }, fire - now);
}

// ── HTTP Server ───────────────────────────────────────
createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');

  // TradingView alert webhook
  if (req.method === 'POST' && url.pathname === '/webhook') {
    const tok = req.headers['x-webhook-token'] || url.searchParams.get('token');
    if (process.env.WEBHOOK_TOKEN && tok !== process.env.WEBHOOK_TOKEN) {
      res.writeHead(401); res.end('Unauthorized'); return;
    }

    let body = '';
    req.on('data', c => { body += c; });
    req.on('end', async () => {
      try {
        const ok = await handleWebhook(body);
        res.writeHead(ok !== false ? 200 : 400);
        res.end(ok !== false ? 'OK' : 'Bad Request');
      } catch (e) {
        console.error('[Webhook] ❌', e.message);
        res.writeHead(500); res.end('Server Error');
      }
    });
    return;
  }

  // Health check / status page
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    bot:      'SMC Trading Bot v3.0',
    status:   'running',
    session:  currentSession(),
    signals:  stats,
    channel:  !!CHANNEL_ID,
    uptime:   Math.round(process.uptime()),
    time:     new Date().toISOString(),
  }, null, 2));

}).listen(PORT, () => {
  console.log('═'.repeat(54));
  console.log('  🤖  SMC Trading Bot v3.0 — Channel Edition');
  console.log('═'.repeat(54));
  console.log(`  📡 Webhook  : POST /webhook`);
  console.log(`  📺 Channel  : ${CHANNEL_ID || '(none — owner DM only)'}`);
  console.log(`  📱 Owner    : ${OWNER_ID}`);
  console.log(`  🌐 Port     : ${PORT}`);
  console.log('═'.repeat(54));
});

// ── Start ─────────────────────────────────────────────
scheduleAt(7, 0, morningBriefing);
pollTelegram();

broadcast(
`🚀 <b>SMC Trading Bot v3.0 — يعمل الآن</b>

📡 جاهز لاستقبال إشارات TradingView على:
<code>/webhook</code>

<b>📊 المؤشرات:</b>
• VWAP Bounce Pro (07:00–20:00 UTC)
• Kill Zone Sweep Pro (لندن + نيويورك)

📺 Channel: ${CHANNEL_ID ? '✅ مفعّل' : '⚠️ غير مفعّل — أضف CHANNEL_ID في Railway'}
🌅 تقرير صباحي يومياً الساعة 07:00 UTC
/help للمساعدة`
).catch(() => {});
