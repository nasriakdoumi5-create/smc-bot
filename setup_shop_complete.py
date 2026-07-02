"""
setup_shop_complete.py

Complete shop setup — runs everything in sequence:
  Step 1 — Create 6 shop sections + assign all 119 listings
  Step 2 — Update digital thank-you message (post-purchase email)
  Step 3 — Generate shop logo (1000x1000) + banner (1600x400) — upload manually
  Step 4 — Print About section text — paste manually in Shop Manager
  Step 5 — Print 5 Pinterest pin descriptions — post manually
"""
import json, os, glob, time, requests, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
OUT_DIR    = Path("thumbnails/brand")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Section definitions ──────────────────────────────────────────────────────
SECTIONS = [
    {
        "title": "Finance & Budget",
        "keywords": ["budget","finance","expense","cash flow","debt","savings",
                     "money","spending","financial","income","revenue","profit"],
    },
    {
        "title": "Business & KPIs",
        "keywords": ["kpi","dashboard","business","sales","marketing","crm",
                     "project","client","lead","pipeline","employee"],
    },
    {
        "title": "Freelancer Tools",
        "keywords": ["invoice","freelancer","billing","time track","client track",
                     "content planner","social media","contract","proposal"],
    },
    {
        "title": "Health & Fitness",
        "keywords": ["workout","fitness","health","meal","weight","sleep",
                     "habit","calories","exercise","body","nutrition","water"],
    },
    {
        "title": "Planners & Goals",
        "keywords": ["planner","productivity","goal","weekly","daily","schedule",
                     "task","study","life","journal","routine","focus"],
    },
    {
        "title": "Bundles & Systems",
        "keywords": ["bundle","complete","system","os","starter kit","all-in-one",
                     "collection","mega","pack","set"],
    },
]

DIGITAL_SALE_MESSAGE = """Thank you for your purchase! Here's how to get started in 2 minutes:

STEP 1: Download your file from this order page
STEP 2: Go to sheets.google.com
STEP 3: File → Import → Upload → select your file
STEP 4: Customize categories and amounts to match your life

That's it — you're ready to go!

━━━━━━━━━━━━━━━━━━━━━━━━━
NEED HELP?
Message us on Etsy — we reply within 24 hours.
We're happy to help you customize anything.

━━━━━━━━━━━━━━━━━━━━━━━━━
LOVING IT?
A quick review helps us grow and helps other buyers decide.
It takes 30 seconds and means everything to a small shop.

→ More templates: nasritools.etsy.com
Use code WELCOME10 for 10% off your next order.

© NasriTools — Professional Google Sheets Templates"""

ABOUT_TEXT = """
═══════════════════════════════════════════════════════
ABOUT SECTION — Paste in: Shop Manager → Info & Appearance → About
═══════════════════════════════════════════════════════

TITLE: Professional Google Sheets Templates — Simple, Powerful, Free to Use

STORY:
We built NasriTools because we were tired of paying monthly subscriptions
for tools that should be simple.

Google Sheets is free. Your data stays yours. It works on every device.
So we built 119 professional templates on top of it — for budgeting,
business tracking, fitness, invoicing, and productivity.

Every template is designed to work immediately:
no setup, no account, no learning curve.
Download → open → start using in under 2 minutes.

WHO WE HELP:
• Freelancers who need simple invoicing without expensive software
• Families tracking monthly budgets and saving more
• Fitness enthusiasts logging workouts and measuring progress
• Business owners who want clear KPI dashboards without complexity
• Students and professionals who want to plan their weeks better

WHY GOOGLE SHEETS:
✓ Free for everyone, forever
✓ Works on phone, tablet, and desktop
✓ Auto-saves to your Drive
✓ Easy to share with family or team
✓ Fully customizable — change anything

We answer every message within 24 hours.
If you need a modification, just ask.

nasritools.etsy.com — built for people who get things done.
═══════════════════════════════════════════════════════
"""

