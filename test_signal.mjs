/**
 * اختبار سريع — يرسل إشارة تجريبية حقيقية على تيليغرام
 * ويعرض حالة السوق الآن
 */
import { get5mBars, get15mBars, get1hBars } from './data.js';
import { analyzeSimple, currentSession }     from './strategy_simple.js';

const TOKEN   = process.env.TELEGRAM_TOKEN   || '8986679008:AAHmT44SZeoUzdkiaKg-OlnA3NHOonHZ2cw';
const CHAT_ID = process.env.TELEGRAM_CHAT_ID || '6526134897';

async function tg(text) {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' }),
  });
  const j = await r.json();
  if (!j.ok) console.error('❌ Telegram Error:', j.description);
  return j.ok;
}

console.log('\n🔍 جاري جلب بيانات السوق...');

const [bars5m, bars15m, bars1h] = await Promise.all([
  get5mBars('MNQ'),
  get15mBars('MNQ'),
  get1hBars('MNQ'),
]);

console.log(`✅ بيانات مستلمة: ${bars5m.length} شمعة 5M | ${bars15m.length} شمعة 15M | ${bars1h.length} شمعة 1H`);

const r = analyzeSimple(bars5m, bars15m, bars1h);

if (r.error) {
  console.error('❌ خطأ في التحليل:', r.error);
  process.exit(1);
}

// ── عرض الحالة الكاملة في الكونسول
const session = currentSession();
console.log('\n══════════════════════════════════════');
console.log('  حالة السوق الآن');
console.log('══════════════════════════════════════');
console.log(`  السعر      : ${r.price}`);
console.log(`  الاتجاه    : ${r.htfTrend}`);
console.log(`  الجلسة     : ${session}`);
console.log(`  EMA21 (5M) : ${r.e21_5m}`);
console.log(`  RSI        : ${r.rsi}`);
console.log(`  ATR        : ${r.atr}`);
console.log(`  نقاط LONG  : ${r.scoreLong}/5`);
console.log(`  نقاط SHORT : ${r.scoreShort}/5`);
console.log(`  إشارة       : ${r.signal ? r.signal.type + ' ⭐' : 'لا توجد'}`);
if (r.debug?.reason) console.log(`  السبب       : ${r.debug.reason}`);

// ── إرسال رسالة الاختبار على تيليغرام
console.log('\n📱 إرسال رسالة اختبار على تيليغرام...');

const statusMsg =
`🧪 <b>اختبار البوت — حالة السوق الآن</b>

💹 MNQ @ <b>${r.price}</b>
📈 الاتجاه: <b>${r.htfTrend}</b>
🕐 الجلسة: <b>${session}</b>
📉 EMA21 (5M): <b>${r.e21_5m}</b>
📊 RSI: <b>${r.rsi}</b>

⭐ نقاط LONG:  <b>${r.scoreLong}/5</b>
⭐ نقاط SHORT: <b>${r.scoreShort}/5</b>
🎯 الإشارة: <b>${r.signal ? r.signal.type : 'لا توجد حتى الآن'}</b>

${r.debug?.reason ? `💬 السبب: ${r.debug.reason}` : ''}

━━━━━━━━━━━━━━━━━━━━
✅ الاتصال يعمل — البوت متصل بتيليغرام
⏱ يفحص كل 5 دقائق — الإشارة ستصل عند توفر الشروط`;

const ok = await tg(statusMsg);

if (ok) {
  console.log('✅ تم إرسال رسالة الاختبار على تيليغرام بنجاح!');
} else {
  console.log('❌ فشل إرسال رسالة تيليغرام');
}

// ── إرسال إشارة تجريبية شكلية
if (!r.signal) {
  console.log('\n📤 إرسال إشارة تجريبية (Demo)...');
  const demoPrice = r.price;
  const demoSL    = +(demoPrice - r.atr * 1.5).toFixed(2);
  const demoTP1   = +(demoPrice + r.atr * 3).toFixed(2);
  const demoTP2   = +(demoPrice + r.atr * 5).toFixed(2);
  const risk      = (demoPrice - demoSL).toFixed(0);

  await tg(
`📈 <b>LONG — NQ Futures</b>   ⭐⭐ [DEMO — اختبار فقط]

💰 الدخول:  <b>${demoPrice}</b>
🛑 SL:      <b>${demoSL}</b>   (−${risk} نقطة)
🎯 TP1:     <b>${demoTP1}</b>
🎯 TP2:     <b>${demoTP2}</b>

📊 RSI: ${r.rsi}   |   ATR: ${r.atr}
🕐 ${session}

✅ هذه رسالة تجريبية — هكذا ستبدو الإشارة الحقيقية
⚠️ <i>لا تتداول بناءً على هذه الرسالة</i>`
  );
  console.log('✅ تم إرسال الإشارة التجريبية!');
}

console.log('\n🎯 تحقق من تيليغرام الآن!');
