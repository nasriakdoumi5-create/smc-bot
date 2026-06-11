/**
 * Order Flow Engine — Tradovate Tick Data
 *
 * يجلب tick data حقيقي ويحسب:
 * - Delta (حجم شراء − حجم بيع) لكل شمعة
 * - Cumulative Delta
 * - Footprint Stacked Imbalance (مثل الصورة)
 * - Delta Divergence (ضعف الاتجاه)
 * - High Volume Node (أكثر مستوى سعري نشاطاً)
 */

import WebSocket from 'ws';

const MD_WS          = 'wss://md.tradovateapi.com/v1/websocket';
const REST_DEMO      = 'https://demo.tradovateapi.com/v1';
const REST_LIVE      = 'https://live.tradovateapi.com/v1';
const TICK_SIZE      = 0.25;   // NQ tick = 0.25 نقطة
const IMBALANCE_RATIO = 3.0;
const STACKED_MIN    = 3;
const TIMEOUT_MS     = 20000;

// ══ Auth ═════════════════════════════════════
async function getToken() {
  const user   = process.env.TRADOVATE_USERNAME;
  const pass   = process.env.TRADOVATE_PASSWORD;
  const isDemo = process.env.TRADOVATE_DEMO !== 'false';
  if (!user || !pass) return null;

  try {
    const r = await fetch(`${isDemo ? REST_DEMO : REST_LIVE}/auth/accesstokenrequest`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name:       user,
        password:   pass,
        appId:      'SMC Elite Bot',
        appVersion: '1.0',
        deviceId:   process.env.TRADOVATE_DEVICE_ID || 'smc-bot-001',
        cid:        Number(process.env.TRADOVATE_CID || 0),
        sec:        process.env.TRADOVATE_SECRET || '',
      }),
    });
    const d = await r.json();
    return d.accessToken || null;
  } catch { return null; }
}

// ══ جلب Tick Data عبر WebSocket ══════════════
function fetchTickData(token, symbol, tickCount = 1500) {
  return new Promise((resolve) => {
    const ws  = new WebSocket(MD_WS);
    let msgId = 0;
    let bars  = null;

    const done = (result) => {
      clearTimeout(timer);
      try { ws.close(); } catch {}
      resolve(result);
    };

    const timer = setTimeout(() => done(null), TIMEOUT_MS);
    ws.on('error', () => done(null));

    ws.on('message', (raw) => {
      const text = raw.toString();
      if (text === 'o') {
        ws.send(`authorize\n${++msgId}\n\n${JSON.stringify({ token })}`);
        return;
      }
      if (text === 'h' || text === '[]') return;

      let msgs;
      try { msgs = JSON.parse(text); } catch { return; }

      for (const msg of msgs) {
        // بعد التفويض — اطلب tick chart
        if (msg.e === 'authorized' || (msg.i === 1 && msg.s === 200)) {
          ws.send(`md/getChart\n${++msgId}\n\n${JSON.stringify({
            symbol,
            chartDescription: {
              underlyingType:   'Tick',
              elementSize:      1,
              elementSizeUnit:  'UnderlyingUnits',
              withHistogram:    false,
            },
            timeRange: { asMuchAsElements: tickCount },
          })}`);
        }

        // استقبال بيانات الشارت
        if (msg.e === 'charts' && msg.d?.bars) {
          bars = msg.d.bars;
          done(bars);
        }
        // بعض الإصدارات ترسل 'chart' بدل 'charts'
        if (msg.e === 'chart' && msg.d?.bars) {
          bars = msg.d.bars;
          done(bars);
        }
      }
    });
  });
}