PINTEREST_PINS = """
═══════════════════════════════════════════════════════
PINTEREST PINS — Post one per day, different boards
═══════════════════════════════════════════════════════

PIN 1 — Board: Personal Finance / Budgeting
Image: Budget Tracker thumbnail
Title: Free Budget Tracker Google Sheets Template 2025
Description:
Stop wondering where your money goes. This free Google Sheets budget
tracker automatically calculates your income, expenses, and savings
every month. Works on phone and desktop. No app, no subscription.
→ Download free: nasritools.etsy.com
#BudgetTracker #GoogleSheets #PersonalFinance #FreeBudget #MoneyTracker

──────────────────────────────────────────────────────

PIN 2 — Board: Productivity / Planning
Image: Weekly Planner thumbnail
Title: Weekly Planner Google Sheets Template — Free Download
Description:
Plan your entire week in one clean spreadsheet. Track tasks, goals,
habits, and priorities — all auto-calculating. Works on any device.
Designed for people who actually want to get things done.
→ nasritools.etsy.com
#WeeklyPlanner #ProductivityTemplate #GoogleSheets #GoalTracker #Planner

──────────────────────────────────────────────────────

PIN 3 — Board: Health / Fitness
Image: Workout Tracker thumbnail
Title: Workout Tracker Google Sheets — Track Every Session
Description:
Log your workouts, track weight progress, and plan your meals — all
in one free Google Sheets template. See real progress week by week.
No gym app needed.
→ nasritools.etsy.com
#WorkoutTracker #FitnessTemplate #GoogleSheets #GymLog #HealthTracker

──────────────────────────────────────────────────────

PIN 4 — Board: Business / Freelancing
Image: Invoice Tracker thumbnail
Title: Invoice Tracker for Freelancers — Google Sheets Template
Description:
Track every invoice, client, and payment in one place. See what's
paid, what's pending, and what's overdue — at a glance. Built for
freelancers who hate chasing clients.
→ nasritools.etsy.com
#InvoiceTracker #FreelancerTools #GoogleSheets #BusinessTemplate #Invoice

──────────────────────────────────────────────────────

PIN 5 — Board: Small Business / Tools
Image: KPI Dashboard thumbnail
Title: KPI Dashboard Google Sheets — Business Metrics Made Simple
Description:
Track your key business metrics without expensive software. Revenue,
leads, conversion rates, and growth — all in one clean dashboard.
Built for small business owners who want clarity.
→ nasritools.etsy.com
#KPIDashboard #BusinessTracker #GoogleSheets #SmallBusiness #Analytics
═══════════════════════════════════════════════════════
"""


# ─── Utilities ────────────────────────────────────────────────────────────────
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def load_font(size):
    for c in ["arialbd.ttf","calibrib.ttf","arial.ttf",
              "C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(c, size)
        except: continue
    for p in ["C:/Windows/Fonts/*.ttf","/usr/share/fonts/**/*.ttf"]:
        for f in glob.glob(p, recursive=True):
            try: return ImageFont.truetype(f, size)
            except: continue
    try: return ImageFont.load_default(size=size)
    except: return ImageFont.load_default()

def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"]})
        r.raise_for_status(); t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def auth_headers(token):
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                        headers=auth_headers(token),
                        params={"limit": 100, "offset": offset}, timeout=30)
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100; time.sleep(0.3)
    return listings

def match_section(title):
    tl = title.lower()
    for i, sec in enumerate(SECTIONS):
        if any(k in tl for k in sec["keywords"]):
            return i
    return 4  # default: Planners & Goals


# ─── STEP 1: Shop Sections ────────────────────────────────────────────────────
def step1_sections(token, listings):
    print("\n" + "─"*55)
    print("STEP 1 — Shop Sections")
    print("─"*55)

    # Get existing sections
    r = requests.get(f"{API}/shops/{SHOP_ID}/sections",
                    headers=auth_headers(token), timeout=30)
    existing = {s["title"]: s["shop_section_id"]
                for s in (r.json().get("results", []) if r.ok else [])}

    # Create missing sections
    section_ids = []
    for sec in SECTIONS:
        title = sec["title"]
        if title in existing:
            sid = existing[title]
            print(f"  [skip] '{title}' exists (id={sid})")
        else:
            token = get_token()
            r2 = requests.post(f"{API}/shops/{SHOP_ID}/sections",
                               headers={**auth_headers(token),
                                        "Content-Type": "application/x-www-form-urlencoded"},
                               data=f"title={urllib.parse.quote(title)}", timeout=30)
            if r2.ok:
                sid = r2.json().get("shop_section_id")
                print(f"  [create] '{title}' → id={sid}")
            else:
                print(f"  [fail] '{title}' ({r2.status_code}): {r2.text[:80]}")
                sid = None
            time.sleep(1)
        section_ids.append(sid)

    # Assign listings to sections
    print(f"\n  Assigning {len(listings)} listings to sections...")
    ok = fail = 0
    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        title = l["title"]
        si    = match_section(title)
        sid   = section_ids[si]
        if not sid:
            fail += 1; continue

        token = get_token()
        r3 = requests.patch(
            f"{API}/shops/{SHOP_ID}/listings/{lid}",
            headers={**auth_headers(token),
                     "Content-Type": "application/x-www-form-urlencoded"},
            data=f"shop_section_id={sid}", timeout=30)

        status = "OK" if r3.ok else f"FAIL({r3.status_code})"
        sec_name = SECTIONS[si]["title"]
        print(f"  [{idx:3}/{len(listings)}] {title[:35]}... → {sec_name} {status}")
        if r3.ok: ok += 1
        else: fail += 1
        time.sleep(0.6)

    print(f"\n  Sections done: {ok} OK | {fail} failed")


