"""
generate_fix_heroes.py  (runs on server)
Hero images for the 12 fixed listings:
  • 8 bundles — special bundle design (included templates table)
  • 2 premium managers — standard product design
  • starter/free budget design refresh
Output: output/_fix/<key>/hero.jpg  (+ starter hero refresh)
"""
import asyncio, glob, html, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_heroes_v2 import build_html
from build_remaining import BUNDLES, FREELANCE_CFG, RESTAURANT_CFG

OUTPUT = Path(__file__).parent / "output"
FIX    = OUTPUT / "_fix"

def esc(s): return html.escape(str(s))

BUNDLE_DESCRIPTIONS = {
    "budget_tracker": "Know where every euro goes",
    "meal_planner": "Plan meals + auto grocery list",
    "workout_tracker": "Log workouts, see progress",
    "habit_tracker": "Build habits that stick",
    "weekly_planner": "Your week on one page",
    "goals_planner": "Set goals, track progress",
    "travel_planner": "Trips, budgets & packing",
    "student_planner": "Classes, deadlines & grades",
    "debt_payoff_planner": "Crush debt with a plan",
    "annual_review_planner": "Reflect & plan your year",
    "freelancer_invoice_tracker": "Invoices & client payments",
    "emergency_fund_tracker": "Build your safety net",
    "grocery_budget_tracker": "Cut your food spending",
    "sleep_tracker": "Better sleep, tracked",
    "weight_loss_tracker": "Progress you can see",
    "kpi_dashboard": "Business numbers, live",
    "inventory_management": "Stock levels & reorders",
    "lead_tracker": "Never lose a lead again",
    "social_media_analytics": "Know what content works",
    "keto_diet_tracker": "Macros made simple",
    "project_management": "Tasks, deadlines, owners",
    "content_creator_planner": "Content calendar + ideas",
}

