/**
 *  SMCoin Exchange — منصة تداول كاملة
 *  تشغيل: node coin/exchange-server.js
 *  ثم افتح: http://localhost:5000
 */

import { createServer } from 'http';
import { createHash, randomBytes } from 'crypto';

const PORT = process.env.EXCHANGE_PORT || 5000;

// ══════════════════════════════════════════════════════
//  ENGINE
// ══════════════════════════════════════════════════════

const users    = new Map();   // username → user
const sessions = new Map();   // token → username
const allOrders = new Map();  // id → order
const bids     = [];          // buy orders (sorted desc price)
const asks     = [];          // sell orders (sorted asc price)
const recentTrades = [];      // last 200 trades
const priceCandles = [];      // 1-min OHLCV

let orderSeq = 1;
let lastPrice = 1.0;
let open24h   = 1.0;

const sha256 = s => createHash('sha256').update(s).digest('hex');
const newTok = () => randomBytes(24).toString('hex');
const oid    = () => 'O' + String(orderSeq++).padStart(7, '0');

function parseCookies(req) {
  const out = {};
  (req.headers.cookie || '').split(';').forEach(c => {
    const [k, ...vs] = c.trim().split('=');
    if (k) out[k] = vs.join('=');
  });
  return out;
}
function getUser(req) {
  const auth = (req.headers.authorization || '').replace('Bearer ', '').trim()
            || parseCookies(req)['smcex'] || '';
  const uname = sessions.get(auth);
  return uname ? users.get(uname) : null;
}

// ── Order Book helpers ─────────────────────────────────
function insertBid(o) {
  const i = bids.findIndex(x => x.price < o.price);
  i < 0 ? bids.push(o) : bids.splice(i, 0, o);
}
function insertAsk(o) {
  const i = asks.findIndex(x => x.price > o.price);
  i < 0 ? asks.push(o) : asks.splice(i, 0, o);
}
function removeFromBook(o) {
  if (o.side === 'buy')  { const i = bids.indexOf(o); if (i >= 0) bids.splice(i, 1); }
  else                   { const i = asks.indexOf(o); if (i >= 0) asks.splice(i, 1); }
}

// ── Candle update ──────────────────────────────────────
function updateCandle(price, vol) {
  const t = Math.floor(Date.now() / 60000) * 60000;
  const last = priceCandles[priceCandles.length - 1];
  if (last && last.t === t) {
    last.h = Math.max(last.h, price);
    last.l = Math.min(last.l, price);
    last.c = price; last.v += vol;
  } else {
    priceCandles.push({ t, o: price, h: price, l: price, c: price, v: vol });
    if (priceCandles.length > 300) priceCandles.shift();
  }
}

// ── Matching Engine ────────────────────────────────────
function matchOrder(newOrd) {
  const opposites = newOrd.side === 'buy' ? asks : bids;
  while (newOrd.remaining > 1e-8 && opposites.length) {
    const best = opposites[0];
    const canMatch = newOrd.side === 'buy' ? best.price <= newOrd.price : best.price >= newOrd.price;
    if (!canMatch) break;

    const qty   = Math.min(newOrd.remaining, best.remaining);
    const price = best.price;
    const buyer  = users.get(newOrd.side === 'buy' ? newOrd.username : best.username);
    const seller = users.get(newOrd.side === 'sell' ? newOrd.username : best.username);

    buyer.smc   = +(buyer.smc  + qty).toFixed(8);
    buyer.usd   = +(buyer.usd  - qty * price).toFixed(6);
    seller.smc  = +(seller.smc - qty).toFixed(8);
    seller.usd  = +(seller.usd + qty * price).toFixed(6);

    newOrd.remaining = +(newOrd.remaining - qty).toFixed(8);
    newOrd.filled    = +(newOrd.filled    + qty).toFixed(8);
    best.remaining   = +(best.remaining   - qty).toFixed(8);
    best.filled      = +(best.filled      + qty).toFixed(8);

    lastPrice = price;
    updateCandle(price, qty);

    recentTrades.unshift({
      id: recentTrades.length + 1, price, amount: qty, total: +(qty * price).toFixed(4),
      buyer: buyer.username, seller: seller.username, t: Date.now(),
      side: newOrd.side,
    });
    if (recentTrades.length > 200) recentTrades.pop();

    if (best.remaining <= 1e-8) { best.status = 'filled'; opposites.shift(); }
  }
  if (newOrd.remaining <= 1e-8) newOrd.status = 'filled';
}

