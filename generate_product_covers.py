"""
NasriTools - Product Cover Images (Dashboard Style v2 — large text)
4 columns · 5 rows · fonts 2x larger for readability at thumbnail size.
Run: python generate_product_covers.py
"""
import io, json, os, time, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

# ── 10 products: max 4 cols, 5 rows each ─────────────────────────────────────
PRODUCTS = [
    {
        "search_kw": ["budget", "expense"],
        "color": (20, 115, 60), "light": (220, 247, 233),
        "label": "BUDGET TRACKER",
        "headline": "Know Where Every\nEuro Goes.",
        "benefits": ["Auto expense tracking", "Savings goals on autopilot", "Zero manual math"],
        "sheet_title": "Monthly Budget & Expense System",
        "cols": [("CATEGORY", 520), ("BUDGET", 340), ("SPENT", 340), ("STATUS", 660)],
        "rows": [
            [("Housing & Rent",  "t"), ("€800",   "a"), ("€795",   "a"), ("On Track",    "g")],
            [("Groceries",       "t"), ("€300",   "a"), ("€267",   "a"), ("On Track",    "g")],
            [("Transport",       "t"), ("€120",   "a"), ("€145",   "r"), ("Over Budget", "bad")],
            [("Savings Goal",    "t"), ("€500",   "a"), ("€500",   "a"), ("Saved",       "g")],
            [("TOTAL",           "b"), ("€1,970", "ab"),("€1,922", "ab"), ("Surplus €48","g")],
        ],
    },
    {
        "search_kw": ["habit", "building"],
        "color": (192, 57, 43), "light": (253, 228, 224),
        "label": "HABIT TRACKER",
        "headline": "30 Habits.\nAutomatic Streaks.",
        "benefits": ["Track 30 habits daily", "Auto streak counter", "Visual progress every day"],
        "sheet_title": "30-Day Habit Building System",
        "cols": [("HABIT", 680), ("THIS WEEK", 380), ("STREAK", 320), ("STATUS", 480)],
        "rows": [
            [("Morning Run",   "t"), ("6 / 7 days", "c"), ("6-day",  "c"), ("On Track", "g")],
            [("Read 30 min",   "t"), ("5 / 7 days", "c"), ("5-day",  "c"), ("On Track", "g")],
            [("No Sugar",      "t"), ("5 / 7 days", "c"), ("4-day",  "c"), ("Good",     "y")],
            [("Meditate",      "t"), ("6 / 7 days", "c"), ("5-day",  "c"), ("On Track", "g")],
            [("DAY 18 / 30",   "b"), ("83% done",   "c"), ("",       ""),  ("Complete", "g")],
        ],
    },
    {
        "search_kw": ["meal", "planner"],
        "color": (39, 174, 141), "light": (209, 250, 229),
        "label": "MEAL PLANNER",
        "headline": "7 Days of Meals\nin 15 Minutes.",
        "benefits": ["Auto grocery list", "Nutrition tracked", "Save €80+ weekly"],
        "sheet_title": "Weekly Meal Planning System",
        "cols": [("DAY", 240), ("LUNCH", 560), ("DINNER", 560), ("CALORIES", 500)],
        "rows": [
            [("Monday",    "c"), ("Chicken & Rice",  "t"), ("Salmon + Veg",    "t"), ("1,850 kcal","a")],
            [("Tuesday",   "c"), ("Greek Salad",     "t"), ("Beef Stir-fry",   "t"), ("1,720 kcal","a")],
            [("Wednesday", "c"), ("Tuna Wrap",       "t"), ("Pasta Bolognese", "t"), ("1,900 kcal","a")],
            [("Thursday",  "c"), ("Lentil Soup",     "t"), ("Grilled Chicken", "t"), ("1,650 kcal","a")],
            [("GROCERIES", "b"), ("Auto-generated",  "t"), ("47 items",        "t"), ("Save €80+", "g")],
        ],
    },
    {
        "search_kw": ["wedding", "planner"],
        "color": (210, 82, 162), "light": (252, 228, 243),
        "label": "WEDDING PLANNER",
        "headline": "Plan Your Perfect\nWedding.",
        "benefits": ["Budget tracked to the cent", "All vendors in one place", "Zero missed details"],
        "sheet_title": "Complete Wedding Planning System",
        "cols": [("CATEGORY", 420), ("BUDGET", 300), ("SPENT", 300), ("STATUS", 840)],
        "rows": [
            [("Venue",       "t"), ("€5,000", "a"), ("€4,800","a"), ("Booked",      "g")],
            [("Catering",    "t"), ("€3,500", "a"), ("€3,500","a"), ("Booked",      "g")],
            [("Photography", "t"), ("€1,800", "a"), ("€900",  "a"), ("Deposit Paid","y")],
            [("Flowers",     "t"), ("€600",   "a"), ("€0",    "a"), ("Pending",     "y")],
            [("TOTAL",       "b"), ("€12,900","ab"),("€11,200","ab"),("€1,700 left", "y")],
        ],
    },
    {
        "search_kw": ["workout", "tracker"],
        "color": (192, 57, 43), "light": (253, 228, 224),
        "label": "WORKOUT TRACKER",
        "headline": "See Your Strength\nGrow Every Session.",
        "benefits": ["PRs tracked automatically", "Progress charts auto-generated", "Beat last week every time"],
        "sheet_title": "Gym & Workout Tracking System",
        "cols": [("EXERCISE", 500), ("WEIGHT", 320), ("REPS", 240), ("PROGRESS", 800)],
        "rows": [
            [("Bench Press",    "t"), ("80 kg",  "c"), ("4 x 8",  "c"), ("82%","p")],
            [("Squats",         "t"), ("100 kg", "c"), ("4 x 6",  "c"), ("91%","p")],
            [("Deadlift",       "t"), ("120 kg", "c"), ("3 x 5",  "c"), ("78%","p")],
            [("Pull-Ups",       "t"), ("BW",     "c"), ("4 x 10", "c"), ("95%","p")],
            [("THIS WEEK",      "b"), ("",       ""),  ("",       ""),   ("New PR +5%","g")],
        ],
    },
    {
        "search_kw": ["content", "creator"],
        "color": (230, 126, 34), "light": (254, 243, 224),
        "label": "CONTENT CREATOR",
        "headline": "Post Consistently.\nGrow Systematically.",
        "benefits": ["3 months planned in 1 weekend", "Analytics tracked weekly", "Brand deals never missed"],
        "sheet_title": "Content Creator Business System",
        "cols": [("PLATFORM", 320), ("POST TITLE", 640), ("VIEWS", 280), ("STATUS", 620)],
        "rows": [
            [("Instagram",  "t"), ("5 Morning Habits",      "t"), ("12.4K","a"), ("Published",  "g")],
            [("YouTube",    "t"), ("Budget €2k/month",      "t"), ("8.2K", "a"), ("Published",  "g")],
            [("TikTok",     "t"), ("Meal Prep Sunday",      "t"), ("31K",  "a"), ("Published",  "g")],
            [("Instagram",  "t"), ("Weekly Workout Split",  "t"), ("9.1K", "a"), ("Scheduled",  "y")],
            [("JUNE TOTAL", "b"), ("6 posts planned",       "t"), ("",     ""),  ("On Schedule","g")],
        ],
    },
    {
        "search_kw": ["invoice", "client"],
        "color": (52, 152, 219), "light": (214, 234, 248),
        "label": "INVOICE TRACKER",
        "headline": "Stop Chasing Invoices.\nGet Paid on Time.",
        "benefits": ["All invoices at a glance", "Tax prep ready instantly", "Revenue calculated auto"],
        "sheet_title": "Freelancer Invoice & Client System",
        "cols": [("CLIENT", 460), ("AMOUNT", 300), ("DUE DATE", 300), ("STATUS", 800)],
        "rows": [
            [("Studio Bright",  "t"), ("€1,200","a"), ("Jun 01","c"), ("Paid",          "g")],
            [("Nova Agency",    "t"), ("€850",  "a"), ("Jun 05","c"), ("Paid",          "g")],
            [("TechStart GmbH", "t"), ("€2,400","a"), ("Jun 15","c"), ("Pending",       "y")],
            [("Bloom Creative", "t"), ("€650",  "a"), ("Jun 20","c"), ("Sent",          "y")],
            [("JUNE TOTAL",     "b"), ("€10,100","ab"),("",      ""),  ("€5,700 pending","y")],
        ],
    },
    {
        "search_kw": ["student", "academic"],
        "color": (108, 52, 131), "light": (237, 228, 252),
        "label": "STUDENT PLANNER",
        "headline": "Ace Your Semester.\nGPA Tracked. Done.",
        "benefits": ["Zero missed deadlines", "GPA calculated live", "Exam ready every time"],
        "sheet_title": "Student Academic Success System",
        "cols": [("SUBJECT", 440), ("ASSIGNMENT", 560), ("DUE DATE", 280), ("STATUS", 580)],
        "rows": [
            [("Mathematics",  "t"), ("Problem Set 8",       "t"), ("Jun 05","c"), ("Submitted",  "g")],
            [("Economics",    "t"), ("Market Analysis",     "t"), ("Jun 08","c"), ("Submitted",  "g")],
            [("Data Science", "t"), ("ML Model Project",    "t"), ("Jun 12","c"), ("In Progress","y")],
            [("Marketing",    "t"), ("Brand Strategy Deck", "t"), ("Jun 15","c"), ("In Progress","y")],
            [("CURRENT GPA",  "b"), ("3.8 / 4.0",           "t"), ("",      ""),  ("Top 15%",   "g")],
        ],
    },
    {
        "search_kw": ["annual", "goal"],
        "color": (30, 100, 180), "light": (220, 235, 252),
        "label": "GOALS PLANNER",
        "headline": "Stop Setting Goals.\nStart Achieving Them.",
        "benefits": ["Goals broken into weekly steps", "90-day sprint plan", "Progress tracked %"],
        "sheet_title": "Annual Goals & 90-Day Action System",
        "cols": [("GOAL", 560), ("DEADLINE", 280), ("PROGRESS", 540), ("STATUS", 480)],
        "rows": [
            [("Launch Online Course",  "t"), ("Dec 31","c"), ("45%","p"), ("On Track","g")],
            [("Save €10,000",          "t"), ("Dec 31","c"), ("62%","p"), ("On Track","g")],
            [("Run Half Marathon",     "t"), ("Sep 15","c"), ("70%","p"), ("On Track","g")],
            [("Read 24 Books",         "t"), ("Dec 31","c"), ("54%","p"), ("On Track","g")],
            [("Q2 SPRINT SCORE",       "b"), ("",      ""),  ("",   ""),  ("5/6 goals","g")],
        ],
    },
    {
        "search_kw": ["weekly", "productivity"],
        "color": (108, 52, 131), "light": (237, 228, 252),
        "label": "WEEKLY PLANNER",
        "headline": "Plan Your Perfect Week\nin 15 Minutes.",
        "benefits": ["Time-blocked for deep work", "Top 3 priorities always done", "2x more done, less stress"],
        "sheet_title": "Weekly Productivity System",
        "cols": [("TASK", 580), ("PRIORITY", 280), ("TIME BLOCK", 380), ("STATUS", 620)],
        "rows": [
            [("Deep Work: Project A",  "t"), ("HIGH","bad"), ("08:00-11:00","c"), ("In Progress","y")],
            [("Weekly Review",         "t"), ("HIGH","bad"), ("07:00-07:30","c"), ("Done",       "g")],
            [("Client Presentation",   "t"), ("HIGH","bad"), ("14:00-15:00","c"), ("Done",       "g")],
            [("Study: Data Analysis",  "t"), ("MED", "y"),   ("19:00-21:00","c"), ("Pending",    "y")],
            [("WEEK SCORE",            "b"), ("",    ""),    ("",           ""),  ("83% done",   "g")],
        ],
    },
]

