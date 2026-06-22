/**
 * ═══════════════════════════════════════════════════════
 *   Nasri Futures Signals Bot — v2.0 Expert Edition
 *   VWAP Bounce + Liquidity Sweep
 *   يعمل 24/7 على Railway
 * ═══════════════════════════════════════════════════════
 */

import { get5mBars }                      from './data.js';
import { detectSignal, checkOpenTrade }   from './engine.js';
import { getUpcomingHigh, isNewsTime, todaySummary } from './calendar.js';
import { createServer }                   from 'http';

// ══ إعدادات ══════════════════════════════════════════
const TOKEN   = process.env.TELEGRAM_TOKEN   || '8986679008:AAHmT44SZeoUzdkiaKg-OlnA3NHOonHZ2cw';
const CHAT_ID = process.env.TELEGRAM_CHAT_ID || '6526134897';
const SYMBOLS = (process.env.SYMBOLS || 'MNQ').split(',').map(s => s.trim());

const SYMBOL_NAMES = {
  MNQ: 'Micro Nasdaq',
  MCL: 'Micro Crude Oil',
  MGC: 'Micro Gold',
  MES: 'Micro S&P 500',
};

const COOLDOWN_MS  = 30 * 60 * 1000;   // 30 دقيقة بين إشارات نفس الرمز
const CHECK_MS     = 5  * 60 * 1000;   // فحص كل 5 دقائق
const MAX_DAILY_SL = 3;                 // وقف بعد 3 خسائر يومية

// ══ الحالة ════════════════════════════════════════════
const symState = {};
for (const s of SYMBOLS) {
  symState[s] = {
    lastSigTime:  0,
    lastSigKey:   '',
    openTrade:    null,     // الصفقة المفتوحة حالياً
  };
}

const daily = {
  date:    '',
  signals: 0,
  wins:    0,
  losses:  0,
  pnlR:    0,   // ربح/خسارة بوحدة R
};

let botRunning = false;
let tgOffset   = 0;

// ══ Telegram ═════════════════════════════════════════

async function tg(text, chatId = CHAT_ID) {
  try {
    await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ chat_id: chatId, text, parse_mode: 'HTML' }),
    });
  } catch (e) {
    console.error('[Telegram]', e.message);
  }
}

// ══ الجلسة الحالية ════════════════════════════════════

function session() {
  const h = new Date().getUTCHours();
  const m = new Date().getUTCMinutes();
  const t = h * 60 + m;
  if (t >= 420  && t < 660)  return '🇬🇧 London';
  if (t >= 660  && t < 810)  return '🔀 London/NY';
  if (t >= 810  && t < 1260) return '🇺🇸 New York';
  if (t >= 60   && t < 240)  return '🌏 Asia';
  return '🌙 Off-Hours';
}

function inTradingSession() {
  const h = new Date().getUTCHours();
  return h >= 7 && h < 20;
}

function localTime() {
  return new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' });
}

// ══ إعادة ضبط اليومي ═════════════════════════════════

function resetDailyIfNeeded() {
  const today = new Date().toISOString().slice(0, 10);
  if (daily.date !== today) {
    daily.date    = today;
    daily.signals = 0;
    daily.wins    = 0;
    daily.losses  = 0;
    daily.pnlR    = 0;
  }
}

// ══ رسالة الإشارة ════════════════════════════════════

function signalMsg(sym, sig) {
  const name  = SYMBOL_NAMES[sym] || sym;
  const icon  = sig.type === 'LONG' ? '📈' : '📉';
  const stars = sig.priority >= 5 ? '⭐⭐⭐' : sig.priority >= 4 ? '⭐⭐' : '⭐';
  const risk  = sig.risk;
  const mnqPnl = sym === 'MNQ' ? ` (~$${(risk * 2 * 2).toFixed(0)})` : '';

  return (
`${icon} <b>${sig.type} — ${name}</b>   ${stars}

💰 الدخول:  <b>${sig.entry}</b>
🛑 SL:      <b>${sig.sl}</b>   (−${risk.toFixed(0)} نقطة)
🎯 TP1:     <b>${sig.tp1}</b>   (+${(risk * 2).toFixed(0)} نقطة${mnqPnl})
🎯 TP2:     <b>${sig.tp2}</b>   (+${(risk * 3).toFixed(0)} نقطة)

〰️ VWAP: ${sig.vwap}   |   RSI: ${sig.rsi}   |   ATR: ${sig.atr}
${sig.pdh ? `📌 PDH: ${sig.pdh}   |   PDL: ${sig.pdl ?? '-'}` : ''}
📋 <i>${sig.reason}</i>
🕐 ${session()}   |   ${localTime()}

<i>⚠️ انتظر إغلاق الشمعة — لا تخاطر أكثر من 1% من رأس المال</i>`
  );
}

