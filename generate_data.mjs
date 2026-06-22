/**
 * مولد بيانات NQ/MNQ محلي — 730 يوم، إطار 1H
 * يحاكي تذبذب NQ الحقيقي (تريند + تصحيح + أخبار)
 */

function generateNQBars(days = 730, startPrice = 15000) {
  const bars = [];
  const hoursPerDay = 16; // 6am - 10pm ET
  const totalBars = days * hoursPerDay;

  let price = startPrice;
  let trend = 1; // 1 = صاعد، -1 = هابط
  let trendDays = 0;
  const atrBase = 80; // ATR متوسط NQ بالنقاط

  const now = Date.now();
  const startTime = now - (days * 24 * 60 * 60 * 1000);

  for (let i = 0; i < totalBars; i++) {
    // تغيير الاتجاه كل 20-60 يوم
    trendDays++;
    if (trendDays > 20 + Math.floor(Math.random() * 40)) {
      trend *= -1;
      trendDays = 0;
    }

    // حركة السعر
    const trendBias = trend * (atrBase * 0.15);
    const noise = (Math.random() - 0.5) * atrBase * 1.5;
    const move = trendBias + noise;

    const open = price;
    const close = price + move;
    const bodySize = Math.abs(close - open);
    const wickSize = bodySize * (0.3 + Math.random() * 0.7);

    const high = Math.max(open, close) + wickSize * Math.random();
    const low = Math.min(open, close) - wickSize * Math.random();
    const volume = Math.floor(50000 + Math.random() * 150000);

    // توقيت الشمعة
    const hourOffset = i * 60 * 60 * 1000;
    const time = Math.floor((startTime + hourOffset) / 1000);

    bars.push({ time, open, high, low, close, volume });
    price = close;

    // حماية من قيم سالبة
    if (price < 5000) price = 5000;
  }

  return bars;
}

// تصدير JSON
const bars = generateNQBars(730, 15000);
console.log(JSON.stringify(bars));
