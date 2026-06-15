"""
Freelance Business Manager — 5 Etsy Product Images (2000x2000 px)
"""
from PIL import Image, ImageDraw, ImageFont
import os

FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO   = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

C_DARK   = (13, 27, 42)
C_NAV    = (27, 42, 74)
C_ACCENT = (67, 97, 238)
C_GREEN  = (6, 214, 160)
C_RED    = (239, 35, 60)
C_YELLOW = (255, 209, 102)
C_LIGHT  = (248, 249, 250)
C_GRAY   = (173, 181, 189)
C_WHITE  = (255, 255, 255)
C_PURPLE = (114, 9, 183)

def fnt(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

def new_img():
    return Image.new("RGB", (2000, 2000), C_DARK)

def gradient_bg(img, top_color, bot_color):
    d = ImageDraw.Draw(img)
    W, H = img.size
    for y in range(H):
        r = int(top_color[0] + (bot_color[0]-top_color[0]) * y/H)
        g = int(top_color[1] + (bot_color[1]-top_color[1]) * y/H)
        b = int(top_color[2] + (bot_color[2]-top_color[2]) * y/H)
        d.line([(0,y),(W,y)], fill=(r,g,b))

def rounded_rect(d, x1, y1, x2, y2, r=20, fill=None, outline=None, width=3):
    d.rounded_rectangle([x1,y1,x2,y2], radius=r, fill=fill, outline=outline, width=width)

def draw_spreadsheet_mock(d, x, y, w, h, scale=1.0):
    """Draw a mini spreadsheet mockup"""
    cols = [int(c*scale) for c in [120, 200, 160, 130, 120, 100]]
    rows = 8
    rh   = int(36*scale)
    cx   = x

    # Header row
    headers = ["Date", "Client", "Project", "Status", "Budget", "Paid"]
    colors_h = [C_NAV]*6
    for ci, (hdr, col) in enumerate(zip(headers, cols)):
        rounded_rect(d, cx, y, cx+col-4, y+rh-4, r=4, fill=C_NAV)
        d.text((cx+col//2-10, y+8), hdr,
               font=fnt(FONT_BOLD, int(13*scale)), fill=C_WHITE)
        cx += col

    # Data rows
    data = [
        ("01/06","TechStart","Logo Design","✓ Done","$1,200","$1,200"),
        ("03/06","CreativeAg","Website","● Active","$3,500","$1,750"),
        ("05/06","EcomStore","SEO Audit","✓ Done","$800","$800"),
        ("08/06","FoodBrand","Copywriting","● Active","$600","$0"),
        ("10/06","StartupXYZ","App UI","⏸ Hold","$2,200","$0"),
        ("12/06","MediaGroup","Branding","✓ Done","$1,800","$1,800"),
        ("15/06","RetailCo","Analytics","● Active","$950","$475"),
    ]
    stat_colors = {
        "✓ Done": C_GREEN,
        "● Active": C_ACCENT,
        "⏸ Hold": (180, 180, 180),
    }
    for ri, row in enumerate(data):
        ry = y + rh + ri * rh
        cx = x
        bg = C_LIGHT if ri % 2 == 0 else C_WHITE
        rounded_rect(d, x, ry, x+w-4, ry+rh-4, r=4, fill=bg)
        for ci, (val, col) in enumerate(zip(row, cols)):
            sc = stat_colors.get(val, C_DARK) if ci == 3 else C_DARK
            bold = ci == 3
            d.text((cx + 6, ry + 10), val,
                   font=fnt(FONT_BOLD if bold else FONT_REG, int(12*scale)),
                   fill=sc)
            cx += col


# ── IMAGE 1: HERO ──────────────────────────────────────────────
def img1_hero():
    img = new_img()
    gradient_bg(img, (10, 20, 50), (13, 27, 42))
    d = ImageDraw.Draw(img)
    W, H = 2000, 2000

    # Decorative circles
    for r, alpha in [(700, 40), (550, 60), (400, 80)]:
        d.ellipse([W//2-r, 200-r, W//2+r, 200+r], outline=(*C_ACCENT, alpha), width=3)

    # Accent bar top
    d.rectangle([0, 0, W, 14], fill=C_ACCENT)

    # Badge
    rounded_rect(d, W//2-180, 140, W//2+180, 210, r=40, fill=C_ACCENT)
    d.text((W//2-155, 155), "GOOGLE SHEETS TEMPLATE",
           font=fnt(FONT_BOLD, 36), fill=C_WHITE)

    # Title
    d.text((W//2-700, 260), "FREELANCE",
           font=fnt(FONT_BOLD, 200), fill=C_WHITE)
    d.text((W//2-820, 440), "BUSINESS MANAGER",
           font=fnt(FONT_BOLD, 130), fill=C_ACCENT)

    # Subtitle
    d.text((W//2-530, 620), "Track Clients • Projects • Invoices • Time",
           font=fnt(FONT_REG, 52), fill=C_GRAY)

    # Mock spreadsheet card
    rounded_rect(d, 140, 730, 1860, 1480, r=24, fill=C_WHITE)

    # Spreadsheet header
    rounded_rect(d, 160, 750, 1840, 820, r=10, fill=C_NAV)
    d.text((180, 762), "📊  FREELANCE BUSINESS MANAGER — Dashboard",
           font=fnt(FONT_BOLD, 36), fill=C_WHITE)

    # KPI cards row
    kpis = [
        ("Monthly Revenue", "$8,350", C_ACCENT),
        ("Active Projects", "7", C_GREEN),
        ("Overdue Invoices", "2", C_RED),
        ("Hours This Month", "124h", C_YELLOW),
    ]
    for i, (label, val, color) in enumerate(kpis):
        kx = 160 + i * 425
        rounded_rect(d, kx, 840, kx+405, 1020, r=16, fill=C_LIGHT)
        d.rectangle([kx, 840, kx+10, 1020], fill=color)
        d.text((kx+28, 860), label, font=fnt(FONT_REG, 28), fill=C_GRAY)
        d.text((kx+28, 906), val, font=fnt(FONT_BOLD, 64), fill=color)

    # Table inside card
    draw_spreadsheet_mock(d, 160, 1040, 1680, 400, scale=1.4)

    # Bottom feature pills
    features = ["✓ 7 Tabs", "✓ Auto Formulas", "✓ Instant Download", "✓ Google Sheets & Excel"]
    pill_x = 200
    for feat in features:
        tw = len(feat) * 22 + 40
        rounded_rect(d, pill_x, 1520, pill_x+tw, 1590, r=35, fill=C_ACCENT)
        d.text((pill_x+20, 1535), feat, font=fnt(FONT_BOLD, 34), fill=C_WHITE)
        pill_x += tw + 30

    # Price badge
    rounded_rect(d, 800, 1640, 1200, 1780, r=24, fill=C_GREEN)
    d.text((870, 1655), "ONLY", font=fnt(FONT_REG, 40), fill=C_DARK)
    d.text((870, 1700), "$19.00", font=fnt(FONT_BOLD, 90), fill=C_DARK)

    # Store name
    d.text((W//2-160, 1840), "NasriTools",
           font=fnt(FONT_BOLD, 60), fill=C_ACCENT)
    d.text((W//2-300, 1910), "nasritools.etsy.com",
           font=fnt(FONT_REG, 40), fill=C_GRAY)

    img.save("/home/user/smc-bot/fl_01_hero.jpg", quality=96)
    print("✅ fl_01_hero.jpg")


# ── IMAGE 2: WHAT'S INCLUDED ────────────────────────────────────
def img2_included():
    img = new_img()
    gradient_bg(img, (20, 30, 70), (13, 27, 42))
    d = ImageDraw.Draw(img)
    W, H = 2000, 2000

    d.rectangle([0, 0, W, 14], fill=C_GREEN)

    rounded_rect(d, W//2-300, 70, W//2+300, 150, r=40, fill=C_GREEN)
    d.text((W//2-265, 88), "WHAT'S INCLUDED",
           font=fnt(FONT_BOLD, 44), fill=C_DARK)

    d.text((W//2-580, 200), "7 Professional Tabs — Everything You Need",
           font=fnt(FONT_BOLD, 56), fill=C_WHITE)

    tabs = [
        ("🏠", "Dashboard",           "Real-time: revenue, profit,\ntax estimate, top clients",        C_ACCENT),
        ("👥", "Clients",             "Client database with auto\nproject count & revenue",             C_GREEN),
        ("📋", "Projects",            "Status, budget, deadline\ntracker with dropdowns",               C_YELLOW),
        ("🧾", "Invoices",            "Auto overdue detection,\npayment status tracking",              C_RED),
        ("💰", "Income & Expenses",   "Full P&L with 25%\ntax estimate formula",                       (114, 9, 183)),
        ("⏱️", "Time Tracker",        "Log hours, auto-calculate\nearnings per task",                  (6, 182, 212)),
        ("📊", "Reports",             "Auto P&L, project,\ninvoice & time summaries",                  C_GREEN),
    ]

    cols_per_row = 2
    for i, (emoji, name, desc, color) in enumerate(tabs):
        col = i % 2
        row = i // 2
        tx = 140 + col * 940
        ty = 330 + row * 380
        if i == 6:  # last one centered
            tx = W // 2 - 420

        rounded_rect(d, tx, ty, tx+840, ty+340, r=20, fill=(*C_NAV,), outline=color, width=4)
        d.rectangle([tx, ty, tx+16, ty+340], fill=color)

        d.text((tx+40, ty+30), emoji, font=fnt(FONT_REG, 70), fill=C_WHITE)
        d.text((tx+130, ty+35), name, font=fnt(FONT_BOLD, 44), fill=C_WHITE)
        for li, line in enumerate(desc.split("\n")):
            d.text((tx+130, ty+100+li*42), line, font=fnt(FONT_REG, 32), fill=C_GRAY)

        rounded_rect(d, tx+660, ty+30, tx+820, ty+90, r=20, fill=color)
        d.text((tx+680, ty+44), "AUTO", font=fnt(FONT_BOLD, 30), fill=C_DARK if color==C_YELLOW else C_WHITE)

    d.text((W//2-240, 1920), "NasriTools  •  $19",
           font=fnt(FONT_BOLD, 50), fill=C_ACCENT)

    img.save("/home/user/smc-bot/fl_02_included.jpg", quality=96)
    print("✅ fl_02_included.jpg")


# ── IMAGE 3: HOW IT WORKS ──────────────────────────────────────
def img3_how():
    img = new_img()
    gradient_bg(img, (15, 25, 60), (10, 18, 45))
    d = ImageDraw.Draw(img)
    W, H = 2000, 2000

    d.rectangle([0, 0, W, 14], fill=C_YELLOW)

    rounded_rect(d, W//2-240, 70, W//2+240, 148, r=40, fill=C_YELLOW)
    d.text((W//2-210, 86), "HOW IT WORKS",
           font=fnt(FONT_BOLD, 44), fill=C_DARK)

    d.text((W//2-620, 200), "Up & Running in Under 5 Minutes",
           font=fnt(FONT_BOLD, 64), fill=C_WHITE)

    steps = [
        ("01", "Purchase & Download",
         "Buy on Etsy → immediate download\nof .xlsx file + PDF guide",
         C_ACCENT, "📥"),
        ("02", "Open in Google Sheets",
         "Upload to Google Drive → open\nwith Google Sheets (free!)",
         C_GREEN, "☁️"),
        ("03", "Fill Yellow Cells",
         "Enter your clients, projects,\ninvoices in the yellow cells",
         C_YELLOW, "✏️"),
        ("04", "Dashboard Updates Live",
         "Revenue, profit, tax, overdue\ninvoices — all auto-calculated",
         C_RED, "🚀"),
    ]

    for i, (num, title, desc, color, icon) in enumerate(steps):
        sy = 380 + i * 390
        rounded_rect(d, 140, sy, 1860, sy+340, r=24, fill=(*C_NAV,), outline=color, width=3)

        # Step number circle
        cx, cy = 250, sy+170
        d.ellipse([cx-80,cy-80,cx+80,cy+80], fill=color)
        d.text((cx-45 if int(num)>9 else cx-25, cy-42), num,
               font=fnt(FONT_BOLD, 72), fill=C_WHITE if color != C_YELLOW else C_DARK)

        # Icon
        d.text((400, sy+50), icon, font=fnt(FONT_REG, 110), fill=color)

        # Text
        d.text((560, sy+60), title, font=fnt(FONT_BOLD, 56), fill=C_WHITE)
        for li, line in enumerate(desc.split("\n")):
            d.text((560, sy+140+li*48), line, font=fnt(FONT_REG, 38), fill=C_GRAY)

        # Connector arrow (not for last)
        if i < 3:
            ax = 250
            ay = sy + 340 + 15
            d.polygon([(ax-20,ay),(ax+20,ay),(ax,ay+50)], fill=color)

    d.text((W//2-240, 1940), "NasriTools  •  $19",
           font=fnt(FONT_BOLD, 50), fill=C_ACCENT)

    img.save("/home/user/smc-bot/fl_03_how.jpg", quality=96)
    print("✅ fl_03_how.jpg")


# ── IMAGE 4: FEATURES GRID ──────────────────────────────────────
def img4_features():
    img = new_img()
    gradient_bg(img, (8, 15, 40), (20, 35, 80))
    d = ImageDraw.Draw(img)
    W, H = 2000, 2000

    d.rectangle([0, 0, W, 14], fill=C_PURPLE)

    rounded_rect(d, W//2-220, 70, W//2+220, 148, r=40, fill=(114, 9, 183))
    d.text((W//2-195, 86), "KEY FEATURES",
           font=fnt(FONT_BOLD, 44), fill=C_WHITE)

    d.text((W//2-680, 198), "Everything a Freelancer Needs to Succeed",
           font=fnt(FONT_BOLD, 58), fill=C_WHITE)

    features = [
        ("⚡", "Auto Overdue Detection",  "Invoices turn red\nwhen past due date",     C_RED),
        ("⏱️", "Time Tracker Formula",    "Hours = auto-calculated\nfrom start & end", C_ACCENT),
        ("💰", "Tax Estimate Built-In",   "25% auto-calculated\n(adjustable rate)",     C_GREEN),
        ("📊", "Live Dashboard",          "Updates instantly\nno manual refresh",       C_YELLOW),
        ("🔗", "Cross-Tab Formulas",      "SUMIF links all tabs\nautomatically",        (114,9,183)),
        ("🎨", "Color-Coded Status",      "Green = done\nRed = overdue",               C_GREEN),
        ("📥", "Instant Download",        "Works offline, no\nsubscriptions needed",   C_ACCENT),
        ("💼", "50+ Sample Rows",         "Pre-filled to guide\nyou from day one",     C_YELLOW),
    ]

    for i, (icon, title, desc, color) in enumerate(features):
        col = i % 2
        row = i // 2
        fx = 140 + col * 930
        fy = 320 + row * 400

        rounded_rect(d, fx, fy, fx+880, fy+360, r=20, fill=C_NAV, outline=color, width=3)

        # Color accent bar left
        d.rectangle([fx, fy, fx+12, fy+360], fill=color)

        d.text((fx+50, fy+30), icon, font=fnt(FONT_REG, 90), fill=color)
        d.text((fx+160, fy+40), title, font=fnt(FONT_BOLD, 42), fill=C_WHITE)
        for li, line in enumerate(desc.split("\n")):
            d.text((fx+160, fy+108+li*46), line, font=fnt(FONT_REG, 34), fill=C_GRAY)

        # Check mark badge
        rounded_rect(d, fx+760, fy+20, fx+860, fy+80, r=16, fill=color)
        d.text((fx+790, fy+30), "✓", font=fnt(FONT_BOLD, 46),
               fill=C_DARK if color==C_YELLOW else C_WHITE)

    d.text((W//2-240, 1940), "NasriTools  •  $19",
           font=fnt(FONT_BOLD, 50), fill=C_ACCENT)

    img.save("/home/user/smc-bot/fl_04_features.jpg", quality=96)
    print("✅ fl_04_features.jpg")


# ── IMAGE 5: CALL TO ACTION ─────────────────────────────────────
def img5_cta():
    img = new_img()
    gradient_bg(img, (5, 12, 35), (25, 45, 100))
    d = ImageDraw.Draw(img)
    W, H = 2000, 2000

    # Background shapes
    for r in [900, 750, 600]:
        d.ellipse([W//2-r, H//2-r, W//2+r, H//2+r],
                  outline=(*C_ACCENT, 20), width=2)

    d.rectangle([0, 0, W, 14], fill=C_ACCENT)

    # Headline
    d.text((W//2-580, 80), "STOP LOSING MONEY",
           font=fnt(FONT_BOLD, 90), fill=C_RED)
    d.text((W//2-430, 190), "TO DISORGANIZATION",
           font=fnt(FONT_BOLD, 80), fill=C_WHITE)
    d.text((W//2-420, 310), "Get your freelance business",
           font=fnt(FONT_REG, 52), fill=C_GRAY)
    d.text((W//2-350, 375), "organized in 5 minutes.",
           font=fnt(FONT_REG, 52), fill=C_GRAY)

    # Pain vs Solution columns
    rounded_rect(d, 80, 480, 950, 1200, r=24, fill=(80,15,15), outline=C_RED, width=3)
    rounded_rect(d, 1050, 480, 1920, 1200, r=24, fill=(10,50,30), outline=C_GREEN, width=3)

    d.text((340, 510), "❌ WITHOUT IT", font=fnt(FONT_BOLD, 48), fill=C_RED)
    d.text((1270, 510), "✅ WITH IT", font=fnt(FONT_BOLD, 48), fill=C_GREEN)

    pain_points = [
        "Forget to invoice clients",
        "Miss payment deadlines",
        "Don't know your real profit",
        "Lose track of project hours",
        "No tax estimate prepared",
        "Clients fall through cracks",
    ]
    solutions = [
        "Invoice tracker + alerts",
        "Auto overdue detection",
        "Live P&L dashboard",
        "Time tracker + formulas",
        "25% tax auto-calculated",
        "Full client database",
    ]

    for i, (pain, sol) in enumerate(zip(pain_points, solutions)):
        py = 600 + i * 90
        d.text((110, py), f"• {pain}", font=fnt(FONT_REG, 34), fill=(255,150,150))
        d.text((1080, py), f"• {sol}", font=fnt(FONT_REG, 34), fill=(150,255,200))

    # Testimonial (fictional)
    rounded_rect(d, 80, 1230, 1920, 1440, r=20, fill=C_NAV)
    d.text((130, 1258),
           '"This spreadsheet replaced 3 apps I was paying for.',
           font=fnt(FONT_REG, 40), fill=C_WHITE)
    d.text((130, 1312),
           ' Saved me $50/month and everything is in one place!"',
           font=fnt(FONT_REG, 40), fill=C_WHITE)
    d.text((130, 1378), "— Freelance Designer, 5 ⭐⭐⭐⭐⭐",
           font=fnt(FONT_BOLD, 36), fill=C_YELLOW)

    # Price + CTA
    rounded_rect(d, 480, 1480, 1520, 1720, r=40, fill=C_ACCENT)
    d.text((640, 1510), "INSTANT DOWNLOAD", font=fnt(FONT_BOLD, 52), fill=C_WHITE)
    d.text((740, 1585), "Only  $19.00", font=fnt(FONT_BOLD, 80), fill=C_YELLOW)
    d.text((520, 1665), "Works in Google Sheets & Excel", font=fnt(FONT_REG, 38), fill=C_WHITE)

    # What you get
    files = ["Freelance_Business_Manager.xlsx", "Freelance_Guide.pdf (Setup Guide)"]
    d.text((W//2-280, 1760), "FILES INCLUDED:", font=fnt(FONT_BOLD, 38), fill=C_GRAY)
    for i, f in enumerate(files):
        d.text((W//2-350, 1820+i*52), f"📄 {f}", font=fnt(FONT_REG, 34), fill=C_WHITE)

    d.text((W//2-240, 1940), "NasriTools  •  nasritools.etsy.com",
           font=fnt(FONT_BOLD, 42), fill=C_ACCENT)

    img.save("/home/user/smc-bot/fl_05_cta.jpg", quality=96)
    print("✅ fl_05_cta.jpg")


if __name__ == "__main__":
    img1_hero()
    img2_included()
    img3_how()
    img4_features()
    img5_cta()
    print("\n✅ All 5 Etsy images created!")