// ══ رسالة نتيجة الصفقة ═══════════════════════════════

function resultMsg(sym, trade, outcome) {
  const name = SYMBOL_NAMES[sym] || sym;
  const icon = outcome === 'TP1' ? '✅' : '❌';
  const pnlR = outcome === 'TP1' ? '+2R' : '-1R';
  return (
`${icon} <b>${outcome} — ${name}</b>   ${pnlR}

${trade.type === 'LONG' ? '📈' : '📉'} ${trade.type} @ ${trade.entry}
🎯 ${outcome}: ${outcome === 'TP1' ? trade.tp1 : trade.sl}
📋 <i>${trade.reason}</i>
🕐 ${localTime()}`
  );
}

// ══ الفحص الرئيسي ════════════════════════════════════

async function checkSymbol(sym) {
  const st = symState[sym];

  // ── جلب البيانات ──
  let bars;
  try {
    bars = await get5mBars(sym);
  } catch (e) {
    console.error(`[${sym}] data error:`, e.message);
    return;
  }
  if (!bars || bars.length < 50) {
    console.log(`[${sym}] ⚠️ بيانات غير كافية (${bars?.length ?? 0})`);
    return;
  }

  const lastBar = bars[bars.length - 1];
  const price   = lastBar.close;

  // ── فحص الصفقة المفتوحة أولاً ──
  if (st.openTrade) {
    const outcome = checkOpenTrade(st.openTrade, lastBar);
    if (outcome) {
      const pnl = outcome === 'TP1' ? 2 : -1;
      daily.wins    += outcome === 'TP1' ? 1 : 0;
      daily.losses  += outcome === 'SL'  ? 1 : 0;
      daily.pnlR    += pnl;
      await tg(resultMsg(sym, st.openTrade, outcome));
      console.log(`[${sym}] ${outcome} | PnL: ${pnl > 0 ? '+' : ''}${pnl}R | اليوم: ${daily.pnlR}R`);
      st.openTrade = null;

      // وقف التداول بعد 3 خسائر
      if (daily.losses >= MAX_DAILY_SL) {
        await tg(`🛑 <b>وقف اليوم</b> — ${daily.losses} خسائر متتالية\nالبوت سيستأنف غداً.`);
        console.log(`[${sym}] 🛑 حد الخسائر اليومية`);
      }
    }
    return; // لا نبحث عن إشارة جديدة وهناك صفقة مفتوحة
  }

  // ── حد الخسائر اليومية ──
  if (daily.losses >= MAX_DAILY_SL) return;

  // ── شروط الجلسة ──
  if (!inTradingSession()) return;
  if (await isNewsTime()) {
    console.log(`[${sym}] 🚫 خبر جارٍ`);
    return;
  }

  // ── Cooldown ──
  const now = Date.now();
  if (now - st.lastSigTime < COOLDOWN_MS) return;

  // ── كشف الإشارة ──
  const sig = detectSignal(bars);
  if (!sig) {
    console.log(`[${sym}] @ ${price} | ${session()} | لا إشارة`);
    return;
  }

  // ── تجنب تكرار نفس الإشارة ──
  const sigKey = `${sig.type}_${Math.round(sig.entry / 25)}`;
  if (sigKey === st.lastSigKey && now - st.lastSigTime < COOLDOWN_MS * 2) return;

  // ── إرسال الإشارة ──
  st.lastSigTime = now;
  st.lastSigKey  = sigKey;
  st.openTrade   = { ...sig, sym, openTime: now };
  daily.signals++;

  await tg(signalMsg(sym, sig));
  console.log(`[${sym}] 🚨 ${sig.type} @ ${sig.entry} | ${sig.reason} | ${sig.priority}★`);
}

async function runCheck() {
  if (botRunning) return;
  botRunning = true;
  resetDailyIfNeeded();
  const t = localTime();
  try {
    for (const sym of SYMBOLS) {
      await checkSymbol(sym).catch(e => console.error(`[${sym}]`, e.message));
    }
  } finally {
    botRunning = false;
  }
}

// ══ أوامر Telegram ════════════════════════════════════

