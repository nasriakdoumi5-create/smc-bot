/**
 *  SMCoin — عملة رقمية مبنية على Blockchain
 *  تشغيل: node coin/demo.js
 */

import { Blockchain } from './blockchain.js';
import { Wallet }     from './wallet.js';

const line = () => console.log('─'.repeat(60));
const sep  = () => console.log('═'.repeat(60));

sep();
console.log('       💰  SMCoin Blockchain Demo');
sep();

// ══ إنشاء المحافظ ══════════════════════════════════════
console.log('\n📥 إنشاء المحافظ...\n');

const alice  = new Wallet();
const bob    = new Wallet();
const miner  = new Wallet();

console.log(`👤 Alice  — ${alice.address}`);
console.log(`👤 Bob    — ${bob.address}`);
console.log(`⛏️  Miner  — ${miner.address}`);

// ══ إنشاء البلوكشين ════════════════════════════════════
const smcoin = new Blockchain();

// ══ الجولة 1: Alice تعدّن كتلتين للحصول على عملات ══════
line();
console.log('\n🔄 الجولة 1 — تعدين كتل لـ Alice');
smcoin.minePendingTransactions(alice.publicKey);  // +50 SMC
smcoin.minePendingTransactions(alice.publicKey);  // +50 SMC

console.log(`\n💰 رصيد Alice: ${smcoin.getBalance(alice.publicKey)} SMC`);
console.log(`💰 رصيد Bob:   ${smcoin.getBalance(bob.publicKey)} SMC`);

// ══ الجولة 2: Alice ترسل لـ Bob ════════════════════════
line();
console.log('\n🔄 الجولة 2 — Alice ترسل 30 SMC إلى Bob');

const tx1 = alice.createTransaction(bob, 30);
smcoin.addTransaction(tx1);

const tx2 = alice.createTransaction(bob, 10);
smcoin.addTransaction(tx2);

console.log(`📤 معاملة 1 — ${tx1.amount} SMC  (تنتظر التأكيد)`);
console.log(`📤 معاملة 2 — ${tx2.amount} SMC  (تنتظر التأكيد)`);
console.log(`\n⏳ معاملات في الانتظار: ${smcoin.pendingTransactions.length}`);

// Miner يعدّن الكتلة ويحصل على مكافأة
smcoin.minePendingTransactions(miner.publicKey);

line();
console.log('\n💰 الأرصدة بعد التعدين:');
console.log(`   Alice  → ${smcoin.getBalance(alice.publicKey)} SMC`);
console.log(`   Bob    → ${smcoin.getBalance(bob.publicKey)} SMC`);
console.log(`   Miner  → ${smcoin.getBalance(miner.publicKey)} SMC`);

// ══ الجولة 3: Bob يرسل لـ Miner ════════════════════════
line();
console.log('\n🔄 الجولة 3 — Bob يرسل 15 SMC إلى Miner');

const tx3 = bob.createTransaction(miner, 15);
smcoin.addTransaction(tx3);
smcoin.minePendingTransactions(alice.publicKey);  // Alice تعدّن هذه المرة

line();
console.log('\n💰 الأرصدة النهائية:');
console.log(`   Alice  → ${smcoin.getBalance(alice.publicKey)} SMC`);
console.log(`   Bob    → ${smcoin.getBalance(bob.publicKey)} SMC`);
console.log(`   Miner  → ${smcoin.getBalance(miner.publicKey)} SMC`);

// ══ إحصائيات البلوكشين ═════════════════════════════════
sep();
console.log('\n📊 إحصائيات SMCoin:\n');
const stats = smcoin.stats();
for (const [k, v] of Object.entries(stats)) {
  const labels = {
    name: 'الاسم', symbol: 'الرمز', blocks: 'عدد الكتل',
    difficulty: 'الصعوبة', miningReward: 'مكافأة التعدين (SMC)',
    totalMined: 'إجمالي المُعدَّن (SMC)', totalSupply: 'الحد الأقصى للإصدار',
    pending: 'معاملات منتظرة', valid: 'السلسلة صالحة',
  };
  console.log(`   ${(labels[k] || k).padEnd(28)} ${v}`);
}

// ══ سجل معاملات Bob ════════════════════════════════════
sep();
console.log('\n📜 سجل معاملات Bob:\n');
const txHistory = smcoin.getTransactionsOf(bob.publicKey);
for (const tx of txHistory) {
  const dir = tx.toPublicKey === bob.publicKey ? '📥 استقبل' : '📤 أرسل  ';
  console.log(`   ${dir}  ${tx.amount} SMC  (كتلة #${tx.block})`);
}

// ══ التحقق من صحة السلسلة ══════════════════════════════
sep();
console.log(`\n🔐 التحقق من صحة البلوكشين: ${smcoin.isValid() ? '✅ صالح' : '❌ مزوّر!'}\n`);

// ══ محاولة التلاعب بالبيانات ══════════════════════════
console.log('⚠️  محاولة التلاعب بالبيانات...');
smcoin.chain[1].transactions[0].amount = 9999;
console.log(`🔐 البلوكشين بعد التلاعب: ${smcoin.isValid() ? '✅ صالح' : '❌ مزوّر — تم الكشف!'}`);

sep();
console.log('  ✅  انتهى العرض التوضيحي — SMCoin يعمل بنجاح!');
sep();
