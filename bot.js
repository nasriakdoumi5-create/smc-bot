/**
 * MNQ Bot — 14:00 UTC Reversal
 * صفقة واحدة يومياً | RR 1.5 | 5M
 */

import { get5mBars }    from './data_tradovate.js';
import { analyze1400 }  from './strategy_1400.js';
import { createServer } from 'http';

// ══ إعدادات ══════════════════════════════════════
const TOKEN    = process.env.TELEGRAM_TOKEN   || '8986679008:AAHmT44SZeoUzdkiaKg-OlnA3NHOonHZ2cw';
const CHAT_ID  = process.env.TELEGRAM_CHAT_ID || '6526134897';
const SYMBOL   = process.env.SYMBOL           || 'MNQ';
const LOOKBACK = parseInt(process.env.LOOKBACK   || '11');
const RR_RATIO = parseFloat(process.env.RR_RATIO || '1.5');
const MAX_DAILY_LOSSES = 2;
const TIMEOUT_HOURS    = 4;

// ══ الحالة ════════════════════════════════════════
let lastUpdateId = 0;
let running      = false;
let activeTrade  = null;

const daily = { traded: false, losses: 0, wins: 0, halted: false, date: '' };

// ══ Telegram ══════════════════════════════════════
async function tg(text) {
  try {
    await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' }),
    });
  } catch (_) {}
}

// ══ أوامر Telegram ════════════════════════════════
async function pollCommands() {
  try {
    const r = await fetch(
      `https://api.telegram.org/bot${TOKEN}/getUpdates?offset=${lastUpdateId + 1}&timeout=0`
    );
    const j = await r.json();
    for (const u of j.result || []) {
      lastUpdateId = u.update_id;
      const cmd = (u.message?.text || '').trim().toLowerCase();

      if (cmd === '/status') {
        const tradeInfo = activeTrade
          ? `\n📊 صفقة مفتوحة: ${activeTrade.type} @ ${activeTrade.price}\n🛑 SL: ${activeTrade.sl} | 🎯 TP: ${activeTrade.tp}`
          : '\n📭 لا توجد صفقات مفتوحة';
        await tg(
`📊 <b>حالة البوت</b>
${daily.halted ? '🛑 موقوف' : '✅ يعمل'}
✅ أرباح اليوم: ${daily.wins}
❌ خسائر اليوم: ${daily.losses}/${MAX_DAILY_LOSSES}
📋 صفقة اليوم: ${daily.traded ? 'تم' : 'لم تُنفَّذ بعد'}
⏰ الإشارة: 14:00 UTC${tradeInfo}`);

      } else if (cmd === '/win') {
        daily.wins++;
        await tg(`✅ ربح مسجّل — الإجمالي: ${daily.wins} ربح`);

      } else if (cmd === '/loss') {
        daily.losses++;
        if (daily.losses >= MAX_DAILY_LOSSES) {
          daily.halted = true;
          await tg(`🛑 خسارة #${daily.losses} — إيقاف البوت حتى الغد`);
        } else {
          await tg(`⚠️ خسارة #${daily.losses} — تبقّى ${MAX_DAILY_LOSSES - daily.losses} قبل الإيقاف`);
        }

      } else if (cmd === '/reset') {
        Object.assign(daily, { traded: false, losses: 0, wins: 0, halted: false });
        activeTrade = null;
        await tg('🔄 تم إعادة تعيين البوت');

      } else if (cmd === '/help') {
        await tg(
`📋 <b>الأوامر:</b>
/status — الحالة
/win    — تسجيل ربح
/loss   — تسجيل خسارة
/reset  — إعادة تعيين`);
      }
    }
  } catch (_) {}
}

// ══ إعادة تعيين يومي ══════════════════════════════
function resetDailyIfNeeded() {
  const today = new Date().toISOString().slice(0, 10);
  if (daily.date !== today) {
    Object.assign(daily, { traded: false, losses: 0, wins: 0, halted: false, date: today });
    activeTrade = null;
    console.log(`[Reset] يوم جديد — ${today}`);
  }
}

