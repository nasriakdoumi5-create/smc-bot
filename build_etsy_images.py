"""
Build 5 professional Etsy product images (2000×2000px each)
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ── Fonts ────────────────────────────────────────────
FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def fnt(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# ── Colors ───────────────────────────────────────────
DARK    = (26,  26,  46)
PRIMARY = (22,  33,  62)
ACCENT  = (233, 69,  96)
GREEN   = (15,  155, 88)
YELLOW  = (255, 215, 0)
BLUE    = (74,  144, 217)
ORANGE  = (255, 107, 53)
WHITE   = (255, 255, 255)
LIGHT   = (245, 245, 245)
GRAY    = (150, 150, 150)

SIZE = (2000, 2000)
OUT  = "/home/user/smc-bot/etsy_images"
os.makedirs(OUT, exist_ok=True)

# ── Helpers ──────────────────────────────────────────
def new_img(bg=DARK):
    img = Image.new("RGB", SIZE, bg)
    d   = ImageDraw.Draw(img)
    return img, d

def rect(d, x0, y0, x1, y1, fill, radius=0):
    if radius:
        d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)
    else:
        d.rectangle([x0, y0, x1, y1], fill=fill)

def text_c(d, text, y, font, color=WHITE, x=1000):
    """Draw centered text."""
    bb = d.textbbox((0, 0), text, font=font)
    w  = bb[2] - bb[0]
    d.text((x - w // 2, y), text, font=font, fill=color)

def text_l(d, text, x, y, font, color=WHITE):
    d.text((x, y), text, font=font, fill=color)

def gradient_bg(img, top_color, bot_color):
    """Vertical gradient background."""
    d = ImageDraw.Draw(img)
    for y in range(SIZE[1]):
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * y / SIZE[1])
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * y / SIZE[1])
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * y / SIZE[1])
        d.line([(0, y), (SIZE[0], y)], fill=(r, g, b))
    return img

def draw_badge(d, x, y, text, bg=ACCENT, fg=WHITE, size=28):
    f = fnt(FONT_BOLD, size)
    bb = d.textbbox((0, 0), text, font=f)
    w, h = bb[2]-bb[0]+30, bb[3]-bb[1]+16
    d.rounded_rectangle([x, y, x+w, y+h], radius=10, fill=bg)
    d.text((x+15, y+8), text, font=f, fill=fg)
    return w, h

def draw_star_row(d, x, y, count=5, size=40, color=YELLOW):
    for i in range(count):
        d.text((x + i*(size+5), y), "★", font=fnt(FONT_REG, size), fill=color)

def divider(d, y, color=(60,60,80), x0=100, x1=1900):
    d.line([(x0, y), (x1, y)], fill=color, width=2)

# ══════════════════════════════════════════════════════
#  IMAGE 1 — Hero / Main Cover
# ══════════════════════════════════════════════════════
def img1_hero():
    img = gradient_bg(Image.new("RGB", SIZE), DARK, (10, 20, 50))
    d   = ImageDraw.Draw(img)

    # Top accent bar
    rect(d, 0, 0, 2000, 12, ACCENT)

    # Decorative circles
    d.ellipse([1500, -300, 2300, 500],   fill=(30, 40, 80), outline=None)
    d.ellipse([-300, 1500, 500, 2300],  fill=(30, 40, 80), outline=None)

    # Badge — top
    draw_badge(d, 750, 100, "  INSTANT DIGITAL DOWNLOAD  ", bg=GREEN, size=30)

    # Main icon
    text_c(d, "🍽️", 220, fnt(FONT_REG, 160))

    # Main title
    text_c(d, "RESTAURANT &", 430, fnt(FONT_BOLD, 110), WHITE)
    text_c(d, "CAFE MANAGER", 560, fnt(FONT_BOLD, 110), YELLOW)

    # Subtitle
    text_c(d, "Smart Business Automation Template", 710, fnt(FONT_REG, 52), GRAY)

    divider(d, 790, ACCENT, 300, 1700)

    # Feature pills
    features = [
        ("📊", "DASHBOARD",     GREEN),
        ("📦", "INVENTORY",     BLUE),
        ("📈", "DAILY SALES",   ORANGE),
        ("👥", "STAFF",         ACCENT),
        ("📋", "REPORTS",       (120, 80, 200)),
    ]
    cols = [200, 580, 960, 1340, 1650]
    for i, (icon, label, color) in enumerate(features):
        x = cols[i]
        rect(d, x, 830, x+290, 1020, color, radius=18)
        text_c(d, icon,  870, fnt(FONT_REG, 60),  WHITE,  x+145)
        text_c(d, label, 945, fnt(FONT_BOLD, 26), WHITE,  x+145)

    # Central value prop
    text_c(d, "5 POWERFUL TABS", 1090, fnt(FONT_BOLD, 64), WHITE)
    text_c(d, "Everything you need to run your business", 1180,
           fnt(FONT_REG, 44), GRAY)

    # Mockup spreadsheet visual
    rect(d, 200, 1260, 1800, 1720, (18, 28, 55), radius=20)
    rect(d, 200, 1260, 1800, 1320, PRIMARY, radius=20)

    cols_data = ["Item", "Category", "Stock", "Min", "Status", "Value"]
    col_x = [230, 450, 720, 900, 1080, 1400]
    for i, h in enumerate(cols_data):
        text_l(d, h, col_x[i], 1278, fnt(FONT_BOLD, 30), YELLOW)

    rows_data = [
        ("Coffee Beans", "Beverage", "50 kg", "10", "✅ OK",   "$125.00"),
        ("Milk",         "Beverage", "30 L",  "10", "✅ OK",   "$45.00"),
        ("Sugar",        "Dry Good", "4 kg",  "5",  "⚠️ LOW",  "$8.00"),
        ("Flour",        "Dry Good", "15 kg", "5",  "✅ OK",   "$22.50"),
        ("Olive Oil",    "Condiment","2 L",   "2",  "⚠️ LOW",  "$18.00"),
    ]
    for ri, row in enumerate(rows_data):
        y  = 1340 + ri * 74
        bg = (22, 33, 62) if ri % 2 == 0 else (26, 38, 70)
        rect(d, 205, y, 1795, y+68, bg)
        clr = ACCENT if "LOW" in row[4] else GREEN
        for ci, val in enumerate(row):
            c = clr if ci == 4 else (200, 200, 220)
            text_l(d, val, col_x[ci], y+18, fnt(FONT_REG, 26), c)

    # Price + CTA
    text_c(d, "Only  $27  — One-Time Purchase", 1790, fnt(FONT_BOLD, 54), YELLOW)
    text_c(d, "No subscription  •  Use forever  •  Works in Google Sheets & Excel",
           1880, fnt(FONT_REG, 36), GRAY)

    # Stars
    draw_star_row(d, 850, 1950, 5, 44, YELLOW)

    rect(d, 0, 1988, 2000, 2000, ACCENT)

    img.save(f"{OUT}/01_hero.jpg", quality=95)
    print("✅ Image 1 — Hero")

# ══════════════════════════════════════════════════════
#  IMAGE 2 — What's Included
# ══════════════════════════════════════════════════════
def img2_included():
    img = gradient_bg(Image.new("RGB", SIZE), PRIMARY, DARK)
    d   = ImageDraw.Draw(img)

    rect(d, 0, 0, 2000, 12, BLUE)

    text_c(d, "WHAT'S INCLUDED", 80, fnt(FONT_BOLD, 90), WHITE)
    text_c(d, "5 tabs. Everything automated.", 195, fnt(FONT_REG, 46), GRAY)

    divider(d, 265, BLUE)

    tabs = [
        ("📊", "DASHBOARD",       GREEN,   "Real-time KPI cards + auto weekly summary"),
        ("📦", "INVENTORY",       BLUE,    "Track 50+ items with low-stock alerts"),
        ("📈", "DAILY SALES",     ORANGE,  "Log transactions + auto daily total"),
        ("👥", "STAFF SCHEDULE",  ACCENT,  "Weekly shifts + auto hours calculation"),
        ("📋", "REPORTS",         (120,80,200), "Auto P&L + profit margin + indicators"),
    ]

    for i, (icon, title, color, desc) in enumerate(tabs):
        y = 310 + i * 330

        # Card background
        rect(d, 100, y, 1900, y+300, (18, 28, 55), radius=22)
        rect(d, 100, y, 100+14, y+300, color, radius=3)   # left accent

        # Icon circle
        d.ellipse([130, y+45, 310, y+225], fill=color)
        text_c(d, icon, y+70, fnt(FONT_REG, 100), WHITE, 220)

        # Title
        text_l(d, title, 345, y+55,  fnt(FONT_BOLD, 56), color)
        text_l(d, desc,  345, y+145, fnt(FONT_REG,  38), (180,180,200))

        # Badge
        draw_badge(d, 1600, y+105, "AUTO ✓", bg=color, size=28)

    # Bottom note
    rect(d, 100, 1970, 1900, 1985, BLUE, radius=4)
    text_c(d, "🟡 Yellow = Enter data   |   🟢 Green = Calculated automatically",
           1940, fnt(FONT_REG, 36), YELLOW)

    img.save(f"{OUT}/02_included.jpg", quality=95)
    print("✅ Image 2 — What's Included")

# ══════════════════════════════════════════════════════
#  IMAGE 3 — How It Works
# ══════════════════════════════════════════════════════
def img3_how():
    img = gradient_bg(Image.new("RGB", SIZE), DARK, (10,25,45))
    d   = ImageDraw.Draw(img)

    rect(d, 0, 0, 2000, 12, GREEN)

    text_c(d, "HOW IT WORKS", 80, fnt(FONT_BOLD, 90), WHITE)
    text_c(d, "Ready in 3 simple steps", 195, fnt(FONT_REG, 46), GRAY)
    divider(d, 270, GREEN)

    steps = [
        (GREEN,  "1",  "DOWNLOAD",
         "Purchase and instantly download\nthe .xlsx file to your device"),
        (BLUE,   "2",  "OPEN",
         "Upload to Google Drive → Open\nwith Google Sheets (free) or Excel"),
        (ACCENT, "3",  "USE",
         "Fill yellow cells with your data.\nEverything else is automatic!"),
    ]

    for i, (color, num, title, desc) in enumerate(steps):
        y = 340 + i * 520

        # Large number background
        rect(d, 100, y, 400, y+450, color, radius=22)
        text_c(d, num, y+130, fnt(FONT_BOLD, 220), WHITE, 250)

        # Content area
        rect(d, 430, y, 1900, y+450, (18,28,55), radius=22)
        text_l(d, title, 500, y+70,  fnt(FONT_BOLD, 72), color)
        for li, line in enumerate(desc.split("\n")):
            text_l(d, line, 500, y+185+li*70, fnt(FONT_REG, 42), (200,200,220))

        # Connector arrow
        if i < 2:
            for ay in range(y+460, y+520, 6):
                d.ellipse([245, ay, 255, ay+3], fill=color)

    # Bonus row
    rect(d, 100, 1920, 1900, 2000, PRIMARY, radius=22)
    bonuses = ["✓ No coding required", "✓ Works offline", "✓ Share with team", "✓ Free support 30 days"]
    bx = 150
    for b in bonuses:
        text_l(d, b, bx, 1946, fnt(FONT_BOLD, 34), YELLOW)
        bx += 450

    img.save(f"{OUT}/03_how_it_works.jpg", quality=95)
    print("✅ Image 3 — How It Works")

# ══════════════════════════════════════════════════════
#  IMAGE 4 — Features & Benefits
# ══════════════════════════════════════════════════════
def img4_features():
    img = gradient_bg(Image.new("RGB", SIZE), (8,18,40), DARK)
    d   = ImageDraw.Draw(img)

    rect(d, 0, 0, 2000, 12, ORANGE)

    text_c(d, "WHY CHOOSE THIS", 80,  fnt(FONT_BOLD, 88), WHITE)
    text_c(d, "TEMPLATE?",        185, fnt(FONT_BOLD, 88), YELLOW)
    text_c(d, "Save time. Make better decisions. Grow your business.",
           310, fnt(FONT_REG, 42), GRAY)
    divider(d, 380, ORANGE)

    features = [
        (GREEN,  "⏰", "Saves 5+ Hours Per Week",   "No more manual calculations or messy notes"),
        (BLUE,   "💰", "Boost Profitability",        "Spot your best-selling items and peak hours"),
        (ORANGE, "📱", "Works on Any Device",        "Google Sheets app — iPhone, Android, tablet"),
        (ACCENT, "👥", "Share with Your Team",       "Give access to staff with one click"),
        (GREEN,  "🔄", "Auto-Updates Everything",   "Change one number — all reports update instantly"),
        (BLUE,   "🛡️", "No Subscription Needed",    "Pay once. Use forever. No hidden fees."),
    ]

    for i, (color, icon, title, sub) in enumerate(features):
        col = i % 2
        row = i // 2
        x = 100  + col * 960
        y = 440  + row * 480

        rect(d, x, y, x+870, y+430, (18,28,55), radius=22)

        # Icon circle
        d.ellipse([x+30, y+30, x+160, y+160], fill=color)
        text_c(d, icon, y+50, fnt(FONT_REG, 80), WHITE, x+95)

        # Text
        text_l(d, title, x+190, y+55,  fnt(FONT_BOLD, 46), WHITE)
        text_l(d, sub,   x+190, y+140, fnt(FONT_REG,  34), (170,170,200))

        # Bottom bar
        rect(d, x, y+390, x+870, y+430, color, radius=22)
        text_c(d, "INCLUDED ✓", y+400, fnt(FONT_BOLD, 28), WHITE, x+435)

    # Price CTA
    rect(d, 100, 1910, 1900, 1990, GREEN, radius=22)
    text_c(d, "ONE-TIME PURCHASE  •  $27  •  INSTANT DOWNLOAD",
           1932, fnt(FONT_BOLD, 48), WHITE)

    img.save(f"{OUT}/04_features.jpg", quality=95)
    print("✅ Image 4 — Features")

# ══════════════════════════════════════════════════════
#  IMAGE 5 — Social Proof / CTA
# ══════════════════════════════════════════════════════
def img5_cta():
    img = gradient_bg(Image.new("RGB", SIZE), (5,15,35), DARK)
    d   = ImageDraw.Draw(img)

    rect(d, 0, 0, 2000, 12, YELLOW)

    # Stars
    draw_star_row(d, 700, 60, 5, 56, YELLOW)
    text_c(d, "Loved by Restaurant & Cafe Owners", 145, fnt(FONT_BOLD, 60), WHITE)

    divider(d, 230, (60,60,80))

    # Testimonials
    reviews = [
        ("★★★★★", "Ahmed K.",
         '"Finally a template that works!\nSaved me hours every single week."',
         GREEN),
        ("★★★★★", "Maria S.",
         '"So easy to use. My whole\nstaff uses it daily now!"',
         BLUE),
        ("★★★★★", "James T.",
         '"The inventory alerts alone\nare worth 10x the price."',
         ORANGE),
    ]

    for i, (stars, name, quote, color) in enumerate(reviews):
        x = 60 + i * 640
        rect(d, x, 270, x+600, 770, (18,28,55), radius=22)
        rect(d, x, 270, x+600, 285, color, radius=10)

        text_l(d, stars, x+30, 305, fnt(FONT_REG,  44), YELLOW)
        text_l(d, name,  x+30, 365, fnt(FONT_BOLD, 38), color)
        for li, line in enumerate(quote.strip('"').split("\n")):
            text_l(d, f'"{line}', x+30, 435+li*70, fnt(FONT_REG, 32), (200,200,220))

    # Divider
    divider(d, 810, (60,60,80))

    # Big promise
    text_c(d, "YOUR BUSINESS,", 870, fnt(FONT_BOLD, 100), WHITE)
    text_c(d, "ON AUTOPILOT",   985, fnt(FONT_BOLD, 100), YELLOW)

    # 3-column guarantees
    guarantees = [
        (GREEN,  "✓", "Instant Download\nAfter Purchase"),
        (BLUE,   "✓", "Works in Google\nSheets & Excel"),
        (ACCENT, "✓", "Free Support\n30 Days"),
    ]
    for i, (color, check, text) in enumerate(guarantees):
        x = 200 + i * 540
        rect(d, x, 1120, x+460, 1340, (18,28,55), radius=22)
        text_c(d, check, 1140, fnt(FONT_BOLD, 90), color, x+230)
        for li, line in enumerate(text.split("\n")):
            text_c(d, line, 1235+li*60, fnt(FONT_BOLD, 36), WHITE, x+230)

    # Price section
    rect(d, 200, 1400, 1800, 1680, PRIMARY, radius=30)
    text_c(d, "COMPLETE PACKAGE", 1440, fnt(FONT_BOLD, 56), GRAY)
    text_c(d, "$27",              1520, fnt(FONT_BOLD, 120), YELLOW)
    text_c(d, "One-Time  •  No Subscription  •  Instant Access",
           1648, fnt(FONT_REG, 38), WHITE)

    # What you get
    items = ["✓ Manager Template .xlsx",
             "✓ PDF User Guide",
             "✓ 5 Powerful Tabs"]
    for i, item in enumerate(items):
        text_c(d, item, 1730+i*70, fnt(FONT_BOLD, 38), GREEN,
               [500, 1000, 1500][i])

    # Bottom bar
    rect(d, 0, 1960, 2000, 2000, ACCENT)
    text_c(d, "⭐ BEST SELLER  •  INSTANT DIGITAL DOWNLOAD  •  etsy.com",
           1968, fnt(FONT_BOLD, 34), WHITE)

    img.save(f"{OUT}/05_cta.jpg", quality=95)
    print("✅ Image 5 — CTA / Social Proof")


# ══ MAIN ═════════════════════════════════════════════
if __name__ == "__main__":
    print("🎨 Building Etsy product images...\n")
    img1_hero()
    img2_included()
    img3_how()
    img4_features()
    img5_cta()
    print(f"\n🎉 All 5 images saved to: {OUT}/")
    sizes = [os.path.getsize(f"{OUT}/{f}") for f in sorted(os.listdir(OUT))]
    for fname, sz in zip(sorted(os.listdir(OUT)), sizes):
        print(f"   {fname}  ({sz//1024} KB)")
