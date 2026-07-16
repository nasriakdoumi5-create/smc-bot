"""
build_remaining.py  (runs on server)
Builds everything for the 12 unmatched listings:
  • 8 bundle ZIPs (real v2 templates grouped by theme + README)
  • 2 custom premium workbooks (Freelance Business Manager, Restaurant Cafe Manager)
  • hero images for all of them
Output: output/_fix/<key>/...
"""
import sys, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from nasritools.factory2 import build_workbook, OUTPUT_DIR

FIX = OUTPUT_DIR / "_fix"
FIX.mkdir(exist_ok=True)

# ── bundle definitions: listing_id → contents ──────────────────────────
BUNDLES = {
    "complete_life_system": {
        "listing_id": 4524724846,
        "name": "Complete Life System",
        "zipname": "NasriTools_Complete_Life_System_10_Templates.zip",
        "includes": ["budget_tracker", "meal_planner", "workout_tracker",
                     "habit_tracker", "weekly_planner", "goals_planner",
                     "travel_planner", "student_planner", "debt_payoff_planner",
                     "annual_review_planner"],
    },
    "finance_os": {
        "listing_id": 4525136892,
        "name": "Complete Finance OS",
        "zipname": "NasriTools_Complete_Finance_OS.zip",
        "includes": ["budget_tracker", "freelancer_invoice_tracker",
                     "debt_payoff_planner", "emergency_fund_tracker",
                     "grocery_budget_tracker"],
    },
    "health_os": {
        "listing_id": 4525136928,
        "name": "Complete Health OS",
        "zipname": "NasriTools_Complete_Health_OS.zip",
        "includes": ["workout_tracker", "meal_planner", "habit_tracker",
                     "sleep_tracker", "weight_loss_tracker"],
    },
    "business_bundle": {
        "listing_id": 4524724798,
        "name": "Business Bundle",
        "zipname": "NasriTools_Business_Bundle.zip",
        "includes": ["kpi_dashboard", "inventory_management",
                     "freelancer_invoice_tracker", "lead_tracker",
                     "social_media_analytics"],
    },
    "planner_bundle": {
        "listing_id": 4524724758,
        "name": "Productivity Planner Bundle",
        "zipname": "NasriTools_Productivity_Planner_Bundle.zip",
        "includes": ["weekly_planner", "goals_planner", "habit_tracker",
                     "annual_review_planner", "student_planner"],
    },
    "health_bundle": {
        "listing_id": 4524724720,
        "name": "Health & Meal Bundle",
        "zipname": "NasriTools_Health_Meal_Bundle.zip",
        "includes": ["meal_planner", "keto_diet_tracker", "workout_tracker",
                     "weight_loss_tracker", "sleep_tracker"],
    },
    "ultimate_bundle": {
        "listing_id": 4524283886,
        "name": "Ultimate Bundle — 10 Templates",
        "zipname": "NasriTools_Ultimate_Bundle_10_Templates.zip",
        "includes": ["budget_tracker", "freelancer_invoice_tracker",
                     "kpi_dashboard", "meal_planner", "workout_tracker",
                     "habit_tracker", "weekly_planner", "project_management",
                     "inventory_management", "content_creator_planner"],
    },
}

# free budget listings → deliver starter v2 file under their original names
FREE_LISTINGS = {
    4523968643: "free_budget_tracker.xlsx",
    4524681057: "NasriTools_Budget_Tracker_FREE.xlsx",
    4526750401: "Budget_Tracker_FREE_NasriTools.xlsx",
}

