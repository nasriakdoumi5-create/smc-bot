/**
 *  SMCoin Explorer — واجهة ويب للبلوكشين
 *  تشغيل: node coin/server.js
 *  ثم افتح: http://localhost:4000
 */

import { createServer } from 'http';
import { createHash }   from 'crypto';
import { Blockchain }   from './blockchain.js';
import { Wallet }       from './wallet.js';

const PORT = process.env.COIN_PORT || 4000;

// ── البلوكشين والمحافظ ────────────────────────────────
const chain   = new Blockchain();
const wallets = {
  alice: new Wallet(),
  bob:   new Wallet(),
  miner: new Wallet(),
};

const addr = (pk) => pk
  ? createHash('sha256').update(pk).digest('hex').substring(0, 16)
  : 'Mining Reward';

// بيانات تجريبية أولية
console.log('⛏️  تهيئة البلوكشين...');
chain.minePendingTransactions(wallets.alice.publicKey);
chain.minePendingTransactions(wallets.alice.publicKey);
chain.addTransaction(wallets.alice.createTransaction(wallets.bob, 30));
chain.addTransaction(wallets.alice.createTransaction(wallets.bob, 15));
chain.minePendingTransactions(wallets.miner.publicKey);
chain.addTransaction(wallets.bob.createTransaction(wallets.miner, 10));
chain.minePendingTransactions(wallets.alice.publicKey);
console.log('✅ البلوكشين جاهز — 4 كتل / 3 محافظ\n');

// ── API helpers ────────────────────────────────────────
function serializeBlock(b) {
  return {
    index:   b.index,
    hash:    b.hash,
    short:   b.hash.substring(0, 20) + '…',
    prev:    b.previousHash.substring(0, 20) + '…',
    nonce:   b.nonce,
    txCount: b.transactions.length,
    time:    b.index === 0 ? 'Genesis' : new Date(Number(b.timestamp)).toLocaleString('ar'),
    transactions: b.transactions.map(tx => ({
      hash:   tx.hash.substring(0, 16) + '…',
      from:   addr(tx.fromPublicKey),
      to:     addr(tx.toPublicKey),
      amount: tx.amount,
      time:   tx.fromPublicKey === null ? 'Mining Reward' : new Date(tx.timestamp).toLocaleString('ar'),
    })),
  };
}

