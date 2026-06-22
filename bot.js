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
import { validateSignal }                             from './gemini.js';
import { analyzeVWAP, formatSignalsMsg }              from './vwap_signals.js';
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

// ══ فحص رمز واحد — VWAP Bounce + Liquidity ════════
async function checkSymbol(symbol, t) {
  const bars5m = await get5mBars(symbol);
  if (!bars5m || bars5m.length < 50) {
    console.log(`[${t}] ${symbol} ⚠️ بيانات غير كافية`);
    return;
  }

  // ── حساب المؤشرات مباشرة ──
  const i = bars5m.length - 1;
  const b = bars5m[i];
  const p1 = bars5m[i - 1];

  // ATR
  let atrSum = 0;
  for (let j = i - 13; j <= i; j++)
    atrSum += Math.max(bars5m[j].high - bars5m[j].low,
      Math.abs(bars5m[j].high - bars5m[j-1].close),
      Math.abs(bars5m[j].low  - bars5m[j-1].close));
  const atr = atrSum / 14;

  // RSI
  let g = 0, l = 0;
  for (let j = i - 13; j <= i; j++) {
    const d = bars5m[j].close - bars5m[j-1].close;
    if (d > 0) g += d; else l -= d;
  }
  const rsi = l === 0 ? 100 : 100 - 100 / (1 + g / l);

  // VWAP (daily)
  const barDate = new Date(b.time * 1000);
  barDate.setUTCHours(0,0,0,0);
  const dayTs = barDate.getTime() / 1000;
  let tpv = 0, vn = 0;
  for (let j = i; j >= 0; j--) {
    if (bars5m[j].time < dayTs) break;
    tpv += (bars5m[j].high + bars5m[j].low + bars5m[j].close) / 3;
    vn++;
  }
  const vwap = vn > 0 ? tpv / vn : b.close;
  const upper = vwap + atr * 1.5;
  const lower = vwap - atr * 1.5;

  // PDH/PDL
  const todayTs = dayTs;
  const yestTs  = todayTs - 86400;
  let pdh = -Infinity, pdl = Infinity;
  for (let j = i; j >= 0; j--) {
    if (bars5m[j].time < yestTs) break;
    if (bars5m[j].time < todayTs) {
      pdh = Math.max(pdh, bars5m[j].high);
      pdl = Math.min(pdl, bars5m[j].low);
    }
  }
  pdh = isFinite(pdh) ? pdh : null;
  pdl = isFinite(pdl) ? pdl : null;

  // Session check 07:00-20:00 UTC
  const nowH = new Date(b.time * 1000).getUTCHours();
  const inSession = nowH >= 7 && nowH < 20;

  const price  = b.close;
  const wUp    = b.high  - Math.max(b.open, b.close);
  const wDn    = Math.min(b.open, b.close) - b.low;
  const session = currentSession();

  console.log(
    `[${t}] ${symbol} @ ${price.toFixed(2)} | VWAP:${vwap.toFixed(0)} ` +
    `U:${upper.toFixed(0)} L:${lower.toFixed(0)} | RSI:${rsi.toFixed(0)} | ${session}`
  );

  if (!inSession) return;
  if (await isNewsTime()) { console.log(`[${t}] ${symbol} 🚫 خبر جارٍ`); return; }

  // ── شروط الإشارة ──
  let sigType = null, reason = '', priority = 0;

  // ① PDH Sweep SHORT (أعلى أولوية)
  if (pdh && b.high > pdh && b.close < pdh && b.close < b.open && wUp >= atr * 0.15 && rsi >= 55) {
    sigType = 'SHORT'; reason = '⚡ سحب سيولة PDH'; priority = 5;

  // ② PDL Sweep LONG (أعلى أولوية)
  } else if (pdl && b.low < pdl && b.close > pdl && b.close > b.open && wDn >= atr * 0.15 && rsi <= 45) {
    sigType = 'LONG'; reason = '⚡ سحب سيولة PDL'; priority = 5;

  // ③ VWAP Upper Band SHORT
  } else if (b.high >= upper && b.close < upper && b.close < b.open && wUp >= atr * 0.15 && rsi >= 56) {
    sigType = 'SHORT'; reason = 'VWAP Upper Band'; priority = 3;

  // ④ VWAP Lower Band LONG
  } else if (b.low <= lower && b.close > lower && b.close > b.open && wDn >= atr * 0.15 && rsi <= 44) {
    sigType = 'LONG'; reason = 'VWAP Lower Band'; priority = 3;
  }

  if (!sigType) return;

  // Cooldown
  const now    = Date.now();
  const sym    = state[symbol];
  const sigKey = `${sigType}_${Math.round(price / 30)}`;
  if (sigKey === sym.lastSignalKey && now - sym.lastSignalTime < COOLDOWN) {
    console.log(`[${t}] ${symbol} ⏳ Cooldown`);
    return;
  }

  sym.lastSignalKey  = sigKey;
  sym.lastSignalTime = now;
  stats.total++;
  sigType === 'LONG' ? stats.long++ : stats.short++;
  stats.bySymbol[symbol] = (stats.bySymbol[symbol] || 0) + 1;

  const sl   = sigType === 'LONG' ? b.low  - atr * 0.1 : b.high + atr * 0.1;
  const risk = Math.abs(price - sl);
  const tp1  = sigType === 'LONG' ? price + risk * 2   : price - risk * 2;
  const tp2  = sigType === 'LONG' ? price + risk * 3   : price - risk * 3;
  const name = SYMBOL_NAMES[symbol] || symbol;
  const stars = priority >= 5 ? '⭐⭐⭐' : priority >= 4 ? '⭐⭐' : '⭐';

  await tg(
`${sigType === 'LONG' ? '📈' : '📉'} <b>${sigType} — ${name}</b>   ${stars}

💰 الدخول:  <b>${price.toFixed(2)}</b>
🛑 SL:      <b>${sl.toFixed(2)}</b>   (−${risk.toFixed(0)} نقطة)
🎯 TP1:     <b>${tp1.toFixed(2)}</b>   (R:R 1:2)
🎯 TP2:     <b>${tp2.toFixed(2)}</b>   (R:R 1:3)

〰️ VWAP: ${vwap.toFixed(2)}   |   RSI: ${rsi.toFixed(0)}   |   ATR: ${atr.toFixed(0)}
${pdh ? `📌 PDH: ${pdh.toFixed(2)}   |   PDL: ${pdl?.toFixed(2) ?? '-'}` : ''}
📋 <i>${reason}</i>
🕐 ${session}   |   ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}

<i>⚠️ انتظر إغلاق الشمعة قبل الدخول — لا تخاطر أكثر من 1-2%</i>`
  );

  console.log(`[${t}] ✅ إشارة #${stats.total} — ${symbol} ${sigType} @ ${price.toFixed(2)} | ${reason}`);
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

// ══ TradingView Webhook Handler ══════════════════
async function handleTVWebhook(data) {
  console.log('[TV Webhook]', JSON.stringify(data));

  const { symbol, type, price, sl, tp1, tp2, rsi, atr } = data;
  if (!symbol || !type || !price) {
    console.log('[TV Webhook] ⚠️ بيانات ناقصة');
    return;
  }

  const name    = SYMBOL_NAMES[symbol] || symbol;
  const isBull  = type === 'LONG';
  const risk    = sl ? Math.abs(price - sl) : 0;
  const rr      = (risk > 0 && tp1) ? (Math.abs(tp1 - price) / risk).toFixed(1) : '?';
  const session = currentSession();

  await tg(
`${isBull ? '📈' : '📉'} <b>${type} — ${name}</b>   📡 TradingView

💰 الدخول:  <b>${price}</b>
${sl  ? `🛑 SL:      <b>${sl}</b>   (−${risk.toFixed(0)} نقطة)` : ''}
${tp1 ? `🎯 TP1:     <b>${tp1}</b>   (R:R ${rr}:1)` : ''}
${tp2 ? `🎯 TP2:     <b>${tp2}</b>` : ''}
${rsi ? `📊 RSI: ${rsi}${atr ? `   |   ATR: ${atr}` : ''}` : ''}
🕐 ${session}   |   ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}

<i>⚠️ إدارة المخاطر: لا تخاطر بأكثر من 1-2% من رأس المال</i>`
  );

  stats.total++;
  type === 'LONG' ? stats.long++ : stats.short++;
  stats.bySymbol[symbol] = (stats.bySymbol[symbol] || 0) + 1;
  console.log(`[TV Webhook] ✅ إشارة أُرسلت — ${symbol} ${type} @ ${price}`);
}

// ══ HTTP Server (Health check + Webhook) ═════════
createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost`);

  // ── TradingView Webhook ──
  if (req.method === 'POST' && url.pathname === '/webhook') {
    const token = req.headers['x-webhook-token'] || url.searchParams.get('token');
    if (process.env.WEBHOOK_TOKEN && token !== process.env.WEBHOOK_TOKEN) {
      res.writeHead(401);
      return res.end('Unauthorized');
    }

    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', async () => {
      try {
        const data = JSON.parse(body);
        await handleTVWebhook(data);
        res.writeHead(200);
        res.end('OK');
      } catch (e) {
        console.error('[TV Webhook] ❌', e.message);
        res.writeHead(400);
        res.end('Bad Request');
      }
    });
    return;
  }

  // ── Health check ──
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
  console.log(`  🌐 Health check + Webhook: port ${process.env.PORT || 3000}`);
});

// ══ Telegram Polling — أوامر المستخدم ═════════════
let tgOffset = 0;

async function pollTelegram() {
  try {
    const res  = await fetch(`https://api.telegram.org/bot${TOKEN}/getUpdates?offset=${tgOffset}&timeout=25`);
    const data = await res.json();
    for (const upd of data.result || []) {
      tgOffset = upd.update_id + 1;
      const msg = upd.message;
      if (!msg?.text) continue;
      const text   = msg.text.trim().toLowerCase();
      const chatId = msg.chat.id;

      if (text.startsWith('/signals') || text.startsWith('/إشارات')) {
        await handleSignalsCmd(chatId);
      } else if (text.startsWith('/status') || text.startsWith('/حالة')) {
        await handleStatusCmd(chatId);
      } else if (text.startsWith('/help') || text.startsWith('/مساعدة')) {
        await tg(`📋 <b>الأوامر المتاحة:</b>\n\n/signals — أفضل 3 إشارات الآن\n/status  — حالة البوت\n/help    — هذه القائمة`);
      }
    }
  } catch (e) {
    console.error('[Poll]', e.message);
  }
  setTimeout(pollTelegram, 2000);
}