# ── custom premium workbooks ────────────────────────────────────────────
FREELANCE_CFG = {
    "slug": "Freelance_Business_Manager",
    "name": "Freelance Business Manager",
    "subtitle": "Invoices, Clients, Expenses & Profit — one system",
    "listing_emoji": "🧾",
    "description_intro": "Run your entire freelance business from one sheet: send invoices on time, know who owes you, and see your real profit.",
    "accent_color": "F97316", "dark_color": "1A1A2E", "green_color": "22C55E",
    "tabs": [
        {"name": "Dashboard", "emoji": "📊", "type": "dashboard",
         "description": "Billed, paid, pending and profit — live.",
         "kpis": [
             {"label": "Total Billed",  "formula": "=SUM(Invoices!F:F)"},
             {"label": "Paid",          "formula": '=SUMIF(Invoices!G:G,"Paid",Invoices!F:F)'},
             {"label": "Pending",       "formula": '=SUMIF(Invoices!G:G,"Sent",Invoices!F:F)+SUMIF(Invoices!G:G,"Overdue",Invoices!F:F)'},
             {"label": "Profit",        "formula": "=SUM(Invoices!F:F)-SUM(Expenses!D:D)"},
         ]},
        {"name": "Invoices", "emoji": "🧾", "type": "table",
         "description": "Every invoice with status — nothing slips through.",
         "columns": [
             {"name": "Invoice #", "width": 12, "sample": "INV-001"},
             {"name": "Client",    "width": 20, "sample": "Acme Studio"},
             {"name": "Project",   "width": 24, "sample": "Logo design"},
             {"name": "Issue Date","width": 14, "sample": "2026-06-01"},
             {"name": "Due Date",  "width": 14, "sample": "2026-06-15"},
             {"name": "Amount",    "width": 14, "sample": "850"},
             {"name": "Status",    "width": 13, "dropdown": ["Draft", "Sent", "Paid", "Overdue", "Cancelled"]},
         ]},
        {"name": "Clients", "emoji": "👥", "type": "table",
         "description": "Your client base with contact info and status.",
         "columns": [
             {"name": "Client Name", "width": 22, "sample": "Acme Studio"},
             {"name": "Contact",     "width": 20, "sample": "John Doe"},
             {"name": "Email",       "width": 24, "sample": "john@acme.com"},
             {"name": "Rate/hr",     "width": 12, "sample": "45"},
             {"name": "Status",      "width": 13, "dropdown": ["Lead", "Active", "VIP", "Inactive"]},
         ]},
        {"name": "Expenses", "emoji": "💳", "type": "table",
         "description": "Business expenses — software, gear, subscriptions.",
         "columns": [
             {"name": "Date",     "width": 14, "sample": "2026-06-03"},
             {"name": "Item",     "width": 24, "sample": "Adobe subscription"},
             {"name": "Category", "width": 16, "dropdown": ["Software", "Hardware", "Marketing", "Office", "Travel", "Other"]},
             {"name": "Amount",   "width": 14, "sample": "25"},
             {"name": "Notes",    "width": 24, "sample": "Monthly"},
         ]},
        {"name": "Income Report", "emoji": "📈", "type": "reports",
         "sections": [
            {"title": "Business Summary", "items": [
                {"label": "Total Revenue",  "formula": "=SUM(Invoices!F:F)"},
                {"label": "Total Expenses", "formula": "=SUM(Expenses!D:D)"},
                {"label": "Net Profit",     "formula": "=SUM(Invoices!F:F)-SUM(Expenses!D:D)"},
                {"label": "Active Clients", "formula": '=COUNTIF(Clients!E:E,"Active")+COUNTIF(Clients!E:E,"VIP")'},
            ]},
         ]},
    ],
    "features": ["Auto-calculating dashboard", "Invoice status tracking",
                 "Works on phone, tablet & desktop", "No subscription — yours forever"],
}