// ── HTML Explorer ─────────────────────────────────────
const HTML = `<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SMCoin Explorer</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d1117;--card:#161b22;--border:#30363d;
  --accent:#00d4aa;--accent2:#7c3aed;
  --text:#e6edf3;--muted:#8b949e;
  --green:#3fb950;--red:#f85149;--yellow:#d29922;
}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',Tahoma,sans-serif;min-height:100vh}

/* ── Header ── */
header{background:var(--card);border-bottom:1px solid var(--border);padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:64px;position:sticky;top:0;z-index:10}
.logo{display:flex;align-items:center;gap:10px;font-size:1.3rem;font-weight:700;color:var(--accent)}
.logo span{color:var(--text)}
.live-badge{background:#1a2e2a;color:var(--accent);border:1px solid var(--accent);border-radius:20px;padding:4px 12px;font-size:.75rem;display:flex;align-items:center;gap:6px}
.live-dot{width:7px;height:7px;background:var(--accent);border-radius:50%;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}

/* ── Stats Bar ── */
.stats-bar{background:#0a0e13;border-bottom:1px solid var(--border);display:flex;gap:0;overflow-x:auto}
.stat-item{padding:10px 24px;border-left:1px solid var(--border);white-space:nowrap;min-width:160px}
.stat-item:last-child{border-left:none}
.stat-label{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.stat-value{font-size:1.05rem;font-weight:600;color:var(--accent);margin-top:2px}

/* ── Tabs ── */
nav{background:var(--card);border-bottom:1px solid var(--border);padding:0 24px;display:flex;gap:0}
.tab{padding:14px 20px;cursor:pointer;border-bottom:2px solid transparent;color:var(--muted);font-size:.9rem;transition:.2s;user-select:none}
.tab:hover{color:var(--text)}
.tab.active{color:var(--accent);border-bottom-color:var(--accent)}

/* ── Main ── */
main{padding:24px;max-width:1200px;margin:0 auto}

/* ── Cards ── */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px}
.card-icon{font-size:1.8rem;margin-bottom:8px}
.card-label{font-size:.78rem;color:var(--muted);margin-bottom:6px}
.card-value{font-size:1.6rem;font-weight:700}
.card-value.green{color:var(--green)}
.card-value.accent{color:var(--accent)}
.card-value.yellow{color:var(--yellow)}
.card-value.purple{color:#a78bfa}

/* ── Grid 2 col ── */
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px}
@media(max-width:700px){.grid2{grid-template-columns:1fr}}

/* ── Section ── */
.section{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:20px}
.section-header{padding:14px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.section-title{font-weight:600;font-size:.95rem}
.view-all{color:var(--accent);font-size:.8rem;cursor:pointer;text-decoration:none}

/* ── Table ── */
table{width:100%;border-collapse:collapse;font-size:.85rem}
th{padding:10px 16px;text-align:right;color:var(--muted);font-weight:500;border-bottom:1px solid var(--border);white-space:nowrap}
td{padding:11px 16px;border-bottom:1px solid #1c2128;white-space:nowrap}
tr:last-child td{border-bottom:none}
tr:hover td{background:#1c2128}
.hash{font-family:monospace;color:var(--accent);font-size:.82rem}
.addr{font-family:monospace;font-size:.82rem;color:#a78bfa}
.badge{padding:3px 8px;border-radius:4px;font-size:.75rem;font-weight:500}
.badge-green{background:#1a2e1a;color:var(--green)}
.badge-blue{background:#1a2233;color:#60a5fa}
.badge-reward{background:#2a1a2e;color:#c084fc}

/* ── Wallet Cards ── */
.wallets{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-bottom:20px}
.wallet-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px}
.wallet-name{font-weight:700;font-size:1.05rem;margin-bottom:6px;display:flex;align-items:center;gap:8px}
.wallet-addr{font-family:monospace;font-size:.78rem;color:var(--muted);margin-bottom:12px;word-break:break-all}
.wallet-balance{font-size:1.8rem;font-weight:700;color:var(--accent)}
.wallet-symbol{font-size:.85rem;color:var(--muted);margin-right:4px}

/* ── Form ── */
.form-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:24px}
.form-title{font-weight:600;margin-bottom:16px;font-size:1rem}
.form-row{display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:10px;align-items:end}
@media(max-width:600px){.form-row{grid-template-columns:1fr}}
label{font-size:.8rem;color:var(--muted);display:block;margin-bottom:4px}
select,input{width:100%;background:#0d1117;border:1px solid var(--border);border-radius:8px;color:var(--text);padding:9px 12px;font-size:.9rem;outline:none}
select:focus,input:focus{border-color:var(--accent)}
.btn{padding:9px 20px;border-radius:8px;border:none;cursor:pointer;font-size:.9rem;font-weight:600;transition:.2s;white-space:nowrap}
.btn-primary{background:var(--accent);color:#000}
.btn-primary:hover{opacity:.85}
.btn-mine{background:var(--accent2);color:#fff}
.btn-mine:hover{opacity:.85}
.btn-sm{padding:5px 12px;font-size:.78rem}
.toast{position:fixed;bottom:24px;right:24px;background:#1c2128;border:1px solid var(--accent);border-radius:8px;padding:12px 18px;color:var(--text);font-size:.88rem;z-index:100;display:none;max-width:320px}

/* ── Blocks page ── */
.block-hash{font-family:monospace;font-size:.78rem}
.page{display:none}
.page.active{display:block}
</style>
</head>
<body>

<header>
  <div class="logo">💰 <span>SMCoin</span> Explorer</div>
  <div class="live-badge"><div class="live-dot"></div> شبكة مباشرة</div>
</header>

<div class="stats-bar" id="stats-bar">
  <div class="stat-item"><div class="stat-label">عدد الكتل</div><div class="stat-value" id="sb-blocks">—</div></div>
  <div class="stat-item"><div class="stat-label">المُعدَّن</div><div class="stat-value" id="sb-mined">—</div></div>
  <div class="stat-item"><div class="stat-label">الصعوبة</div><div class="stat-value" id="sb-diff">—</div></div>
  <div class="stat-item"><div class="stat-label">مكافأة التعدين</div><div class="stat-value" id="sb-reward">—</div></div>
  <div class="stat-item"><div class="stat-label">معاملات منتظرة</div><div class="stat-value" id="sb-pending">—</div></div>
  <div class="stat-item"><div class="stat-label">حالة السلسلة</div><div class="stat-value" id="sb-valid">—</div></div>
</div>

<nav>
  <div class="tab active" onclick="showPage('dashboard')">لوحة التحكم</div>
  <div class="tab" onclick="showPage('blocks')">الكتل</div>
  <div class="tab" onclick="showPage('transactions')">المعاملات</div>
  <div class="tab" onclick="showPage('wallets')">المحافظ</div>
</nav>

<main>

<!-- ══ Dashboard ══ -->
<div id="page-dashboard" class="page active">
  <div class="cards">
    <div class="card">
      <div class="card-icon">🧱</div>
      <div class="card-label">إجمالي الكتل</div>
      <div class="card-value accent" id="c-blocks">—</div>
    </div>
    <div class="card">
      <div class="card-icon">💸</div>
      <div class="card-label">إجمالي المعاملات</div>
      <div class="card-value green" id="c-txcount">—</div>
    </div>
    <div class="card">
      <div class="card-icon">💰</div>
      <div class="card-label">SMC مُعدَّن</div>
      <div class="card-value yellow" id="c-mined">—</div>
    </div>
    <div class="card">
      <div class="card-icon">⛏️</div>
      <div class="card-label">صعوبة التعدين</div>
      <div class="card-value purple" id="c-diff">—</div>
    </div>
  </div>

  <div class="grid2">
    <div class="section">
      <div class="section-header">
        <span class="section-title">🧱 آخر الكتل</span>
        <span class="view-all" onclick="showPage('blocks')">عرض الكل</span>
      </div>
      <table>
        <thead><tr><th>#</th><th>Hash</th><th>المعاملات</th><th>Nonce</th></tr></thead>
        <tbody id="latest-blocks"></tbody>
      </table>
    </div>
    <div class="section">
      <div class="section-header">
        <span class="section-title">💸 آخر المعاملات</span>
        <span class="view-all" onclick="showPage('transactions')">عرض الكل</span>
      </div>
      <table>
        <thead><tr><th>من</th><th>إلى</th><th>المبلغ</th></tr></thead>
        <tbody id="latest-txs"></tbody>
      </table>
    </div>
  </div>

  <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
    <button class="btn btn-mine" onclick="mine()">⛏️ تعدين كتلة جديدة</button>
  </div>
</div>

<!-- ══ Blocks ══ -->
<div id="page-blocks" class="page">
  <div class="section">
    <div class="section-header"><span class="section-title">🧱 جميع الكتل</span></div>
    <table>
      <thead><tr><th>#</th><th>Hash</th><th>السابق</th><th>المعاملات</th><th>Nonce</th><th>الوقت</th></tr></thead>
      <tbody id="all-blocks"></tbody>
    </table>
  </div>
</div>

<!-- ══ Transactions ══ -->
<div id="page-transactions" class="page">
  <div class="section">
    <div class="section-header"><span class="section-title">💸 جميع المعاملات</span></div>
    <table>
      <thead><tr><th>كتلة</th><th>Hash</th><th>من</th><th>إلى</th><th>المبلغ (SMC)</th><th>الوقت</th></tr></thead>
      <tbody id="all-txs"></tbody>
    </table>
  </div>
</div>

<!-- ══ Wallets ══ -->
<div id="page-wallets" class="page">
  <div class="wallets" id="wallets-grid"></div>

  <div class="form-card">
    <div class="form-title">📤 إرسال SMC</div>
    <div class="form-row">
      <div>
        <label>من</label>
        <select id="f-from">
          <option value="alice">Alice</option>
          <option value="bob">Bob</option>
          <option value="miner">Miner</option>
        </select>
      </div>
      <div>
        <label>إلى</label>
        <select id="f-to">
          <option value="bob">Bob</option>
          <option value="alice">Alice</option>
          <option value="miner">Miner</option>
        </select>
      </div>
      <div>
        <label>المبلغ (SMC)</label>
        <input type="number" id="f-amount" value="10" min="1">
      </div>
      <div>
        <label>&nbsp;</label>
        <button class="btn btn-primary" onclick="sendTx()">إرسال</button>
      </div>
    </div>
    <p style="margin-top:12px;font-size:.8rem;color:var(--muted)">⚠️ بعد الإرسال اضغط "تعدين كتلة جديدة" لتأكيد المعاملة</p>
  </div>

  <div style="margin-top:16px;display:flex;gap:12px;flex-wrap:wrap">
    <button class="btn btn-mine" onclick="mine()">⛏️ تعدين كتلة جديدة</button>
  </div>
</div>

</main>

<div class="toast" id="toast"></div>

<script>
const tabs = document.querySelectorAll('.tab');
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + id).classList.add('active');
  tabs.forEach((t,i) => {
    const names = ['dashboard','blocks','transactions','wallets'];
    t.classList.toggle('active', names[i] === id);
  });
}

function toast(msg, ok=true) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.style.display = 'block';
  el.style.borderColor = ok ? 'var(--accent)' : 'var(--red)';
  setTimeout(() => el.style.display = 'none', 3000);
}

async function fetchJSON(url) {
  const r = await fetch(url);
  return r.json();
}

async function refresh() {
  try {
    const [stats, blocks, txs, ws] = await Promise.all([
      fetchJSON('/api/stats'),
      fetchJSON('/api/blocks'),
      fetchJSON('/api/transactions'),
      fetchJSON('/api/wallets'),
    ]);
    updateStats(stats, txs);
    updateDashboard(blocks, txs);
    updateBlocksPage(blocks);
    updateTxsPage(txs);
    updateWallets(ws);
  } catch(e) { console.error(e); }
}

function updateStats(s, txs) {
  const total = txs.length;
  document.getElementById('sb-blocks').textContent  = s.blocks;
  document.getElementById('sb-mined').textContent   = s.totalMined + ' SMC';
  document.getElementById('sb-diff').textContent    = s.difficulty;
  document.getElementById('sb-reward').textContent  = s.miningReward + ' SMC';
  document.getElementById('sb-pending').textContent = s.pending;
  document.getElementById('sb-valid').textContent   = s.valid ? '✅ صالح' : '❌ مزوّر';
  document.getElementById('c-blocks').textContent   = s.blocks;
  document.getElementById('c-txcount').textContent  = total;
  document.getElementById('c-mined').textContent    = s.totalMined + ' SMC';
  document.getElementById('c-diff').textContent     = s.difficulty;
}

function updateDashboard(blocks, txs) {
  const lb = [...blocks].reverse().slice(0, 5);
  document.getElementById('latest-blocks').innerHTML = lb.map(b => \`
    <tr>
      <td><span class="badge badge-blue">#\${b.index}</span></td>
      <td><span class="hash">\${b.short}</span></td>
      <td>\${b.txCount}</td>
      <td style="color:var(--muted)">\${b.nonce}</td>
    </tr>\`).join('');

  const lt = txs.slice(0, 5);
  document.getElementById('latest-txs').innerHTML = lt.map(tx => \`
    <tr>
      <td><span class="addr">\${tx.from.substring(0,10)}…</span></td>
      <td><span class="addr">\${tx.to.substring(0,10)}…</span></td>
      <td><b style="color:var(--accent)">\${tx.amount}</b> SMC</td>
    </tr>\`).join('');
}

function updateBlocksPage(blocks) {
  document.getElementById('all-blocks').innerHTML = [...blocks].reverse().map(b => \`
    <tr>
      <td><span class="badge badge-blue">#\${b.index}</span></td>
      <td><span class="hash" title="\${b.fullHash}">\${b.short}</span></td>
      <td><span class="hash">\${b.prev}</span></td>
      <td>\${b.txCount}</td>
      <td style="color:var(--muted)">\${b.nonce.toLocaleString()}</td>
      <td style="color:var(--muted);font-size:.8rem">\${b.time}</td>
    </tr>\`).join('');
}

function updateTxsPage(txs) {
  document.getElementById('all-txs').innerHTML = txs.map(tx => \`
    <tr>
      <td><span class="badge badge-blue">#\${tx.block}</span></td>
      <td><span class="hash">\${tx.hash}</span></td>
      <td><span class="addr">\${tx.from === 'Mining Reward' ? '<span class="badge badge-reward">Mining Reward</span>' : tx.from + '…'}</span></td>
      <td><span class="addr">\${tx.to}…</span></td>
      <td><b style="color:var(--accent)">\${tx.amount}</b></td>
      <td style="color:var(--muted);font-size:.78rem">\${tx.time}</td>
    </tr>\`).join('');
}

function updateWallets(ws) {
  const icons = { alice:'👩', bob:'👨', miner:'⛏️' };
  document.getElementById('wallets-grid').innerHTML = ws.map(w => \`
    <div class="wallet-card">
      <div class="wallet-name">\${icons[w.name]||'👤'} \${w.name.charAt(0).toUpperCase()+w.name.slice(1)}</div>
      <div class="wallet-addr">\${w.address}…</div>
      <div class="wallet-balance">\${w.balance} <span class="wallet-symbol">SMC</span></div>
    </div>\`).join('');
}

async function mine() {
  const from = document.getElementById('f-from')?.value || 'miner';
  const r = await fetch('/api/mine', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ wallet: from }) });
  const d = await r.json();
  if (d.success) {
    toast(\`✅ تم تعدين الكتلة #\${d.block} بنجاح!\`);
    refresh();
  } else {
    toast('❌ ' + (d.error || 'خطأ'), false);
  }
}

async function sendTx() {
  const from   = document.getElementById('f-from').value;
  const to     = document.getElementById('f-to').value;
  const amount = Number(document.getElementById('f-amount').value);
  if (from === to) return toast('❌ المرسل والمستقبل نفس المحفظة!', false);
  const r = await fetch('/api/send', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ from, to, amount }) });
  const d = await r.json();
  if (d.success) {
    toast(\`✅ تمت إضافة المعاملة — عدّن كتلة لتأكيدها\`);
    refresh();
  } else {
    toast('❌ ' + d.error, false);
  }
}

// تحديث كل 5 ثواني
refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>`;

