"""
NasriTools - Product Cover Images (Dashboard Style)
Shows real spreadsheet data inside each product image.
Run: python generate_product_covers.py
"""
import io, json, os, time, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

PRODUCTS = [
    {
        "search_kw": ["budget", "expense"],
        "color": (20, 115, 60), "light": (220, 247, 233),
        "label": "BUDGET TRACKER",
        "headline": "Know Where Every\nEuro Goes.",
        "benefits": ["Auto expense tracking", "Savings goals on autopilot", "Zero manual math"],
        "sheet_title": "Monthly Budget & Expense System",
        "cols": [("CATEGORY", 370), ("BUDGET", 220), ("SPENT", 220), ("REMAINING", 220), ("STATUS", 830)],
        "rows": [
            [("Housing & Rent",  "t"), ("€800",   "a"), ("€795",   "a"), ("€5",    "a"),  ("On Track",    "g")],
            [("Groceries",       "t"), ("€300",   "a"), ("€267",   "a"), ("€33",   "a"),  ("On Track",    "g")],
            [("Transport",       "t"), ("€120",   "a"), ("€145",   "a"), ("-€25",  "r"),  ("Over Budget", "bad")],
            [("Savings Goal",    "t"), ("€500",   "a"), ("€500",   "a"), ("€0",    "a"),  ("Saved",       "g")],
            [("Entertainment",   "t"), ("€100",   "a"), ("€72",    "a"), ("€28",   "a"),  ("Under Budget","g")],
            [("Utilities",       "t"), ("€150",   "a"), ("€143",   "a"), ("€7",    "a"),  ("On Track",    "g")],
            [("TOTAL",           "b"), ("€1,970", "ab"),("€1,922", "ab"),("€48",   "ab"), ("Surplus: €48","g")],
        ],
    },
    {
        "search_kw": ["habit", "building"],
        "color": (192, 57, 43), "light": (253, 228, 224),
        "label": "HABIT TRACKER",
        "headline": "30 Habits.\nAutomatic Streaks.",
        "benefits": ["Track 30 habits daily", "Auto streak counter", "Visual progress every day"],
        "sheet_title": "30-Day Habit Building System",
        "cols": [("HABIT", 480), ("MON", 140), ("TUE", 140), ("WED", 140), ("THU", 140), ("FRI", 140), ("SAT", 140), ("STREAK", 540)],
        "rows": [
            [("Morning Run",   "t"), ("OK","g"), ("OK","g"), ("OK","g"), ("OK","g"), ("OK","g"), ("OK","g"), ("6-day streak","g")],
            [("Read 30 min",   "t"), ("OK","g"), ("OK","g"), ("--","n"), ("OK","g"), ("OK","g"), ("OK","g"), ("5-day streak","g")],
            [("No Sugar",      "t"), ("OK","g"), ("OK","g"), ("OK","g"), ("--","n"), ("OK","g"), ("OK","g"), ("4-day streak","y")],
            [("Meditate",      "t"), ("--","n"), ("OK","g"), ("OK","g"), ("OK","g"), ("OK","g"), ("OK","g"), ("5-day streak","g")],
            [("Cold Shower",   "t"), ("OK","g"), ("--","n"), ("OK","g"), ("OK","g"), ("OK","g"), ("--","n"), ("3-day streak","y")],
            [("1L Water",      "t"), ("OK","g"), ("OK","g"), ("OK","g"), ("OK","g"), ("OK","g"), ("OK","g"), ("6-day streak","g")],
            [("DAY 18/30",     "b"), ("",  ""),  ("",  ""),  ("",  ""),  ("",  ""),  ("",  ""),  ("",  ""),  ("83% complete","g")],
        ],
    },
    {
        "search_kw": ["meal", "planning"],
        "color": (39, 174, 141), "light": (209, 250, 229),
        "label": "MEAL PLANNER",
        "headline": "7 Days of Meals\nin 15 Minutes.",
        "benefits": ["Auto grocery list", "Nutrition tracked", "Save €80+ weekly"],
        "sheet_title": "Weekly Meal Planning System",
        "cols": [("DAY", 200), ("BREAKFAST", 400), ("LUNCH", 400), ("DINNER", 400), ("CALORIES", 460)],
        "rows": [
            [("Monday",    "c"), ("Oats + Banana",    "t"), ("Chicken & Rice",  "t"), ("Salmon + Veg",    "t"), ("1,850 kcal","a")],
            [("Tuesday",   "c"), ("Eggs + Toast",     "t"), ("Greek Salad",     "t"), ("Beef Stir-fry",   "t"), ("1,720 kcal","a")],
            [("Wednesday", "c"), ("Smoothie Bowl",    "t"), ("Tuna Wrap",       "t"), ("Pasta Bolognese", "t"), ("1,900 kcal","a")],
            [("Thursday",  "c"), ("Yogurt + Berries", "t"), ("Lentil Soup",     "t"), ("Grilled Chicken", "t"), ("1,650 kcal","a")],
            [("Friday",    "c"), ("Avocado Toast",    "t"), ("Caesar Salad",    "t"), ("Pizza Night",     "t"), ("2,100 kcal","a")],
            [("Saturday",  "c"), ("Pancakes",         "t"), ("Veggie Burger",   "t"), ("Sushi",           "t"), ("2,200 kcal","a")],
            [("GROCERIES", "b"), ("Auto-generated",   "t"), ("47 items",        "t"), ("€62 total",       "t"), ("Save €80+", "g")],
        ],
    },
    {
        "search_kw": ["wedding", "planning"],
        "color": (210, 82, 162), "light": (252, 228, 243),
        "label": "WEDDING PLANNER",
        "headline": "Plan Your Perfect\nWedding.",
        "benefits": ["Budget tracked to the cent", "All vendors in one place", "Zero missed details"],
        "sheet_title": "Complete Wedding Planning System",
        "cols": [("CATEGORY", 360), ("BUDGET", 220), ("SPENT", 220), ("VENDOR", 440), ("STATUS", 620)],
        "rows": [
            [("Venue",        "t"), ("€5,000","a"), ("€4,800","a"), ("Sunny Gardens",  "t"), ("Booked",    "g")],
            [("Catering",     "t"), ("€3,500","a"), ("€3,500","a"), ("Chef Marco",     "t"), ("Booked",    "g")],
            [("Photography",  "t"), ("€1,800","a"), ("€900",  "a"), ("Studio Luz",     "t"), ("Deposit",   "y")],
            [("Flowers",      "t"), ("€600",  "a"), ("€0",    "a"), ("TBD",            "t"), ("Pending",   "y")],
            [("Music / DJ",   "t"), ("€800",  "a"), ("€800",  "a"), ("DJ Marcos",      "t"), ("Booked",    "g")],
            [("Dress",        "t"), ("€1,200","a"), ("€1,200","a"), ("Bridal Boutique","t"), ("Ready",     "g")],
            [("TOTAL",        "b"), ("€12,900","ab"),("€11,200","ab"),("",              ""),  ("€1,700 left","y")],
        ],
    },
    {
        "search_kw": ["workout", "tracking"],
        "color": (192, 57, 43), "light": (253, 228, 224),
        "label": "WORKOUT TRACKER",
        "headline": "See Your Strength\nGrow Every Session.",
        "benefits": ["PRs tracked automatically", "Progress charts auto-generated", "Beat last week every time"],
        "sheet_title": "Gym & Workout Tracking System",
        "cols": [("EXERCISE", 420), ("SETS", 190), ("REPS", 190), ("WEIGHT", 240), ("PROGRESS", 820)],
        "rows": [
            [("Bench Press",    "t"), ("4","c"), ("8", "c"), ("80 kg", "c"), ("82%","p")],
            [("Squats",         "t"), ("4","c"), ("6", "c"), ("100 kg","c"), ("91%","p")],
            [("Deadlift",       "t"), ("3","c"), ("5", "c"), ("120 kg","c"), ("78%","p")],
            [("Pull-Ups",       "t"), ("4","c"), ("10","c"), ("BW",    "c"), ("95%","p")],
            [("Shoulder Press", "t"), ("3","c"), ("10","c"), ("55 kg", "c"), ("70%","p")],
            [("Bicep Curls",    "t"), ("3","c"), ("12","c"), ("22 kg", "c"), ("88%","p")],
            [("THIS WEEK",      "b"), ("", ""),  ("",  ""),  ("",     ""),   ("New PR: +5%","g")],
        ],
    },
    {
        "search_kw": ["content", "creator"],
        "color": (230, 126, 34), "light": (254, 243, 224),
        "label": "CONTENT CREATOR",
        "headline": "From Posting Randomly\nto Growing Systematically.",
        "benefits": ["3 months planned in 1 weekend", "Analytics tracked weekly", "Brand deals never missed"],
        "sheet_title": "Content Creator Business System",
        "cols": [("PLATFORM", 280), ("POST / TITLE", 520), ("DATE", 200), ("VIEWS", 200), ("STATUS", 660)],
        "rows": [
            [("Instagram",  "t"), ("5 Morning Habits",         "t"), ("Jun 01","c"), ("12.4K","a"), ("Published",  "g")],
            [("YouTube",    "t"), ("How I Budget €2k/month",   "t"), ("Jun 03","c"), ("8.2K", "a"), ("Published",  "g")],
            [("TikTok",     "t"), ("Meal Prep Sunday Routine", "t"), ("Jun 05","c"), ("31K",  "a"), ("Published",  "g")],
            [("Instagram",  "t"), ("Weekly Workout Split",     "t"), ("Jun 08","c"), ("9.1K", "a"), ("Scheduled",  "y")],
            [("YouTube",    "t"), ("Google Sheets Tutorial",   "t"), ("Jun 10","c"), ("--",   "c"), ("Draft",      "y")],
            [("Brand Deal", "t"), ("SkinCare Co. — €350",      "t"), ("Jun 15","c"), ("--",   "c"), ("Invoice Sent","y")],
            [("JUNE TOTAL", "b"), ("6 posts planned",          "t"), ("",      ""),  ("",     ""),  ("On Schedule","g")],
        ],
    },
    {
        "search_kw": ["invoice", "client"],
        "color": (52, 152, 219), "light": (214, 234, 248),
        "label": "INVOICE TRACKER",
        "headline": "Stop Chasing Invoices.\nGet Paid on Time.",
        "benefits": ["All invoices at a glance", "Tax prep ready instantly", "Revenue calculated auto"],
        "sheet_title": "Freelancer Invoice & Client System",
        "cols": [("CLIENT", 360), ("INVOICE #", 230), ("AMOUNT", 230), ("DUE DATE", 270), ("STATUS", 770)],
        "rows": [
            [("Studio Bright",  "t"), ("#INV-047","c"), ("€1,200","a"), ("Jun 01","c"), ("Paid",         "g")],
            [("Nova Agency",    "t"), ("#INV-048","c"), ("€850",  "a"), ("Jun 05","c"), ("Paid",         "g")],
            [("TechStart GmbH", "t"), ("#INV-049","c"), ("€2,400","a"), ("Jun 15","c"), ("Pending",      "y")],
            [("Bloom Creative", "t"), ("#INV-050","c"), ("€650",  "a"), ("Jun 20","c"), ("Sent",         "y")],
            [("MindSpace Co.",  "t"), ("#INV-051","c"), ("€1,800","a"), ("Jun 22","c"), ("Pending",      "y")],
            [("RetailPro Ltd",  "t"), ("#INV-052","c"), ("€3,200","a"), ("Jun 30","c"), ("Overdue",      "bad")],
            [("JUNE TOTAL",     "b"), ("",        ""),  ("€10,100","ab"),("",      ""),  ("€5,700 pending","y")],
        ],
    },
    {
        "search_kw": ["student", "academic"],
        "color": (108, 52, 131), "light": (237, 228, 252),
        "label": "STUDENT PLANNER",
        "headline": "Ace Your Semester.\nGPA Tracked. Deadlines Met.",
        "benefits": ["Zero missed deadlines", "GPA calculated live", "Exam ready every time"],
        "sheet_title": "Student Academic Success System",
        "cols": [("SUBJECT", 370), ("ASSIGNMENT", 480), ("DUE DATE", 240), ("GRADE", 200), ("STATUS", 570)],
        "rows": [
            [("Mathematics",  "t"), ("Problem Set 8",        "t"), ("Jun 05","c"), ("94/100","a"), ("Submitted",  "g")],
            [("Economics",    "t"), ("Market Analysis Essay","t"), ("Jun 08","c"), ("88/100","a"), ("Submitted",  "g")],
            [("Data Science", "t"), ("ML Model Project",     "t"), ("Jun 12","c"), ("--",    "c"), ("In Progress","y")],
            [("Marketing",    "t"), ("Brand Strategy Deck",  "t"), ("Jun 15","c"), ("--",    "c"), ("In Progress","y")],
            [("Statistics",   "t"), ("Final Exam",           "t"), ("Jun 20","c"), ("--",    "c"), ("Studying",   "y")],
            [("Thesis",       "t"), ("Chapter 3 Draft",      "t"), ("Jun 30","c"), ("--",    "c"), ("Pending",    "y")],
            [("CURRENT GPA",  "b"), ("3.8 / 4.0",            "t"), ("",      ""),  ("",      ""),  ("Top 15%",   "g")],
        ],
    },
    {
        "search_kw": ["annual", "goal"],
        "color": (30, 100, 180), "light": (220, 235, 252),
        "label": "GOALS PLANNER",
        "headline": "Stop Setting Goals.\nStart Achieving Them.",
        "benefits": ["Goals broken into weekly steps", "90-day sprint plan", "Progress tracked %"],
        "sheet_title": "Annual Goals & 90-Day Action System",
        "cols": [("GOAL", 440), ("DEADLINE", 240), ("PROGRESS", 480), ("THIS WEEK", 500), ("STATUS", 200)],
        "rows": [
            [("Launch Online Course",    "t"), ("Dec 31","c"), ("45%","p"), ("Record 3 videos",  "t"), ("On Track","g")],
            [("Save €10,000",            "t"), ("Dec 31","c"), ("62%","p"), ("Save €400 more",   "t"), ("On Track","g")],
            [("Run Half Marathon",       "t"), ("Sep 15","c"), ("70%","p"), ("Long run 16km",    "t"), ("On Track","g")],
            [("Read 24 Books",           "t"), ("Dec 31","c"), ("54%","p"), ("Finish Chapter 8", "t"), ("On Track","g")],
            [("Grow to 10K followers",   "t"), ("Dec 31","c"), ("38%","p"), ("Post 5x this week","t"), ("Behind",  "y")],
            [("Learn Spanish B2",        "t"), ("Jun 30","c"), ("80%","p"), ("30 min daily",     "t"), ("On Track","g")],
            [("Q2 SPRINT SCORE",         "b"), ("",       ""),  ("",   ""),  ("",                 ""),  ("5/6 goals","g")],
        ],
    },
    {
        "search_kw": ["weekly", "productivity"],
        "color": (108, 52, 131), "light": (237, 228, 252),
        "label": "WEEKLY PLANNER",
        "headline": "Plan Your Perfect Week\nin 15 Minutes.",
        "benefits": ["Time-blocked for deep work", "Top 3 priorities always done", "2x more done, 50% less stress"],
        "sheet_title": "Weekly Productivity System",
        "cols": [("TASK", 490), ("PRIORITY", 220), ("TIME BLOCK", 300), ("DUE", 240), ("STATUS", 610)],
        "rows": [
            [("Deep Work: Project A",  "t"), ("HIGH","bad"), ("08:00-11:00","c"), ("Today","c"), ("In Progress","y")],
            [("Weekly Review",         "t"), ("HIGH","bad"), ("07:00-07:30","c"), ("Mon",  "c"), ("Done",       "g")],
            [("Client Presentation",   "t"), ("HIGH","bad"), ("14:00-15:00","c"), ("Tue",  "c"), ("Done",       "g")],
            [("Study: Data Analysis",  "t"), ("MED", "y"),   ("19:00-21:00","c"), ("Wed",  "c"), ("Pending",    "y")],
            [("Gym Session",           "t"), ("MED", "y"),   ("17:00-18:30","c"), ("Daily","c"), ("Done",       "g")],
            [("Review Goals & KPIs",   "t"), ("HIGH","bad"), ("18:00-18:30","c"), ("Fri",  "c"), ("Pending",    "y")],
            [("WEEK SCORE",            "b"), ("",    ""),    ("",           ""),  ("",     ""),  ("83% done",   "g")],
        ],
    },
]

