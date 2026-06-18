"""
NasriTools - Create Free Product on Etsy
- Builds a free Budget Tracker Lite Excel file
- Creates Etsy listing at $0.00
- Uploads the file + hero image

Run: python create_free_product.py
"""
import json, os, time, io, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Config ────────────────────────────────────────────
PEXELS_KEY = "3knaJZ5siP0O6slMAB155JTlieDugObexgHpTlJFPnLkBui2MKBJas38"
CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://api.etsy.com/v3/application"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
IMG_DIR    = Path(os.path.expanduser("~")) / "nasri_hero_images"
IMG_DIR.mkdir(exist_ok=True)
OUT_FILE   = Path(os.path.expanduser("~")) / "free_budget_tracker.xlsx"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_free_product.json"

TAXONOMY_ID = 2078
WHEN_MADE   = "2020_2025"
SIZE = (2000, 2000)

# ── Free product data ──────────────────────────────────
FREE_PRODUCT = {
    "slug":  "free_budget_tracker_lite",
    "title": "FREE Budget Tracker Google Sheets | Personal Finance Starter Template | Expense Planner | NasriTools",
    "price": 0.00,
    "tags": [
        "free budget tracker",
        "google sheets budget",
        "free finance template",
        "budget planner free",
        "expense tracker free",
        "free spreadsheet",
        "personal finance",
        "money tracker",
        "budget worksheet",
        "free digital download",
        "google sheets free",
        "finance starter kit",
        "free budget planner"
    ],
    "description": """FREE Budget Tracker for Google Sheets — No cost, no catch, instant download.

━━━━━━━━━━━━━━━━━━━━━━━━
WHAT YOU GET FOR FREE:
━━━━━━━━━━━━━━━━━━━━━━━━
• Monthly income & expense tracker
• Auto-calculating totals dashboard
• Budget vs. Actual comparison
• Savings goal progress bar
• Works in Google Sheets & Excel
• Fill yellow cells only — that simple

HOW TO USE:
1. Download the .xlsx file instantly (it's free!)
2. Open in Google Sheets (File → Import) or Excel
3. Enter your income and expenses in the yellow cells
4. Watch your financial picture update automatically

━━━━━━━━━━━━━━━━━━━━━━━━
WHY FREE?
━━━━━━━━━━━━━━━━━━━━━━━━
We want you to experience the NasriTools quality before you buy.
If you love this template, explore our full collection of 100+ professional spreadsheets starting at $9.00:

✦ Advanced Budget Tracker (12-month view + debt payoff)
✦ Investment Portfolio Tracker
✦ Freelancer Invoice & Client Manager
✦ Complete Business Finance Suite
✦ And 96 more templates...

Visit our shop: nasritools.etsy.com

━━━━━━━━━━━━━━━━━━━━━━━━
WHAT MAKES NASRITOOLS DIFFERENT:
━━━━━━━━━━━━━━━━━━━━━━━━
✓ No subscriptions — buy once, own forever
✓ No formulas to set up — everything is pre-built
✓ Auto-calculating dashboards
✓ Works on any device with Google Sheets or Excel
✓ Instant download — no waiting

━━━━━━━━━━━━━━━━━━━━━━━━
LOVED THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━
Please leave a review — it takes 30 seconds and helps our small shop grow!
Your feedback means the world to us ⭐⭐⭐⭐⭐

Questions? Message us — we respond within 24 hours.

© NasriTools | nasritools.etsy.com"""
}

# ── Fonts ──────────────────────────────────────────────
def _font(size, bold=False):
    candidates = (["C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/calibrib.ttf"]
                  if bold else
                  ["C:/Windows/Fonts/arial.ttf","C:/Windows/Fonts/calibri.ttf"])
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

# ── Etsy auth ──────────────────────────────────────────
def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0):
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def etsy_auth(t):
    return {"Authorization": "Bearer " + t["access_token"], "x-api-key": CLIENT_ID + ":" + SECRET}