async function cmdSignals(chatId) {
  await tg('⏳ جاري تحليل السوق...', chatId);
  try {
    const lines = [];
    for (const sym of SYMBOLS) {
      const bars = await get5mBars(sym).catch(() => null);
      if (!bars || bars.length < 50) { lines.push(`⚠️ ${sym}: لا بيانات`); continue; }

      const { calcATR, calcRSI, calcVWAP, calcPDHL, calcSessionHL } = await import('./engine.js');
      const atr  = calcATR(bars);
      const rsi  = calcRSI(bars);
      const vwap = calcVWAP(bars);
      const { pdh, pdl }             = calcPDHL(bars);
      const { sessionHigh, sessionLow } = calcSessionHL(bars);
      const price = bars[bars.length - 1].close;
      const upper = vwap + atr * 1.5;
      const lower = vwap - atr * 1.5;

      const sig = symState[sym].openTrade;
      const openLine = sig ? `🔵 صفقة مفتوحة: ${sig.type} @ ${sig.entry}` : 'لا صفقة مفتوحة';

      lines.push(
`<b>${sym}</b> @ ${price}
〰️ VWAP: ${vwap.toFixed(0)} | U: ${upper.toFixed(0)} | L: ${lower.toFixed(0)}
📌 PDH: ${pdh?.toFixed(0) ?? '-'} | PDL: ${pdl?.toFixed(0) ?? '-'}
📍 Session H: ${sessionHigh?.toFixed(0) ?? '-'} | L: ${sessionLow?.toFixed(0) ?? '-'}
📊 RSI: ${rsi.toFixed(0)} | ATR: ${atr.toFixed(0)}
${openLine}`
      );
    }

    await tg(
`📊 <b>تحليل السوق — ${localTime()}</b>\n\n${lines.join('\n\n─────────────\n\n')}

<i>استخدم /trade للحصول على الإشارة القادمة</i>`
    , chatId);
  } catch (e) {
    await tg(`❌ خطأ: ${e.message}`, chatId);
  }
}

async function cmdStatus(chatId) {
  const openTrades = SYMBOLS
    .filter(s => symState[s].openTrade)
    .map(s => {
      const t = symState[s].openTrade;
      return `  ${t.type === 'LONG' ? '📈' : '📉'} ${s} ${t.type} @ ${t.entry} → TP: ${t.tp1}`;
    })
    .join('\n') || '  لا صفقات مفتوحة';

  await tg(
`🤖 <b>حالة البوت</b>

🟢 يعمل | ⏱ ${Math.round(process.uptime() / 60)} دقيقة
📊 الرموز: ${SYMBOLS.join(', ')}
🕐 ${session()}

<b>اليوم ${daily.date}:</b>
📨 إشارات: ${daily.signals}
✅ TP1: ${daily.wins}   ❌ SL: ${daily.losses}   💰 PnL: ${daily.pnlR > 0 ? '+' : ''}${daily.pnlR}R

<b>الصفقات المفتوحة:</b>
${openTrades}

⏰ ${localTime()}`
  , chatId);
}

async function cmdHelp(chatId) {
  await tg(
`📋 <b>الأوامر المتاحة</b>

/signals — تحليل السوق الآن
/status  — حالة البوت والإحصائيات
/help    — هذه القائمة

<b>الاستراتيجية:</b>
⭐⭐⭐ سحب سيولة PDH/PDL
⭐⭐   سحب قمة/قاع الجلسة
⭐    ارتداد VWAP ± 1.5 ATR

<b>الجلسات النشطة:</b>
🇬🇧 London:   09:00-11:00 CEST
🇺🇸 New York: 15:30-19:00 CEST`
  , chatId);
}

// ══ Telegram Polling ════════════════════════════════

async function pollTelegram() {
  try {
    const res  = await fetch(
      `https://api.telegram.org/bot${TOKEN}/getUpdates?offset=${tgOffset}&timeout=20`
    );
    const data = await res.json();
    for (const upd of data.result || []) {
      tgOffset = upd.update_id + 1;
      const msg  = upd.message;
      if (!msg?.text) continue;
      const cmd    = msg.text.trim().split(' ')[0].toLowerCase();
      const chatId = String(msg.chat.id);
      console.log(`[Telegram] ${msg.from?.username ?? '?'}: ${msg.text}`);
      if (cmd === '/signals' || cmd === '/تحليل')  await cmdSignals(chatId);
      else if (cmd === '/status' || cmd === '/حالة') await cmdStatus(chatId);
      else if (cmd === '/help'   || cmd === '/مساعدة') await cmdHelp(chatId);
    }
  } catch (e) {
    if (!e.message.includes('allowlist')) console.error('[Poll]', e.message);
  }
  setTimeout(pollTelegram, 3000);
}

