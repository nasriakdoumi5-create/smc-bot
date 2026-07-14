/**
 * Local Chart Analyzer — يعمل على حاسوبك، يتصل بـ Chrome:9222
 * ──────────────────────────────────────────────────────────
 * يحلّل شارتك المفتوح في TradingView بنفس نظام IFA-OS، ويرسل
 * التقرير إلى تيليجرام (اختياري) ويطبعه في الطرفية.
 *
 * الاستخدام (على حاسوبك):
 *   1) أغلق Chrome تماماً، ثم افتحه بمنفذ التصحيح:
 *      Windows:
 *        "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
 *      mac:
 *        /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
 *   2) في ذلك Chrome: افتح TradingView وسجّل الدخول
 *   3) في الطرفية داخل مجلد المشروع:
 *        set CDP_ENDPOINT=http://localhost:9222   (Windows: set / mac,linux: export)
 *        set ANTHROPIC_API_KEY=sk-ant-...
 *        node analyze_local.js MNQ
 *
 * متغيرات اختيارية للإرسال لتيليجرام:
 *   TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
 */

import { runVisionAnalysis, VISION_SYMBOLS } from './chart_vision.js';

const symbol = (process.argv[2] || 'MNQ').toUpperCase();

if (!VISION_SYMBOLS.includes(symbol)) {
  console.error(`رمز غير مدعوم: ${symbol} — المتاح: ${VISION_SYMBOLS.join(', ')}`);
  process.exit(1);
}
if (!process.env.CDP_ENDPOINT) {
  console.error('⚠️  CDP_ENDPOINT غير مضبوط — للاتصال بـ Chrome المحلي اضبط: CDP_ENDPOINT=http://localhost:9222');
}

async function tgSend(text) {
  const token = process.env.TELEGRAM_TOKEN, chat = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chat) return;
  // تقسيم على حد تيليجرام
  for (let i = 0; i < text.length; i += 4000) {
    await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chat, text: text.slice(i, i + 4000), disable_web_page_preview: true }),
    }).catch(() => {});
  }
}

(async () => {
  console.log(`👁️  فتح شارت ${symbol} والتقاط الأطر (يومي/4H/1H/15M/5M)...`);
  try {
    const report = await runVisionAnalysis(symbol);
    console.log('\n' + '═'.repeat(60) + '\n');
    console.log(report);
    console.log('\n' + '═'.repeat(60));
    await tgSend(`👁️ تحليل بصري — ${symbol}\n\n${report}`);
    console.log('\n✅ اكتمل' + (process.env.TELEGRAM_TOKEN ? ' — أُرسل لتيليجرام أيضاً' : ''));
  } catch (e) {
    console.error('❌ فشل التحليل:', e.message);
    process.exit(1);
  }
})();