// ── Place / Cancel ─────────────────────────────────────
function placeOrder(user, side, price, amount) {
  price  = +parseFloat(price).toFixed(4);
  amount = +parseFloat(amount).toFixed(4);
  if (!price  || price  <= 0) throw new Error('سعر غير صالح');
  if (!amount || amount <= 0) throw new Error('كمية غير صالحة');

  if (side === 'buy') {
    const need = +(price * amount).toFixed(6);
    if (user.usd < need - 1e-4) throw new Error('رصيد USD غير كافٍ (' + user.usd.toFixed(2) + '$)');
    user.usd = +(user.usd - need).toFixed(6);
  } else {
    if (user.smc < amount - 1e-4) throw new Error('رصيد SMC غير كافٍ (' + user.smc.toFixed(4) + ')');
    user.smc = +(user.smc - amount).toFixed(8);
  }

  const order = { id: oid(), username: user.username, side, price, amount,
                  remaining: amount, filled: 0, status: 'open', t: Date.now() };
  allOrders.set(order.id, order);
  matchOrder(order);
  if (order.status === 'open') side === 'buy' ? insertBid(order) : insertAsk(order);
  return order;
}

function cancelOrder(orderId, username) {
  const o = allOrders.get(orderId);
  if (!o) throw new Error('الأمر غير موجود');
  if (o.username !== username) throw new Error('ليس أمرك');
  if (o.status !== 'open') throw new Error('الأمر منتهٍ بالفعل');
  const user = users.get(username);
  if (o.side === 'buy') user.usd = +(user.usd + o.remaining * o.price).toFixed(6);
  else user.smc = +(user.smc + o.remaining).toFixed(8);
  o.status = 'cancelled';
  removeFromBook(o);
  return o;
}

// ── Seed ──────────────────────────────────────────────
(function seed() {
  users.set('_mm_', { username: '_mm_', passHash: '', smc: 1e6, usd: 1e6, t: Date.now() });
  const mm = users.get('_mm_');

  // Fake candle history (60 mins)
  let p = 1.0;
  for (let i = 60; i >= 0; i--) {
    p += (Math.random() - 0.47) * 0.018;
    p = Math.max(0.3, Math.min(4, p));
    priceCandles.push({
      t: Math.floor(Date.now() / 60000) * 60000 - i * 60000,
      o: +(p - 0.006).toFixed(4), h: +(p + 0.012).toFixed(4),
      l: +(p - 0.012).toFixed(4), c: +p.toFixed(4),
      v: +(50 + Math.random() * 150).toFixed(2),
    });
  }
  lastPrice = p; open24h = priceCandles[0].c;

  // Seed order book
  for (let i = 1; i <= 10; i++) {
    placeOrder(mm, 'buy',  +(p - i * 0.005).toFixed(4), +(10 + Math.random() * 90).toFixed(2));
    placeOrder(mm, 'sell', +(p + i * 0.005).toFixed(4), +(10 + Math.random() * 90).toFixed(2));
  }

  // Seed recent trades
  for (let i = 0; i < 20; i++) {
    const tp = +(p + (Math.random() - 0.5) * 0.05).toFixed(4);
    const ta = +(5 + Math.random() * 50).toFixed(2);
    recentTrades.push({
      id: i + 1, price: tp, amount: ta, total: +(tp * ta).toFixed(4),
      buyer: 'market', seller: 'market', t: Date.now() - (20 - i) * 30000,
      side: Math.random() > 0.5 ? 'buy' : 'sell',
    });
  }
})();

// ══════════════════════════════════════════════════════
//  HTML
// ══════════════════════════════════════════════════════