_BOLD = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
_REG = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def _f(p, s):
    for path in p:
        if Path(path).exists():
            return ImageFont.truetype(path, s)
    return ImageFont.load_default()

def fb(s): return _f(_BOLD, s)
def fr(s): return _f(_REG, s)

def tw(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[2] - bb[0]

def pill(draw, x0, y0, x1, y1, fill, r=None):
    r = r or (y1-y0)//2
    r = min(r, (x1-x0)//2, (y1-y0)//2)
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx,cy in [(x0,y0),(x1-2*r,y0),(x0,y1-2*r),(x1-2*r,y1-2*r)]:
        draw.ellipse([cx,cy,cx+2*r,cy+2*r], fill=fill)

PILL_COLORS = {
    "g":   (34, 164, 85),
    "y":   (230, 152, 18),
    "bad": (214, 62, 45),
    "n":   (160, 165, 175),
}

def draw_cell(draw, col_x, col_w, row_y, row_h, text, ctype, color):
    if not text or not ctype: return
    cy = row_y + row_h // 2
    PAD = 16

    if ctype == "p":
        pct = int(text.replace("%","")) / 100
        bx, by = col_x+PAD, cy-12
        bw = col_w - PAD*2 - 65
        pill(draw, bx, by, bx+bw, by+24, (215,220,232))
        pill(draw, bx, by, bx+max(14,int(bw*pct)), by+24, color)
        draw.text((bx+bw+8, by-1), text, font=fb(26), fill=color)
        return

    if ctype in ("g","y","bad","n"):
        pc = PILL_COLORS[ctype]
        f  = fr(26)
        tw_ = tw(draw, text, f)
        pw = min(tw_+34, col_w-PAD*2)
        px0 = col_x + PAD
        py0 = cy - 19
        pill(draw, px0, py0, px0+pw, py0+38, pc)
        draw.text((px0+17, py0+6), text, font=f, fill=(255,255,255))
        return

    if ctype == "r":
        draw.text((col_x+PAD, cy-18), text, font=fb(30), fill=(214,62,45))
        return

    if ctype in ("a","ab"):
        draw.text((col_x+PAD, cy-19), text, font=fb(32 if ctype=="ab" else 30), fill=(28,30,38))
        return

    if ctype == "b":
        draw.text((col_x+PAD, cy-19), text, font=fb(30), fill=(28,30,38))
        return

    if ctype == "c":
        f = fr(28)
        cx2 = col_x + (col_w - tw(draw, text, f))//2
        draw.text((cx2, cy-16), text, font=f, fill=(55,60,75))
        return

    draw.text((col_x+PAD, cy-17), text, font=fr(30), fill=(55,60,75))


def generate(p):
    W, H  = 2000, 2000
    color = p["color"]
    light = p["light"]

    img  = Image.new("RGB", (W, H), (245,247,250))
    draw = ImageDraw.Draw(img)

    # ── HEADER (0-280) ────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 280], fill=color)
    # diagonal accent
    dark = tuple(max(0,int(c*0.72)) for c in color)
    draw.polygon([(W-420,0),(W,0),(W,280)], fill=dark)

    # label badge (top-left)
    draw.text((78, 22), p["label"], font=fb(38), fill=(255,255,255))

    # INSTANT DOWNLOAD pill (top-right)
    it = "INSTANT DOWNLOAD"
    if_ = fb(32)
    iw = tw(draw, it, if_)
    pill(draw, W-iw-120, 18, W-60, 80, (255,255,255), 20)
    draw.text((W-iw-100, 28), it, font=if_, fill=color)

    # Headline (2 lines)
    lines = p["headline"].split("\n")
    h1f = fb(88)
    h2f = fb(72)
    draw.text((78, 98), lines[0], font=h1f, fill=(255,255,255))
    if len(lines) > 1:
        draw.text((78, 196), lines[1], font=h2f, fill=(255,255,255))

    # ── SPREADSHEET MOCKUP (300-1680) ────────────────────────────────────────
    SL, SR = 68, W-68
    ST, SB = 300, 1680
    SW     = SR - SL

    # shadow
    draw.rectangle([SL+7, ST+7, SR+7, SB+7], fill=(195,202,215))
    # white bg
    draw.rectangle([SL, ST, SR, SB], fill=(255,255,255))

    # browser chrome
    CH = 48
    draw.rectangle([SL, ST, SR, ST+CH], fill=(241,243,245))
    for i, dc in enumerate([(232,72,72),(252,185,60),(36,168,90)]):
        ox = SL+20+i*30
        draw.ellipse([ox, ST+13, ox+22, ST+35], fill=dc)
    pill(draw, SL+110, ST+11, SR-100, ST+38, (255,255,255), 6)
    draw.text((SL+130, ST+14),
              "docs.google.com  —  " + p["sheet_title"],
              font=fr(19), fill=(100,105,118))

    # sheet title bar
    TT = ST+CH
    draw.rectangle([SL, TT, SR, TT+54], fill=color)
    draw.text((SL+22, TT+11), p["sheet_title"], font=fb(32), fill=(255,255,255))

    # col headers
    CT = TT+54
    COL_H = 48
    draw.rectangle([SL, CT, SR, CT+COL_H], fill=light)

    cols   = p["cols"]
    col_xs = []
    x      = SL
    for i,(cname,cw) in enumerate(cols):
        col_xs.append(x)
        if i>0:
            draw.line([(x,CT),(x,SB)], fill=(210,218,230), width=2)
        cf = fb(26)
        draw.text((x+16, CT+(COL_H-22)//2), cname, font=cf, fill=tuple(max(0,int(c*0.72)) for c in color))
        x += cw

    # rows
    RT    = CT+COL_H
    nrows = len(p["rows"])
    ROW_H = (SB-RT)//nrows

    for ri, row in enumerate(p["rows"]):
        ry = RT + ri*ROW_H
        is_last = (ri == nrows-1)
        bg = light if is_last else ((251,252,254) if ri%2==0 else (255,255,255))
        draw.rectangle([SL, ry, SR, ry+ROW_H], fill=bg)
        draw.line([(SL, ry+ROW_H),(SR, ry+ROW_H)],
                  fill=tuple(int(c*0.92) for c in light) if is_last else (220,226,235),
                  width=1)
        for ci,(ct,ctype) in enumerate(row):
            draw_cell(draw, col_xs[ci], cols[ci][1], ry, ROW_H, ct, ctype, color)

    draw.rectangle([SL, ST, SR, SB], outline=(195,202,215), width=2)

    # ── BENEFITS STRIP (1700-2000) ────────────────────────────────────────────
    BY = 1700
    draw.rectangle([0, BY, W, H], fill=color)

    bf = fb(40)
    rf = fr(36)
    bx = 78
    for i, ben in enumerate(p["benefits"]):
        # checkmark circle
        draw.ellipse([bx, BY+30+i*88, bx+48, BY+78+i*88], fill=(255,255,255))
        draw.text((bx+14, BY+40+i*88), "✓", font=fb(28), fill=color)
        draw.text((bx+68, BY+35+i*88), ben, font=rf, fill=(255,255,255))

    url = "nasritools.etsy.com"
    uf  = fr(28)
    draw.text((W-tw(draw,url,uf)-78, BY+248), url, font=uf,
              fill=tuple(min(255,int(c*1.4)) for c in color))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf


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
        if len(batch) < 100: break
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
    print(f"  NasriTools - Product Dashboard Covers")
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
        if ok_: ok += 1
        time.sleep(2)

    print(f"\n{'='*65}")
    print(f"  Done: {ok}/10 product covers updated")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
