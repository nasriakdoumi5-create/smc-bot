/**
 * Institutional Futures Analyst — Claude API integration
 * ─────────────────────────────────────────────────────
 * System prompt : prompts/futures-analyst-os.md (18 parts)
 * Live data     : TradingView raw candles ONLY (market_db.js)
 * Market memory : market_memory.js — Structure/BOS/CHOCH/Liquidity/FVG/OB
 * Macro         : ForexFactory calendar (calendar.js)
 * Trigger       : Telegram commands in bot.js (/mnq /bias ... or bare symbol)
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'fs';
import { getCandles, dbStatus } from './market_db.js';
import { getMemory, updateMemory } from './market_memory.js';
import { currentSession } from './strategy_simple.js';
import { fetchCalendar } from './calendar.js';

const SYSTEM_PROMPT = readFileSync(
  new URL('./prompts/futures-analyst-os.md', import.meta.url), 'utf8'
);

export const ANALYST_SYMBOLS = ['MNQ', 'MGC', 'MCL'];

// أوامر مكتبة الأوامر (COMMAND LIBRARY في البرومبت) → التعليمة المرسلة للمحلل
export const ANALYST_COMMANDS = {
  bias:      'Execute the /BIAS command: return only the market bias (Bullish / Bearish / Neutral) with an explanation in less than 100 words.',
  entry:     'Execute the /ENTRY command: search only for the highest quality entry. If no institutional setup exists, output NO ENTRY.',
  exit:      'Execute the /EXIT command: determine TP1, TP2, TP3, trailing logic, and exit conditions.',
  levels:    'Execute the /LEVELS command: return only major support, major resistance, demand, supply, liquidity high, liquidity low.',
  liquidity: 'Execute the /LIQUIDITY command: analyze external liquidity, internal liquidity, liquidity sweeps, untouched liquidity.',
  structure: 'Execute the /STRUCTURE command: analyze only trend, BOS, CHOCH, market structure.',
  session:   'Execute the /SESSION command: analyze current session, session quality, expected behavior, session risks.',
  news:      'Execute the /NEWS command: evaluate macroeconomic risk and whether scheduled events may invalidate technical analysis.',
  report:    'Execute the /REPORT command: generate the complete institutional report.',
  checklist: 'Execute the /CHECKLIST command: run the complete institutional checklist and return PASS or FAIL for every category.',
  risk:      'Execute the /RISK command: evaluate risk, reward, invalidation, trade quality, capital protection.',
  scenarios: 'Execute the /SCENARIOS command: generate primary scenario, alternative scenario, failure scenario.',
  wait:      'Execute the /WAIT command: determine whether waiting is preferable to trading right now.',
  notrade:   'Execute the /NOTRADE command: explain objectively why no institutional trade currently exists.',
  battle:    'Execute the /BATTLE command: conduct a structured evidence review — bullish evidence, bearish evidence, neutral evidence, contradicting evidence, final verdict.',
  quality:   'Execute the /QUALITY command: calculate the Trade Quality Score and explain every deduction.',
  audit:     'Execute the /AUDIT command: perform a complete audit of the analysis, search for logical weaknesses, attempt to invalidate the trade before approving it.',
};

const FULL_ANALYSIS =
  'Perform the complete institutional analysis (the /MNQ-style full command): ' +
  'executive summary, Daily/4H/1H bias, 15M structure, 5M execution, liquidity, ' +
  'supply, demand, primary scenario, alternative scenario, entry plan, risk review, final verdict. ' +
  'Follow the Part 13 report structure.';

const client = new Anthropic(); // ANTHROPIC_API_KEY من متغيرات البيئة

// ── تنسيق الشموع بشكل مضغوط (سطر لكل شمعة) ───────────
function fmtBars(bars, count) {
  return bars.slice(-count).map(b => {
    const t = new Date(b.time * 1000).toISOString().slice(0, 16).replace('T', ' ');
    return `${t} O:${b.open.toFixed(2)} H:${b.high.toFixed(2)} L:${b.low.toFixed(2)} C:${b.close.toFixed(2)} V:${b.volume || 0}`;
  }).join('\n');
}

// ── الأحداث الاقتصادية القادمة (USD، خلال 48 ساعة) ────
async function upcomingEvents() {
  try {
    const events = await fetchCalendar();
    const now = Date.now(), limit = now + 48 * 3600 * 1000;
    const usd = events.filter(e => {
      const t = new Date(e.date).getTime();
      return e.country === 'USD' && t >= now - 3600 * 1000 && t <= limit
        && (e.impact === 'High' || e.impact === 'Medium');
    });
    if (!usd.length) return 'No high/medium impact USD events in the next 48 hours.';
    return usd
      .sort((a, b) => new Date(a.date) - new Date(b.date))
      .map(e => `${new Date(e.date).toISOString().slice(0, 16).replace('T', ' ')} UTC [${e.impact}] ${e.title}`)
      .join('\n');
  } catch {
    return 'UNAVAILABLE — economic calendar could not be fetched.';
  }
}

// ── بناء حزمة البيانات الحية (من TradingView حصراً) ────
async function buildMarketData(symbol) {
  const status = dbStatus(symbol);
  if (!status.hasData) {
    throw new Error(
      `لا توجد بيانات TradingView لـ ${symbol} بعد — ` +
      `أضف مؤشر "IFA Data Feed V2" على شارتات الأطر الخمسة وفعّل الـ Alerts (انظر /setup)`
    );
  }

  const bars1d = getCandles(symbol, '1d');
  const bars4h = getCandles(symbol, '4h');
  const bars1h = getCandles(symbol, '1h');
  const bars15 = getCandles(symbol, '15m');
  const bars5  = getCandles(symbol, '5m');
  const bars1  = getCandles(symbol, '1m');

  const last = bars1[bars1.length - 1] || bars5[bars5.length - 1] || bars15[bars15.length - 1] || bars1h[bars1h.length - 1];

  const tf = (name, bars, target) => {
    if (!bars.length) {
      return `=== ${name} ===\nUNAVAILABLE — no TradingView feed data received yet for this timeframe.`;
    }
    const depthNote = bars.length < target
      ? ` (only ${bars.length} of ${target} target bars accumulated so far — history is still building)`
      : '';
    return `=== ${name}${depthNote} ===\n${fmtBars(bars, target)}`;
  };

  const feedAge = status.lastIngest
    ? `${Math.round((Date.now() - status.lastIngest) / 60000)} min ago`
    : 'unknown';

  const calendar = await upcomingEvents();

  // لقطة ذاكرة السوق — محدثة من محرك الأحداث عند كل شمعة
  const memory = getMemory(symbol) || updateMemory(symbol);

  return {
    price: last?.close ?? null,
    text: [
      `LIVE MARKET DATA — ${symbol} (TradingView raw candle feed via webhook; last update: ${feedAge})`,
      `Current time (UTC): ${new Date().toISOString().slice(0, 16).replace('T', ' ')}`,
      `Current session: ${currentSession()}`,
      `Last price: ${last ? last.close.toFixed(2) : 'UNAVAILABLE'}`,
      '',
      tf('DAILY (target 60 bars)', bars1d, 60),
      '',
      tf('4H (target 60 bars)', bars4h, 60),
      '',
      tf('1H (target 96 bars)', bars1h, 96),
      '',
      tf('15M (target 96 bars)', bars15, 96),
      '',
      tf('5M (target 78 bars)', bars5, 78),
      '',
      tf('1M (execution timeframe, target 60 bars)', bars1, 60),
      '',
      '=== MARKET MEMORY (computed by the deterministic event engine from the raw candles above) ===',
      'Treat this as pre-computed supporting evidence. Verify it against the raw candles;',
      'your own reading of structure always prevails over the computed snapshot.',
      JSON.stringify(memory, null, 1),
      '',
      `=== ECONOMIC CALENDAR (USD, next 48h) ===\n${calendar}`,
    ].join('\n'),
  };
}

/**
 * تشغيل تحليل كامل أو أمر مركّز.
 * @param {string} symbol   MNQ | MGC | MCL
 * @param {string} [command] مفتاح من ANALYST_COMMANDS — يترك فارغاً للتحليل الكامل
 * @returns {Promise<string>} نص التقرير
 */