RESTAURANT_CFG = {
    "slug": "Restaurant_Cafe_Manager",
    "name": "Restaurant & Cafe Manager",
    "subtitle": "Sales, Inventory & Costs — your whole operation",
    "listing_emoji": "🍽️",
    "description_intro": "Know your daily revenue, what's low in stock, and your real margins — without expensive POS reports.",
    "accent_color": "F97316", "dark_color": "1A1A2E", "green_color": "22C55E",
    "tabs": [
        {"name": "Dashboard", "emoji": "📊", "type": "dashboard",
         "description": "Revenue, costs, profit and low-stock alerts.",
         "kpis": [
             {"label": "Revenue",   "formula": "=SUM(Sales!E:E)"},
             {"label": "Expenses",  "formula": "=SUM(Expenses!D:D)"},
             {"label": "Profit",    "formula": "=SUM(Sales!E:E)-SUM(Expenses!D:D)"},
             {"label": "Low Stock", "formula": "=SUMPRODUCT((Inventory!C2:C500<Inventory!D2:D500)*(Inventory!A2:A500<>\"\")*1)"},
         ]},
        {"name": "Sales", "emoji": "💶", "type": "table",
         "description": "Daily sales log by item and category.",
         "columns": [
             {"name": "Date",     "width": 14, "sample": "2026-06-01"},
             {"name": "Item",     "width": 22, "sample": "Cappuccino"},
             {"name": "Category", "width": 14, "dropdown": ["Food", "Drinks", "Dessert", "Other"]},
             {"name": "Qty",      "width": 10, "sample": "12"},
             {"name": "Amount",   "width": 14, "sample": "42"},
         ]},
        {"name": "Inventory", "emoji": "📦", "type": "table",
         "description": "Stock levels with reorder alerts.",
         "columns": [
             {"name": "Item",          "width": 22, "sample": "Coffee beans 1kg"},
             {"name": "Unit",          "width": 10, "sample": "kg"},
             {"name": "In Stock",      "width": 12, "sample": "8"},
             {"name": "Reorder Level", "width": 14, "sample": "5"},
             {"name": "Supplier",      "width": 20, "sample": "BeanCo"},
             {"name": "Unit Cost",     "width": 12, "sample": "14"},
         ]},
        {"name": "Expenses", "emoji": "💳", "type": "table",
         "description": "Every cost: ingredients, staff, rent, utilities.",
         "columns": [
             {"name": "Date",     "width": 14, "sample": "2026-06-02"},
             {"name": "Item",     "width": 24, "sample": "Vegetable order"},
             {"name": "Category", "width": 16, "dropdown": ["Ingredients", "Staff", "Rent", "Utilities", "Equipment", "Other"]},
             {"name": "Amount",   "width": 14, "sample": "180"},
             {"name": "Notes",    "width": 22, "sample": "Weekly"},
         ]},
        {"name": "Monthly Report", "emoji": "📈", "type": "reports",
         "sections": [
            {"title": "Performance", "items": [
                {"label": "Total Revenue",   "formula": "=SUM(Sales!E:E)"},
                {"label": "Total Costs",     "formula": "=SUM(Expenses!D:D)"},
                {"label": "Net Profit",      "formula": "=SUM(Sales!E:E)-SUM(Expenses!D:D)"},
                {"label": "Food Sales",      "formula": '=SUMIF(Sales!C:C,"Food",Sales!E:E)'},
                {"label": "Drink Sales",     "formula": '=SUMIF(Sales!C:C,"Drinks",Sales!E:E)'},
            ]},
         ]},
    ],
    "features": ["Low-stock alerts built in", "Auto profit calculation",
                 "Works on phone, tablet & desktop", "No subscription — yours forever"],
}

README_TMPL = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {name} — NasriTools
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for your purchase! 🧡

WHAT'S IN THIS BUNDLE
{filelist}

HOW TO USE (2 minutes)
1. Unzip this folder
2. Go to sheets.google.com → blank spreadsheet
3. File → Import → Upload → pick a template
4. Choose "Replace spreadsheet" → done!
   (Or open directly in Excel — both work.)

Each template has a START HERE tab with instructions.

TIP: Delete the sample rows once you see how it works.

Need help? Message NasriTools on Etsy — I reply fast.
If you love the templates, a 5-star review means the world
to a small shop like mine. Thank you!

— Nasri
nasritools.etsy.com • Buy once, own forever
"""

def build_zip(key, cfg):
    folder = FIX / key
    folder.mkdir(exist_ok=True)
    zpath = folder / cfg["zipname"]
    names = []
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for slug in cfg["includes"]:
            src = OUTPUT_DIR / slug / f"{slug}.xlsx"
            if not src.exists():
                print(f"    ⚠ missing {slug}")
                continue
            pretty = slug.replace("_", " ").title().replace(" ", "_") + ".xlsx"
            z.write(src, pretty)
            names.append(pretty)
        filelist = "\n".join(f"  • {n}" for n in names)
        z.writestr("README_START_HERE.txt",
                   README_TMPL.format(name=cfg["name"], filelist=filelist))
    return zpath, len(names)

def main():
    print("=" * 60)
    print("  Building fix assets for 12 remaining listings")
    print("=" * 60)

    # 1. bundle zips
    print("\n  [1/2] Bundle ZIPs:")
    for key, cfg in BUNDLES.items():
        zpath, n = build_zip(key, cfg)
        print(f"    ✓ {cfg['zipname']}  ({n} templates, {zpath.stat().st_size//1024}KB)")

    # 2. custom premium workbooks
    print("\n  [2/2] Premium workbooks:")
    for cfg in (FREELANCE_CFG, RESTAURANT_CFG):
        out = build_workbook(cfg)
        print(f"    ✓ {out.name}  ({out.stat().st_size:,} bytes)")

    print("\n  Done. Next: python3 generate_fix_heroes.py")

if __name__ == "__main__":
    main()