// ══ متابعة الصفقة المفتوحة ════════════════════════
async function checkActiveTrade() {
  if (!activeTrade) return;

  try {
    const bars = await get5mBars(SYMBOL);
    if (!bars?.length) return;

    const openSec = activeTrade.openTime / 1000;
    const newBars = bars.filter(b => b.time > openSec);
    if (!newBars.length) return;

    let result = null;
    let resultPrice = null;

    if (Date.now() - activeTrade.openTime > TIMEOUT_HOURS * 60 * 60 * 1000) {
      result      = 'TIMEOUT';
      resultPrice = bars.at(-1).close;
    } else {
      for (const bar of newBars) {
        if (activeTrade.type === 'LONG') {
          if (bar.low  <= activeTrade.sl) { result = 'LOSS'; resultPrice = activeTrade.sl; break; }
          if (bar.high >= activeTrade.tp) { result = 'WIN';  resultPrice = activeTrade.tp; break; }
        } else {
          if (bar.high >= activeTrade.sl) { result = 'LOSS'; resultPrice = activeTrade.sl; break; }
          if (bar.low  <= activeTrade.tp) { result = 'WIN';  resultPrice = activeTrade.tp; break; }
        }
      }
    }

    if (!result) return;

    const mins  = Math.round((Date.now() - activeTrade.openTime) / 60000);
    const trade = activeTrade;
    activeTrade = null;

    if (result === 'WIN') {
      daily.wins++;
      await tg(
`✅ <b>ربح — MNQ</b>
🎯 TP: <b>${resultPrice}</b>
📈 ${trade.type} من ${trade.price} (+${Math.abs(resultPrice - trade.price).toFixed(0)} نقطة)
⏱ المدة: ${mins} دقيقة
─────
✅ أرباح اليوم: ${daily.wins} | ❌ خسائر: ${daily.losses}`);

    } else if (result === 'LOSS') {
      daily.losses++;
      if (daily.losses >= MAX_DAILY_LOSSES) {
        daily.halted = true;
        await tg(
`❌ <b>خسارة — MNQ</b>
🛑 SL: <b>${resultPrice}</b>
⏱ ${mins} دقيقة
─────
🛑 <b>${daily.losses} خسائر اليوم — البوت موقوف حتى الغد</b>`);
      } else {
        await tg(
`❌ <b>خسارة — MNQ</b>
🛑 SL: <b>${resultPrice}</b>
⏱ ${mins} دقيقة
⚠️ خسارة #${daily.losses} — تبقّى ${MAX_DAILY_LOSSES - daily.losses} قبل الإيقاف`);
      }
    } else {
      await tg(
`⏳ <b>Timeout — MNQ</b>
لم يصل TP أو SL خلال ${TIMEOUT_HOURS} ساعات
السعر: ${resultPrice} | الدخول: ${trade.price}
أغلق الصفقة يدوياً إذا كانت مفتوحة`);
    }

    console.log(`[Trade] ${SYMBOL} → ${result} @ ${resultPrice} (${mins}m)`);
  } catch (e) {
    console.error('[Trade]', e.message);
  }
}

// ══ إشارة 14:00 UTC ═══════════════════════════════
async function signal1400() {
  resetDailyIfNeeded();

  if (daily.halted)  { console.log('[14:00] 🛑 موقوف'); return; }
  if (daily.traded)  { console.log('[14:00] ✅ صفقة اليوم منفذة'); return; }
  if (activeTrade)   { console.log('[14:00] صفقة مفتوحة'); return; }

  console.log('[14:00] 🔍 تحليل MNQ...');
  try {
    const bars   = await get5mBars(SYMBOL);
    const result = analyze1400(bars, LOOKBACK, RR_RATIO);

    if (!result.signal) {
      const why = result.error || result.reason || 'لا إشارة';
      console.log(`[14:00] ⏭ ${why}`);
      await tg(`⏭ <b>14:00 UTC — لا إشارة</b>\n${why}`);
      return;
    }

    const sig  = result.signal;
    const risk = Math.abs(sig.price - sig.sl).toFixed(0);
    const pts  = Math.abs(sig.tp - sig.price).toFixed(0);

    daily.traded = true;
    activeTrade  = {
      type:     sig.type,
      price:    sig.price,
      sl:       sig.sl,
      tp:       sig.tp,
      openTime: Date.now(),
    };

    await tg(
`${sig.type === 'LONG' ? '📈' : '📉'} <b>${sig.type} — MNQ</b>

💰 الدخول:  <b>${sig.price}</b>
🛑 SL:      <b>${sig.sl}</b>   (${risk} نقطة)
🎯 TP:      <b>${sig.tp}</b>   (+${pts} نقطة)
📊 RR:      1:${sig.rr}
🌊 الموجة:  ${sig.waveSize} نقطة

⏰ 14:00 UTC | البوت يتابع تلقائياً`);

    console.log(`[14:00] ✅ ${sig.type} @ ${sig.price} | SL:${sig.sl} TP:${sig.tp}`);
  } catch (e) {
    console.error('[14:00] ❌', e.message);
    await tg(`⚠️ <b>14:00 — خطأ</b>\n${e.message}`);
  }
}