export async function runAnalysis(symbol, command = null) {
  if (!process.env.ANTHROPIC_API_KEY) {
    throw new Error('ANTHROPIC_API_KEY غير مضبوط — أضفه في متغيرات البيئة (Railway → Variables)');
  }

  const instruction = command ? ANALYST_COMMANDS[command] : FULL_ANALYSIS;
  const { text: marketData } = await buildMarketData(symbol);

  const stream = client.messages.stream({
    model: 'claude-opus-4-8',
    max_tokens: 32000,
    thinking: { type: 'adaptive' },
    system: [
      { type: 'text', text: SYSTEM_PROMPT, cache_control: { type: 'ephemeral' } },
    ],
    messages: [
      {
        role: 'user',
        content: `${marketData}\n\n=== REQUEST ===\n${instruction}\n\nRespond in Arabic. Keep all technical terms (BOS, CHOCH, liquidity, supply, demand, R:R, verdicts like APPROVED / WATCHLIST / WAIT / NO TRADE) in English.`,
      },
    ],
  });

  const final = await stream.finalMessage();

  if (final.stop_reason === 'refusal') {
    throw new Error('رفض النموذج إتمام هذا التحليل');
  }

  const text = final.content
    .filter(b => b.type === 'text')
    .map(b => b.text)
    .join('\n')
    .trim();

  if (!text) throw new Error('رد فارغ من المحلل');
  return text;
}