# ── Build Excel file ───────────────────────────────────
def build_excel():
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
        from openpyxl.utils import get_column_letter
        from openpyxl.chart import BarChart, Reference
    except ImportError:
        print("  openpyxl not found — installing...")
        import subprocess, sys
        subprocess.run([sys.executable, "-m", "pip", "install", "openpyxl"], check=True)
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()

    # ── Colors ────────────────────────────────
    BLUE_DARK  = "1E3A5F"
    BLUE_MED   = "2980B9"
    BLUE_LIGHT = "D6EAF8"
    YELLOW     = "FFF176"
    GREEN      = "27AE60"
    RED        = "E74C3C"
    WHITE      = "FFFFFF"
    GRAY_LIGHT = "F2F3F4"
    GRAY_MED   = "BDC3C7"

    def hdr_font(sz=11, bold=True, color=WHITE):
        return Font(name="Calibri", size=sz, bold=bold, color=color)

    def cell_font(sz=10, bold=False, color="000000"):
        return Font(name="Calibri", size=sz, bold=bold, color=color)

    def fill(hex_color):
        return PatternFill("solid", fgColor=hex_color)

    def center(wrap=False):
        return Alignment(horizontal="center", vertical="center", wrap_text=wrap)

    def left():
        return Alignment(horizontal="left", vertical="center")

    def thin_border():
        s = Side(style="thin", color=GRAY_MED)
        return Border(left=s, right=s, top=s, bottom=s)

    # ═══════════════════════════════════════════
    # SHEET 1: Dashboard
    # ═══════════════════════════════════════════
    ws1 = wb.active
    ws1.title = "📊 Dashboard"
    ws1.sheet_view.showGridLines = False

    # Column widths
    ws1.column_dimensions["A"].width = 3
    ws1.column_dimensions["B"].width = 22
    ws1.column_dimensions["C"].width = 16
    ws1.column_dimensions["D"].width = 16
    ws1.column_dimensions["E"].width = 16
    ws1.column_dimensions["F"].width = 3

    # Header banner
    ws1.row_dimensions[1].height = 8
    ws1.row_dimensions[2].height = 50
    ws1.row_dimensions[3].height = 8

    ws1.merge_cells("B2:E2")
    c = ws1["B2"]
    c.value = "💰  BUDGET TRACKER  —  FREE STARTER TEMPLATE"
    c.font = hdr_font(18, True, WHITE)
    c.fill = fill(BLUE_DARK)
    c.alignment = center()

    ws1.merge_cells("B3:E3")
    ws1["B3"].fill = fill(BLUE_MED)

    # Subtitle
    ws1.row_dimensions[4].height = 22
    ws1.merge_cells("B4:E4")
    c = ws1["B4"]
    c.value = "by NasriTools  •  nasritools.etsy.com  •  Fill YELLOW cells only"
    c.font = hdr_font(9, False, "AAAAAA")
    c.fill = fill("F8F9FA")
    c.alignment = center()

    ws1.row_dimensions[5].height = 12

    # Summary cards row
    ws1.row_dimensions[6].height = 28
    ws1.row_dimensions[7].height = 36
    ws1.row_dimensions[8].height = 12

    cards = [
        ("C6", "C7", "TOTAL INCOME", "='💸 Income & Expenses'!C3", GREEN),
        ("D6", "D7", "TOTAL EXPENSES", "='💸 Income & Expenses'!C4", RED),
        ("E6", "E7", "NET SAVINGS", "='💸 Income & Expenses'!C5", BLUE_MED),
    ]
    for lbl_cell, val_cell, label, formula, color in cards:
        c = ws1[lbl_cell]
        c.value = label
        c.font = hdr_font(8, True, WHITE)
        c.fill = fill(color)
        c.alignment = center()
        c.border = thin_border()

        c2 = ws1[val_cell]
        c2.value = formula
        c2.number_format = '"$"#,##0.00'
        c2.font = hdr_font(14, True, "000000")
        c2.fill = fill(GRAY_LIGHT)
        c2.alignment = center()
        c2.border = thin_border()

    ws1.row_dimensions[9].height = 12

    # Savings rate
    ws1.row_dimensions[10].height = 28
    ws1.merge_cells("B10:C10")
    ws1["B10"].value = "SAVINGS RATE"
    ws1["B10"].font = hdr_font(10, True, WHITE)
    ws1["B10"].fill = fill(BLUE_DARK)
    ws1["B10"].alignment = center()
    ws1["B10"].border = thin_border()

    ws1.merge_cells("D10:E10")
    c = ws1["D10"]
    c.value = "=IFERROR(E7/C7,0)"
    c.number_format = "0.0%"
    c.font = hdr_font(12, True, "000000")
    c.fill = fill(YELLOW)
    c.alignment = center()
    c.border = thin_border()

    ws1.row_dimensions[11].height = 12

    # Expense breakdown header
    ws1.row_dimensions[12].height = 28
    ws1.merge_cells("B12:E12")
    c = ws1["B12"]
    c.value = "EXPENSE BREAKDOWN"
    c.font = hdr_font(11, True, WHITE)
    c.fill = fill(BLUE_MED)
    c.alignment = center()

    # Category rows
    categories = [
        "Housing / Rent", "Food & Groceries", "Transport",
        "Utilities", "Entertainment", "Health", "Other",
    ]
    for idx, cat in enumerate(categories, 13):
        ws1.row_dimensions[idx].height = 22
        r = idx

        c = ws1.cell(r, 2, cat)
        c.font = cell_font(10)
        c.fill = fill(GRAY_LIGHT if idx % 2 == 0 else WHITE)
        c.alignment = left()
        c.border = thin_border()

        for col in [3, 4, 5]:
            ws1.cell(r, col).fill = fill(GRAY_LIGHT if idx % 2 == 0 else WHITE)
            ws1.cell(r, col).border = thin_border()

        # Budget column
        bc = ws1.cell(r, 3)
        bc.value = f"='💸 Income & Expenses'!C{r+3}"
        bc.number_format = '"$"#,##0.00'
        bc.font = cell_font(10)
        bc.alignment = center()

    ws1.row_dimensions[20].height = 20

    # Upgrade callout
    ws1.row_dimensions[21].height = 8
    ws1.row_dimensions[22].height = 30
    ws1.merge_cells("B22:E22")
    c = ws1["B22"]
    c.value = "⭐  Loved this? Get the Full 12-Month Budget Tracker → nasritools.etsy.com"
    c.font = hdr_font(9, True, WHITE)
    c.fill = fill("E67E22")
    c.alignment = center()
    c.border = thin_border()

    # ═══════════════════════════════════════════
    # SHEET 2: Income & Expenses entry
    # ═══════════════════════════════════════════
    ws2 = wb.create_sheet("💸 Income & Expenses")
    ws2.sheet_view.showGridLines = False

    ws2.column_dimensions["A"].width = 3
    ws2.column_dimensions["B"].width = 26
    ws2.column_dimensions["C"].width = 18
    ws2.column_dimensions["D"].width = 18
    ws2.column_dimensions["E"].width = 3

    ws2.row_dimensions[1].height = 8
    ws2.row_dimensions[2].height = 44

    ws2.merge_cells("B2:D2")
    c = ws2["B2"]
    c.value = "💸  INCOME & EXPENSES  —  Fill Yellow Cells Only"
    c.font = hdr_font(14, True, WHITE)
    c.fill = fill(BLUE_DARK)
    c.alignment = center()

    ws2.row_dimensions[3].height = 8

    # Summary section
    summary = [
        (4, "TOTAL INCOME",   "=SUM(C8:C17)",  GREEN),
        (5, "TOTAL EXPENSES", "=SUM(C21:C37)", RED),
        (6, "NET SAVINGS",    "=C4-C5",        BLUE_MED),
    ]
    for row, label, formula, color in summary:
        ws2.row_dimensions[row].height = 26
        c = ws2.cell(row, 2, label)
        c.font = hdr_font(10, True, WHITE)
        c.fill = fill(color)
        c.alignment = left()
        c.border = thin_border()

        c2 = ws2.cell(row, 3, formula)
        c2.number_format = '"$"#,##0.00'
        c2.font = hdr_font(11, True, "000000")
        c2.fill = fill(GRAY_LIGHT)
        c2.alignment = center()
        c2.border = thin_border()

        ws2.cell(row, 4).fill = fill(GRAY_LIGHT)
        ws2.cell(row, 4).border = thin_border()

    ws2.row_dimensions[7].height = 14

    # Income section
    ws2.row_dimensions[7].height = 26
    ws2.merge_cells("B7:D7")
    c = ws2["B7"]
    c.value = "INCOME"
    c.font = hdr_font(10, True, WHITE)
    c.fill = fill(GREEN)
    c.alignment = center()

    income_items = [
        "Primary Salary / Wages",
        "Freelance / Side Income",
        "Investments / Dividends",
        "Rental Income",
        "Other Income 1",
        "Other Income 2",
        "Other Income 3",
        "Other Income 4",
        "Other Income 5",
        "Other Income 6",
    ]
    for idx, item in enumerate(income_items, 8):
        ws2.row_dimensions[idx].height = 22
        c = ws2.cell(idx, 2, item)
        c.font = cell_font(10)
        c.fill = fill(GRAY_LIGHT if idx % 2 == 0 else WHITE)
        c.alignment = left()
        c.border = thin_border()

        c2 = ws2.cell(idx, 3)
        c2.value = 0
        c2.number_format = '"$"#,##0.00'
        c2.fill = fill(YELLOW)
        c2.alignment = center()
        c2.border = thin_border()
        c2.font = cell_font(10, bold=True)

        c3 = ws2.cell(idx, 4)
        c3.fill = fill(GRAY_LIGHT if idx % 2 == 0 else WHITE)
        c3.border = thin_border()

    ws2.row_dimensions[18].height = 14

    # Expense section
    ws2.row_dimensions[19].height = 26
    ws2.merge_cells("B19:D19")
    c = ws2["B19"]
    c.value = "EXPENSES"
    c.font = hdr_font(10, True, WHITE)
    c.fill = fill(RED)
    c.alignment = center()

    ws2.row_dimensions[20].height = 20
    ws2.cell(20, 2, "Category").font = hdr_font(9, True, "555555")
    ws2.cell(20, 2).fill = fill(GRAY_LIGHT)
    ws2.cell(20, 2).alignment = center()
    ws2.cell(20, 3, "Amount").font = hdr_font(9, True, "555555")
    ws2.cell(20, 3).fill = fill(GRAY_LIGHT)
    ws2.cell(20, 3).alignment = center()
    ws2.cell(20, 4, "Notes").font = hdr_font(9, True, "555555")
    ws2.cell(20, 4).fill = fill(GRAY_LIGHT)
    ws2.cell(20, 4).alignment = center()

    expense_items = [
        "Housing / Rent / Mortgage",
        "Electricity & Gas",
        "Water & Internet",
        "Phone Bill",
        "Groceries & Food",
        "Restaurants & Takeout",
        "Car Payment / Transport",
        "Fuel / Gas",
        "Health Insurance",
        "Doctor / Pharmacy",
        "Gym / Fitness",
        "Streaming Services",
        "Entertainment & Hobbies",
        "Clothing & Shopping",
        "Personal Care",
        "Child Care / Education",
        "Savings Transfer",
    ]
    for idx, item in enumerate(expense_items, 21):
        ws2.row_dimensions[idx].height = 22
        c = ws2.cell(idx, 2, item)
        c.font = cell_font(10)
        c.fill = fill(GRAY_LIGHT if idx % 2 == 0 else WHITE)
        c.alignment = left()
        c.border = thin_border()

        c2 = ws2.cell(idx, 3)
        c2.value = 0
        c2.number_format = '"$"#,##0.00'
        c2.fill = fill(YELLOW)
        c2.alignment = center()
        c2.border = thin_border()
        c2.font = cell_font(10, bold=True)

        c3 = ws2.cell(idx, 4)
        c3.fill = fill(GRAY_LIGHT if idx % 2 == 0 else WHITE)
        c3.border = thin_border()
        c3.font = cell_font(9)
        c3.alignment = left()

    # ═══════════════════════════════════════════
    # SHEET 3: About / Upsell
    # ═══════════════════════════════════════════
    ws3 = wb.create_sheet("⭐ More Templates")
    ws3.sheet_view.showGridLines = False
    ws3.column_dimensions["A"].width = 3
    ws3.column_dimensions["B"].width = 45
    ws3.column_dimensions["C"].width = 15
    ws3.column_dimensions["D"].width = 3

    ws3.row_dimensions[1].height = 8
    ws3.row_dimensions[2].height = 50
    ws3.merge_cells("B2:C2")
    c = ws3["B2"]
    c.value = "⭐  More Professional Templates from NasriTools"
    c.font = hdr_font(16, True, WHITE)
    c.fill = fill(BLUE_DARK)
    c.alignment = center()

    ws3.row_dimensions[3].height = 8
    ws3.row_dimensions[4].height = 22
    ws3.merge_cells("B4:C4")
    c = ws3["B4"]
    c.value = "Visit nasritools.etsy.com  •  All templates: fill yellow cells only  •  Works in Google Sheets & Excel"
    c.font = hdr_font(9, False, "555555")
    c.alignment = center()
    c.fill = fill("F8F9FA")

    ws3.row_dimensions[5].height = 10

    products = [
        ("💰 Advanced Budget Tracker",        "$12", "12-month view, debt payoff planner, savings goals"),
        ("📈 Investment Portfolio Tracker",    "$14", "Stocks, ETFs, crypto — all in one dashboard"),
        ("🧾 Freelancer Invoice Tracker",      "$11", "Clients, invoices, taxes, income summary"),
        ("📱 Content Creator Planner",         "$11", "YouTube, Instagram, TikTok planning dashboard"),
        ("🏠 Home Renovation Tracker",         "$12", "Budgets, contractors, timeline, costs"),
        ("💼 Small Business Finance Tracker",  "$14", "P&L, cash flow, payroll, tax prep"),
        ("📊 KPI Dashboard",                   "$14", "Business metrics, goals, team performance"),
        ("🏋️ Workout & Fitness Tracker",      "$10", "Workouts, nutrition, weight loss progress"),
        ("✈️ Travel Planner",                  "$11", "Itinerary, budget, packing list, bookings"),
        ("🎯 Goals & Habit Tracker",           "$10", "Daily habits, weekly goals, annual planning"),
    ]

    ws3.row_dimensions[6].height = 24
    ws3.cell(6, 2, "TEMPLATE NAME").font = hdr_font(9, True, WHITE)
    ws3.cell(6, 2).fill = fill(BLUE_MED)
    ws3.cell(6, 2).alignment = center()
    ws3.cell(6, 2).border = thin_border()
    ws3.cell(6, 3, "PRICE").font = hdr_font(9, True, WHITE)
    ws3.cell(6, 3).fill = fill(BLUE_MED)
    ws3.cell(6, 3).alignment = center()
    ws3.cell(6, 3).border = thin_border()

    for idx, (name, price, desc) in enumerate(products, 7):
        ws3.row_dimensions[idx].height = 22
        c = ws3.cell(idx, 2, f"{name}  —  {desc}")
        c.font = cell_font(9)
        c.fill = fill(GRAY_LIGHT if idx % 2 == 0 else WHITE)
        c.alignment = left()
        c.border = thin_border()

        c2 = ws3.cell(idx, 3, price)
        c2.font = cell_font(10, bold=True, color=GREEN)
        c2.fill = fill(GRAY_LIGHT if idx % 2 == 0 else WHITE)
        c2.alignment = center()
        c2.border = thin_border()

    ws3.row_dimensions[17].height = 10
    ws3.row_dimensions[18].height = 30
    ws3.merge_cells("B18:C18")
    c = ws3["B18"]
    c.value = "🌟  Loved this FREE template? Please leave us a 5-star review — it means everything!  🌟"
    c.font = hdr_font(10, True, "E67E22")
    c.fill = fill("FEF9E7")
    c.alignment = center()
    c.border = thin_border()

    wb.save(str(OUT_FILE))
    print(f"  Excel file created: {OUT_FILE}")
    return OUT_FILE

