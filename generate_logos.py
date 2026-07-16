"""
generate_logos.py  — 3 shop icon options (500x500) for Etsy.
Psychology: warmth (orange), clarity (grid = spreadsheets), trust (clean, premium).
Output: logos/logo_1.png, logo_2.png, logo_3.png
"""
import asyncio, glob
from pathlib import Path

OUT = Path(__file__).parent / "logos"
OUT.mkdir(exist_ok=True)

# ── Option 1: "The Living Grid" — refined grid mark, one glowing cell ──
LOGO_1 = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:500px;height:500px;display:grid;place-items:center;
background:radial-gradient(400px 400px at 30% 20%,#FFF3E8 0%,#FFE8D6 60%,#FFDDBF 100%)}
.mark{width:300px;height:300px;border-radius:64px;position:relative;
background:linear-gradient(135deg,#FB923C 0%,#F97316 45%,#EA580C 100%);
box-shadow:0 30px 60px rgba(234,88,12,.35),0 10px 24px rgba(234,88,12,.25),
inset 0 2px 6px rgba(255,255,255,.35);
display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);
gap:14px;padding:38px}
.cell{background:rgba(0,0,0,.22);border-radius:16px}
.cell.lit{background:#fff;box-shadow:0 0 30px rgba(255,255,255,.9),0 4px 10px rgba(0,0,0,.15)}
</style></head><body>
<div class="mark">
  <div class="cell lit"></div><div class="cell"></div><div class="cell"></div>
  <div class="cell"></div><div class="cell"></div><div class="cell"></div>
  <div class="cell"></div><div class="cell"></div><div class="cell"></div>
</div>
</body></html>"""

# ── Option 2: "N Monogram" — the letter N built from grid cells ──
LOGO_2 = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:500px;height:500px;display:grid;place-items:center;
background:#1A1A2E}
.frame{width:330px;height:330px;border-radius:72px;
background:linear-gradient(150deg,#23233B,#15152A);
box-shadow:inset 0 2px 10px rgba(255,255,255,.06),0 30px 60px rgba(0,0,0,.5);
display:grid;place-items:center}
.n{display:grid;grid-template-columns:repeat(4,52px);grid-template-rows:repeat(4,52px);gap:10px}
.c{border-radius:12px;background:rgba(249,115,22,.14)}
.on{background:linear-gradient(135deg,#FB923C,#F97316);
box-shadow:0 6px 18px rgba(249,115,22,.45)}
</style></head><body>
<div class="frame"><div class="n">
  <div class="c on"></div><div class="c"></div><div class="c"></div><div class="c on"></div>
  <div class="c on"></div><div class="c on"></div><div class="c"></div><div class="c on"></div>
  <div class="c on"></div><div class="c"></div><div class="c on"></div><div class="c on"></div>
  <div class="c on"></div><div class="c"></div><div class="c"></div><div class="c on"></div>
</div></div>
</body></html>"""

# ── Option 3: "The Smile Sheet" — grid + smile curve (friendly & human) ──
LOGO_3 = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:500px;height:500px;display:grid;place-items:center;
background:linear-gradient(160deg,#FFFBF7,#FFEDD5)}
.card{width:310px;height:310px;border-radius:60px;background:#fff;position:relative;
box-shadow:0 30px 70px rgba(26,26,46,.16),0 8px 20px rgba(249,115,22,.12);overflow:hidden}
.head{height:74px;background:linear-gradient(90deg,#F97316,#FB923C);
display:flex;align-items:center;gap:10px;padding:0 26px}
.dot{width:14px;height:14px;border-radius:50%;background:rgba(255,255,255,.55)}
.grid{position:absolute;inset:74px 0 0 0;
background-image:linear-gradient(#F4EDE6 2px,transparent 2px),
linear-gradient(90deg,#F4EDE6 2px,transparent 2px);background-size:59px 59px}
svg{position:absolute;left:50%;top:57%;transform:translate(-50%,-50%)}
</style></head><body>
<div class="card">
  <div class="head"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
  <div class="grid"></div>
  <svg width="200" height="130" viewBox="0 0 200 130">
    <circle cx="52" cy="34" r="17" fill="#1A1A2E"/>
    <circle cx="148" cy="34" r="17" fill="#1A1A2E"/>
    <path d="M30 78 Q100 150 170 78" stroke="#F97316" stroke-width="26"
          stroke-linecap="round" fill="none"/>
  </svg>
</div>
</body></html>"""

async def main():
    from playwright.async_api import async_playwright
    exe = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=exe[0] if exe else None)
        page = await b.new_page(viewport={"width": 500, "height": 500})
        for i, html in enumerate([LOGO_1, LOGO_2, LOGO_3], 1):
            tmp = OUT / f"_l{i}.html"
            tmp.write_text(html, encoding="utf-8")
            await page.goto(f"file://{tmp}")
            await page.wait_for_timeout(150)
            await page.screenshot(path=str(OUT / f"logo_{i}.png"))
            tmp.unlink()
            print(f"  ✓ logo_{i}.png")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