// ── تقرير موحّد لكل الرموز (/all) ──────────────────────
// لقطة حتمية من ذاكرة كل رمز — فورية، بلا تكلفة API، وبلا تداخل بين الرموز.
// ليست حكم محلل كامل؛ للتقرير المؤسسي الكامل استخدم /mnq /mgc /mcl.
function symbolSnapshot(symbol) {
  const st = dbStatus(symbol);
  if (!st.hasData) return { symbol, ready: false };

  const m = getMemory(symbol) || updateMemory(symbol);
  const price = m.currentPrice;
  const htf = m.structure?.['4h']?.trend || m.bias?.daily || 'Undetermined';
  const dir = /bull/i.test(htf) ? 'bull' : /bear/i.test(htf) ? 'bear' : 'neutral';

  // منطقة مرشّحة متوافقة مع الاتجاه (من المناطق النشطة في الذاكرة) — ليست توصية دخول
  let zone = null;
  const pick = (arr, want, side) => {
    for (const tf of ['15m', '1h', '4h']) {
      for (const z of (arr?.[tf] || [])) {
        if (z.direction !== want || price == null) continue;
        if (side === 'below' && z.top <= price) return { top: z.top, bottom: z.bottom, tf, kind: want };
        if (side === 'above' && z.bottom >= price) return { top: z.top, bottom: z.bottom, tf, kind: want };
      }
    }
    return null;
  };
  if (dir === 'bull') zone = pick(m.activeOrderBlocks, 'Bullish', 'below') || pick(m.activeFVGs, 'Bullish', 'below');
  else if (dir === 'bear') zone = pick(m.activeOrderBlocks, 'Bearish', 'above') || pick(m.activeFVGs, 'Bearish', 'above');

  return {
    symbol, ready: true, price,
    htf,
    dailyBias: m.bias?.daily || 'Undetermined',
    phase: m.marketPhase?.phase || 'Undetermined',
    pdState: m.dealingRange?.currentState || null,
    lastSweep: m.lastLiquiditySweep || m.liquidity?.lastSweep || null,
    zone,
    depth5m: st.depth['5m'],
  };
}

/**
 * تقرير موحّد لكل الرموز — /all
 * @returns {string} نص جاهز للإرسال (بلا استدعاء Claude)
 */
export function buildAllSummary() {
  const lines = ['📊 <b>التقرير الموحّد — كل الرموز</b>', '<i>لقطة من محرك الذاكرة (ليست حكم محلل كامل — استخدم /mnq /mgc /mcl للتقرير المؤسسي)</i>', ''];
  for (const sym of ANALYST_SYMBOLS) {
    const s = symbolSnapshot(sym);
    if (!s.ready) {
      lines.push(`<b>${sym}</b> — 🔴 لا بيانات بعد (/feed)`, '');
      continue;
    }
    const zoneStr = s.zone
      ? `${Math.max(s.zone.top, s.zone.bottom).toFixed(2)}–${Math.min(s.zone.top, s.zone.bottom).toFixed(2)} (${s.zone.kind} ${s.zone.tf})`
      : 'لا منطقة متوافقة نشطة';
    lines.push(
      `<b>${sym}</b>  ${s.price != null ? '@ ' + s.price.toFixed(2) : ''}`,
      `HTF: ${s.htf}`,
      `Daily Bias: ${s.dailyBias}  |  Phase: ${s.phase}${s.pdState ? '  |  ' + s.pdState : ''}`,
      `Zone: ${zoneStr}`,
      s.lastSweep ? `Last sweep: ${s.lastSweep.direction} @ ${s.lastSweep.price}` : '',
      '',
    );
  }
  lines.push('<i>⚠️ المناطق مرشّحات من الذاكرة وليست توصيات دخول معتمدة.</i>');
  return lines.filter(l => l !== '').join('\n');
}
