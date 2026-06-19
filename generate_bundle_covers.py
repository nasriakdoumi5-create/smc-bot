"""
NasriTools - Bundle Cover Images (v4-pro)
Professional Google Sheets mockup — dark header + live spreadsheet preview.
Run: python generate_bundle_covers.py
"""
import io, json, os, time, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

# ── Bundle definitions ───────────────────────────────────────────────────────
BUNDLES = [
    {
        "listing_id": 4524283886,
        "color":   (18, 78, 155),
        "accent":  (100, 190, 255),
        "light":   (214, 234, 255),
        "badge":   "3 SYSTEMS  ·  SAVE 33%",
        "line1":   "Total Financial Control.",
        "line2":   "Budget. Invoices. Goals.",
        "result":  "Know where every euro goes. Get paid on time. Achieve every goal.",
        "price":   "€19.99",
        "worth":   "worth €37",
        "sheet_title": "Monthly Budget & Expense System",
        "cols": [("CATEGORY", 400), ("BUDGET", 230), ("SPENT", 230), ("REMAINING", 230), ("STATUS", 750)],
        "rows": [
            [("Housing & Rent",  "t"), ("€800",   "a"), ("€795",   "a"), ("€5",    "a"),  ("On Track",    "g")],
            [("Groceries",       "t"), ("€300",   "a"), ("€267",   "a"), ("€33",   "a"),  ("On Track",    "g")],
            [("Transport",       "t"), ("€120",   "a"), ("€145",   "a"), ("-€25",  "ar"), ("Over Budget", "r")],
            [("Savings Goal",    "t"), ("€500",   "a"), ("€500",   "a"), ("€0",    "a"),  ("Saved",       "g")],
            [("Entertainment",   "t"), ("€100",   "a"), ("€72",    "a"), ("€28",   "a"),  ("Under Budget","g")],
            [("Utilities",       "t"), ("€150",   "a"), ("€143",   "a"), ("€7",    "a"),  ("On Track",    "g")],
            [("TOTAL",           "b"), ("€1,970", "ab"),("€1,922", "ab"),("€48",   "ab"), ("Surplus: €48","g")],
        ],
    },
    {
        "listing_id": 4524724720,
        "color":   (15, 115, 55),
        "accent":  (100, 255, 160),
        "light":   (209, 250, 229),
        "badge":   "3 SYSTEMS  ·  SAVE 50%",
        "line1":   "Transform Your Health.",
        "line2":   "Workout. Eat. Build Habits.",
        "result":  "Track every session. Plan every meal. Build 30 habits — automatically.",
        "price":   "€17.99",
        "worth":   "worth €36",
        "sheet_title": "Gym & Workout Tracking System",
        "cols": [("EXERCISE", 450), ("SETS", 190), ("REPS", 190), ("WEIGHT", 240), ("PROGRESS", 770)],
        "rows": [
            [("Bench Press",    "t"), ("4", "c"), ("8",  "c"), ("80 kg",  "c"), ("82%", "p")],
            [("Squats",         "t"), ("4", "c"), ("6",  "c"), ("100 kg", "c"), ("91%", "p")],
            [("Deadlift",       "t"), ("3", "c"), ("5",  "c"), ("120 kg", "c"), ("78%", "p")],
            [("Pull-Ups",       "t"), ("4", "c"), ("10", "c"), ("BW",     "c"), ("95%", "p")],
            [("Shoulder Press", "t"), ("3", "c"), ("10", "c"), ("55 kg",  "c"), ("70%", "p")],
            [("Bicep Curls",    "t"), ("3", "c"), ("12", "c"), ("22 kg",  "c"), ("88%", "p")],
            [("THIS WEEK",      "b"), ("",  ""),  ("",   ""),  ("",       ""),  ("Personal Record!", "g")],
        ],
    },
    {
        "listing_id": 4524724758,
        "color":   (82, 28, 130),
        "accent":  (210, 160, 255),
        "light":   (237, 228, 252),
        "badge":   "3 SYSTEMS  ·  SAVE 50%",
        "line1":   "Master Your Time.",
        "line2":   "Weekly. Academic. Goals.",
        "result":  "Plan your perfect week. Ace every semester. Achieve every goal.",
        "price":   "€17.99",
        "worth":   "worth €36",
        "sheet_title": "Weekly Productivity System",
        "cols": [("TASK", 510), ("PRIORITY", 220), ("TIME BLOCK", 310), ("DUE", 240), ("STATUS", 560)],
        "rows": [
            [("Deep Work: Project A",  "t"), ("HIGH", "r"), ("08:00-11:00", "c"), ("Today", "c"), ("In Progress", "y")],
            [("Weekly Review",         "t"), ("HIGH", "r"), ("07:00-07:30", "c"), ("Mon",   "c"), ("Done",        "g")],
            [("Client Presentation",   "t"), ("HIGH", "r"), ("14:00-15:00", "c"), ("Tue",   "c"), ("Done",        "g")],
            [("Study: Data Analysis",  "t"), ("MED",  "y"), ("19:00-21:00", "c"), ("Wed",   "c"), ("Pending",     "y")],
            [("Gym Session",           "t"), ("MED",  "y"), ("17:00-18:30", "c"), ("Daily", "c"), ("Done",        "g")],
            [("Review Goals",          "t"), ("HIGH", "r"), ("18:00-18:30", "c"), ("Fri",   "c"), ("Pending",     "y")],
            [("WEEK SCORE",            "b"), ("",     ""),  ("",            ""),  ("",      ""),  ("83% Complete","g")],
        ],
    },
    {
        "listing_id": 4524724798,
        "color":   (168, 58, 8),
        "accent":  (255, 190, 110),
        "light":   (254, 235, 220),
        "badge":   "3 SYSTEMS  ·  SAVE 50%",
        "line1":   "Run Your Business.",
        "line2":   "Content. Invoices. Budget.",
        "result":  "Grow your audience. Get paid. Know your numbers — all in one system.",
        "price":   "€21.99",
        "worth":   "worth €43",
        "sheet_title": "Freelancer Invoice & Client System",
        "cols": [("CLIENT", 380), ("INVOICE #", 240), ("AMOUNT", 240), ("DUE DATE", 280), ("STATUS", 700)],
        "rows": [
            [("Studio Bright",  "t"), ("#INV-047", "c"), ("€1,200", "a"), ("Jun 01", "c"), ("Paid",      "g")],
            [("Nova Agency",    "t"), ("#INV-048", "c"), ("€850",   "a"), ("Jun 05", "c"), ("Paid",      "g")],
            [("TechStart GmbH", "t"), ("#INV-049", "c"), ("€2,400", "a"), ("Jun 15", "c"), ("Pending",   "y")],
            [("Bloom Creative", "t"), ("#INV-050", "c"), ("€650",   "a"), ("Jun 20", "c"), ("Sent",      "y")],
            [("MindSpace Co.",  "t"), ("#INV-051", "c"), ("€1,800", "a"), ("Jun 22", "c"), ("Pending",   "y")],
            [("RetailPro Ltd",  "t"), ("#INV-052", "c"), ("€3,200", "a"), ("Jun 30", "c"), ("Overdue",   "r")],
            [("JUNE TOTAL",     "b"), ("",         ""),  ("€10,100","ab"),("",        ""),  ("€5,700 due","y")],
        ],
    },
    {
        "listing_id": 4524724846,
        "color":   (14, 24, 92),
        "accent":  (120, 175, 255),
        "light":   (220, 230, 255),
        "badge":   "10 SYSTEMS  ·  SAVE 65%",
        "line1":   "Systems That Run",
        "line2":   "Your Entire Life.",
        "result":  "Finance. Health. Business. Planning. All 10 premium Google Sheets in one bundle.",
        "price":   "€39.99",
        "worth":   "worth €120",
        "sheet_title": "Complete Life System — All 10 Templates Included",
        "cols": [("SYSTEM", 490), ("CATEGORY", 290), ("KEY FEATURE", 720), ("STATUS", 340)],
        "rows": [
            [("Budget & Expense",    "t"), ("Finance",  "c"), ("Auto expense tracking + savings goals", "t"), ("Included", "g")],
            [("Invoice & Clients",   "t"), ("Business", "c"), ("Invoice tracker + payment status",      "t"), ("Included", "g")],
            [("Goals & 90-Day Plan", "t"), ("Planning", "c"), ("Break big goals into weekly actions",   "t"), ("Included", "g")],
            [("Gym & Workout",       "t"), ("Health",   "c"), ("Log reps, PRs, auto progress charts",   "t"), ("Included", "g")],
            [("Meal Planning",       "t"), ("Health",   "c"), ("7-day meals + auto grocery list",       "t"), ("Included", "g")],
            [("Habit Building",      "t"), ("Health",   "c"), ("30 habits + auto streak counter",       "t"), ("Included", "g")],
            [("+ 4 More Systems",    "b"), ("",         ""),  ("Content · Student · Weekly · Wedding",  "t"), ("Included", "g")],
        ],
    },
]

