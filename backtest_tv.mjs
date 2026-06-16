import { readFileSync } from 'fs';

const raw = readFileSync('C:/Users/nasri/.claude/projects/C--Users-nasri--claude/b6fd1f80-a8e7-48d6-9bfb-ff88677c10b1/tool-results/mcp-tradingview-data_get_ohlcv-1781648326107.txt', 'utf8');
const bars = JSON.parse(raw).bars;

function ema(data, period) {
  const k = 2 / (period + 1), out = new Array(data.length).fill(null);
  for (let i = period - 1; i < data.length; i++) {
    if (out[i-1] === null) {
      out[i] = data.slice(i - period + 1, i + 1).reduce((a,b) => a+b, 0) / period;
    } else {
      out[i] = data[i] * k + out[i-1] * (1 - k);
    }
  }
  return out;
}

function atr(bars, period) {
  const tr = bars.map((b, i) => {
    if (i === 0) return b.high - b.low;
    const prev = bars[i-1];
    return Math.max(b.high - b.low, Math.abs(b.high - prev.close), Math.abs(b.low - prev.close));
  });
  const out = new Array(bars.length).fill(null);
  for (let i = period - 1; i < bars.length; i++) {
    if (i === period - 1) out[i] = tr.slice(0, period).reduce((a,b)=>a+b,0) / period;
    else out[i] = (out[i-1] * (period-1) + tr[i]) / period;
  }
  return out;
}

function rsi(bars, period) {
  const out = new Array(bars.length).fill(50);
  let avgGain = 0, avgLoss = 0;
  for (let i = 1; i <= period; i++) {
    const d = bars[i].close - bars[i-1].close;
    if (d > 0) avgGain += d; else avgLoss += Math.abs(d);
  }
  avgGain /= period; avgLoss /= period;
  out[period] = avgLoss === 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss);
  for (let i = period + 1; i < bars.length; i++) {
    const d = bars[i].close - bars[i-1].close;
    const gain = Math.max(d, 0), loss = Math.max(-d, 0);
    avgGain = (avgGain * (period-1) + gain) / period;
    avgLoss = (avgLoss * (period-1) + loss) / period;
    out[i] = avgLoss === 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss);
  }
  return out;
}

const closes = bars.map(b => b.close);
const e21    = ema(closes, 21);
const e50    = ema(closes, 50);
const e200   = ema(closes, 200);
const atrArr = atr(bars, 14);
const rsiArr = rsi(bars, 14);

const results = [];
let lastBar = -5;
let lossStreak = 0;