# ── Fonts ─────────────────────────────────────────────────────────────────────
_BOLD = [
    # Windows
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
    "C:/Windows/Fonts/verdanab.ttf",
    "C:/Windows/Fonts/trebucbd.ttf",
    # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
_REG = [
    # Windows
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/verdana.ttf",
    "C:/Windows/Fonts/trebuc.ttf",
    # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]

def _f(p, s):
    for path in p:
        if Path(path).exists():
            return ImageFont.truetype(path, s)
    return ImageFont.load_default()

def fb(s): return _f(_BOLD, s)
def fr(s): return _f(_REG, s)

def tw(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]

def pill(draw, x0, y0, x1, y1, fill, r=None):
    r = r or (y1-y0)//2
    r = min(r, (x1-x0)//2, (y1-y0)//2)
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx, cy in [(x0,y0),(x1-2*r,y0),(x0,y1-2*r),(x1-2*r,y1-2*r)]:
        draw.ellipse([cx, cy, cx+2*r, cy+2*r], fill=fill)

PILL_COLORS = {
    "g":   (34, 164, 85),
    "y":   (210, 140, 18),
    "bad": (214, 62, 45),
    "n":   (150, 155, 165),
}

def draw_cell(draw, col_x, col_w, row_y, row_h, text, ctype, color):
    if not text or not ctype:
        return
    cy  = row_y + row_h // 2
    PAD = 22

    # ── progress bar ──────────────────────────────────────────────────────────
    if ctype == "p":
        pct = int(text.replace("%", "")) / 100
        bx, by = col_x + PAD, cy - 18
        bw = col_w - PAD * 2 - 100
        pill(draw, bx, by, bx+bw, by+36, (215, 220, 232))
        pill(draw, bx, by, bx + max(18, int(bw*pct)), by+36, color)
        draw.text((bx+bw+12, by-4), text, font=fb(44), fill=color)
        return

    # ── status pill ───────────────────────────────────────────────────────────
    if ctype in ("g", "y", "bad", "n"):
        pc   = PILL_COLORS[ctype]
        f    = fr(42)
        tw_  = tw(draw, text, f)
        pw   = min(tw_ + 48, col_w - PAD * 2)
        px0  = col_x + PAD
        py0  = cy - 32
        pill(draw, px0, py0, px0+pw, py0+64, pc)
        draw.text((px0+24, py0+11), text, font=f, fill=(255, 255, 255))
        return

    # ── red text ──────────────────────────────────────────────────────────────
    if ctype == "r":
        draw.text((col_x+PAD, cy-28), text, font=fb(48), fill=(214, 62, 45))
        return

    # ── amounts ───────────────────────────────────────────────────────────────
    if ctype in ("a", "ab"):
        draw.text((col_x+PAD, cy-28), text,
                  font=fb(52 if ctype == "ab" else 48), fill=(28, 30, 38))
        return

    # ── bold label ────────────────────────────────────────────────────────────
    if ctype == "b":
        draw.text((col_x+PAD, cy-28), text, font=fb(52), fill=(28, 30, 38))
        return

    # ── centered text ─────────────────────────────────────────────────────────
    if ctype == "c":
        f   = fr(44)
        cx2 = col_x + (col_w - tw(draw, text, f)) // 2
        draw.text((cx2, cy-24), text, font=f, fill=(55, 60, 75))
        return

    # ── regular text ──────────────────────────────────────────────────────────
    draw.text((col_x+PAD, cy-26), text, font=fr(48), fill=(55, 60, 75))


def generate(p):
    W, H  = 2000, 2000
    color = p["color"]
    light = p["light"]

    # ── Dark background with subtle product color tint ────────────────────────
    bg = tuple(max(0, int(c * 0.07) + 8) for c in color)
    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    for y in range(H):
        t = y / H
        rc = tuple(int(bg[i] * (1 - t * 0.45)) for i in range(3))
        draw.line([(0, y), (W, y)], fill=rc)

    # Ambient glow top-left (product color, subtle)
    for r in range(380, 0, -12):
        t  = (380 - r) / 380
        gc = tuple(int(c * 0.20 * (1 - t)) for c in color)
        draw.ellipse([-r, -r, r, r], fill=gc)

    # ── HEADER (y=0 to y=270) ────────────────────────────────────────────────
    # Product label pill
    lf = fb(42)
    lw = tw(draw, p["label"], lf)
    pill(draw, 80, 44, 80+lw+50, 108, color, 22)
    draw.text((106, 57), p["label"], font=lf, fill=(255, 255, 255))

    # INSTANT DOWNLOAD badge (top right)
    it  = "INSTANT DOWNLOAD"
    if_ = fb(34)
    iw  = tw(draw, it, if_)
    pill(draw, W-iw-128, 40, W-66, 110, (255, 255, 255), 26)
    draw.text((W-iw-108, 54), it, font=if_,
              fill=tuple(max(0, int(c * 0.75)) for c in color))

    # Title (large white, 2 lines)
    lines = p["headline"].split("\n")
    draw.text((80, 128), lines[0], font=fb(114), fill=(255, 255, 255))
    if len(lines) > 1:
        lc = tuple(min(255, int(c * 1.3 + 80)) for c in color)
        draw.text((80, 252), lines[1], font=fb(92), fill=lc)

    # ── MACBOOK FRAME (y=300 to y=1640) ──────────────────────────────────────
    LX0, LY0 = 55,  300
    LX1, LY1 = 1945, 1640
    R = 30

    MAC_BODY = (36, 38, 45)
    # Rounded body
    draw.rectangle([LX0+R, LY0, LX1-R, LY1], fill=MAC_BODY)
    draw.rectangle([LX0, LY0+R, LX1, LY1-R], fill=MAC_BODY)
    for cx, cy in [(LX0,LY0),(LX1-2*R,LY0),(LX0,LY1-2*R),(LX1-2*R,LY1-2*R)]:
        draw.ellipse([cx, cy, cx+2*R, cy+2*R], fill=MAC_BODY)
    # Top edge highlight
    draw.rectangle([LX0+R, LY0, LX1-R, LY0+4], fill=(62, 65, 75))

    # Camera
    cam_x, cam_y = W//2, LY0+26
    draw.ellipse([cam_x-8, cam_y-8, cam_x+8, cam_y+8], fill=(55, 58, 68))

    # Screen area
    SX0, SY0 = LX0+44, LY0+52
    SX1, SY1 = LX1-44, LY1-42
    SW_S = SX1 - SX0   # ~1857
    SH_S = SY1 - SY0   # ~1246
    draw.rectangle([SX0, SY0, SX1, SY1], fill=(7, 9, 18))

    # ── Mini spreadsheet inside screen ───────────────────────────────────────
    COL_TOTAL = sum(cw for _, cw in p["cols"])
    scale     = SW_S / COL_TOTAL

    # Browser chrome (38px)
    BCH = 38
    draw.rectangle([SX0, SY0, SX1, SY0+BCH], fill=(24, 26, 36))
    for i, dc in enumerate([(175,60,58),(178,148,45),(52,155,75)]):
        ox = SX0 + 14 + i*20
        draw.ellipse([ox, SY0+11, ox+14, SY0+25], fill=dc)
    draw.rectangle([SX0+82, SY0+8, SX1-72, SY0+30], fill=(36, 38, 50))
    draw.text((SX0+96, SY0+12),
              "docs.google.com  —  " + p["sheet_title"],
              font=fr(16), fill=(105, 112, 135))

    # Sheet title bar (product color, 64px)
    TBH = 64
    TT  = SY0 + BCH
    draw.rectangle([SX0, TT, SX1, TT+TBH], fill=color)
    draw.text((SX0+18, TT+16), p["sheet_title"], font=fb(36), fill=(255, 255, 255))

    # Column headers (50px)
    CHH = 50
    CT  = TT + TBH
    draw.rectangle([SX0, CT, SX1, CT+CHH], fill=light)
    x   = SX0
    col_xs_s, col_ws_s = [], []
    for i, (cname, cw) in enumerate(p["cols"]):
        cw_s = int(cw * scale)
        col_xs_s.append(x)
        col_ws_s.append(cw_s)
        if i > 0:
            draw.line([(x, CT), (x, SY1)], fill=(190, 202, 218), width=1)
        draw.text((x+10, CT+(CHH-24)//2), cname[:14], font=fb(24),
                  fill=tuple(max(0, int(c*0.62)) for c in color))
        x += cw_s

    # Data rows (show first 4)
    ROWS_T  = CT + CHH
    nrows   = min(4, len(p["rows"]))
    ROW_H_S = (SY1 - ROWS_T) // nrows
    PC_S = {"g":(34,164,85),"y":(210,140,18),"bad":(214,62,45),"n":(140,148,162)}

    for ri in range(nrows):
        ry    = ROWS_T + ri * ROW_H_S
        bg_r  = (15, 17, 28) if ri % 2 == 0 else (11, 13, 22)
        is_last = ri == nrows - 1
        if is_last:
            bg_r = tuple(int(c * 0.18) for c in color)
        draw.rectangle([SX0, ry, SX1, ry+ROW_H_S], fill=bg_r)
        draw.line([(SX0, ry+ROW_H_S),(SX1, ry+ROW_H_S)],
                  fill=(26, 30, 46), width=1)

        if ri >= len(p["rows"]):
            continue
        for ci, (ct_text, ctype) in enumerate(p["rows"][ri]):
            if ci >= len(col_xs_s) or not ct_text or not ctype:
                continue
            cx_s = col_xs_s[ci]
            cw_s = col_ws_s[ci]
            cy_s = ry + ROW_H_S // 2

            if ctype in ("g", "y", "bad", "n"):
                pc = PC_S.get(ctype, (100,100,100))
                pf = fr(20)
                pw = min(tw(draw, ct_text, pf)+22, cw_s-14)
                pill(draw, cx_s+8, cy_s-15, cx_s+8+pw, cy_s+15, pc)
                draw.text((cx_s+18, cy_s-11), ct_text, font=pf, fill=(255,255,255))

            elif ctype == "p":
                try:   pct = int(ct_text.replace("%",""))/100
                except: pct = 0.5
                bw = cw_s - 38
                pill(draw, cx_s+8, cy_s-8, cx_s+8+bw, cy_s+8, (38,42,58))
                pill(draw, cx_s+8, cy_s-8, cx_s+8+max(8,int(bw*pct)), cy_s+8, color)

            elif ctype == "r":
                draw.text((cx_s+10, cy_s-13), ct_text, font=fb(24), fill=(210,85,75))

            elif ctype in ("a", "ab"):
                draw.text((cx_s+10, cy_s-13), ct_text,
                          font=fb(26 if ctype=="ab" else 24), fill=(205,215,235))

            elif ctype == "b":
                draw.text((cx_s+10, cy_s-13), ct_text, font=fb(26), fill=(225,230,248))

            elif ctype == "c":
                f   = fr(24)
                cx2 = cx_s + (cw_s - tw(draw, ct_text, f)) // 2
                draw.text((cx2, cy_s-13), ct_text, font=f, fill=(155,168,200))

            else:
                draw.text((cx_s+10, cy_s-13), ct_text, font=fr(26), fill=(165,178,215))

    # Screen reflection (subtle)
    for y in range(SY0, SY0+70):
        t  = (y - SY0) / 70
        rc = tuple(int(255 * 0.05 * (1 - t)) for _ in range(3))
        draw.line([(SX0, y), (SX1, y)], fill=rc)

    # ── KEYBOARD BASE ─────────────────────────────────────────────────────────
    KB_X0, KB_X1 = LX0-28, LX1+28
    KB_Y0, KB_Y1 = LY1, LY1+88
    draw.rectangle([KB_X0, KB_Y0, KB_X1, KB_Y1], fill=(27, 29, 35))
    draw.rectangle([LX0, LY1-3, LX1, LY1+3], fill=(20, 22, 28))
    TP_W, TP_H = 310, 56
    TP_X = W//2 - TP_W//2
    draw.rectangle([TP_X, KB_Y0+16, TP_X+TP_W, KB_Y0+16+TP_H], fill=(38, 40, 48))

    # ── BENEFITS (y≈1750 to y=2000) ───────────────────────────────────────────
    BY = KB_Y1 + 20
    rf = fr(44)
    bx = 80
    for i, ben in enumerate(p["benefits"]):
        draw.ellipse([bx, BY+18+i*76, bx+50, BY+68+i*76], fill=color)
        draw.text((bx+13, BY+28+i*76), "✓", font=fb(28), fill=(255, 255, 255))
        draw.text((bx+70, BY+22+i*76), ben, font=rf, fill=(175, 192, 228))

    url = "nasritools.etsy.com"
    uf  = fr(30)
    draw.text((W - tw(draw, url, uf) - 80, BY+244), url, font=uf,
              fill=tuple(min(255, int(c * 0.8)) for c in color))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf


# ── Etsy API ──────────────────────────────────────────────────────────────────
def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def auth_headers(token):
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}

def fetch_listings(token):
    results, offset = [], 0
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset}, timeout=30,
        )
        batch = r.json().get("results", [])
        results.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
    return results

def find_listing(listings, kws):
    for l in listings:
        title = (l.get("title") or "").lower()
        if all(k in title for k in kws):
            return l["listing_id"]
    return None

def upload(token, lid, buf):
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}/images",
        headers=auth_headers(token),
        files={"image": ("cover.jpg", buf, "image/jpeg")},
        data={"rank": 1, "overwrite": "true"}, timeout=60,
    )
    return r.ok, r.status_code


def main():
    token    = get_token()
    listings = fetch_listings(token)
    print(f"\n{'='*65}")
    print(f"  NasriTools - Product Dashboard Covers (v2 large text)")
    print(f"{'='*65}\n")

    ok = 0
    for i, p in enumerate(PRODUCTS, 1):
        lid = find_listing(listings, p["search_kw"])
        print(f"[{i}/10] {p['label']}", end=" ")
        if not lid:
            print(f"— NOT FOUND (kw: {p['search_kw']})")
            continue
        print(f"[{lid}]")

        print(f"  Generating...", end=" ", flush=True)
        try:
            buf = generate(p)
            print("done", end=" ")
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        token = get_token()
        ok_, code = upload(token, lid, buf)
        print(f"| Upload: {'OK' if ok_ else f'FAIL {code}'}")
        if ok_:
            ok += 1
        time.sleep(2)

    print(f"\n{'='*65}")
    print(f"  Done: {ok}/10 product covers updated")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