def bundle_html(cfg):
    n = len(cfg["includes"])
    rows = []
    for i, slug in enumerate(cfg["includes"][:6]):
        name = slug.replace("_", " ").title()
        desc = BUNDLE_DESCRIPTIONS.get(slug, "Ready-to-use template")
        rows.append(f"""<tr><td><b>{esc(name)}</b></td><td>{esc(desc)}</td>
        <td><span class="pill" style="background:#DCFCE7;color:#166534">✓ INCLUDED</span></td></tr>""")
    more = f"""<tr><td colspan="3" style="text-align:center;color:#B45309;font-weight:bold">
      + {n-6} more templates inside…</td></tr>""" if n > 6 else ""
    value = n * 5
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:2000px;height:2000px;font-family:'Liberation Sans',Arial,sans-serif;
background:radial-gradient(1200px 900px at 85% -10%,#FFE8D6 0%,transparent 60%),
radial-gradient(1000px 800px at -10% 110%,#FFEDD5 0%,transparent 55%),
linear-gradient(160deg,#FFFBF7 0%,#FFF4EA 100%);
overflow:hidden;position:relative;display:flex;flex-direction:column;align-items:center}}
.topbar{{position:absolute;top:0;left:0;right:0;height:22px;background:linear-gradient(90deg,#F97316,#FB923C)}}
.badge{{margin-top:100px;background:linear-gradient(90deg,#F97316,#EA580C);color:#fff;font-size:36px;
font-weight:bold;letter-spacing:6px;padding:20px 48px;border-radius:999px;
box-shadow:0 16px 40px rgba(249,115,22,.35)}}
h1{{margin-top:44px;font-size:104px;font-weight:800;color:#1A1A2E;text-align:center;
line-height:1.05;letter-spacing:-2px;max-width:1700px}}
h1 span{{color:#F97316}}
.sub{{margin-top:26px;font-size:44px;color:#8B7E74}}
.kpis{{margin-top:64px;display:flex;gap:30px}}
.kpi{{border-radius:26px;padding:34px 52px;color:#fff;text-align:center}}
.kpi .v{{font-size:62px;font-weight:800}}
.kpi .l{{font-size:26px;opacity:.85;letter-spacing:2px;margin-top:6px}}
.mockup{{margin-top:64px;width:1560px;background:#fff;border-radius:36px;overflow:hidden;
box-shadow:0 60px 120px rgba(26,26,46,.22),0 20px 40px rgba(249,115,22,.12);transform:rotate(-1deg)}}
.mock-head{{background:#1A1A2E;padding:32px 48px;color:#fff;font-size:33px;font-weight:bold}}
table{{width:calc(100% - 96px);margin:30px 48px 42px;border-collapse:collapse;font-size:31px}}
td{{padding:22px 26px;border-bottom:2px solid #F4EDE6;color:#3A3530}}
tr:nth-child(even) td{{background:#FFFAF4}}
.pill{{display:inline-block;padding:8px 22px;border-radius:999px;font-size:23px;font-weight:bold}}
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
<div class="badge">🔥 TEMPLATE BUNDLE — SAVE 60%</div>
<h1>{esc(cfg['name'])} <span>Bundle</span></h1>
<div class="sub">{n} complete Google Sheets templates — one download</div>
<div class="kpis">
  <div class="kpi" style="background:linear-gradient(135deg,#F97316,#EA580C)">
    <div class="v">{n}</div><div class="l">TEMPLATES</div></div>
  <div class="kpi" style="background:linear-gradient(135deg,#22C55E,#16A34A)">
    <div class="v">€{value}+</div><div class="l">VALUE</div></div>
  <div class="kpi" style="background:linear-gradient(135deg,#1A1A2E,#343456)">
    <div class="v">∞</div><div class="l">LIFETIME</div></div>
</div>
<div class="mockup">
  <div class="mock-head">📦 What's inside this bundle</div>
  <table>{''.join(rows)}{more}</table>
</div>
<div class="footer">
  <div class="logo"><i></i><i></i><i></i><i></i><i></i><i></i></div>
  <span>Nasri<b>Tools</b></span>
  <small>nasritools.etsy.com&nbsp;&nbsp;•&nbsp;&nbsp;Instant Download</small>
</div>
</body></html>"""

STARTER_CFG = {
    "slug": "starter_budget_tracker",
    "name": "Budget Tracker",
    "listing_emoji": "💰",
    "description_intro": "Know exactly where every euro goes — automatically.",
    "tabs": [
        {"name": "Dashboard", "type": "dashboard",
         "kpis": [{"label": "This Month In"}, {"label": "This Month Out"}, {"label": "Savings Rate"}]},
        {"name": "Expenses", "type": "table", "emoji": "💳",
         "description": "Track every expense",
         "columns": [
             {"name": "Date",     "width": 14, "sample": "2026-07-01"},
             {"name": "Item",     "width": 22, "sample": "Groceries"},
             {"name": "Category", "width": 16, "dropdown": ["Housing", "Food", "Fun", "Bills"]},
             {"name": "Amount",   "width": 14, "sample": "65"},
         ]},
    ],
    "features": ["Auto-calculating", "Works on phone", "No subscription"],
}

async def main():
    from playwright.async_api import async_playwright
    exe = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=exe[0] if exe else None)
        page = await browser.new_page(viewport={"width": 2000, "height": 2000})

        async def shot(html_str, out_path):
            tmp = out_path.parent / "_h.html"
            tmp.write_text(html_str, encoding="utf-8")
            await page.goto(f"file://{tmp}")
            await page.wait_for_timeout(120)
            await page.screenshot(path=str(out_path), type="jpeg", quality=88)
            tmp.unlink()

        # bundles
        for key, cfg in BUNDLES.items():
            out = FIX / key / "hero.jpg"
            out.parent.mkdir(parents=True, exist_ok=True)
            await shot(bundle_html(cfg), out)
            print(f"  ✓ bundle hero: {key}")

        # premium managers
        for cfg in (FREELANCE_CFG, RESTAURANT_CFG):
            out = FIX / cfg["slug"] / "hero.jpg"
            out.parent.mkdir(parents=True, exist_ok=True)
            await shot(build_html(cfg), out)
            print(f"  ✓ premium hero: {cfg['slug']}")

        # starter/free budget design
        out = FIX / "free_budget" / "hero.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        await shot(build_html(STARTER_CFG), out)
        # refresh the starter listing hero too
        (OUTPUT / "starter_budget_tracker").mkdir(exist_ok=True)
        await shot(build_html(STARTER_CFG),
                   OUTPUT / "starter_budget_tracker" / "starter_budget_tracker_01_hero.jpg")
        print("  ✓ free/starter hero")

        await browser.close()
        print("\n  All fix heroes done.")

if __name__ == "__main__":
    asyncio.run(main())
