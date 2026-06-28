/**
 * Tradovate API — DOM + Stacked Imbalance
 * يجلب Order Book حي من Tradovate ويحسب Stacked Imbalances
 */

import WebSocket from 'ws';

const REST_DEMO = 'https://demo.tradovateapi.com/v1';
const REST_LIVE = 'https://live.tradovateapi.com/v1';
const MD_WS_URL = 'wss://md.tradovateapi.com/v1/websocket';

const IMBALANCE_RATIO  = 3.0;   // نسبة اعتبار الـ imbalance (3:1)
const STACKED_MIN      = 3;     // عدد levels متتالية لاعتبارها stacked
const SNAPSHOT_TIMEOUT = 12000; // 12 ثانية max انتظار

// ══ Auth ═════════════════════════════════════
async function getAccessToken() {
  const user   = process.env.TRADOVATE_USERNAME;
  const pass   = process.env.TRADOVATE_PASSWORD;
  const isDemo = process.env.TRADOVATE_DEMO !== 'false';

  if (!user || !pass) return null;

  const base = isDemo ? REST_DEMO : REST_LIVE;
  try {
    const r = await fetch(`${base}/auth/accesstokenrequest`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name:       user,
        password:   pass,
        appId:      'SMC Elite Bot',
        appVersion: '1.0',
        deviceId:   process.env.TRADOVATE_DEVICE_ID || 'smc-bot-001',
        cid:        Number(process.env.TRADOVATE_CID  || 0),
        sec:        process.env.TRADOVATE_SECRET || '',
      }),
    });
    const data = await r.json();
    return data.accessToken || null;
  } catch {
    return null;
  }
}

// ══ DOM Snapshot via WebSocket ════════════════
export async function getDOMSnapshot(symbol = 'NQM6') {
  const token = await getAccessToken();
  if (!token) return null;

  return new Promise((resolve) => {
    const ws  = new WebSocket(MD_WS_URL);
    let msgId = 0;

    const done = (result) => {
      clearTimeout(timer);
      try { ws.close(); } catch {}
      resolve(result);
    };

    const timer = setTimeout(() => done(null), SNAPSHOT_TIMEOUT);

    ws.on('error', () => done(null));

    ws.on('message', (raw) => {
      const text = raw.toString();

      // Handshake
      if (text === 'o') {
        ws.send(`authorize\n${++msgId}\n\n${JSON.stringify({ token })}`);
        return;
      }
      if (text === 'h' || text === '[]') return;

      let msgs;
      try { msgs = JSON.parse(text); } catch { return; }

      for (const msg of msgs) {
        // بعد التفويض — اشترك في DOM
        if (msg.e === 'authorized' || (msg.i === 1 && msg.s === 200)) {
          ws.send(`md/subscribeDom\n${++msgId}\n\n${JSON.stringify({ symbol })}`);
        }

        // استقبال DOM
        if (msg.e === 'dom' && msg.d) {
          done(parseDOM(msg.d, symbol));
        }
      }
    });
  });
}

// ══ تحليل Order Book ═══════════════════════════
function parseDOM(dom, symbol) {
  // bids: [{price, size}]  ترتيب تنازلي (أعلى bid أولاً)
  // asks: [{price, size}]  ترتيب تصاعدي (أدنى ask أولاً)
  const bids = (dom.bids || []).sort((a, b) => b.price - a.price);
  const asks = (dom.asks || []).sort((a, b) => a.price - b.price);

  const levels = Math.min(bids.length, asks.length, 20);

  // ── Stacked Imbalance ────────────────────────
  // نقارن كل level: bid[i] vs ask[i] بنفس الترتيب من السعر الحالي
  let buyStack = 0, sellStack = 0;
  let maxBuyStack = 0, maxSellStack = 0;
  const stackedBuyLevels  = [];
  const stackedSellLevels = [];

  for (let i = 0; i < levels; i++) {
    const b = bids[i]?.size || 0;
    const a = asks[i]?.size || 0;

    // Buy imbalance: bid أكبر بكثير من ask (مشترون عدوانيون)
    if (a > 0 && b / a >= IMBALANCE_RATIO) {
      buyStack++;
      stackedBuyLevels.push({ price: bids[i].price, bid: b, ask: a, ratio: (b/a).toFixed(1) });
    } else {
      buyStack = 0;
    }

    // Sell imbalance: ask أكبر بكثير من bid (بائعون عدوانيون)
    if (b > 0 && a / b >= IMBALANCE_RATIO) {
      sellStack++;
      stackedSellLevels.push({ price: asks[i].price, bid: b, ask: a, ratio: (a/b).toFixed(1) });
    } else {
      sellStack = 0;
    }

    maxBuyStack  = Math.max(maxBuyStack,  buyStack);
    maxSellStack = Math.max(maxSellStack, sellStack);
  }

  // ── إجمالي حجم الـ DOM ──────────────────────
  const totalBid = bids.slice(0, 10).reduce((s, x) => s + x.size, 0);
  const totalAsk = asks.slice(0, 10).reduce((s, x) => s + x.size, 0);
  const depthRatio = totalAsk > 0 ? (totalBid / totalAsk).toFixed(2) : '0';

  // ── الحكم النهائي ────────────────────────────
  const stackedBuy  = maxBuyStack  >= STACKED_MIN;
  const stackedSell = maxSellStack >= STACKED_MIN;

  // أكبر order في الـ book (iceberg/wall detector)
  const bigBid = bids.slice(0, 5).reduce((max, x) => x.size > max.size ? x : max, { size: 0 });
  const bigAsk = asks.slice(0, 5).reduce((max, x) => x.size > max.size ? x : max, { size: 0 });

  return {
    symbol,
    stackedBuy,
    stackedSell,
    maxBuyStack,
    maxSellStack,
    stackedBuyLevels:  stackedBuyLevels.slice(0, 3),
    stackedSellLevels: stackedSellLevels.slice(0, 3),
    totalBid,
    totalAsk,
    depthRatio: +depthRatio,
    bigBid,
    bigAsk,
    bestBid: bids[0]?.price,
    bestAsk: asks[0]?.price,
  };
}