// ══ الفحص الدوري (كل دقيقة) ════════════════════════
async function tick() {
  if (running) return;
  running = true;
  try {
    await pollCommands();
    resetDailyIfNeeded();
    await checkActiveTrade();
  } catch (e) {
    console.error('[tick]', e.message);
  } finally {
    running = false;
  }
}

// ══ جدولة 14:00 UTC ═══════════════════════════════
function schedule1400() {
  function msUntil1400() {
    const now  = new Date();
    const next = new Date();
    next.setUTCHours(14, 0, 0, 0);
    if (next <= now) next.setUTCDate(next.getUTCDate() + 1);
    return next - now;
  }
  setTimeout(function fire() {
    signal1400();
    setTimeout(fire, msUntil1400());
  }, msUntil1400());

  const mins = Math.round(msUntil1400() / 60000);
  console.log(`  ⏰ إشارة 14:00 UTC خلال ${mins} دقيقة`);
}

// ══ ملخص صباحي ════════════════════════════════════
function scheduleDailySummary() {
  function msUntil8() {
    const now = new Date(), next = new Date();
    next.setUTCHours(8, 0, 0, 0);
    if (next <= now) next.setUTCDate(next.getUTCDate() + 1);
    return next - now;
  }
  setTimeout(function fire() {
    tg(
`🌅 <b>صباح الخير — MNQ Bot</b>
📅 ${new Date().toISOString().slice(0, 10)}
✅ أرباح أمس: ${daily.wins}
❌ خسائر أمس: ${daily.losses}
⏰ إشارة اليوم: 14:00 UTC
🤖 البوت يعمل`
    ).catch(() => {});
    setTimeout(fire, msUntil8());
  }, msUntil8());
}

// ══ بدء التشغيل ══════════════════════════════════
console.log('═'.repeat(48));
console.log('  🤖  MNQ Bot — 14:00 UTC Reversal');
console.log('═'.repeat(48));
console.log(`  📊 Symbol   : ${SYMBOL}`);
console.log(`  ⏰ Signal   : 14:00 UTC يومياً`);
console.log(`  🌊 Lookback : ${LOOKBACK} bars (${LOOKBACK * 5} دقيقة)`);
console.log(`  🎯 RR Ratio : 1:${RR_RATIO}`);
console.log(`  🛑 Max Loss : ${MAX_DAILY_LOSSES} / يوم`);
console.log('═'.repeat(48));

tg(
`🚀 <b>MNQ Bot — 14:00 UTC Reversal</b>

📊 <b>الأداة:</b> MNQ (Micro NQ)
⏰ <b>الإشارة:</b> 14:00 UTC يومياً (صفقة واحدة)
🌊 <b>Lookback:</b> ${LOOKBACK} bars (${LOOKBACK * 5} دقيقة)
🎯 <b>RR:</b> 1:${RR_RATIO}
🛑 <b>حد الخسارة:</b> ${MAX_DAILY_LOSSES} / يوم

<b>الأوامر:</b> /status /win /loss /reset /help`
).catch(() => {});

schedule1400();
scheduleDailySummary();
setInterval(tick, 60 * 1000);
tick();

// ══ Health check ════════════════════════════════
createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status:      daily.halted ? 'halted' : 'running',
    symbol:      SYMBOL,
    daily,
    activeTrade,
    uptime:      Math.round(process.uptime()),
    time:        new Date().toISOString(),
    next1400:    (() => {
      const next = new Date();
      next.setUTCHours(14, 0, 0, 0);
      if (next <= new Date()) next.setUTCDate(next.getUTCDate() + 1);
      return next.toISOString();
    })(),
  }));
}).listen(process.env.PORT || 3000, () => {
  console.log(`  🌐 Health check: port ${process.env.PORT || 3000}`);
});
