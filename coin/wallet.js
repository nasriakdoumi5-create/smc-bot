import { generateKeyPairSync, createHash } from 'crypto';
import { Transaction } from './transaction.js';

export class Wallet {
  constructor() {
    const { privateKey, publicKey } = generateKeyPairSync('ec', {
      namedCurve: 'secp256k1',
      publicKeyEncoding:  { type: 'spki',  format: 'pem' },
      privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
    });

    this.privateKey = privateKey;
    this.publicKey  = publicKey;

    // عنوان مختصر (40 حرف hex) — مثل Bitcoin
    this.address = createHash('sha256')
      .update(publicKey)
      .digest('hex')
      .substring(0, 40);
  }

  // إنشاء معاملة موقعة
  createTransaction(toWalletOrPublicKey, amount) {
    const toKey = typeof toWalletOrPublicKey === 'string'
      ? toWalletOrPublicKey
      : toWalletOrPublicKey.publicKey;

    const tx = new Transaction(this.publicKey, toKey, amount);
    tx.sign(this.privateKey);
    return tx;
  }

  toString() {
    return `Wallet(${this.address})`;
  }
}