# ─── STEP 2: Digital Sale Message ─────────────────────────────────────────────
def step2_message(token):
    print("\n" + "─"*55)
    print("STEP 2 — Digital Thank-You Message")
    print("─"*55)
    token = get_token()
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}",
        headers={**auth_headers(token),
                 "Content-Type": "application/x-www-form-urlencoded"},
        data=f"digital_sale_message={urllib.parse.quote(DIGITAL_SALE_MESSAGE, safe='')}",
        timeout=30)
    if r.ok:
        print("  Digital sale message updated ✅")
    else:
        print(f"  FAIL ({r.status_code}): {r.text[:150]}")


# ─── STEP 3: Logo + Banner ────────────────────────────────────────────────────
def step3_logo_banner():
    print("\n" + "─"*55)
    print("STEP 3 — Logo + Banner (generate & upload manually)")
    print("─"*55)

    accent = "#2563EB"
    dark   = "#0D1B2A"

    # ── LOGO 1000×1000 ────────────────────────────────────────────────────────
    img  = Image.new("RGB", (1000,1000), hex2rgb(dark))
    draw = ImageDraw.Draw(img)

    # Gradient bg
    for i in range(1000):
        t = i/1000
        draw.rectangle([0,i,1000,i+1], fill=(int(13+t*15), int(27+t*25), int(42+t*35)))

    # Accent circle
    draw.ellipse([100,100,900,900], fill=hex2rgb("#0F2744"))
    draw.ellipse([110,110,890,890], fill=hex2rgb("#0D2440"))

    # Accent ring
    for r in range(440,450):
        draw.ellipse([500-r,500-r,500+r,500+r], outline=hex2rgb(accent), width=1)
    draw.ellipse([60,60,940,940], outline=hex2rgb(accent), width=6)

    # "NT" monogram
    f_big = load_font(380)
    f_sub = load_font(80)
    f_tag = load_font(50)
    try:
        nb = f_big.getbbox("NT")
        draw.text(((1000-(nb[2]-nb[0]))//2, 240-nb[1]), "NT",
                 font=f_big, fill=hex2rgb(accent))
    except: pass
    try:
        sb = f_sub.getbbox("NASRITOOLS")
        draw.text(((1000-(sb[2]-sb[0]))//2, 680-sb[1]), "NASRITOOLS",
                 font=f_sub, fill=(255,255,255))
    except: pass
    try:
        tb = f_tag.getbbox("Google Sheets Templates")
        draw.text(((1000-(tb[2]-tb[0]))//2, 790-tb[1]), "Google Sheets Templates",
                 font=f_tag, fill=hex2rgb("#94A3B8"))
    except: pass

    logo_path = OUT_DIR / "shop_logo_1000x1000.png"
    img.save(logo_path, "PNG", quality=95)
    print(f"  Logo saved: {logo_path}")

    # ── BANNER 1600×400 ───────────────────────────────────────────────────────
    img2  = Image.new("RGB", (1600,400), hex2rgb(dark))
    draw2 = ImageDraw.Draw(img2)

    for i in range(400):
        t = i/400
        draw2.rectangle([0,i,1600,i+1], fill=(int(13+t*10), int(27+t*18), int(42+t*28)))

    # Accent bar left
    draw2.rectangle([0,0,8,400], fill=hex2rgb(accent))

    # Brand name
    f_bn  = load_font(110)
    f_tag = load_font(50)
    f_cat = load_font(38)
    try:
        draw2.text((60, 60), "NasriTools", font=f_bn, fill=(255,255,255))
    except: pass
    try:
        draw2.text((62, 196), "Professional Google Sheets Templates", font=f_tag,
                  fill=hex2rgb(accent))
    except: pass

    # Category pills
    cats = ["Finance", "Business", "Health", "Productivity", "Freelancer"]
    cx = 62
    f_pill = load_font(36)
    for cat in cats:
        try:
            cb = f_pill.getbbox(cat)
            cw = cb[2]-cb[0]+32; ch = cb[3]-cb[1]+16
            cy = 272
            draw2.rounded_rectangle([cx,cy,cx+cw,cy+ch], radius=8,
                                   fill=hex2rgb("#1E3A5F"))
            draw2.text((cx+16, cy+8-cb[1]), cat, font=f_pill, fill=hex2rgb(accent))
            cx += cw + 12
        except: pass

    # Right: tagline
    f_right = load_font(44)
    try:
        lines = ["119 Templates", "Instant Download", "Works on Any Device"]
        for i, line in enumerate(lines):
            draw2.text((1100, 110+i*90), line, font=f_right, fill=hex2rgb("#94A3B8"))
    except: pass

    # Watermark
    try:
        wm = "nasritools.etsy.com"
        wb = f_tag.getbbox(wm)
        draw2.text((1600-(wb[2]-wb[0])-40, 340), wm, font=f_tag, fill=hex2rgb("#334155"))
    except: pass

    banner_path = OUT_DIR / "shop_banner_1600x400.png"
    img2.save(banner_path, "PNG", quality=95)
    print(f"  Banner saved: {banner_path}")
    print()
    print("  MANUAL UPLOAD REQUIRED:")
    print("  Shop Manager → Info & Appearance → Shop Icon → upload shop_logo_1000x1000.png")
    print("  Shop Manager → Info & Appearance → Banner → upload shop_banner_1600x400.png")


# ─── STEP 4: About Section ────────────────────────────────────────────────────
def step4_about():
    print("\n" + "─"*55)
    print("STEP 4 — About Section (copy-paste manually)")
    print("─"*55)
    print(ABOUT_TEXT)
    about_path = Path("about_section.txt")
    about_path.write_text(ABOUT_TEXT, encoding="utf-8")
    print(f"  Saved to: {about_path.resolve()}")
    print("  → Shop Manager → Info & Appearance → Story → paste the text above")


# ─── STEP 5: Pinterest Content ────────────────────────────────────────────────
def step5_pinterest():
    print("\n" + "─"*55)
    print("STEP 5 — Pinterest Pins (post manually, 1 per day)")
    print("─"*55)
    print(PINTEREST_PINS)
    pins_path = Path("pinterest_pins.md")
    pins_path.write_text(PINTEREST_PINS, encoding="utf-8")
    print(f"  Saved to: {pins_path.resolve()}")
    print("  → Create account: pinterest.com/nasritools")
    print("  → Post 1 pin per day using descriptions above")
    print("  → Always link to: nasritools.etsy.com")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  NasriTools — Complete Shop Setup")
    print("  5 steps — nothing skipped")
    print("=" * 55)

    token    = get_token()
    listings = get_all_listings(token)
    print(f"[*] {len(listings)} listings loaded")

    step1_sections(token, listings)
    step2_message(token)
    step3_logo_banner()
    step4_about()
    step5_pinterest()

    print("\n" + "=" * 55)
    print("  ALL STEPS COMPLETE")
    print("=" * 55)
    print()
    print("  MANUAL (5 min in Shop Manager):")
    print("  1. Upload logo  → thumbnails/brand/shop_logo_1000x1000.png")
    print("  2. Upload banner → thumbnails/brand/shop_banner_1600x400.png")
    print("  3. Paste About text from: about_section.txt")
    print()
    print("  ONGOING (1 per day):")
    print("  4. Post Pinterest pins from: pinterest_pins.md")
    print("  5. Reply to Reddit comments")

if __name__ == "__main__":
    main()