const HTML = `<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SMCoin Exchange</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0b0e11;--card:#1e2329;--border:#2b3139;
  --green:#0ecb81;--red:#f6465d;--text:#eaecef;
  --muted:#848e9c;--accent:#f0b90b;--accent2:#c09809;
}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',sans-serif;height:100vh;display:flex;flex-direction:column;font-size:13px;overflow:hidden}
/* Header */
header{background:var(--card);border-bottom:1px solid var(--border);padding:0 16px;height:52px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.logo{color:var(--accent);font-weight:800;font-size:1.15rem;letter-spacing:1px}
.ticker{display:flex;gap:20px;align-items:center;flex-wrap:nowrap}
.tick-price{font-size:1.25rem;font-weight:700}
.tick-info{display:flex;flex-direction:column;line-height:1.3}
.tick-label{color:var(--muted);font-size:.68rem}
.tick-value{font-size:.82rem;font-weight:500}
.user-area{display:flex;align-items:center;gap:12px}
.balances{text-align:right;line-height:1.5}
.bal-line{font-size:.75rem;color:var(--muted)}
.bal-val{color:var(--text);font-weight:600}
.btn{padding:5px 14px;border-radius:4px;border:none;cursor:pointer;font-size:.78rem;font-weight:600;transition:.15s}
.btn-outline{background:transparent;border:1px solid var(--border);color:var(--muted)}
.btn-outline:hover{border-color:var(--text);color:var(--text)}

/* Layout */
.layout{display:grid;grid-template-columns:220px 1fr 260px;flex:1;gap:1px;background:var(--border);overflow:hidden;min-height:0}
.panel{background:var(--card);display:flex;flex-direction:column;overflow:hidden}
.ptitle{padding:7px 12px;font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid var(--border);flex-shrink:0;font-weight:600}

/* Order Book */
.ob-head{display:grid;grid-template-columns:repeat(3,1fr);padding:4px 10px;font-size:.68rem;color:var(--muted);flex-shrink:0}
.ob-row{display:grid;grid-template-columns:repeat(3,1fr);padding:2.5px 10px;position:relative;cursor:default;font-size:.78rem}
.ob-row:hover{background:rgba(255,255,255,.04)}
.ob-bar{position:absolute;top:0;bottom:0;right:0;opacity:.12;pointer-events:none}
.ask-color{color:var(--red)} .ask-bar{background:var(--red)}
.bid-color{color:var(--green)} .bid-bar{background:var(--green)}
.ob-mid{padding:5px 10px;background:#252a31;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;font-size:.82rem;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}
.mid-price{font-size:1rem;font-weight:700;cursor:pointer}
.mid-price:hover{opacity:.8}

/* Chart */
svg.chart{display:block}

/* Trades */
.trade-row{display:grid;grid-template-columns:1fr 1fr 1fr;padding:2.5px 10px;font-size:.76rem}
.trade-row:hover{background:rgba(255,255,255,.03)}

/* Right Panel */
.form-tabs{display:flex;flex-shrink:0}
.ftab{flex:1;padding:9px;text-align:center;cursor:pointer;font-weight:700;font-size:.85rem;color:var(--muted);border-bottom:2px solid transparent;transition:.2s}
.ftab.buy.act{color:var(--green);border-color:var(--green)}
.ftab.sell.act{color:var(--red);border-color:var(--red)}
.form-body{padding:12px;display:flex;flex-direction:column;gap:10px}
.frow{display:flex;flex-direction:column;gap:3px}
.frow label{font-size:.7rem;color:var(--muted)}
.frow input{background:var(--bg);border:1px solid var(--border);color:var(--text);padding:7px 10px;border-radius:4px;font-size:.85rem;width:100%}
.frow input:focus{border-color:var(--accent);outline:none}
.finfo{display:flex;justify-content:space-between;font-size:.75rem;color:var(--muted)}
.btn-buy{background:var(--green);color:#000;width:100%;padding:10px;border:none;border-radius:4px;font-weight:700;cursor:pointer;font-size:.88rem;transition:.15s}
.btn-buy:hover{filter:brightness(1.1)}
.btn-sell{background:var(--red);color:#fff;width:100%;padding:10px;border:none;border-radius:4px;font-weight:700;cursor:pointer;font-size:.88rem;transition:.15s}
.btn-sell:hover{filter:brightness(1.1)}

/* My Orders */
.my-ord-row{display:grid;grid-template-columns:40px 70px 60px 1fr 50px;padding:5px 10px;font-size:.75rem;align-items:center;border-bottom:1px solid var(--border)}
.my-ord-row:hover{background:rgba(255,255,255,.03)}
.xbtn{background:transparent;border:1px solid var(--red);color:var(--red);padding:2px 6px;border-radius:3px;cursor:pointer;font-size:.68rem}
.xbtn:hover{background:var(--red);color:#fff}
.empty{padding:16px;text-align:center;color:var(--muted);font-size:.8rem}

/* Auth Modal */
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);display:flex;align-items:center;justify-content:center;z-index:50}
.modal{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:28px;width:360px}
.modal h2{text-align:center;margin-bottom:6px;color:var(--accent);font-size:1.2rem}
.modal p{text-align:center;color:var(--muted);font-size:.78rem;margin-bottom:20px}
.mtabs{display:flex;border:1px solid var(--border);border-radius:4px;overflow:hidden;margin-bottom:18px}
.mtab{flex:1;padding:8px;text-align:center;cursor:pointer;font-size:.85rem;color:var(--muted);transition:.15s}
.mtab.act{background:var(--accent);color:#000;font-weight:700}
.modal input{width:100%;background:var(--bg);border:1px solid var(--border);color:var(--text);padding:10px;border-radius:4px;margin-bottom:12px;font-size:.88rem}
.modal input:focus{border-color:var(--accent);outline:none}
.msub{width:100%;padding:10px;background:var(--accent);border:none;border-radius:4px;color:#000;font-weight:700;font-size:.9rem;cursor:pointer}
.msub:hover{background:var(--accent2)}
.merr{color:var(--red);font-size:.78rem;margin-bottom:8px;display:none}
.gift{text-align:center;margin-top:12px;color:var(--muted);font-size:.75rem}
.gift b{color:var(--green)}

/* Toast */
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--card);border:1px solid var(--green);border-radius:6px;padding:10px 22px;font-size:.85rem;z-index:200;display:none;min-width:220px;text-align:center}
.toast.err{border-color:var(--red)}

::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
</style>
</head>
<body>

<!-- Auth Modal -->
<div class="overlay" id="auth-modal">
  <div class="modal">
    <h2>💰 SMCoin Exchange</h2>
    <p>منصة تداول العملات الرقمية</p>
    <div class="mtabs">
      <div class="mtab act" id="mt-login" onclick="switchAuth('login')">تسجيل الدخول</div>
      <div class="mtab" id="mt-reg" onclick="switchAuth('reg')">حساب جديد</div>
    </div>
    <div class="merr" id="aerr"></div>
    <input type="text" id="au" placeholder="اسم المستخدم" autocomplete="off">
    <input type="password" id="ap" placeholder="كلمة المرور">
    <button class="msub" onclick="doAuth()" id="abtn">دخول</button>
    <div class="gift">حساب جديد يحصل على <b>100 SMC + 500 USD</b> مجاناً 🎁</div>
  </div>
</div>

<!-- Header -->
<header>
  <div class="ticker">
    <div class="logo">SMCoin</div>
    <div>
      <div class="tick-price" id="tp" style="color:var(--green)">—</div>
      <div style="color:var(--muted);font-size:.68rem">SMC / USD</div>
    </div>
    <div class="tick-info"><span class="tick-label">24h تغيير</span><span class="tick-value" id="tc">—</span></div>
    <div class="tick-info"><span class="tick-label">24h أعلى</span><span class="tick-value" id="th">—</span></div>
    <div class="tick-info"><span class="tick-label">24h أدنى</span><span class="tick-value" id="tl">—</span></div>
    <div class="tick-info"><span class="tick-label">24h حجم</span><span class="tick-value" id="tv">—</span></div>
  </div>
  <div class="user-area">
    <div class="balances">
      <div class="bal-line">USD: <span class="bal-val" id="busd">—</span></div>
      <div class="bal-line">SMC: <span class="bal-val" id="bsmc">—</span></div>
    </div>
    <span id="uname" style="color:var(--muted);font-size:.8rem"></span>
    <button class="btn btn-outline" onclick="logout()">خروج</button>
  </div>
</header>

<!-- Main Layout -->
<div class="layout">

  <!-- Left: Order Book -->
  <div class="panel">
    <div class="ptitle">دفتر الأوامر — SMC/USD</div>
    <div class="ob-head"><span>السعر (USD)</span><span style="text-align:center">الكمية</span><span style="text-align:left">الإجمالي</span></div>
    <div style="flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0">
      <div id="ob-asks" style="flex:1;display:flex;flex-direction:column-reverse;overflow:hidden"></div>
      <div class="ob-mid">
        <span class="mid-price" id="mid-price" onclick="setPrice(this.textContent)">—</span>
        <span style="color:var(--muted);font-size:.7rem">Spread: <span id="spread">—</span></span>
      </div>
      <div id="ob-bids" style="flex:1;overflow:hidden"></div>
    </div>
  </div>

  <!-- Center: Chart + Trades -->
  <div class="panel">
    <div class="ptitle" id="chart-title">الرسم البياني — SMC/USD</div>
    <div style="flex:1;overflow:hidden;min-height:0">
      <svg class="chart" id="chart" width="100%" height="100%" viewBox="0 0 900 280" preserveAspectRatio="none"></svg>
    </div>
    <div style="border-top:1px solid var(--border);flex-shrink:0">
      <div class="ptitle">الصفقات الأخيرة</div>
      <div class="ob-head"><span>السعر</span><span style="text-align:center">الكمية (SMC)</span><span style="text-align:left">الوقت</span></div>
      <div id="trades-list" style="height:120px;overflow-y:auto"></div>
    </div>
  </div>

  <!-- Right: Form + My Orders -->
  <div class="panel">
    <div class="form-tabs">
      <div class="ftab buy act" id="tab-buy" onclick="setSide('buy')">شراء</div>
      <div class="ftab sell" id="tab-sell" onclick="setSide('sell')">بيع</div>
    </div>
    <div class="form-body" style="flex-shrink:0">
      <div class="finfo"><span>المتاح</span><span id="favail">—</span></div>
      <div class="frow"><label>السعر (USD)</label><input type="number" id="fp" step="0.0001" value="1.0000" oninput="calcTotal()"></div>
      <div class="frow"><label>الكمية (SMC)</label><input type="number" id="fa" step="0.01" value="10" oninput="calcTotal()"></div>
      <div class="finfo"><span>الإجمالي</span><b id="ftotal" style="color:var(--accent)">10.00 USD</b></div>
      <button class="btn-buy" id="obtn" onclick="submitOrder()">شراء SMC</button>
    </div>
    <div style="border-top:1px solid var(--border);display:flex;flex-direction:column;flex:1;overflow:hidden;min-height:0">
      <div class="ptitle">أوامري المفتوحة</div>
      <div style="flex:1;overflow-y:auto" id="my-orders"><div class="empty">لا توجد أوامر</div></div>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let token = localStorage.getItem('smcex');
let me = null;
let side = 'buy';
let authMode = 'login';

// ── Auth ─────────────────────────────────────────────
function switchAuth(m) {
  authMode = m;
  document.getElementById('mt-login').classList.toggle('act', m==='login');
  document.getElementById('mt-reg').classList.toggle('act', m==='reg');
  document.getElementById('abtn').textContent = m==='login' ? 'دخول' : 'إنشاء حساب';
  document.getElementById('aerr').style.display='none';
}
async function doAuth() {
  const u = document.getElementById('au').value.trim();
  const p = document.getElementById('ap').value;
  const err = document.getElementById('aerr');
  if (!u||!p) { err.textContent='يرجى تعبئة جميع الحقول'; err.style.display='block'; return; }
  const r = await api('POST', '/api/'+authMode, { username:u, password:p });
  if (r.error) { err.textContent=r.error; err.style.display='block'; return; }
  token = r.token;
  localStorage.setItem('smcex', token);
  me = r.user;
  document.getElementById('auth-modal').style.display='none';
  startApp();
}
function logout() {
  localStorage.removeItem('smcex');
  token=null; me=null;
  document.getElementById('auth-modal').style.display='flex';
}

// ── Form ─────────────────────────────────────────────
function setSide(s) {
  side=s;
  document.getElementById('tab-buy').classList.toggle('act', s==='buy');
  document.getElementById('tab-sell').classList.toggle('act', s==='sell');
  const btn = document.getElementById('obtn');
  btn.className = s==='buy' ? 'btn-buy' : 'btn-sell';
  btn.textContent = s==='buy' ? 'شراء SMC' : 'بيع SMC';
  updateAvail();
}
function updateAvail() {
  if (!me) return;
  document.getElementById('favail').textContent = side==='buy'
    ? '$'+parseFloat(me.usd).toFixed(2)
    : parseFloat(me.smc).toFixed(4)+' SMC';
}
function calcTotal() {
  const p = parseFloat(document.getElementById('fp').value)||0;
  const a = parseFloat(document.getElementById('fa').value)||0;
  document.getElementById('ftotal').textContent = (p*a).toFixed(2)+' USD';
}
function setPrice(v) {
  const n = parseFloat(v);
  if (!isNaN(n)) { document.getElementById('fp').value = n.toFixed(4); calcTotal(); }
}
async function submitOrder() {
  const price  = document.getElementById('fp').value;
  const amount = document.getElementById('fa').value;
  const r = await api('POST', '/api/order', { side, price, amount });
  if (r.error) { toast(r.error, false); return; }
  toast(side==='buy' ? '✅ أمر شراء مُسجَّل' : '✅ أمر بيع مُسجَّل');
  refresh();
}
async function cancelOrder(id) {
  const r = await api('DELETE', '/api/order/'+id);
  if (r.error) { toast(r.error, false); return; }
  toast('تم إلغاء الأمر');
  refresh();
}

// ── Render ────────────────────────────────────────────
function renderOB(data) {
  const ROWS = 14;
  const aSlice = data.asks.slice(0, ROWS);
  const bSlice = data.bids.slice(0, ROWS);
  const maxA = Math.max(...aSlice.map(o=>o.total), 1);
  const maxB = Math.max(...bSlice.map(o=>o.total), 1);

  document.getElementById('ob-asks').innerHTML = [...aSlice].reverse().map(o =>
    '<div class="ob-row"><div class="ob-bar ask-bar" style="width:'+((o.total/maxA)*100).toFixed(1)+'%"></div>'
    +'<span class="ask-color">'+o.price.toFixed(4)+'</span>'
    +'<span style="text-align:center">'+o.amount.toFixed(2)+'</span>'
    +'<span style="text-align:left;color:var(--muted)">'+o.total.toFixed(2)+'</span></div>'
  ).join('');

  document.getElementById('ob-bids').innerHTML = bSlice.map(o =>
    '<div class="ob-row"><div class="ob-bar bid-bar" style="width:'+((o.total/maxB)*100).toFixed(1)+'%"></div>'
    +'<span class="bid-color">'+o.price.toFixed(4)+'</span>'
    +'<span style="text-align:center">'+o.amount.toFixed(2)+'</span>'
    +'<span style="text-align:left;color:var(--muted)">'+o.total.toFixed(2)+'</span></div>'
  ).join('');

  const mp = document.getElementById('mid-price');
  mp.textContent = data.lastPrice.toFixed(4);
  mp.style.color = 'var(--green)';
  if (data.asks.length && data.bids.length) {
    document.getElementById('spread').textContent = (data.asks[0].price - data.bids[0].price).toFixed(4);
  }
}

function renderTicker(d) {
  document.getElementById('tp').textContent = d.price.toFixed(4);
  document.getElementById('tp').style.color = d.change>=0 ? 'var(--green)' : 'var(--red)';
  const chEl = document.getElementById('tc');
  chEl.textContent = (d.change>=0?'+':'')+d.change.toFixed(2)+'%';
  chEl.style.color = d.change>=0 ? 'var(--green)' : 'var(--red)';
  document.getElementById('th').textContent = d.high.toFixed(4);
  document.getElementById('tl').textContent = d.low.toFixed(4);
  document.getElementById('tv').textContent = d.volume.toFixed(0)+' SMC';
}

function renderTrades(trades) {
  document.getElementById('trades-list').innerHTML = trades.slice(0, 40).map(t => {
    const d = new Date(t.t);
    const ts = d.getHours().toString().padStart(2,'0')+':'+d.getMinutes().toString().padStart(2,'0')+':'+d.getSeconds().toString().padStart(2,'0');
    return '<div class="trade-row">'
      +'<span style="color:'+(t.side==='buy'?'var(--green)':'var(--red)')+'">'+t.price.toFixed(4)+'</span>'
      +'<span style="text-align:center">'+t.amount.toFixed(2)+'</span>'
      +'<span style="text-align:left;color:var(--muted)">'+ts+'</span></div>';
  }).join('');
}

function renderMyOrders(orders) {
  const open = orders.filter(o=>o.status==='open');
  const el = document.getElementById('my-orders');
  if (!open.length) { el.innerHTML='<div class="empty">لا توجد أوامر مفتوحة</div>'; return; }
  el.innerHTML = open.map(o =>
    '<div class="my-ord-row">'
    +'<span style="color:'+(o.side==='buy'?'var(--green)':'var(--red)')+';">'+(o.side==='buy'?'شراء':'بيع')+'</span>'
    +'<span>'+o.price.toFixed(4)+'</span>'
    +'<span>'+o.remaining.toFixed(2)+'/'+o.amount.toFixed(2)+'</span>'
    +'<span style="color:var(--muted);font-size:.68rem">'+o.id+'</span>'
    +'<button class="xbtn" onclick="cancelOrder(\''+o.id+'\')">إلغاء</button>'
    +'</div>'
  ).join('');
}

function renderMe(u) {
  if (!u) return; me=u;
  document.getElementById('uname').textContent = '👤 '+u.username;
  document.getElementById('busd').textContent = '$'+parseFloat(u.usd).toFixed(2);
  document.getElementById('bsmc').textContent = parseFloat(u.smc).toFixed(4)+' SMC';
  updateAvail();
}

function renderChart(candles) {
  if (!candles||candles.length<2) return;
  const W=900, H=280, PL=8, PR=8, PT=14, PB=14;
  const prices = candles.map(c=>c.c);
  const lo = Math.min(...prices)*0.998;
  const hi = Math.max(...prices)*1.002;
  const range = hi-lo||0.001;
  const px = i => PL + (i/(candles.length-1))*(W-PL-PR);
  const py = p => PT + (1-(p-lo)/range)*(H-PT-PB);
  const pts = candles.map((c,i)=>px(i)+','+py(c.c)).join(' ');
  const lastX=px(candles.length-1), lastY=py(candles[candles.length-1].c);
  const firstY=py(candles[0].c);
  const fill='M '+px(0)+' '+H+' L '+candles.map((c,i)=>px(i)+' '+py(c.c)).join(' L ')+' L '+lastX+' '+H+' Z';
  const color = prices[prices.length-1]>=prices[0] ? '#0ecb81' : '#f6465d';
  document.getElementById('chart').innerHTML =
    '<defs><linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">'
    +'<stop offset="0%" stop-color="'+color+'" stop-opacity="0.25"/>'
    +'<stop offset="100%" stop-color="'+color+'" stop-opacity="0"/></linearGradient></defs>'
    +'<path d="'+fill+'" fill="url(#cg)"/>'
    +'<polyline points="'+pts+'" fill="none" stroke="'+color+'" stroke-width="1.5"/>'
    +'<circle cx="'+lastX+'" cy="'+lastY+'" r="3" fill="'+color+'"/>'
    +'<text x="'+(W-PR)+'" y="'+(PT-2)+'" fill="var(--muted)" font-size="9" text-anchor="end">'+hi.toFixed(4)+'</text>'
    +'<text x="'+(W-PR)+'" y="'+(H-2)+'" fill="var(--muted)" font-size="9" text-anchor="end">'+lo.toFixed(4)+'</text>'
    +'<text x="'+lastX+'" y="'+(lastY-6)+'" fill="'+color+'" font-size="9" text-anchor="middle">'+prices[prices.length-1].toFixed(4)+'</text>';
}

// ── API ───────────────────────────────────────────────
async function api(method, path, body) {
  try {
    const r = await fetch(path, {
      method,
      headers: { 'Content-Type':'application/json', 'Authorization':'Bearer '+(token||'') },
      body: body ? JSON.stringify(body) : undefined,
    });
    return r.json();
  } catch(e) { return { error: e.message }; }
}

// ── Refresh ───────────────────────────────────────────
async function refresh() {
  const [ob, trades, ticker, myOrd, meData, chart] = await Promise.all([
    api('GET','/api/orderbook'),
    api('GET','/api/trades'),
    api('GET','/api/ticker'),
    api('GET','/api/orders/my'),
    api('GET','/api/me'),
    api('GET','/api/chart'),
  ]);
  if (ob.asks)             renderOB(ob);
  if (trades && trades.length) renderTrades(trades);
  if (ticker.price!=null)  renderTicker(ticker);
  if (myOrd)               renderMyOrders(myOrd);
  if (meData.username)     renderMe(meData);
  if (chart && chart.length) renderChart(chart);
}

// ── Toast ─────────────────────────────────────────────
function toast(msg, ok=true) {
  const el = document.getElementById('toast');
  el.textContent = msg; el.className='toast'+(ok?'':' err'); el.style.display='block';
  clearTimeout(el._t); el._t = setTimeout(()=>el.style.display='none', 3000);
}

// ── Start ─────────────────────────────────────────────
function startApp() { refresh(); setInterval(refresh, 2000); }

if (token) {
  api('GET','/api/me').then(u => {
    if (u.username) {
      me=u;
      document.getElementById('auth-modal').style.display='none';
      startApp();
    }
  });
}
document.getElementById('au').addEventListener('keydown', e => { if(e.key==='Enter') doAuth(); });
document.getElementById('ap').addEventListener('keydown', e => { if(e.key==='Enter') doAuth(); });
</script>
</body>
</html>`;

