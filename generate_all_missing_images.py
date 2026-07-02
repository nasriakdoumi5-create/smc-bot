"""
generate_all_missing_images.py

Scans ALL active listings and fills image slots up to 5 images for any
listing that has fewer than 5. Generates category-aware images:
  • "How to Use" 3-step guide
  • "Features" 4-card grid
  • "Trust" guarantee card

Skips listings already at 5+ images.
Run: python generate_all_missing_images.py
"""
import io, json, os, time, requests, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_bulk_images_done.json"
TARGET_IMAGES = 5
SZ = 2000
WHITE = (255, 255, 255)
DARK  = (15, 20, 40)
GRAY  = (100, 110, 130)
LGRAY = (245, 247, 252)

# ─── Category detection ───────────────────────────────────────────────────────
CATEGORIES = {
    "finance": {
        "keywords": ["budget","expense","finance","cash","debt","savings","income",
                     "money","spending","financial","revenue","profit","stock","trading"],
        "color":  (22, 100, 52),
        "light":  (214, 245, 228),
        "emoji":  "💰",
        "tagline": "Track Every Euro. Save More.",
        "features": [
            ("📊", "Auto-Calculating",   "Formulas do the math for you"),
            ("📅", "12 Monthly Sheets",  "Full year covered instantly"),
            ("💸", "50+ Categories",     "Pre-built, fully editable"),
            ("📈", "Visual Dashboard",   "Clear charts and summaries"),
        ],
        "guarantee": "Know exactly where your money goes — or we'll help you customize it.",
    },
    "invoice": {
        "keywords": ["invoice","billing","freelancer","client track","contract",
                     "proposal","time track","receipt"],
        "color":  (14, 116, 144),
        "light":  (207, 236, 245),
        "emoji":  "📄",
        "tagline": "Invoice Clients. Get Paid Faster.",
        "features": [
            ("📄", "Auto Invoice Calc", "Totals calculated instantly"),
            ("📋", "Client Database",   "All contacts in one place"),
            ("📊", "Revenue Reports",   "Monthly summaries ready"),
            ("⏱️", "Time Tracker",     "Log hours automatically"),
        ],
        "guarantee": "Never lose track of an invoice or a client payment again.",
    },
    "kpi": {
        "keywords": ["kpi","dashboard","business","sales","marketing","crm",
                     "pipeline","lead","employee","hr","project","inventory"],
        "color":  (30, 64, 175),
        "light":  (219, 234, 254),
        "emoji":  "📊",
        "tagline": "Track KPIs. Grow Your Business.",
        "features": [
            ("📊", "Live KPI Dashboard", "Numbers update automatically"),
            ("🎯", "Goal Tracking",      "Weekly and monthly targets"),
            ("📈", "Growth Charts",      "Visualize trends instantly"),
            ("👥", "Team Overview",      "Track every metric by person"),
        ],
        "guarantee": "Replace expensive SaaS tools with a system you actually own.",
    },
    "fitness": {
        "keywords": ["workout","fitness","health","meal","weight","sleep",
                     "habit","calories","exercise","body","nutrition","water",
                     "mental health","pet"],
        "color":  (5, 150, 105),
        "light":  (209, 250, 229),
        "emoji":  "💪",
        "tagline": "Build the Habits. Track the Results.",
        "features": [
            ("🏋️", "Workout Logging",  "Every session tracked"),
            ("🔥", "Auto Streak Counter", "Stay motivated daily"),
            ("📉", "Progress Charts",  "Watch the transformation"),
            ("🥗", "Nutrition Tracker", "Calories and macros ready"),
        ],
        "guarantee": "Build consistent habits in 30 days — or we'll help you customize.",
    },
    "productivity": {
        "keywords": ["planner","productivity","goal","weekly","daily","schedule",
                     "task","study","life","journal","routine","focus","event",
                     "car","student","wedding","content","social media"],
        "color":  (109, 40, 217),
        "light":  (237, 233, 254),
        "emoji":  "📅",
        "tagline": "Plan Your Week. Own Your Time.",
        "features": [
            ("📅", "Weekly Overview",   "Every task at a glance"),
            ("🎯", "Goal Setting",      "Monthly targets tracked"),
            ("⏰", "Time Blocking",     "Protect deep work hours"),
            ("✅", "Daily Checklists",  "Never miss a priority again"),
        ],
        "guarantee": "Get more done in 4 days than most people do in 7.",
    },
    "bundle": {
        "keywords": ["bundle","complete","system","all-in-one","collection",
                     "mega","pack","set","starter kit","os"],
        "color":  (180, 83, 9),
        "light":  (254, 243, 199),
        "emoji":  "🎁",
        "tagline": "Everything You Need. One Download.",
        "features": [
            ("🎁", "Multiple Templates", "Full suite in one pack"),
            ("💰", "Save Up to 50%",    "vs buying individually"),
            ("♾️", "Lifetime Access",   "Buy once, yours forever"),
            ("⚡", "Instant Download",  "All files in one click"),
        ],
        "guarantee": "The complete toolkit — everything in one bundle at the best price.",
    },
}