# ── Fonts ────────────────────────────────────────────────────────────────────
_BOLD = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
_REG = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]

def _f(paths, size):
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def fb(s): return _f(_BOLD, s)
def fr(s): return _f(_REG,  s)

# ── Color helpers ─────────────────────────────────────────────────────────────
def darken(c, f=0.78):
    return tuple(max(0, int(x * f)) for x in c)

def lighten(c, f=1.6):
    return tuple(min(255, int(x * f)) for x in c)

def mix_white(c, t=0.35):
    return tuple(int(c[i]*(1-t) + 255*t) for i in range(3))

# ── Drawing helpers ───────────────────────────────────────────────────────────
def pill(draw, x0, y0, x1, y1, fill, radius=None):
    r = radius if radius else (y1 - y0) // 2
    r = min(r, (x1-x0)//2, (y1-y0)//2)
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx, cy in [(x0,y0),(x1-2*r,y0),(x0,y1-2*r),(x1-2*r,y1-2*r)]:
        draw.ellipse([cx, cy, cx+2*r, cy+2*r], fill=fill)

def text_w(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[2] - bb[0]

def text_h(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[3] - bb[1]

def draw_text_center(draw, text, font, cx, y, fill):
    w = text_w(draw, text, font)
    draw.text((cx - w//2, y), text, font=font, fill=fill)

def wrap_lines(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_w(draw, test, font) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ── Cell renderer ─────────────────────────────────────────────────────────────
PILL_H  = 42
PILL_STATUS = {"g": (34, 164, 85), "y": (230, 152, 18), "r": (214, 62, 45)}

def draw_cell(draw, col_x, col_w, row_y, row_h, text, ctype, color):
    if not text or not ctype:
        return
    cy = row_y + row_h // 2
    PAD = 18

    if ctype == "p":
        pct = int(text.replace("%", "")) / 100
        bx  = col_x + PAD
        by  = cy - 13
        bw  = col_w - PAD*2 - 65
        pill(draw, bx, by, bx + bw, by + 26, (215, 220, 232))
        fill_w = max(14, int(bw * pct))
        pill(draw, bx, by, bx + fill_w, by + 26, color)
        pf = fb(28)
        draw.text((bx + bw + 8, by - 2), text, font=pf, fill=color)
        return

    if ctype in ("g", "y", "r"):
        pc  = PILL_STATUS[ctype]
        f   = fr(28)
        tw  = text_w(draw, text, f)
        pw  = min(tw + 38, col_w - PAD*2)
        px0 = col_x + PAD
        py0 = cy - PILL_H // 2
        pill(draw, px0, py0, px0 + pw, py0 + PILL_H, pc)
        draw.text((px0 + 19, py0 + (PILL_H - text_h(draw, text, f))//2 - 1),
                  text, font=f, fill=(255, 255, 255))
        return

    if ctype == "ar":
        draw.text((col_x + PAD, cy - 19), text, font=fb(32), fill=(214, 62, 45))
        return

    if ctype in ("a", "ab"):
        f = fb(34) if ctype == "ab" else fb(32)
        draw.text((col_x + PAD, cy - 20), text, font=f, fill=(28, 30, 38))
        return

    if ctype == "b":
        draw.text((col_x + PAD, cy - 20), text, font=fb(32), fill=(28, 30, 38))
        return

    if ctype == "c":
        f = fr(30)
        cx2 = col_x + (col_w - text_w(draw, text, f)) // 2
        draw.text((cx2, cy - 18), text, font=f, fill=(55, 60, 75))
        return

    # default: regular left-aligned
    draw.text((col_x + PAD, cy - 18), text, font=fr(30), fill=(55, 60, 75))


# ── Main generator ────────────────────────────────────────────────────────────
def generate(b):
    W, H   = 2000, 2000
    color  = b["color"]
    accent = b["accent"]
    light  = b["light"]

    img  = Image.new("RGB", (W, H), (244, 246, 250))
    draw = ImageDraw.Draw(img)

    # ── HEADER (0 – 555) ──────────────────────────────────────────────────────
    HDR = 555
    draw.rectangle([0, 0, W, HDR], fill=color)

    # diagonal dark triangle (top-right decoration)
    draw.polygon([(W-520, 0), (W, 0), (W, HDR)], fill=darken(color, 0.70))

    # brand
    draw.text((78, 50), "NASRITOOLS", font=fb(44), fill=(255, 255, 255))

    # badge pill (top-right)
    bf  = fb(36)
    btxt = b["badge"]
    bw  = text_w(draw, btxt, bf)
    bpad = 32
    bx0 = W - bw - bpad*2 - 68
    pill(draw, bx0, 40, W - 68, 104, (255, 255, 255), radius=20)
    draw.text((bx0 + bpad, 52), btxt, font=bf, fill=color)

    # thin accent underline
    draw.rectangle([78, 110, W - 78, 114], fill=mix_white(color, 0.5))

    # headline line 1 (white, very large)
    draw.text((78, 134), b["line1"], font=fb(100), fill=(255, 255, 255))

    # headline line 2 (accent color)
    draw.text((80, 258), b["line2"], font=fb(86), fill=accent)

    # result statement (2 lines max)
    rf    = fr(40)
    rlines = wrap_lines(draw, b["result"], rf, W - 160)
    ry    = 388
    for line in rlines[:2]:
        draw.text((78, ry), line, font=rf, fill=(255, 255, 255))
        ry += 56

    # ── SPREADSHEET MOCKUP (575 – 1710) ──────────────────────────────────────
    SL, SR = 68, W - 68          # sheet left / right
    ST, SB = 575, 1710           # sheet top / bottom
    SW     = SR - SL             # sheet width  = 1864

    # drop shadow
    draw.rectangle([SL+8, ST+8, SR+8, SB+8], fill=(195, 202, 215))

    # white sheet background
    draw.rectangle([SL, ST, SR, SB], fill=(255, 255, 255))

    # ── browser chrome ──
    CH = 50   # chrome height
    draw.rectangle([SL, ST, SR, ST+CH], fill=(241, 243, 245))
    # 3 dots
    for i, dc in enumerate([(232,72,72),(252,185,60),(36,168,90)]):
        ox = SL + 22 + i*32
        draw.ellipse([ox, ST+15, ox+22, ST+37], fill=dc)
    # URL bar
    url_bar_x0 = SL + 115
    url_bar_x1 = SR - 110
    pill(draw, url_bar_x0, ST+12, url_bar_x1, ST+40, (255,255,255), radius=7)
    draw.text((url_bar_x0+18, ST+15),
              "docs.google.com/spreadsheets  —  " + b["sheet_title"],
              font=fr(20), fill=(100, 105, 118))

    # ── sheet title bar ──
    TT = ST + CH
    TH = 56
    draw.rectangle([SL, TT, SR, TT+TH], fill=color)
    draw.text((SL+24, TT+12), b["sheet_title"], font=fb(34), fill=(255, 255, 255))

    # ── column headers ──
    CT = TT + TH
    COL_H = 50
    draw.rectangle([SL, CT, SR, CT+COL_H], fill=light)

    cols    = b["cols"]
    col_xs  = []
    x       = SL
    for i, (cname, cw) in enumerate(cols):
        col_xs.append(x)
        if i > 0:
            draw.line([(x, CT), (x, SB)], fill=(210, 218, 230), width=2)
        cf = fb(28)
        draw.text((x + 18, CT + (COL_H - text_h(draw, cname, cf))//2),
                  cname, font=cf, fill=darken(color, 0.72))
        x += cw

    # ── data rows ──
    RT     = CT + COL_H
    n_rows = len(b["rows"])
    ROW_H  = (SB - RT) // n_rows

    for ri, row in enumerate(b["rows"]):
        ry = RT + ri * ROW_H

        # row background
        is_last = (ri == n_rows - 1)
        if is_last:
            row_bg = light
        elif ri % 2 == 0:
            row_bg = (251, 252, 254)
        else:
            row_bg = (255, 255, 255)
        draw.rectangle([SL, ry, SR, ry + ROW_H], fill=row_bg)

        # row divider
        lc = darken(light, 0.92) if is_last else (220, 226, 235)
        draw.line([(SL, ry + ROW_H), (SR, ry + ROW_H)], fill=lc, width=1)

        for ci, (cell_text, cell_type) in enumerate(row):
            cw = cols[ci][1]
            draw_cell(draw, col_xs[ci], cw, ry, ROW_H,
                      cell_text, cell_type, color)

    # sheet border
    draw.rectangle([SL, ST, SR, SB], outline=(195, 202, 215), width=2)

    # ── BOTTOM STRIP (1728 – 2000) ────────────────────────────────────────────
    BY = 1728
    draw.rectangle([0, BY, W, H], fill=color)

    # price
    pf = fb(62)
    draw.text((78, BY + 26), b["price"], font=pf, fill=(255, 255, 255))
    pw = text_w(draw, b["price"], pf)
    draw.text((78 + pw + 22, BY + 44), b["worth"], font=fr(38), fill=accent)

    # features
    draw.text((78, BY + 116),
              "Instant Download  ·  Google Sheets & Excel  ·  Lifetime Access  ·  No Subscription",
              font=fr(34), fill=(255, 255, 255))

    # url right
    uf = fr(30)
    ut = "nasritools.etsy.com"
    uw = text_w(draw, ut, uf)
    draw.text((W - uw - 78, BY + 190), ut, font=uf, fill=mix_white(color, 0.55))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf


# ── Etsy helpers ──────────────────────────────────────────────────────────────
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

def upload_image(token, lid, buf):
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}/images",
        headers=auth_headers(token),
        files={"image": ("cover.jpg", buf, "image/jpeg")},
        data={"rank": 1, "overwrite": "true"},
        timeout=60,
    )
    return r.ok, r.status_code, r.text[:200]


def main():
    token = get_token()
    print(f"\n{'='*65}")
    print(f"  NasriTools - Bundle Covers v4-pro (spreadsheet mockup)")
    print(f"{'='*65}\n")

    ok = 0
    for i, b in enumerate(BUNDLES, 1):
        lid = b["listing_id"]
        print(f"[{i}/5] {b['line1']} {b['line2']}")
        print(f"  Generating...", end=" ", flush=True)
        try:
            buf = generate(b)
            print("done")
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        token = get_token()
        print(f"  Uploading to [{lid}]...", end=" ", flush=True)
        img_ok, code, txt = upload_image(token, lid, buf)
        print(f"{'OK' if img_ok else f'FAIL {code}: {txt}'}")
        if img_ok:
            ok += 1
            print(f"  -> https://www.etsy.com/listing/{lid}")
        print()
        time.sleep(2)
        token = get_token()

    print(f"{'='*65}")
    print(f"  Done: {ok}/5 covers updated")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
