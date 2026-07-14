/**
 * Chart Vision — CDP live-chart capture + Claude vision analysis
 * ──────────────────────────────────────────────────────────────
 * يفتح شارت TradingView الحقيقي في Chromium (عبر CDP/Playwright)،
 * يلتقط لقطة لكل إطار (يومي/4H/1H/15M/5M) وهو مسجّل الدخول بحسابك،
 * ثم يرسل اللقطات إلى Claude Vision للتحليل بنظام IFA-OS.
 *
 * هذا "التحليل مباشرة على الشارت" — النموذج ينظر للشارت الحي كإنسان.
 *
 * التسجيل: يُحقن كوكي sessionid من حسابك (بلا كلمة مرور/كابتشا).
 * احصل عليه: افتح tradingview.com وأنت مسجّل → DevTools → Application
 *            → Cookies → انسخ قيمة "sessionid".
 *
 * متغيرات البيئة:
 *   ANTHROPIC_API_KEY   مفتاح Claude
 *   TV_SESSIONID        كوكي جلسة TradingView (للتسجيل)
 *   CHROMIUM_PATH       مسار Chromium (اختياري — يُكتشف تلقائياً)
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';
// ملاحظة: playwright يُحمّل ديناميكياً داخل captureCharts حتى لا يتعطّل
// البوت كله إذا لم يكن Chromium/Playwright مثبّتاً على الخادم.

const SYSTEM_PROMPT = readFileSync(
  new URL('./prompts/futures-analyst-os.md', import.meta.url), 'utf8'
);

// الرمز → tickerid في TradingView
const TV_SYMBOL = {
  MNQ: 'CME_MINI:MNQ1!',
  MGC: 'COMEX:MGC1!',
  MCL: 'NYMEX:MCL1!',
};

// (اسم الإطار للعرض, قيمة interval في رابط TradingView)
const TF = [
  ['Daily', 'D'],
  ['4H', '240'],
  ['1H', '60'],
  ['15M', '15'],
  ['5M', '5'],
];

const client = new Anthropic();

// ── اكتشاف مسار Chromium ──────────────────────────────
function chromiumPath() {
  if (process.env.CHROMIUM_PATH && existsSync(process.env.CHROMIUM_PATH)) {
    return process.env.CHROMIUM_PATH;
  }
  // البحث في مجلد playwright browsers
  try {
    const base = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
    const found = execSync(
      `find ${base} -maxdepth 3 -name chrome -type f -path '*chrome-linux*' 2>/dev/null | head -1`,
      { encoding: 'utf8' }
    ).trim();
    if (found && existsSync(found)) return found;
  } catch {}
  return undefined;   // يترك playwright يكتشفه
}

// ── التقاط لقطات الأطر لرمز واحد ──────────────────────
async function captureCharts(symbol) {
  const sessionId = process.env.TV_SESSIONID;
  const tvSym = TV_SYMBOL[symbol];
  if (!tvSym) throw new Error(`رمز غير مدعوم: ${symbol}`);

  let chromium;
  try {
    ({ chromium } = await import('playwright'));
  } catch {
    throw new Error('playwright غير مثبّت — التحليل البصري يحتاج Chromium (انظر تعليمات النشر)');
  }

  // وضعان:
  //  (أ) CDP_ENDPOINT مضبوط → نتصل بـ Chrome مفتوح عندك (localhost:9222)
  //      يستخدم جلستك المسجّلة مباشرة — لا حاجة لكوكي.
  //  (ب) وإلا → نطلق Chromium خاصاً ونسجّل الدخول بكوكي sessionid (للخادم).
  const cdpEndpoint = process.env.CDP_ENDPOINT;
  let browser, context, ownsBrowser;

  if (cdpEndpoint) {
    browser = await chromium.connectOverCDP(cdpEndpoint);
    context = browser.contexts()[0] || (await browser.newContext());
    ownsBrowser = false;   // لا نغلق متصفح المستخدم
  } else {
    if (!sessionId) {
      throw new Error('TV_SESSIONID غير مضبوط — أضف كوكي جلسة TradingView، أو استخدم CDP_ENDPOINT للاتصال بـ Chrome محلي');
    }
    browser = await chromium.launch({
      executablePath: chromiumPath(),
      headless: true,
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
    });
    context = await browser.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
    await context.addCookies([{
      name: 'sessionid', value: sessionId,
      domain: '.tradingview.com', path: '/', httpOnly: true, secure: true,
    }]);
    ownsBrowser = true;
  }

  const page = await context.newPage();
  const shots = [];
  try {
    for (const [label, interval] of TF) {
      const url = `https://www.tradingview.com/chart/?symbol=${encodeURIComponent(tvSym)}&interval=${interval}`;
      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForTimeout(9000);   // انتظار رسم الشارت (canvas)
        shots.push({ label, png: await page.screenshot({ type: 'png' }) });
      } catch (e) {
        console.error(`[Vision] فشل التقاط ${symbol} ${label}:`, e.message);
      }
    }
    return shots;
  } finally {
    await page.close().catch(() => {});
    if (ownsBrowser) await browser.close().catch(() => {});   // لا نغلق متصفح المستخدم في وضع CDP
  }
}

// ── تحليل اللقطات عبر Claude Vision ────────────────────
async function analyzeShots(symbol, shots) {
  if (!shots.length) throw new Error('لم يُلتقط أي شارت — تحقق من TV_SESSIONID وصلاحية الجلسة');

  const content = [];
  for (const { label, png } of shots) {
    content.push({ type: 'text', text: `=== ${symbol} — ${label} chart ===` });
    content.push({
      type: 'image',
      source: { type: 'base64', media_type: 'image/png', data: png.toString('base64') },
    });
  }
  content.push({
    type: 'text',
    text: `These are LIVE TradingView charts for ${symbol}, one per timeframe (Daily → 5M). ` +
      `Perform the full institutional top-down analysis per the IFA-OS. ` +
      `Read structure/levels visually from the charts; state clearly anything you cannot read precisely. ` +
      `Respond in Arabic; keep technical terms and verdicts (BOS, CHOCH, APPROVED / WATCHLIST / WAIT / NO TRADE) in English.`,
  });

  const stream = client.messages.stream({
    model: 'claude-opus-4-8',
    max_tokens: 16000,
    thinking: { type: 'adaptive' },
    system: [{ type: 'text', text: SYSTEM_PROMPT, cache_control: { type: 'ephemeral' } }],
    messages: [{ role: 'user', content }],
  });

  const final = await stream.finalMessage();
  if (final.stop_reason === 'refusal') throw new Error('رفض النموذج إتمام التحليل');
  const text = final.content.filter(b => b.type === 'text').map(b => b.text).join('\n').trim();
  if (!text) throw new Error('رد فارغ من المحلل');
  return text;
}

/**
 * التحليل البصري الكامل لرمز — يلتقط الأطر ويحللها.
 * @param {string} symbol MNQ | MGC | MCL
 * @returns {Promise<string>} نص التقرير
 */
export async function runVisionAnalysis(symbol) {
  if (!process.env.ANTHROPIC_API_KEY) {
    throw new Error('ANTHROPIC_API_KEY غير مضبوط');
  }
  const shots = await captureCharts(symbol);
  return analyzeShots(symbol, shots);
}

export const VISION_SYMBOLS = Object.keys(TV_SYMBOL);