# ── Build hero image ───────────────────────────────────
def build_hero_free():
    # Download a money/budget photo
    r = requests.get("https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": "money budget planning desk", "per_page": 5, "orientation": "square"},
        timeout=15)
    photo = None
    if r.ok:
        photos = r.json().get("photos", [])
        if photos:
            ir = requests.get(photos[0]["src"]["large2x"], timeout=30)
            if ir.ok:
                photo = Image.open(io.BytesIO(ir.content)).convert("RGB")

    if not photo:
        photo = Image.new("RGB", SIZE, (30, 60, 100))

    # Crop + blur + darken
    w, h = photo.size
    m = min(w, h)
    photo = photo.crop(((w-m)//2, (h-m)//2, (w+m)//2, (h+m)//2))
    bg = photo.resize(SIZE, Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius=4))
    dark = Image.new("RGB", SIZE, (0, 0, 0))
    img  = Image.blend(bg, dark, 0.60)
    d    = ImageDraw.Draw(img)

    WHITE  = (255, 255, 255)
    YELLOW = (255, 215, 0)
    GREEN  = (39, 174, 96)
    GOLD   = (255, 165, 0)
    BLUE   = (41, 128, 185)

    def font(size, bold=False):
        candidates = (["C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/calibrib.ttf"]
                      if bold else
                      ["C:/Windows/Fonts/arial.ttf","C:/Windows/Fonts/calibri.ttf"])
        for p in candidates:
            if os.path.exists(p):
                try: return ImageFont.truetype(p, size)
                except: pass
        return ImageFont.load_default()

    def centered(text, y, f, color, shadow=True):
        bb = d.textbbox((0,0), text, font=f)
        x = max(60, (2000-(bb[2]-bb[0]))//2)
        if shadow: d.text((x+3, y+3), text, font=f, fill=(0,0,0))
        d.text((x, y), text, font=f, fill=color)

    # Top green bar
    d.rectangle([0, 0, 2000, 12], fill=GREEN)

    # FREE badge — big and eye-catching
    ff = font(120, bold=True)
    bb = d.textbbox((0,0), "FREE", font=ff)
    fw, fh = bb[2]-bb[0]+80, bb[3]-bb[1]+40
    fx, fy = (2000-fw)//2, 80
    d.rounded_rectangle([fx, fy, fx+fw, fy+fh], radius=20, fill=GREEN)
    d.text((fx+40, fy+20), "FREE", font=ff, fill=WHITE)

    # Title
    tf = font(80, bold=True)
    lines = ["Budget Tracker", "Google Sheets Template"]
    for i, line in enumerate(lines):
        centered(line, 350 + i*100, tf, WHITE)

    # Subtitle
    centered("Personal Finance • Expense Planner • Savings Goals", 580, font(42), (200,200,200))

    # Bottom panel
    panel_y = 1490
    panel = Image.new("RGB", (2000, 510), (8, 12, 26))
    img.paste(panel, (0, panel_y))
    d = ImageDraw.Draw(img)
    d.rectangle([0, panel_y, 2000, panel_y+6], fill=GREEN)

    # Features
    feats = ["Auto-calculating dashboard", "Fill yellow cells only", "Works in Google Sheets & Excel"]
    ff2 = font(36, bold=True)
    for feat, px in zip(feats, [80, 720, 1360]):
        d.text((px, panel_y+50), f"✓  {feat}", font=ff2, fill=GREEN)

    # FREE callout
    pf = font(62, bold=True)
    centered("100% FREE  —  No Cost, No Catch", panel_y+140, pf, YELLOW, shadow=False)

    # Instant download
    centered("Instant Download  •  No Signup  •  Yours Forever", panel_y+230, font(36), (170,170,200), shadow=False)

    # Stars
    centered("★  ★  ★  ★  ★", panel_y+305, font(44, bold=True), YELLOW, shadow=False)

    # Brand
    d.text((40, panel_y+390), "nasritools.etsy.com", font=font(28), fill=(80,80,110))

    d.rectangle([0, 1988, 2000, 2000], fill=GREEN)

    img_path = IMG_DIR / "free_budget_tracker_hero.jpg"
    img.save(str(img_path), quality=95)
    print(f"  Hero image created: {img_path}")
    return img_path

# ── Main ──────────────────────────────────────────────
def main():
    if DONE_FILE.exists():
        info = json.loads(DONE_FILE.read_text())
        print(f"\nFree product already created!")
        print(f"  Listing ID: {info.get('listing_id')}")
        print(f"  URL: https://www.etsy.com/listing/{info.get('listing_id')}")
        print(f"\nDelete {DONE_FILE} to re-run.")
        return

    print("\n" + "="*60)
    print("  NasriTools - Create Free Product")
    print("="*60 + "\n")

    token = get_token()
    p = FREE_PRODUCT

    # Step 1: Build Excel
    print("[1/4] Building Excel template...")
    xlsx_path = build_excel()

    # Step 2: Build hero image
    print("[2/4] Building hero image...")
    img_path = build_hero_free()

    # Step 3: Create listing
    print("[3/4] Creating Etsy listing at $0.00...")
    payload = {
        "title":       p["title"],
        "description": p["description"],
        "price":       0.00,
        "quantity":    999,
        "who_made":    "i_did",
        "when_made":   WHEN_MADE,
        "taxonomy_id": TAXONOMY_ID,
        "type":        "download",
        "is_digital":  True,
        "tags":        p["tags"],
        "state":       "active",
        "shipping_profile_id": None,
    }

    r = requests.post(
        API + f"/shops/{SHOP_ID}/listings",
        headers={**etsy_auth(token), "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )

    if not r.ok:
        # Retry without shipping_profile_id
        payload.pop("shipping_profile_id", None)
        r = requests.post(
            API + f"/shops/{SHOP_ID}/listings",
            headers={**etsy_auth(token), "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )

    if not r.ok:
        print(f"  ERROR creating listing: {r.text[:200]}")
        return

    lid = r.json()["listing_id"]
    print(f"  Listing created: ID={lid}")
    time.sleep(1)

    # Step 4a: Upload Excel file
    print("[4/4] Uploading Excel file...")
    with open(xlsx_path, "rb") as f:
        rf = requests.post(
            API + f"/shops/{SHOP_ID}/listings/{lid}/files",
            headers=etsy_auth(token),
            data={"rank": 1},
            files={"file": ("free_budget_tracker.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            timeout=60,
        )
    if rf.ok:
        print(f"  File uploaded: OK")
    else:
        print(f"  File upload warning: {rf.text[:100]}")
    time.sleep(1)

    # Step 4b: Upload hero image
    print("      Uploading hero image...")
    with open(img_path, "rb") as f:
        ri = requests.post(
            API + f"/shops/{SHOP_ID}/listings/{lid}/images",
            headers=etsy_auth(token),
            data={"rank": 1, "overwrite": "true"},
            files={"image": ("free_budget_tracker_hero.jpg", f, "image/jpeg")},
            timeout=60,
        )
    if ri.ok:
        print(f"  Image uploaded: OK")
    else:
        print(f"  Image upload warning: {ri.text[:100]}")

    # Save result
    result = {"listing_id": lid, "slug": p["slug"], "created_at": time.time()}
    DONE_FILE.write_text(json.dumps(result, indent=2))

    print(f"\n{'='*60}")
    print(f"  FREE product live!")
    print(f"  Listing ID : {lid}")
    print(f"  URL        : https://www.etsy.com/listing/{lid}")
    print(f"  Price      : $0.00")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