# ─── Auth ─────────────────────────────────────────────────────────────────────
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

# ─── Category detection ───────────────────────────────────────────────────────
def get_category(title):
    tl = title.lower()
    for cat, data in CATEGORIES.items():
        if any(k in tl for k in data["keywords"]):
            return cat, data
    return "productivity", CATEGORIES["productivity"]

# ─── Font helpers ─────────────────────────────────────────────────────────────
def load_font(size, bold=True):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try: return ImageFont.truetype(path, size)
        except: continue
    try: return ImageFont.load_default(size=size)
    except: return ImageFont.load_default()

def ctext(draw, text, font, y, color, width=SZ):
    """Center text horizontally."""
    try:
        bb = font.getbbox(text)
        x = max(30, (width - (bb[2] - bb[0])) // 2)
        draw.text((x, y - bb[1]), text, font=font, fill=color)
    except: pass

def wrap_text(draw, text, font, max_width):
    """Wrap text to fit max_width, return list of lines."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        try:
            w = font.getbbox(test)[2]
        except:
            w = len(test) * 12
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

# ─── Image generators ─────────────────────────────────────────────────────────
def make_how_to_use(cat_key, cat_data):
    """3-step how-to-use guide."""
    color = cat_data["color"]
    light = cat_data["light"]
    emoji = cat_data["emoji"]

    img = Image.new("RGB", (SZ, SZ), LGRAY)
    d = ImageDraw.Draw(img)

    f_big   = load_font(90)
    f_med   = load_font(58)
    f_small = load_font(44)
    f_sub   = load_font(36)
    f_wm    = load_font(28)

    # Header bar
    d.rectangle([0, 0, SZ, 200], fill=color)
    ctext(d, "HOW TO GET STARTED", f_big, 60, WHITE)
    ctext(d, "3 easy steps — takes less than 2 minutes", f_sub, 155, (*light, 220))

    # Steps
    steps = [
        ("1", "Purchase & Download", "Complete checkout on Etsy.\nYour file downloads instantly."),
        ("2", "Open in Google Sheets", "Go to sheets.google.com\nFile → Import → Upload your file."),
        ("3", "Customize & Start", "Edit your data, change colors,\nand start tracking immediately!"),
    ]
    step_y = 280
    for num, title, desc in steps:
        # Step card
        card_top = step_y
        card_bot = step_y + 400
        d.rounded_rectangle([80, card_top, SZ - 80, card_bot], radius=28, fill=WHITE)
        d.rounded_rectangle([80, card_top, SZ - 80, card_bot], radius=28,
                            outline=(*color, 60), width=3)

        # Circle with number
        cx, cy, cr = 200, card_top + 200, 80
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=color)
        try:
            nb = f_big.getbbox(num)
            d.text((cx - (nb[2] - nb[0]) // 2, cy - (nb[3] - nb[1]) // 2 - nb[1]), num,
                  font=f_big, fill=WHITE)
        except: pass

        # Title
        try: d.text((320, card_top + 80), title, font=f_med, fill=DARK)
        except: pass

        # Description
        for i, line in enumerate(desc.split("\n")):
            try: d.text((320, card_top + 180 + i * 70), line, font=f_sub, fill=GRAY)
            except: pass

        step_y += 440

    # Footer
    d.rectangle([0, SZ - 130, SZ, SZ], fill=color)
    ctext(d, f"{emoji}  nasritools.etsy.com", f_sub, SZ - 90, WHITE)

    return img


def make_features_grid(cat_key, cat_data, title):
    """2×2 feature cards grid."""
    color = cat_data["color"]
    light = cat_data["light"]
    feats = cat_data["features"]
    tagline = cat_data["tagline"]

    img = Image.new("RGB", (SZ, SZ), LGRAY)
    d = ImageDraw.Draw(img)

    f_big   = load_font(88)
    f_med   = load_font(56)
    f_card  = load_font(44)
    f_desc  = load_font(34)
    f_sub   = load_font(36)

    # Header
    d.rectangle([0, 0, SZ, 220], fill=color)
    ctext(d, "WHAT'S INCLUDED", f_big, 55, WHITE)
    ctext(d, tagline, f_sub, 160, (*light, 230))

    # 2×2 grid
    pad = 60
    cols = [(pad, SZ // 2 - pad // 2), (SZ // 2 + pad // 2, SZ - pad)]
    rows = [(240, 240 + (SZ - 240 - 200) // 2 - 20),
            (240 + (SZ - 240 - 200) // 2 + 20, SZ - 200)]

    for i, (icon, feat_title, feat_desc) in enumerate(feats[:4]):
        col_idx = i % 2
        row_idx = i // 2
        x0, x1 = cols[col_idx]
        y0, y1 = rows[row_idx]

        is_accent = (i % 2 == 0)
        bg   = color if is_accent else WHITE
        fg   = WHITE if is_accent else DARK
        desc_col = (*light, 230) if is_accent else GRAY

        d.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=bg)

        # Icon circle
        icx = x0 + (x1 - x0) // 2
        icy = y0 + 100
        d.ellipse([icx - 60, icy - 60, icx + 60, icy + 60],
                  fill=(*light, 100) if is_accent else (*color,))
        try: d.text((icx - 30, icy - 35), icon, font=f_med, fill=WHITE if not is_accent else fg)
        except: pass

        # Feature title
        ctext(d, feat_title, f_card, y0 + 195, fg, width=x1 - x0)
        tx = x0 + (x1 - x0) // 2 - (x1 - x0) // 2
        # Center within card
        try:
            tb = f_card.getbbox(feat_title)
            tx = x0 + ((x1 - x0) - (tb[2] - tb[0])) // 2
            d.text((tx, y0 + 195), feat_title, font=f_card, fill=fg)
        except: pass

        # Description
        try:
            db = f_desc.getbbox(feat_desc)
            dx = x0 + ((x1 - x0) - (db[2] - db[0])) // 2
            d.text((dx, y0 + 275), feat_desc, font=f_desc, fill=desc_col)
        except: pass

    # Footer
    d.rectangle([0, SZ - 140, SZ, SZ], fill=color)
    ctext(d, "Instant Download  ·  nasritools.etsy.com", f_sub, SZ - 95, WHITE)

    return img


def make_trust_card(cat_key, cat_data, title):
    """Trust / guarantee card."""
    color = cat_data["color"]
    light = cat_data["light"]
    guarantee = cat_data["guarantee"]

    img = Image.new("RGB", (SZ, SZ), WHITE)
    d = ImageDraw.Draw(img)

    f_huge  = load_font(110)
    f_big   = load_font(76)
    f_med   = load_font(54)
    f_small = load_font(42)
    f_sub   = load_font(34)
    f_wm    = load_font(28)

    # Top accent stripe
    d.rectangle([0, 0, SZ, 16], fill=color)

    # Star rating block
    stars_y = 140
    star_text = "★★★★★"
    try:
        sb = f_big.getbbox(star_text)
        sx = (SZ - (sb[2] - sb[0])) // 2
        d.text((sx, stars_y), star_text, font=f_big, fill=(251, 191, 36))
    except: pass
    ctext(d, "Trusted by Customers Worldwide", f_sub, stars_y + 120, GRAY)

    # Big headline
    d.rectangle([80, 380, SZ - 80, 680], fill=light, outline=None)
    try:
        d.rounded_rectangle([80, 380, SZ - 80, 680], radius=20, fill=light)
    except:
        d.rectangle([80, 380, SZ - 80, 680], fill=light)
    ctext(d, "OUR GUARANTEE", f_med, 430, color)

    # Wrap guarantee text
    f_guar = load_font(40, bold=False)
    lines = wrap_text(d, guarantee, f_guar, SZ - 240)
    for i, line in enumerate(lines[:3]):
        try:
            lb = f_guar.getbbox(line)
            lx = (SZ - (lb[2] - lb[0])) // 2
            d.text((lx, 520 + i * 56), line, font=f_guar, fill=DARK)
        except: pass

    # Bullet promises
    promises = [
        "✓  Instant digital download — no waiting",
        "✓  Works FREE on Google Sheets + Excel",
        "✓  Lifetime access — yours forever",
        "✓  24-hour support if you need help",
    ]
    py = 740
    for p in promises:
        try: d.text((160, py), p, font=f_small, fill=DARK)
        except: pass
        py += 90

    # Badge
    badge_cx, badge_cy = SZ // 2, 1500
    d.ellipse([badge_cx - 160, badge_cy - 160, badge_cx + 160, badge_cy + 160],
              fill=color)
    ctext(d, "100%", f_med, badge_cy - 50, WHITE)
    ctext(d, "DIGITAL", f_sub, badge_cy + 55, (*light, 230))

    # Bottom
    d.rectangle([0, SZ - 140, SZ, SZ], fill=color)
    ctext(d, "nasritools.etsy.com  ·  Google Sheets Templates", f_sub, SZ - 95, WHITE)

    return img


# ─── Etsy API helpers ─────────────────────────────────────────────────────────
def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset}, timeout=30)
        if not r.ok: break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < 100: break
        offset += 100; time.sleep(0.3)
    return listings

def get_listing_images(token, lid):
    r = requests.get(
        f"https://api.etsy.com/v3/application/listings/{lid}/images",
        headers=auth_headers(token), timeout=20)
    return r.json().get("results", []) if r.ok else []

def upload_image(token, lid, img, rank):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90)
    buf.seek(0)
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}/images",
        headers=auth_headers(token),
        files={"image": (f"img_{rank}.jpg", buf, "image/jpeg")},
        data={"rank": rank, "overwrite": "false", "is_watermarked": "false"},
        timeout=60)
    return r.ok, r.status_code


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("  NasriTools — Bulk Image Generator (all listings)")
    print(f"  Target: {TARGET_IMAGES} images per listing")
    print("=" * 65)

    # Load done set
    done = set()
    if DONE_FILE.exists():
        try: done = set(json.loads(DONE_FILE.read_text()))
        except: pass

    token    = get_token()
    listings = get_all_listings(token)
    print(f"[*] {len(listings)} active listings\n")

    needs_images = []
    print("[*] Scanning image counts (this may take 2-3 minutes)...")
    for i, l in enumerate(listings):
        lid = l["listing_id"]
        if lid in done:
            continue
        token = get_token()
        imgs = get_listing_images(token, lid)
        count = len(imgs)
        if count < TARGET_IMAGES:
            needs_images.append((lid, l["title"], count))
        if (i + 1) % 20 == 0:
            print(f"  Scanned {i+1}/{len(listings)}...")
        time.sleep(0.3)

    print(f"\n[*] {len(needs_images)} listings need more images\n")

    added = skipped = failed = 0

    for idx, (lid, title, current_count) in enumerate(needs_images, 1):
        cat_key, cat_data = get_category(title)
        short_title = title[:40]
        print(f"  [{idx:3}/{len(needs_images)}] {short_title}... ({current_count} imgs) [{cat_key}]", end=" ", flush=True)

        token = get_token()

        # Generate needed image types
        # Determine which slots are free (ranks current_count+1 .. TARGET_IMAGES)
        start_rank = current_count + 1
        generators = [
            ("how_to_use",  make_how_to_use,    (cat_key, cat_data)),
            ("features",    make_features_grid,  (cat_key, cat_data, title)),
            ("trust",       make_trust_card,     (cat_key, cat_data, title)),
        ]

        rank = start_rank
        listing_ok = True
        for gen_name, gen_fn, gen_args in generators:
            if rank > TARGET_IMAGES:
                break
            try:
                img = gen_fn(*gen_args)
                ok, code = upload_image(token, lid, img, rank)
                if ok:
                    print(f"[r{rank}✓]", end=" ", flush=True)
                    rank += 1
                    added += 1
                else:
                    print(f"[r{rank}✗{code}]", end=" ", flush=True)
                    failed += 1
                    if code == 429:
                        time.sleep(10)
                time.sleep(1.5)
                token = get_token()
            except Exception as e:
                print(f"[r{rank}ERR:{str(e)[:20]}]", end=" ", flush=True)
                failed += 1

        print()

        done.add(lid)
        DONE_FILE.write_text(json.dumps(list(done)))
        time.sleep(1)

    print(f"\n{'='*65}")
    print(f"  Images added: {added}")
    print(f"  Skipped (already 5+): {skipped}")
    print(f"  Failed uploads: {failed}")
    print(f"  Processed: {len(needs_images)} listings")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
