/**
 * اختبار مباشر — بيانات Tradovate حقيقية
 * node test_live.js
 */

import { tradovate }          from './tradovate.js';
import { get5mBars, get1hBars } from './data_tradovate.js';
import { analyzeSimple }        from './strategy_simple.js';

const SYMBOLS = ['MNQ', 'MES'];

async function test() {
  console.log('═'.repeat(50));
  console.log('  🧪 اختبار مباشر — Tradovate Live Data');
  console.log('═'.repeat(50));

  // 1. اختبار المصادقة
  console.log('\n[1] تسجيل الدخول...');
  try {
    await tradovate.ensureToken();
    console.log('  ✅ تم تسجيل الدخول');
  } catch (e) {
    console.error('  ❌ فشل:', e.message);
    process.exit(1);
  }

  // 2. جلب الحساب
  console.log('\n[2] الحساب...');
  try {
    const acc = await tradovate.getAccount();
    console.log(`  ✅ ${acc.name} — $${acc.cashBalance || '?'}`);
  } catch (e) {
    console.error('  ❌', e.message);
  }

  // 3. جلب البيانات وتحليلها
  for (const sym of SYMBOLS) {
    console.log(`\n[3] ${sym} — جلب الشمعات...`);
    try {
      const [bars5m, bars1h] = await Promise.all([
        get5mBars(sym),
        get1hBars(sym),
      ]);

      console.log(`  ✅ 5M: ${bars5m.length} شمعة | آخر سعر: ${bars5m.at(-1)?.close}`);
      console.log(`  ✅ 1H: ${bars1h.length} شمعة`);

      const r = analyzeSimple(bars5m, bars5m, bars1h);

      if (r.error) {
        console.log(`  ⚠️ تحليل: ${r.error}`);
      } else if (!r.signal) {
        console.log(`  📊 لا إشارة حالياً (السوق لا يستوفي الشروط)`);
        if (r.regime) console.log(`  📈 الاتجاه: ${r.regime.trend} | ADX: ${r.regime.adx?.toFixed(1)}`);
      } else {
        const s = r.signal;
        console.log(`  🚨 إشارة ${s.type}! السعر: ${s.price} | SL: ${s.sl} | TP: ${s.tp1}`);
        console.log(`  ⭐ الجودة: ${s.score}/4`);
      }
    } catch (e) {
      console.error(`  ❌ ${sym}:`, e.message);
    }
  }

  console.log('\n' + '═'.repeat(50));
  console.log('  ✅ انتهى الاختبار');
  console.log('═'.repeat(50));
  process.exit(0);
}

test();