// ══ سعر فوري عبر subscribeQuote ══════════════
export async function getRealtimePrice(symbol = 'NQM6') {
  const token = await getAccessToken();
  if (!token) return null;

  return new Promise((resolve) => {
    const ws  = new WebSocket(MD_WS_URL);
    let msgId = 0;

    const done = (result) => {
      clearTimeout(timer);
      try { ws.close(); } catch {}
      resolve(result);
    };

    const timer = setTimeout(() => done(null), 10000);
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
        if (msg.e === 'authorized' || (msg.i === 1 && msg.s === 200)) {
          ws.send(`md/subscribeQuote\n${++msgId}\n\n${JSON.stringify({ symbol })}`);
        }
        if (msg.e === 'quote' && msg.d) {
          const price = msg.d.trade?.price ?? msg.d.bid ?? null;
          if (price) done({ price, time: Math.floor(Date.now() / 1000) });
        }
      }
    });
  });
}

// ══ بيانات تاريخية عبر WebSocket ════════════
export async function getHistoricalBars(symbol = 'NQM6', intervalMinutes = 5, count = 500) {
  const token = await getAccessToken();
  if (!token) return null;

  return new Promise((resolve) => {
    const ws  = new WebSocket(MD_WS_URL);
    let msgId = 0;

    const done = (result) => {
      clearTimeout(timer);
      try { ws.close(); } catch {}
      resolve(result);
    };

    const timer = setTimeout(() => done(null), 20000);
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
        if (msg.e === 'authorized' || (msg.i === 1 && msg.s === 200)) {
          ws.send(`md/getChart\n${++msgId}\n\n${JSON.stringify({
            symbol,
            chartDescription: {
              underlyingType:  'MinuteBar',
              elementSize:     intervalMinutes,
              elementSizeUnit: 'UnderlyingUnits',
              withHistogram:   false,
            },
            timeRange: { asMuchAsElements: count },
          })}`);
        }

        if (msg.e === 'chart' && msg.d?.bars?.length) {
          const bars = msg.d.bars.map(b => ({
            time:   Math.floor(new Date(b.timestamp).getTime() / 1000),
            open:   b.open,
            high:   b.high,
            low:    b.low,
            close:  b.close,
            volume: (b.upVolume || 0) + (b.downVolume || 0),
          }));
          done(bars);
        }
      }
    });
  });
}

// ══ نص Telegram للـ DOM ══════════════════════
export function domSummaryText(dom) {
  if (!dom) return '';

  const lines = [];

  if (dom.stackedSell) {
    lines.push(`🔴 <b>Stacked Sell Imbalance — ${dom.maxSellStack} levels</b>`);
    dom.stackedSellLevels.forEach(l =>
      lines.push(`   ${l.price} → Bid:${l.bid} / Ask:${l.ask} (${l.ratio}x)`)
    );
  }
  if (dom.stackedBuy) {
    lines.push(`🟢 <b>Stacked Buy Imbalance — ${dom.maxBuyStack} levels</b>`);
    dom.stackedBuyLevels.forEach(l =>
      lines.push(`   ${l.price} → Bid:${l.bid} / Ask:${l.ask} (${l.ratio}x)`)
    );
  }
  if (!dom.stackedSell && !dom.stackedBuy) {
    lines.push(`📊 DOM متوازن — Bid:${dom.totalBid} / Ask:${dom.totalAsk} (${dom.depthRatio}x)`);
  }

  if (dom.bigAsk.size > 200) {
    lines.push(`🧱 جدار بيع كبير @ ${dom.bigAsk.price} (${dom.bigAsk.size} contracts)`);
  }
  if (dom.bigBid.size > 200) {
    lines.push(`💪 دعم شراء قوي @ ${dom.bigBid.price} (${dom.bigBid.size} contracts)`);
  }

  return lines.join('\n');
}
