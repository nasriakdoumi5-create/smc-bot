import { Block }       from './block.js';
import { Transaction } from './transaction.js';

export class Blockchain {
  constructor() {
    this.name        = 'SMCoin';
    this.symbol      = 'SMC';
    this.totalSupply = 21_000_000;   // مثل Bitcoin
    this.difficulty  = 3;            // عدد الأصفار المطلوبة في الـ Hash
    this.miningReward = 50;          // SMC لكل كتلة مُعدَّنة

    this.chain               = [this._genesisBlock()];
    this.pendingTransactions = [];
  }

  // ── الكتلة الأولى (Genesis) ─────────────────────
  _genesisBlock() {
    const block = new Block(0, '2026-01-01T00:00:00Z', [], '0000000000');
    block.hash = block.calculateHash();
    return block;
  }

  getLatestBlock() {
    return this.chain[this.chain.length - 1];
  }

  // ── إضافة معاملة إلى قائمة الانتظار ──────────────
  addTransaction(tx) {
    if (!tx.fromPublicKey || !tx.toPublicKey) {
      throw new Error('المعاملة تحتاج عنوان مرسل وعنوان مستقبل');
    }
    if (!tx.isValid()) {
      throw new Error('توقيع المعاملة غير صالح');
    }
    if (tx.amount <= 0) {
      throw new Error('قيمة المعاملة يجب أن تكون أكبر من صفر');
    }
    const balance = this.getBalance(tx.fromPublicKey);
    if (balance < tx.amount) {
      throw new Error(`رصيد غير كافٍ — المتوفر: ${balance} SMC`);
    }
    this.pendingTransactions.push(tx);
  }

  // ── تعدين كتلة جديدة ──────────────────────────────
  minePendingTransactions(minerPublicKey) {
    // مكافأة المُعدِّن
    const reward = new Transaction(null, minerPublicKey, this.miningReward);
    this.pendingTransactions.push(reward);

    const block = new Block(
      this.chain.length,
      Date.now(),
      this.pendingTransactions,
      this.getLatestBlock().hash
    );

    console.log(`\n⛏️  جاري تعدين الكتلة #${block.index} (صعوبة ${this.difficulty})...`);
    const t0 = Date.now();
    block.mine(this.difficulty);
    const elapsed = ((Date.now() - t0) / 1000).toFixed(2);

    console.log(`✅ تم التعدين في ${elapsed}s  |  Nonce: ${block.nonce}`);
    console.log(`   Hash: ${block.hash}`);

    this.chain.push(block);
    this.pendingTransactions = [];
    return block;
  }

  // ── الرصيد ──────────────────────────────────────
  getBalance(publicKey) {
    let balance = 0;
    for (const block of this.chain) {
      for (const tx of block.transactions) {
        if (tx.fromPublicKey === publicKey) balance -= tx.amount;
        if (tx.toPublicKey   === publicKey) balance += tx.amount;
      }
    }
    return balance;
  }

  // ── سجل المعاملات لمحفظة ─────────────────────────
  getTransactionsOf(publicKey) {
    const result = [];
    for (const block of this.chain) {
      for (const tx of block.transactions) {
        if (tx.fromPublicKey === publicKey || tx.toPublicKey === publicKey) {
          result.push({ block: block.index, ...tx });
        }
      }
    }
    return result;
  }

  // ── التحقق من صحة السلسلة ─────────────────────────
  isValid() {
    for (let i = 1; i < this.chain.length; i++) {
      const cur  = this.chain[i];
      const prev = this.chain[i - 1];

      if (!cur.hasValidTransactions())        return false;
      if (cur.hash !== cur.calculateHash())   return false;
      if (cur.previousHash !== prev.hash)     return false;
    }
    return true;
  }

  // ── معلومات عامة ─────────────────────────────────
  stats() {
    const totalMined = this.chain
      .flatMap(b => b.transactions)
      .filter(tx => tx.fromPublicKey === null)
      .reduce((s, tx) => s + tx.amount, 0);

    return {
      name:        this.name,
      symbol:      this.symbol,
      blocks:      this.chain.length,
      difficulty:  this.difficulty,
      miningReward: this.miningReward,
      totalMined,
      totalSupply: this.totalSupply,
      pending:     this.pendingTransactions.length,
      valid:       this.isValid(),
    };
  }
}
