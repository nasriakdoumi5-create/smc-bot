/**
 * Order Flow Engine — مجاني 100% من Yahoo Finance
 *
 * يحسب من بيانات OHLCV العادية:
 * - Delta (buy vol − sell vol) لكل شمعة
 * - Cumulative Delta
 * - Stacked Imbalance (3+ شموع متتالية بضغط واحد)
 * - Delta Divergence (سعر يتعارض مع الضغط الحقيقي)
 *
 * الصيغة:
 *   buyVol  = volume × (close − low)  / (high − low)
 *   sellVol = volume × (high − close) / (high − low)
 */

const STACKED_MIN     = 3;     // عدد شموع متتالية لـ Stacked
const IMBALANCE_RATIO = 2.5;   // نسبة اعتبار الـ imbalance
const LOOKBACK        = 20;    // عدد الشموع للتحليل

export function analyzeOrderFlow(bars5m) {
  if (!bars5m || bars5m.length < LOOKBACK + 2) return null;

  const recent = bars5m.slice(-LOOKBACK);

  // ── حساب Delta لكل شمعة ──────────────────
  const barDeltas = recent.map(b => {
    const range = b.high - b.low;
    if (range < 0.001) return { ...b, buy: 0, sell: 0, delta: 0 };
    const buy  = b.volume * (b.close - b.low)  / range;
    const sell = b.volume * (b.high - b.close) / range;
    return { ...b, buy: Math.round(buy), sell: Math.round(sell), delta: Math.round(buy - sell) };
  });

  // ── Cumulative Delta ──────────────────────
  let cum = 0;
  const cumDeltas = barDeltas.map(b => (cum += b.delta, cum));

  const last     = barDeltas[barDeltas.length - 1];
  const prev     = barDeltas[barDeltas.length - 2];
  const lastDelta = last.delta;
  const cumDelta  = cum;

  // ── Stacked Imbalance ─────────────────────
  // 3+ شموع متتالية فيها ضغط شراء أو بيع واضح
  let buyStack = 0, sellStack = 0;
  let maxBuyStack = 0, maxSellStack = 0;

  for (const b of barDeltas) {
    if (b.sell > 0 && b.buy / b.sell >= IMBALANCE_RATIO) {
      buyStack++;
      sellStack = 0;
    } else if (b.buy > 0 && b.sell / b.buy >= IMBALANCE_RATIO) {
      sellStack++;
      buyStack = 0;
    } else {
      buyStack  = 0;
      sellStack = 0;
    }
    maxBuyStack  = Math.max(maxBuyStack,  buyStack);
    maxSellStack = Math.max(maxSellStack, sellStack);
  }

  const stackedBuy  = maxBuyStack  >= STACKED_MIN;
  const stackedSell = maxSellStack >= STACKED_MIN;

  // ── Delta Divergence ─────────────────────
  // سعر صاعد (higher close) لكن delta هابط = ضعف مشترين
  const priceUp   = last.close > prev.close;
  const priceDown = last.close < prev.close;
  const bearDivergence = priceUp   && lastDelta < 0;
  const bullDivergence = priceDown && lastDelta > 0;

  // ── High Volume Node (أكثر شمعة حجماً) ──
  const hvnBar = barDeltas.reduce((max, b) => b.volume > max.volume ? b : max, barDeltas[0]);

  // ── اتجاه الـ Delta الأخيرة 5 شموع ──────
  const last5 = barDeltas.slice(-5);
  const avgDelta5 = last5.reduce((s, b) => s + b.delta, 0) / 5;

  return {
    // شروط للاستخدام في التقييم
    positiveDelta:  lastDelta > 0,
    negativeDelta:  lastDelta < 0,
    stackedBuy,
    stackedSell,
    bullDivergence,
    bearDivergence,

    // أرقام تفصيلية
    lastDelta,
    cumDelta,
    avgDelta5:    Math.round(avgDelta5),
    lastBuyVol:   last.buy,
    lastSellVol:  last.sell,
    maxBuyStack,
    maxSellStack,
    hvnPrice:     hvnBar?.close,
    hvnVolume:    hvnBar?.volume,
    barCount:     barDeltas.length,
  };
}

// ══ نص Telegram ══════════════════════════════
export function orderFlowText(of) {
  if (!of) return '';
  const lines = [];

  const dSign = of.lastDelta >= 0 ? '🟢' : '🔴';
  const avgSign = of.avgDelta5 >= 0 ? '+' : '';
  lines.push(`${dSign} Delta: <b>${of.lastDelta >= 0 ? '+' : ''}${of.lastDelta}</b>  |  Cum.Δ: ${of.cumDelta >= 0 ? '+' : ''}${of.cumDelta}  |  Avg5: ${avgSign}${of.avgDelta5}`);
  lines.push(`   Buy Vol: ${of.lastBuyVol}  /  Sell Vol: ${of.lastSellVol}`);

  if (of.stackedSell)
    lines.push(`🔴 Stacked Sell — ${of.maxSellStack} شموع ضغط بيع متتالية`);

  if (of.stackedBuy)
    lines.push(`🟢 Stacked Buy  — ${of.maxBuyStack} شموع ضغط شراء متتالية`);

  if (of.bearDivergence)
    lines.push(`⚠️ <b>Divergence هابط</b> — سعر صاعد لكن البائعون يسيطرون`);

  if (of.bullDivergence)
    lines.push(`⚠️ <b>Divergence صاعد</b> — سعر هابط لكن المشترون يسيطرون`);

  return lines.join('\n');
}
