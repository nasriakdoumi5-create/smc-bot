/**
 * Institutional Futures Analyst — Claude API integration
 * ─────────────────────────────────────────────────────
 * System prompt : prompts/futures-analyst-os.md (18 parts)
 * Live data     : TradingView ONLY (data_tradingview.js) — Daily/4H/1H/15M/5M
 *                 يُغذّى من مؤشر IFA Data Feed عبر webhook التنبيهات الموجود
 * Macro         : ForexFactory calendar (calendar.js)
 * Trigger       : Telegram commands in bot.js (/mnq /bias ... or bare symbol)
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'fs';
import { getBars, feedStatus } from './data_tradingview.js';
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
  const status = feedStatus(symbol);
  if (!status.hasData) {
    throw new Error(
      `لا توجد بيانات TradingView لـ ${symbol} بعد — ` +
      `أضف مؤشر "IFA Data Feed" على شارت 5 دقائق وفعّل الـ Alert (انظر /setup)`
    );
  }

  const bars1d = getBars(symbol, '1d');
  const bars4h = getBars(symbol, '4h');
  const bars1h = getBars(symbol, '1h');
  const bars15 = getBars(symbol, '15m');
  const bars5  = getBars(symbol, '5m');

  const last = bars5[bars5.length - 1] || bars15[bars15.length - 1] || bars1h[bars1h.length - 1];

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

  return {
    price: last?.close ?? null,
    text: [
      `LIVE MARKET DATA — ${symbol} (TradingView live feed via webhook; last update: ${feedAge})`,
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