for (let i = 220; i < bars.length - 12; i++) {
  if (i - lastBar < 4) continue;
  if (lossStreak >= 2) { lossStreak = 0; continue; }

  const b = bars[i], p1 = bars[i-1], p2 = bars[i-2], p3 = bars[i-3];
  const E21 = e21[i], E50 = e50[i], E200 = e200[i];
  const A = atrArr[i], R = rsiArr[i];

  if (!E21 || !E50 || !E200 || !A) continue;

  const avgATR = atrArr.slice(Math.max(0,i-20), i).filter(Boolean).reduce((a,b)=>a+b,0) / 20;
  if (A < avgATR * 0.8) continue;

  const htfBull = E50 > E200;
  const htfBear = E50 < E200;

  const emaDiff = Math.abs(E50 - E200) / E200 * 100;
  if (emaDiff < 0.1) continue;

  const bodySize = Math.abs(b.close - b.open);
  const range    = b.high - b.low || 0.01;
  const strongCandle = bodySize / range > 0.40;

  const touchedBull = p1.low <= E21 * 1.001 || p2.low <= e21[i-1] * 1.001 || p3.low <= e21[i-2] * 1.001;
  const bouncedBull = b.close > E21 && b.close > b.open;
  const longOk = htfBull && touchedBull && bouncedBull && R < 42 && strongCandle;

  const touchedBear = p1.high >= E21 * 0.999 || p2.high >= e21[i-1] * 0.999 || p3.high >= e21[i-2] * 0.999;
  const bouncedBear = b.close < E21 && b.close < b.open;
  const shortOk = htfBear && touchedBear && bouncedBear && R > 58 && strongCandle;

  if (!longOk && !shortOk) continue;

  const type = longOk ? 'LONG' : 'SHORT';
  lastBar = i;

  let sl;
  if (type === 'LONG') {
    sl = Math.min(p1.low, p2.low, p3.low) - A * 0.3;
  } else {
    sl = Math.max(p1.high, p2.high, p3.high) + A * 0.3;
  }

  const risk = Math.abs(b.close - sl);
  if (risk < A * 0.3 || risk > A * 3.5) continue;

  const tp = type === 'LONG' ? b.close + risk * 2.0 : b.close - risk * 2.0;

  let outcome = 'TIMEOUT';
  for (let j = i+1; j < Math.min(i+18, bars.length); j++) {
    const fb = bars[j];
    if (type === 'LONG') {
      if (fb.low  <= sl) { outcome = 'LOSS'; break; }
      if (fb.high >= tp) { outcome = 'WIN';  break; }
    } else {
      if (fb.high >= sl) { outcome = 'LOSS'; break; }
      if (fb.low  <= tp) { outcome = 'WIN';  break; }
    }
  }

  if (outcome === 'WIN') lossStreak = 0;
  else if (outcome === 'LOSS') lossStreak++;
  else lossStreak = 0;

  const d = new Date(b.time * 1000).toLocaleDateString('es-ES', {
    timeZone: 'Europe/Madrid', day: '2-digit', month: '2-digit', year: '2-digit'
  });

  results.push({ d, type, entry: +b.close.toFixed(0), sl: +sl.toFixed(0), tp: +tp.toFixed(0),
    risk: +risk.toFixed(0), rsi: +R.toFixed(0), outcome });
}

const wins    = results.filter(r => r.outcome === 'WIN').length;
const losses  = results.filter(r => r.outcome === 'LOSS').length;
const timeout = results.filter(r => r.outcome === 'TIMEOUT').length;
const total   = wins + losses;
const wr      = total > 0 ? (wins/total*100).toFixed(1) : 0;
const pnl     = (wins * 2 - losses * 1).toFixed(0);

console.log('\n======= MNQ BACKTEST — 500 شمعة 1H من TradingView =======');
results.forEach((r,i) => {
  const icon = r.outcome==='WIN'?'WIN':r.outcome==='LOSS'?'LOSS':'TIME';
  console.log(`${String(i+1).padStart(3)}. [${icon}] ${r.d} ${r.type} @ ${r.entry} SL:${r.sl} TP:${r.tp} RSI:${r.rsi}`);
});

console.log('\n--- ملخص ---');
console.log(`الإجمالي: ${results.length} | WIN: ${wins} | LOSS: ${losses} | TIMEOUT: ${timeout}`);
console.log(`نسبة النجاح: ${wr}%`);
console.log(`P&L (2:1 RR): ${pnl}R`);
console.log(`الهدف 65%? ${parseFloat(wr) >= 65 ? 'نعم!' : 'لا (' + wr + '%)'}`);

const longRes  = results.filter(r => r.type === 'LONG');
const shortRes = results.filter(r => r.type === 'SHORT');
const longWR   = longRes.filter(r=>r.outcome==='WIN').length / (longRes.filter(r=>r.outcome!=='TIMEOUT').length||1) * 100;
const shortWR  = shortRes.filter(r=>r.outcome==='WIN').length / (shortRes.filter(r=>r.outcome!=='TIMEOUT').length||1) * 100;
console.log(`LONG: ${longRes.length} صفقة | ${longWR.toFixed(1)}% نجاح`);
console.log(`SHORT: ${shortRes.length} صفقة | ${shortWR.toFixed(1)}% نجاح`);