async function handleSignalsCmd(chatId) {
  const loadMsg = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chatId, text: '⏳ جاري التحليل...' }),
  }).then(r => r.json()).catch(() => null);

  try {
    const result = await analyzeVWAP('MNQ');
    const msg    = formatSignalsMsg(result);
    await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text: msg, parse_mode: 'HTML' }),
    });
  } catch (e) {
    await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text: `❌ خطأ: ${e.message}` }),
    });
  }
}

async function handleStatusCmd(chatId) {
  const session = currentSession();
  await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      parse_mode: 'HTML',
      text:
`🤖 <b>حالة البوت</b>
🟢 يعمل منذ: ${Math.round(process.uptime() / 60)} دقيقة
📊 الرموز: ${SYMBOLS.join(', ')}
🕐 الجلسة: ${session}
📈 إشارات اليوم: ${stats.total} (LONG: ${stats.long} | SHORT: ${stats.short})
⏱ ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}`,
    }),
  });
}

// ══ إشارات تلقائية 09:00 CEST (07:00 UTC) ═════════
function scheduleDailySignals() {
  const now  = new Date();
  const next = new Date();
  next.setUTCHours(7, 0, 0, 0);
  if (next <= now) next.setDate(next.getDate() + 1);
  setTimeout(async () => {
    console.log('[DailySignals] إرسال إشارات الصباح...');
    await handleSignalsCmd(CHAT_ID);
    setInterval(() => handleSignalsCmd(CHAT_ID), 86400000);
  }, next - now);
  console.log(`  📡 Daily signals: كل يوم 09:00 CEST`);
}

pollTelegram();
scheduleDailySignals();
