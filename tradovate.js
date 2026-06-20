/**
 * Tradovate API Client
 * ══════════════════════════════════════════════
 * يدعم: تسجيل الدخول، جلب الحساب، تنفيذ الصفقات
 * Demo: demo.tradovateapi.com
 * Live: live.tradovateapi.com
 */

const URLS = {
  demo: 'https://demo.tradovateapi.com/v1',
  live: 'https://live.tradovateapi.com/v1',
};

class TradovateClient {
  constructor() {
    this.env      = process.env.TRADOVATE_ENV || 'demo';
    this.base     = URLS[this.env];
    this.token    = null;
    this.expiry   = 0;
    this.accountId   = null;
    this.accountName = null;
  }

  // ── طلب HTTP ──────────────────────────────────
  async _req(method, path, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
    const res = await fetch(`${this.base}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    const text = await res.text();
    try { return JSON.parse(text); }
    catch { return { error: text }; }
  }

  get  = (path)       => this._req('GET',  path);
  post = (path, body) => this._req('POST', path, body);

  // ── تسجيل الدخول ──────────────────────────────
  async login() {
    const username  = process.env.TRADOVATE_USERNAME;
    const password  = process.env.TRADOVATE_PASSWORD;
    const appId     = process.env.TRADOVATE_APP_ID     || 'Sample App';
    const appSecret = process.env.TRADOVATE_APP_SECRET || '';
    const cid       = parseInt(process.env.TRADOVATE_CID || '0');

    if (!username || !password) throw new Error('TRADOVATE_USERNAME و TRADOVATE_PASSWORD مطلوبان');

    console.log(`[Tradovate] تسجيل دخول (${this.env})...`);
    const data = await this.post('/auth/accesstokenrequest', {
      name: username, password, appId,
      appVersion: '1.0', cid, sec: appSecret,
    });

    if (!data.accessToken) throw new Error('فشل تسجيل الدخول: ' + JSON.stringify(data));

    this.token  = data.accessToken;
    this.expiry = data.expirationTime
      ? new Date(data.expirationTime).getTime()
      : Date.now() + 60 * 60 * 1000;

    console.log(`[Tradovate] ✅ تم تسجيل الدخول — Token صالح حتى ${new Date(this.expiry).toLocaleTimeString()}`);
    return data;
  }

  // ── تجديد Token تلقائياً ──────────────────────
  async ensureToken() {
    if (!this.token || Date.now() > this.expiry - 5 * 60 * 1000) {
      await this.login();
    }
  }

  // ── جلب الحساب ────────────────────────────────
  async getAccount() {
    await this.ensureToken();
    const accounts = await this.get('/account/list');
    if (!Array.isArray(accounts) || !accounts.length)
      throw new Error('لا توجد حسابات: ' + JSON.stringify(accounts));
    const acc = accounts[0];
    this.accountId   = acc.id;
    this.accountName = acc.name;
    console.log(`[Tradovate] الحساب: ${acc.name} (ID: ${acc.id}) — ${this.env.toUpperCase()}`);
    return acc;
  }

  // ── البحث عن العقد (MNQ front month) ─────────
  async findContract(symbol = 'MNQ') {
    await this.ensureToken();
    const r = await this.get(`/contract/find?name=${symbol}`);
    if (r.errorText || r.error) {
      // جرب البحث المتقدم
      const search = await this.post('/contractMaturity/suggestContractMaturities', {
        text: symbol, nEntities: 3
      });
      if (Array.isArray(search) && search.length) return search[0];
      throw new Error(`لم يُعثر على عقد ${symbol}: ` + JSON.stringify(r));
    }
    console.log(`[Tradovate] العقد: ${r.name} (ID: ${r.id})`);
    return r;
  }

  // ══ بيانات السوق التاريخية (MD API) ══════════
  async getChartData(contractSymbol, minuteSize, count = 500) {
    await this.ensureToken();
    const res = await fetch('https://md.tradovateapi.com/v1/chart/getchartdata', {
      method: 'POST',
      headers: {
        'Content-Type':  'application/json',
        'Authorization': `Bearer ${this.token}`,
      },
      body: JSON.stringify({
        symbol: contractSymbol,
        chartDescription: {
          underlyingType:   'Bars',
          elementSize:      minuteSize,
          elementSizeUnit:  'Minute',
          withHistogram:    false,
        },
        timeRange: { asMuchAsElements: count },
      }),
    });
    const text = await res.text();
    let data;
    try { data = JSON.parse(text); }
    catch { throw new Error(`MD parse: ${text.slice(0, 200)}`); }
    if (data.errorText || data.error)
      throw new Error(`MD: ${data.errorText || JSON.stringify(data)}`);
    // Tradovate يُعيد {bars:[]} أو مصفوفة مباشرة
    const bars = Array.isArray(data) ? data : (data.bars || data.d || []);
    console.log(`[MD] ${contractSymbol} ${minuteSize}M → ${bars.length} شمعة`);
    return bars;
  }

  // ── رصيد الحساب ───────────────────────────────
  async getBalance() {
    await this.ensureToken();
    const r = await this.get(`/cashBalance/getcashbalancesnapshot?accountId=${this.accountId}`);
    return r;
  }

  // ── المراكز المفتوحة ──────────────────────────
  async getPositions() {
    await this.ensureToken();
    return this.get('/position/list');
  }

  // ── الأوامر المعلقة ───────────────────────────
  async getOrders() {
    await this.ensureToken();
    return this.get('/order/list');
  }

  // ══ تنفيذ صفقة مع SL و TP ════════════════════
  async placeBracketOrder({ action, contractId, contractName, qty, slPrice, tp1Price, tp2Price }) {
    await this.ensureToken();
    if (!this.accountId) await this.getAccount();

    const side = action === 'LONG' ? 'Buy' : 'Sell';
    const exitSide = action === 'LONG' ? 'Sell' : 'Buy';
    const qty2 = Math.max(1, Math.floor(qty / 2)); // نصف الكمية لـ TP2

    console.log(`[Tradovate] 📤 أمر ${side} × ${qty} ${contractName} | SL:${slPrice} TP1:${tp1Price}`);

    // دخول بسعر السوق + bracket (SL + TP1)
    const order = await this.post('/order/placeoso', {
      entryOrder: {
        accountSpec: this.accountName,
        accountId:   this.accountId,
        action:      side,
        symbol:      contractName,
        orderQty:    qty,
        orderType:   'Market',
        isAutomated: true,
      },
      brackets: [{
        qty:        qty,
        stopPrice:  slPrice,   // SL — وقف الخسارة
        limitPrice: tp1Price,  // TP1 — هدف الربح
      }],
    });

    if (order.failureReason || order.error) {
      throw new Error('فشل الأمر: ' + JSON.stringify(order));
    }

    console.log(`[Tradovate] ✅ تم تنفيذ الأمر — ID: ${order.orderId || JSON.stringify(order)}`);
    return order;
  }

  // ══ إغلاق كل المراكز ════════════════════════
  async closeAll(contractName) {
    await this.ensureToken();
    const positions = await this.getPositions();
    for (const pos of positions) {
      if (pos.netPos === 0) continue;
      const action = pos.netPos > 0 ? 'Sell' : 'Buy';
      await this.post('/order/placeorder', {
        accountId:   this.accountId,
        action,
        symbol:      contractName || pos.contractId,
        orderQty:    Math.abs(pos.netPos),
        orderType:   'Market',
        isAutomated: true,
      });
      console.log(`[Tradovate] 🔒 أُغلق مركز ${pos.contractId}`);
    }
  }
}

// Singleton
export const tradovate = new TradovateClient();

// ══ دالة التنفيذ المستخدمة في bot.js ══════════
export async function executeSignal(signal) {
  const qty = parseInt(process.env.TRADE_QTY || '1');

  // جلب العقد
  const contract = await tradovate.findContract(process.env.SYMBOL || 'MNQ');

  // تنفيذ
  return tradovate.placeBracketOrder({
    action:       signal.type,          // 'LONG' أو 'SHORT'
    contractId:   contract.id,
    contractName: contract.name,
    qty,
    slPrice:  signal.sl,
    tp1Price: signal.tp1,
    tp2Price: signal.tp2,
  });
}