// ── HTTP Server ────────────────────────────────────────
const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost`);

  const json = (data, code = 200) => {
    res.writeHead(code, {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    });
    res.end(typeof data === 'string' ? data : JSON.stringify(data));
  };

  // الصفحة الرئيسية
  if (req.method === 'GET' && url.pathname === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(HTML);
    return;
  }

  // GET /api/stats
  if (req.method === 'GET' && url.pathname === '/api/stats') {
    return json(chain.stats());
  }

  // GET /api/blocks
  if (req.method === 'GET' && url.pathname === '/api/blocks') {
    return json(chain.chain.map(serializeBlock));
  }

  // GET /api/transactions
  if (req.method === 'GET' && url.pathname === '/api/transactions') {
    const txs = [];
    for (const b of chain.chain) {
      for (const tx of b.transactions) {
        txs.push({
          block:  b.index,
          hash:   tx.hash.substring(0, 16) + '…',
          from:   addr(tx.fromPublicKey),
          to:     addr(tx.toPublicKey),
          amount: tx.amount,
          time:   b.index === 0 ? 'Genesis' : new Date(Number(tx.timestamp)).toLocaleString('ar'),
        });
      }
    }
    return json(txs.reverse());
  }

  // GET /api/wallets
  if (req.method === 'GET' && url.pathname === '/api/wallets') {
    return json(
      Object.entries(wallets).map(([name, w]) => ({
        name,
        address: addr(w.publicKey),
        balance: chain.getBalance(w.publicKey),
      }))
    );
  }

  // POST /api/mine
  if (req.method === 'POST' && url.pathname === '/api/mine') {
    let body = '';
    req.on('data', d => (body += d));
    req.on('end', () => {
      try {
        const { wallet: wName = 'miner' } = JSON.parse(body || '{}');
        const w = wallets[wName] || wallets.miner;
        console.log(`⛏️  تعدين كتلة جديدة...`);
        const block = chain.minePendingTransactions(w.publicKey);
        console.log(`✅ كتلة #${block.index} مُعدَّنة`);
        json({ success: true, block: block.index, hash: block.hash });
      } catch (e) {
        json({ error: e.message }, 400);
      }
    });
    return;
  }

  // POST /api/send
  if (req.method === 'POST' && url.pathname === '/api/send') {
    let body = '';
    req.on('data', d => (body += d));
    req.on('end', () => {
      try {
        const { from, to, amount } = JSON.parse(body);
        const fromW = wallets[from];
        const toW   = wallets[to];
        if (!fromW || !toW) return json({ error: 'محفظة غير موجودة' }, 400);
        const tx = fromW.createTransaction(toW, Number(amount));
        chain.addTransaction(tx);
        console.log(`💸 معاملة: ${from} → ${to}  ${amount} SMC`);
        json({ success: true, txHash: tx.hash });
      } catch (e) {
        json({ error: e.message }, 400);
      }
    });
    return;
  }

  res.writeHead(404);
  res.end('Not Found');
});

server.listen(PORT, () => {
  console.log('═'.repeat(50));
  console.log('  💰  SMCoin Explorer');
  console.log('═'.repeat(50));
  console.log(`  🌐  http://localhost:${PORT}`);
  console.log('═'.repeat(50));
});
