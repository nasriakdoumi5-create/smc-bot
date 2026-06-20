import { createHash, createSign, createVerify } from 'crypto';

export class Transaction {
  constructor(fromPublicKey, toPublicKey, amount) {
    this.fromPublicKey = fromPublicKey;  // null for mining rewards
    this.toPublicKey   = toPublicKey;
    this.amount        = amount;
    this.timestamp     = Date.now();
    this.signature     = null;
    this.hash          = this._hash();
  }

  _hash() {
    return createHash('sha256')
      .update((this.fromPublicKey || '') + this.toPublicKey + this.amount + this.timestamp)
      .digest('hex');
  }

  sign(privateKey) {
    const signer = createSign('SHA256');
    signer.update(this.hash);
    signer.end();
    this.signature = signer.sign(privateKey, 'hex');
  }

  isValid() {
    // مكافأة التعدين — لا تحتاج توقيعاً
    if (this.fromPublicKey === null) return true;

    if (!this.signature || this.signature.length === 0) {
      throw new Error('لا يوجد توقيع على هذه المعاملة');
    }

    const verifier = createVerify('SHA256');
    verifier.update(this.hash);
    verifier.end();
    return verifier.verify(this.fromPublicKey, this.signature, 'hex');
  }
}