// ══════════════════════════════════════════════════════
//  HTTP SERVER
// ══════════════════════════════════════════════════════

async function readBody(req) {
  return new Promise(resolve => {
    let body = '';
    req.on('data', d => (body += d));
    req.on('end', () => resolve(body));
  });
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  const path = url.pathname;

  const json = (data, code = 200) => {
    res.writeHead(code, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
    res.end(JSON.stringify(data));
  };

  // HTML
  if (req.method === 'GET' && path === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(HTML);
    return;
  }

  // OPTIONS
  if (req.method === 'OPTIONS') {
    res.writeHead(204, { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Authorization,Content-Type', 'Access-Control-Allow-Methods': 'GET,POST,DELETE' });
    res.end(); return;
  }

  // POST /api/login
  if (req.method === 'POST' && path === '/api/login') {
    const { username, password } = JSON.parse(await readBody(req));
    const user = users.get(username);
    if (!user || user.passHash !== sha256(password)) return json({ error: 'اسم المستخدم أو كلمة المرور غير صحيحة' }, 401);
    const tok = newTok();
    sessions.set(tok, username);
    return json({ token: tok, user: { username: user.username, usd: user.usd, smc: user.smc } });
  }

  // POST /api/reg
  if (req.method === 'POST' && path === '/api/reg') {
    const { username, password } = JSON.parse(await readBody(req));
    if (!username || username.length < 3) return json({ error: 'اسم المستخدم قصير جداً (3 أحرف على الأقل)' }, 400);
    if (!password || password.length < 4) return json({ error: 'كلمة المرور قصيرة (4 أحرف على الأقل)' }, 400);
    if (users.has(username)) return json({ error: 'اسم المستخدم محجوز' }, 400);
    const user = { username, passHash: sha256(password), usd: 500, smc: 100, t: Date.now() };
    users.set(username, user);
    const tok = newTok();
    sessions.set(tok, username);
    return json({ token: tok, user: { username, usd: user.usd, smc: user.smc } });
  }

  // Authenticated routes
  const user = getUser(req);

  // GET /api/me
  if (req.method === 'GET' && path === '/api/me') {
    if (!user) return json({ error: 'غير مسجَّل' }, 401);
    return json({ username: user.username, usd: user.usd, smc: user.smc });
  }

  // GET /api/ticker
  if (req.method === 'GET' && path === '/api/ticker') {
    const change = open24h > 0 ? ((lastPrice - open24h) / open24h) * 100 : 0;
    const candles24 = priceCandles.slice(-1440);
    const high  = Math.max(...candles24.map(c => c.h), lastPrice);
    const low   = Math.min(...candles24.map(c => c.l), lastPrice);
    const volume = candles24.reduce((s, c) => s + c.v, 0);
    return json({ price: lastPrice, change, high, low, volume });
  }

  // GET /api/orderbook
  if (req.method === 'GET' && path === '/api/orderbook') {
    const aggBids = [];
    for (const o of bids) {
      if (o.status !== 'open') continue;
      const last = aggBids[aggBids.length - 1];
      if (last && last.price === o.price) { last.amount += o.remaining; last.total += o.remaining * o.price; }
      else aggBids.push({ price: o.price, amount: o.remaining, total: o.remaining * o.price });
    }
    const aggAsks = [];
    for (const o of asks) {
      if (o.status !== 'open') continue;
      const last = aggAsks[aggAsks.length - 1];
      if (last && last.price === o.price) { last.amount += o.remaining; last.total += o.remaining * o.price; }
      else aggAsks.push({ price: o.price, amount: o.remaining, total: o.remaining * o.price });
    }
    return json({ bids: aggBids, asks: aggAsks, lastPrice });
  }

  // GET /api/trades
  if (req.method === 'GET' && path === '/api/trades') {
    return json(recentTrades.slice(0, 60));
  }

  // GET /api/chart
  if (req.method === 'GET' && path === '/api/chart') {
    return json(priceCandles.slice(-120));
  }

  // GET /api/orders/my
  if (req.method === 'GET' && path === '/api/orders/my') {
    if (!user) return json({ error: 'غير مسجَّل' }, 401);
    const myOrders = [...allOrders.values()].filter(o => o.username === user.username);
    return json(myOrders.slice(-50).reverse());
  }

  // POST /api/order
  if (req.method === 'POST' && path === '/api/order') {
    if (!user) return json({ error: 'يجب تسجيل الدخول أولاً' }, 401);
    try {
      const { side, price, amount } = JSON.parse(await readBody(req));
      const order = placeOrder(user, side, price, amount);
      return json({ success: true, order });
    } catch (e) { return json({ error: e.message }, 400); }
  }

  // DELETE /api/order/:id
  if (req.method === 'DELETE' && path.startsWith('/api/order/')) {
    if (!user) return json({ error: 'غير مسجَّل' }, 401);
    try {
      const id = path.split('/').pop();
      const order = cancelOrder(id, user.username);
      return json({ success: true, order });
    } catch (e) { return json({ error: e.message }, 400); }
  }

  res.writeHead(404); res.end('Not Found');
});

server.listen(PORT, () => {
  console.log('═'.repeat(52));
  console.log('   💰  SMCoin Exchange — منصة التداول');
  console.log('═'.repeat(52));
  console.log('   🌐  افتح المتصفح على: http://localhost:' + PORT);
  console.log('   💡  أنشئ حساباً للحصول على 100 SMC + 500 USD');
  console.log('═'.repeat(52));
});
