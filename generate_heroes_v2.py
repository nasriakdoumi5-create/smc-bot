"""
generate_heroes_v2.py
Browser-rendered hero images (2000x2000) for ALL catalog products.
Each hero: badge → big title → subtitle → floating dashboard mockup
(real KPIs + real table from the product's own config) → chips → brand footer.
Run on server:  python3 generate_heroes_v2.py
"""
import asyncio, glob, html, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nasritools.products import CATALOG
from nasritools.factory2 import _sample_value, _is_money, _num
from datetime import date

OUTPUT = Path(__file__).parent / "output"

PILL_STYLES = [
    ("({}DCFCE7)", "#166534"), ]  # placeholder, replaced below

def esc(s):
    return html.escape(str(s))

def kpi_value(label, i):
    l = label.lower()
    if "rate" in l or "%" in l or "progress" in l:
        return ["50%", "68%", "82%"][i % 3]
    if any(w in l for w in ("count", "clients", "tasks", "items", "orders",
                            "total #", "active", "open", "done", "guests", "leads")):
        return ["24", "12", "38"][i % 3]
    return ["€2,930", "€1,458", "€1,472"][i % 3]

def short_subtitle(cfg):
    intro = cfg.get("description_intro", "") or cfg.get("subtitle", "")
    first = re.split(r"(?<=[.!?])\s", intro)[0]
    return first[:80].rstrip(".") if first else "Everything organized in one clean sheet"

def split_title(name):
    words = name.split()
    if len(words) == 1:
        return "", words[0]
    return " ".join(words[:-1]), words[-1]