// ══ ملخص صباحي ══════════════════════════════════════

async function morningBriefing() {
  try {
    const calSummary = await todaySummary().catch(() => 'تعذّر جلب الأخبار');
    const date = new Date().toLocaleDateString('ar-SA', { timeZone: 'Europe/Madrid', weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    await tg(
`🌅 <b>صباح الخير — ${date}</b>

<b>📰 أخبار USD اليوم:</b>
${calSummary}

<b>الاستراتيجية اليوم:</b>
⭐⭐⭐ راقب PDH: اخترق ثم انعكاس → SHORT
⭐⭐⭐ راقب PDL: اخترق ثم انعكاس → LONG
⭐⭐   قمة/قاع الجلسة → انعكاس
⭐    VWAP ± 1.5 ATR → ارتداد

🕐 أفضل الأوقات (توقيت إسبانيا):
🇬🇧 09:00 – 11:00   |   🇺🇸 15:30 – 19:00

🤖 البوت يعمل — فحص كل 5 دقائق
اكتب /signals لتحليل فوري`
    );
  } catch (e) {
    console.error('[Morning]', e.message);
  }
}

// ══ الجدولة ══════════════════════════════════════════

function scheduleAt(utcHour, utcMin, fn) {
  function msUntilNext() {
    const now  = new Date();
    const next = new Date();
    next.setUTCHours(utcHour, utcMin, 0, 0);
    if (next <= now) next.setDate(next.getDate() + 1);
    return next - now;
  }
  setTimeout(function fire() {
    fn();
    setTimeout(fire, 86400000);
  }, msUntilNext());
}

// ══ Webhook لـ TradingView ════════════════════════════

async function handleWebhook(body) {
  const { symbol, type, price, sl, tp1, rsi, atr } = body;
  if (!symbol || !type || !price) return;
  const name = SYMBOL_NAMES[symbol] || symbol;
  const risk = sl ? Math.abs(price - sl) : 0;
  await tg(
`📡 <b>TradingView — ${type} ${name}</b>

💰 الدخول: <b>${price}</b>
🛑 SL:     <b>${sl ?? '-'}</b>
🎯 TP1:    <b>${tp1 ?? '-'}</b>
${rsi ? `📊 RSI: ${rsi}${atr ? ` | ATR: ${atr}` : ''}` : ''}
🕐 ${localTime()}`
  );
}

// ══ HTTP Server ══════════════════════════════════════

createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');

  if (req.method === 'POST' && url.pathname === '/webhook') {
    let body = '';
    req.on('data', c => { body += c; });
    req.on('end', async () => {
      try {
        await handleWebhook(JSON.parse(body));
        res.writeHead(200); res.end('OK');
      } catch { res.writeHead(400); res.end('Bad Request'); }
    });
    return;
  }

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status:  'running',
    version: '2.0',
    symbols: SYMBOLS,
    session: session(),
    daily,
    openTrades: SYMBOLS.filter(s => symState[s].openTrade).map(s => ({
      sym: s, ...symState[s].openTrade
    })),
    uptime: Math.round(process.uptime()),
    time:   new Date().toISOString(),
  }));
}).listen(process.env.PORT || 3000);

// ══ بدء التشغيل ══════════════════════════════════════

const LINE = '═'.repeat(52);
console.log(LINE);
console.log('  🤖  Nasri Futures Bot — v2.0 Expert Edition');
console.log(LINE);
console.log(`  📊 Symbols : ${SYMBOLS.join(', ')}`);
console.log(`  ⏱️  Check   : every ${CHECK_MS / 60000} min`);
console.log(`  ⏸️  Cooldown : ${COOLDOWN_MS / 60000} min/symbol`);
console.log(`  🛑 Max SL/d : ${MAX_DAILY_SL}`);
console.log(LINE);

resetDailyIfNeeded();
pollTelegram();
scheduleAt(7, 0, morningBriefing);   // 09:00 CEST = 07:00 UTC

tg(
`🚀 <b>Nasri Bot v2.0 — يعمل الآن</b>

📊 الرموز: ${SYMBOLS.map(s => SYMBOL_NAMES[s] || s).join(', ')}
⚡ الاستراتيجية: VWAP Bounce + Liquidity Sweep
🛡️ إدارة المخاطر: وقف عند ${MAX_DAILY_SL} خسائر يومياً
🔁 فحص كل 5 دقائق | Cooldown 30 دقيقة

اكتب /help للأوامر`
).catch(() => {});

runCheck();
setInterval(runCheck, CHECK_MS);