// ══ تحليل Order Flow ══════════════════════════
function analyzeFlow(ticks) {
  if (!ticks || ticks.length < 10) return null;

  // ── تجميع الـ ticks حسب شمعة 5 دقائق ────────
  const barMs  = 5 * 60 * 1000;
  const barMap = new Map();

  for (const t of ticks) {
    const ts      = new Date(t.timestamp).getTime();
    const barKey  = Math.floor(ts / barMs) * barMs;

    if (!barMap.has(barKey)) {
      barMap.set(barKey, { ts: barKey, footprint: new Map(), buyVol: 0, sellVol: 0 });
    }

    const bar   = barMap.get(barKey);
    // Tradovate: offerVolume = trades hitting ask (buyers)
    //            bidVolume   = trades hitting bid (sellers)
    const buy   = t.offerVolume ?? t.upVolume   ?? 0;
    const sell  = t.bidVolume   ?? t.downVolume ?? 0;
    bar.buyVol  += buy;
    bar.sellVol += sell;

    // مستوى السعر مقرّب لـ tick size
    const price = Math.round(t.close / TICK_SIZE) * TICK_SIZE;
    const prev  = bar.footprint.get(price) || { buy: 0, sell: 0 };
    bar.footprint.set(price, { buy: prev.buy + buy, sell: prev.sell + sell });
  }

  const bars = [...barMap.values()].sort((a, b) => a.ts - b.ts);
  if (bars.length === 0) return null;

  // ── Delta لكل شمعة ────────────────────────
  const deltas = bars.map(b => b.buyVol - b.sellVol);

  // ── Cumulative Delta ────────────────────────
  let cumDelta = 0;
  const cumDeltas = deltas.map(d => (cumDelta += d, cumDelta));

  const lastBar    = bars[bars.length - 1];
  const lastDelta  = deltas[deltas.length - 1];
  const prevDelta  = deltas[deltas.length - 2] ?? 0;

  // ── Stacked Imbalance (Footprint) ──────────
  const levels = [...lastBar.footprint.entries()]
    .map(([price, v]) => ({ price, buy: v.buy, sell: v.sell }))
    .sort((a, b) => b.price - a.price);  // تنازلي من أعلى سعر

  let buyStack = 0, sellStack = 0;
  let maxBuyStack = 0, maxSellStack = 0;
  const buyImbalanceLevels  = [];
  const sellImbalanceLevels = [];

  for (const lv of levels) {
    // Sell imbalance: أكثر بيع عند هذا المستوى
    if (lv.buy > 0 && lv.sell / lv.buy >= IMBALANCE_RATIO) {
      sellStack++;
      if (sellStack <= 4) sellImbalanceLevels.push(lv);
    } else { sellStack = 0; }

    // Buy imbalance: أكثر شراء عند هذا المستوى
    if (lv.sell > 0 && lv.buy / lv.sell >= IMBALANCE_RATIO) {
      buyStack++;
      if (buyStack <= 4) buyImbalanceLevels.push(lv);
    } else { buyStack = 0; }

    maxBuyStack  = Math.max(maxBuyStack,  buyStack);
    maxSellStack = Math.max(maxSellStack, sellStack);
  }

  const stackedBuy  = maxBuyStack  >= STACKED_MIN;
  const stackedSell = maxSellStack >= STACKED_MIN;

  // ── High Volume Node ───────────────────────
  const hvn = levels.reduce((max, lv) =>
    (lv.buy + lv.sell) > (max.buy + max.sell) ? lv : max, levels[0] || { price: 0 });

  // ── Delta Divergence ───────────────────────
  // سعر صاعد لكن delta هابط = ضعف المشترين (إشارة بيع)
  // سعر هابط لكن delta صاعد = ضعف البائعين (إشارة شراء)
  const priceUp   = bars.length >= 2 && lastBar.buyVol + lastBar.sellVol > 0
    && (bars[bars.length - 1].footprint.keys().next().value > bars[bars.length - 2].footprint.keys().next().value);
  const bullDivergence = !priceUp && lastDelta > 0 && lastDelta > prevDelta;  // سعر هابط، delta صاعد
  const bearDivergence = priceUp  && lastDelta < 0 && lastDelta < prevDelta;  // سعر صاعد، delta هابط

  return {
    // الشروط الرئيسية للإشارة
    positiveDelta:  lastDelta > 0,
    negativeDelta:  lastDelta < 0,
    stackedBuy,
    stackedSell,
    bullDivergence,
    bearDivergence,

    // أرقام تفصيلية
    lastDelta,
    cumDelta:        cumDelta,
    lastBuyVol:      lastBar.buyVol,
    lastSellVol:     lastBar.sellVol,
    maxBuyStack,
    maxSellStack,
    hvnPrice:        hvn?.price,
    hvnVolume:       hvn ? hvn.buy + hvn.sell : 0,
    buyImbalanceLevels:  buyImbalanceLevels.slice(0, 3),
    sellImbalanceLevels: sellImbalanceLevels.slice(0, 3),
    totalBars:       bars.length,
  };
}

// ══ الدالة الرئيسية ═══════════════════════════
export async function getOrderFlow(symbol = 'NQM6') {
  const token = await getToken();
  if (!token) return null;

  const ticks = await fetchTickData(token, symbol);
  return analyzeFlow(ticks);
}

// ══ نص Telegram ══════════════════════════════
export function orderFlowText(of) {
  if (!of) return '';
  const lines = [];

  // Delta
  const dSign = of.lastDelta >= 0 ? '🟢' : '🔴';
  lines.push(`${dSign} Delta: <b>${of.lastDelta >= 0 ? '+' : ''}${of.lastDelta}</b>  |  Cum.Δ: ${of.cumDelta >= 0 ? '+' : ''}${of.cumDelta}`);
  lines.push(`   Buy: ${of.lastBuyVol}  /  Sell: ${of.lastSellVol}`);

  // Stacked Imbalance
  if (of.stackedSell) {
    lines.push(`\n🔴 <b>Stacked Sell Imbalance — ${of.maxSellStack} مستويات</b>`);
    of.sellImbalanceLevels.forEach(l => {
      const r = l.buy > 0 ? (l.sell / l.buy).toFixed(1) : '∞';
      lines.push(`   ${l.price} → Buy:${l.buy} / Sell:${l.sell} (${r}x)`);
    });
  }
  if (of.stackedBuy) {
    lines.push(`\n🟢 <b>Stacked Buy Imbalance — ${of.maxBuyStack} مستويات</b>`);
    of.buyImbalanceLevels.forEach(l => {
      const r = l.sell > 0 ? (l.buy / l.sell).toFixed(1) : '∞';
      lines.push(`   ${l.price} → Buy:${l.buy} / Sell:${l.sell} (${r}x)`);
    });
  }

  // Divergence
  if (of.bearDivergence) lines.push(`\n⚠️ <b>Delta Divergence هابط</b> — سعر صاعد لكن البائعون يتحكمون`);
  if (of.bullDivergence) lines.push(`\n⚠️ <b>Delta Divergence صاعد</b> — سعر هابط لكن المشترون يتحكمون`);

  // HVN
  if (of.hvnPrice) lines.push(`\n📍 HVN @ ${of.hvnPrice} (${of.hvnVolume} عقد)`);

  return lines.join('\n');
}