def table_html(cfg):
    tab = next((t for t in cfg.get("tabs", []) if t.get("type") == "table"), None)
    if not tab:
        return ""
    cols = tab.get("columns", [])[:5]
    ths = "".join(f"<th>{esc(c.get('name','').upper()[:14])}</th>" for c in cols)
    rows = []
    base = date(2026, 6, 1)
    pills = [("#DCFCE7", "#166534"), ("#DBEAFE", "#1E40AF"),
             ("#FEF3C7", "#92400E"), ("#FEE2E2", "#991B1B")]
    for r in range(4):
        tds = []
        for c in cols:
            if c.get("formula"):
                v = "—"
            else:
                v = _sample_value(c, r, base)
            if isinstance(v, date):
                v = v.strftime("%b %d")
            elif isinstance(v, (int, float)):
                v = f"€{v:,.2f}" if _is_money(c.get("name", "")) else f"{v:g}"
            v = str(v)[:22]
            if c.get("dropdown") and len(str(v)) <= 14:
                bg, fg = pills[r % 4]
                tds.append(f'<td><span class="pill" style="background:{bg};color:{fg}">{esc(v)}</span></td>')
            else:
                tds.append(f"<td>{esc(v)}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return f"<table><tr>{ths}</tr>{''.join(rows)}</table>"

def kpis_html(cfg):
    tab = next((t for t in cfg.get("tabs", []) if t.get("type") == "dashboard"), None)
    kpis = (tab or {}).get("kpis", [])[:3]
    if not kpis:
        kpis = [{"label": "This Month"}, {"label": "Total"}, {"label": "Rate"}]
    grads = ["linear-gradient(135deg,#22C55E,#16A34A)",
             "linear-gradient(135deg,#F97316,#EA580C)",
             "linear-gradient(135deg,#1A1A2E,#343456)"]
    out = []
    for i, k in enumerate(kpis):
        out.append(
            f'<div class="kpi" style="background:{grads[i%3]}">'
            f'<div class="l">{esc(k.get("label","").upper()[:16])}</div>'
            f'<div class="v">{kpi_value(k.get("label",""), i)}</div></div>')
    return "".join(out)

def chips_html(cfg):
    feats = cfg.get("features", []) or []
    defaults = ["⚡ <b>Auto</b>-calculating", "📱 Works on <b>phone</b>", "🚫 <b>No</b> subscription"]
    if len(feats) >= 2:
        picked = []
        for f in feats:
            if "auto" in f.lower():
                picked.append("⚡ <b>Auto</b>-calculating")
            elif "phone" in f.lower() or "device" in f.lower():
                picked.append("📱 Works on <b>phone</b>")
        picked.append("🚫 <b>No</b> subscription")
        seen, out = set(), []
        for p in picked + defaults:
            if p not in seen:
                seen.add(p); out.append(p)
        defaults = out[:3]
    return "".join(f'<div class="chip">{c}</div>' for c in defaults[:3])

def build_html(cfg):
    first, last = split_title(cfg["name"])
    title_len = len(cfg["name"])
    tsize = 120 if title_len <= 22 else (96 if title_len <= 30 else 76)
    emoji = cfg.get("listing_emoji", "📊")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:2000px;height:2000px;font-family:'Liberation Sans',Arial,sans-serif;
background:radial-gradient(1200px 900px at 85% -10%,#FFE8D6 0%,transparent 60%),
radial-gradient(1000px 800px at -10% 110%,#FFEDD5 0%,transparent 55%),
linear-gradient(160deg,#FFFBF7 0%,#FFF4EA 100%);
overflow:hidden;position:relative;display:flex;flex-direction:column;align-items:center}}
.topbar{{position:absolute;top:0;left:0;right:0;height:22px;background:linear-gradient(90deg,#F97316,#FB923C)}}
.badge{{margin-top:100px;background:#1A1A2E;color:#FFD166;font-size:34px;font-weight:bold;
letter-spacing:6px;padding:18px 44px;border-radius:999px}}
h1{{margin-top:44px;font-size:{tsize}px;font-weight:800;color:#1A1A2E;text-align:center;
line-height:1.05;letter-spacing:-2px;max-width:1700px}}
h1 span{{color:#F97316}}
.sub{{margin-top:26px;font-size:42px;color:#8B7E74;max-width:1600px;text-align:center}}
.mockup{{margin-top:70px;width:1560px;background:#fff;border-radius:36px;overflow:hidden;
box-shadow:0 60px 120px rgba(26,26,46,.22),0 20px 40px rgba(249,115,22,.12);transform:rotate(-1.2deg)}}
.mock-head{{background:#1A1A2E;padding:34px 48px;display:flex;align-items:center;gap:20px}}
.dot{{width:22px;height:22px;border-radius:50%}}
.mock-title{{color:#fff;font-size:33px;font-weight:bold;margin-left:24px}}
.kpis{{display:flex;gap:28px;padding:42px 48px 6px}}
.kpi{{flex:1;border-radius:24px;padding:30px 34px;color:#fff}}
.kpi .l{{font-size:25px;opacity:.85;letter-spacing:2px}}
.kpi .v{{font-size:54px;font-weight:800;margin-top:10px}}
table{{width:calc(100% - 96px);margin:34px 48px 46px;border-collapse:collapse;font-size:29px}}
th{{background:#F97316;color:#fff;padding:20px 24px;text-align:left;font-size:25px;letter-spacing:1px}}
td{{padding:19px 24px;border-bottom:2px solid #F4EDE6;color:#3A3530}}
tr:nth-child(even) td{{background:#FFFAF4}}
.pill{{display:inline-block;padding:7px 20px;border-radius:999px;font-size:23px;font-weight:bold}}
.chips{{margin-top:64px;display:flex;gap:26px}}
.chip{{background:#fff;border:3px solid #F1E5D8;border-radius:999px;font-size:34px;font-weight:bold;
color:#1A1A2E;padding:22px 42px;box-shadow:0 8px 24px rgba(26,26,46,.06)}}
.chip b{{color:#F97316}}
.footer{{position:absolute;bottom:0;left:0;right:0;height:150px;background:#1A1A2E;
display:flex;align-items:center;justify-content:center;gap:30px}}
.logo{{width:64px;height:64px;background:#F97316;border-radius:14px;display:grid;
grid-template-columns:repeat(3,1fr);gap:5px;padding:10px}}
.logo i{{background:rgba(0,0,0,.35);border-radius:4px}}
.logo i:first-child{{background:#fff}}
.footer span{{color:#fff;font-size:40px;font-weight:bold}}
.footer span b{{color:#F97316}}
.footer small{{color:#8B90A5;font-size:30px}}
</style></head><body>
<div class="topbar"></div>
<div class="badge">GOOGLE SHEETS TEMPLATE</div>
<h1>{esc(first)} <span>{esc(last)}</span></h1>
<div class="sub">{esc(short_subtitle(cfg))}</div>
<div class="mockup">
  <div class="mock-head">
    <div class="dot" style="background:#EF4444"></div>
    <div class="dot" style="background:#FBBF24"></div>
    <div class="dot" style="background:#22C55E"></div>
    <div class="mock-title">{emoji} {esc(cfg['name'])} — Dashboard</div>
  </div>
  <div class="kpis">{kpis_html(cfg)}</div>
  {table_html(cfg)}
</div>
<div class="chips">{chips_html(cfg)}</div>
<div class="footer">
  <div class="logo"><i></i><i></i><i></i><i></i><i></i><i></i></div>
  <span>Nasri<b>Tools</b></span>
  <small>nasritools.etsy.com&nbsp;&nbsp;•&nbsp;&nbsp;Instant Download</small>
</div>
</body></html>"""

async def main():
    from playwright.async_api import async_playwright
    exe = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=exe[0] if exe else None)
        page = await browser.new_page(viewport={"width": 2000, "height": 2000})
        ok = 0
        for i, cfg in enumerate(CATALOG, 1):
            slug = cfg["slug"]
            out = OUTPUT / slug / f"{slug}_01_hero.jpg"
            out.parent.mkdir(parents=True, exist_ok=True)
            tmp = OUTPUT / slug / "_hero.html"
            tmp.write_text(build_html(cfg), encoding="utf-8")
            await page.goto(f"file://{tmp}")
            await page.wait_for_timeout(120)
            await page.screenshot(path=str(out), type="jpeg", quality=88)
            tmp.unlink()
            ok += 1
            print(f"  [{i:3}/{len(CATALOG)}] ✓ {slug}")
        await browser.close()
        print(f"\n  Done: {ok} hero images")

if __name__ == "__main__":
    asyncio.run(main())
