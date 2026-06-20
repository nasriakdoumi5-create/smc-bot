"""
generate_extra_images.py

Generates 3 additional listing images for each of 10 products and uploads
them to Etsy at rank 2, 3, and 4. Rank 1 (the dashboard image) is
assumed to already be uploaded.
"""

import io
import json
import os
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------
CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

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
    return {
        "Authorization": "Bearer " + token["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }

# ---------------------------------------------------------------------------
# Font loading — works on Windows AND Linux
# ---------------------------------------------------------------------------
_BOLD = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
    "C:/Windows/Fonts/verdanab.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
_REG = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/verdana.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _f(paths, size):
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fb(s):
    return _f(_BOLD, s)


def fr(s):
    return _f(_REG, s)

# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
PRODUCTS = [
    {
        "search_kw": ["budget", "expense"],
        "color": (20, 115, 60), "light": (220, 247, 233),
        "label": "BUDGET TRACKER",
        "features": [
            "Monthly Budget Dashboard (auto-totals)",
            "Daily Expense Log — 50+ categories",
            "Savings Goals Tracker",
            "Category Breakdown Overview",
            "Annual 12-Month Summary",
            "Budget vs Actual Comparison",
        ],
    },
    {
        "search_kw": ["habit", "building"],
        "color": (192, 57, 43), "light": (253, 228, 224),
        "label": "HABIT TRACKER",
        "features": [
            "30-Day Habit Grid (track 20 habits)",
            "Automatic Streak Counter",
            "Weekly Check-In Sheet",
            "Monthly Progress Overview",
            "Pre-loaded Habit Templates",
            "Visual Completion % Dashboard",
        ],
    },
    {
        "search_kw": ["meal", "planning"],
        "color": (39, 174, 141), "light": (209, 250, 229),
        "label": "MEAL PLANNER",
        "features": [
            "7-Day Meal Plan Grid",
            "Auto Grocery List Generator",
            "Daily Calorie Counter",
            "Weekly Shopping Budget",
            "Pantry & Inventory Tracker",
            "Meal Ideas Database (50+ recipes)",
        ],
    },
    {
        "search_kw": ["wedding", "planning"],
        "color": (210, 82, 162), "light": (252, 228, 243),
        "label": "WEDDING PLANNER",
        "features": [
            "Full Budget Tracker (20+ categories)",
            "Guest List & RSVP Manager",
            "Vendor Contact & Status Sheet",
            "Day-of Timeline Builder",
            "Seating Chart Organizer",
            "Wedding Countdown Dashboard",
        ],
    },
    {
        "search_kw": ["workout", "tracking"],
        "color": (192, 57, 43), "light": (253, 228, 224),
        "label": "WORKOUT TRACKER",
        "features": [
            "Exercise Log (unlimited sessions)",
            "Personal Record (PR) Tracker",
            "Weekly Volume Calculator",
            "Auto-generated Progress Charts",
            "Exercise Library (50+ exercises)",
            "Body Measurements & Weight Log",
        ],
    },
    {
        "search_kw": ["content", "creator"],
        "color": (230, 126, 34), "light": (254, 243, 224),
        "label": "CONTENT CREATOR",
        "features": [
            "90-Day Content Calendar",
            "Multi-Platform Analytics Tracker",
            "Brand Deal CRM",
            "Content Ideas Database",
            "Income & Expense Log",
            "Audience Growth Chart",
        ],
    },
    {
        "search_kw": ["invoice", "client"],
        "color": (52, 152, 219), "light": (214, 234, 248),
        "label": "INVOICE TRACKER",
        "features": [
            "Invoice Tracker (paid / pending / overdue)",
            "Client Database & CRM",
            "Monthly & Annual Revenue Summary",
            "Tax Preparation Sheet (auto-calculated)",
            "Business Expense Tracker",
            "Outstanding Payment Dashboard",
        ],
    },
    {
        "search_kw": ["student", "academic"],
        "color": (108, 52, 131), "light": (237, 228, 252),
        "label": "STUDENT PLANNER",
        "features": [
            "Assignment & Deadline Tracker",
            "Live GPA Calculator (auto-updates)",
            "Study Schedule Builder",
            "Exam Countdown Dashboard",
            "Grade Tracker per Subject",
            "Semester Overview Summary",
        ],
    },
    {
        "search_kw": ["annual", "goal"],
        "color": (30, 100, 180), "light": (220, 235, 252),
        "label": "GOALS PLANNER",
        "features": [
            "Annual Goals Dashboard (12 goals)",
            "90-Day Sprint Planner",
            "Weekly Action Steps Breakdown",
            "Auto Progress % Calculator",
            "Habit-to-Goal Linking System",
            "Year-End Review Sheet",
        ],
    },
    {
        "search_kw": ["weekly", "productivity"],
        "color": (108, 52, 131), "light": (237, 228, 252),
        "label": "WEEKLY PLANNER",
        "features": [
            "Time-Blocked Weekly Grid (Mon-Sun)",
            "Top 3 Priorities System",
            "Task Completion Tracker with % score",
            "Energy Level & Focus Planner",
            "Rolling To-Do List",
            "Weekly Reflection & Review Sheet",
        ],
    },
]

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def mix(c1, c2, t):
    """Blend c1 toward c2 by factor t (0=c1, 1=c2)."""
    return tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))


def tw(draw, text, font):
    """Text width."""
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]


def th(draw, text, font):
    """Text height."""
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]


def pill(draw, x0, y0, x1, y1, fill, r=None):
    """Draw a rounded-rectangle (pill) shape."""
    r = r or (y1 - y0) // 2
    r = min(r, (x1 - x0) // 2, (y1 - y0) // 2)
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    for cx, cy in [(x0, y0), (x1 - 2 * r, y0), (x0, y1 - 2 * r), (x1 - 2 * r, y1 - 2 * r)]:
        draw.ellipse([cx, cy, cx + 2 * r, cy + 2 * r], fill=fill)

# ---------------------------------------------------------------------------
# Image generator 1: What's Included (rank 2)
# ---------------------------------------------------------------------------

def gen_whats_included(p):
    W, H = 2000, 2000
    color = p["color"]
    bg = mix(color, (0, 0, 0), 0.85)

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Subtle vignette-like accent: very dark overlay in corners would require
    # compositing, so we add a faint color strip at the top instead.
    draw.rectangle([0, 0, W, 6], fill=color)

    # "NASRITOOLS" top-left label
    font_brand = fb(36)
    draw.text((100, 40), "NASRITOOLS", font=font_brand, fill=(255, 255, 255))

    # "WHAT'S INSIDE" heading
    font_heading = fb(110)
    draw.text((100, 120), "WHAT'S INSIDE", font=font_heading, fill=(255, 255, 255))

    # Thin colored line
    draw.rectangle([100, 440, 900, 448], fill=color)

    # Product label pill
    font_label = fb(44)
    label_text = p["label"]
    pad_x, pad_y = 36, 18
    lw = tw(draw, label_text, font_label)
    lh = th(draw, label_text, font_label)
    pill_x0, pill_y0 = 100, 460
    pill_x1 = pill_x0 + lw + pad_x * 2
    pill_y1 = pill_y0 + lh + pad_y * 2
    pill(draw, pill_x0, pill_y0, pill_x1, pill_y1, fill=color)
    draw.text((pill_x0 + pad_x, pill_y0 + pad_y), label_text, font=font_label, fill=(255, 255, 255))

    # Features list
    font_feat = fr(54)
    circle_d = 60
    row_height = 190
    start_y = 580

    for i, feature in enumerate(p["features"]):
        y = start_y + i * row_height
        cx = 100 + circle_d // 2
        cy = y + circle_d // 2

        # Colored circle
        draw.ellipse(
            [cx - circle_d // 2, cy - circle_d // 2, cx + circle_d // 2, cy + circle_d // 2],
            fill=color,
        )
        # Checkmark
        font_check = fb(42)
        check = "✓"
        cw = tw(draw, check, font_check)
        ch = th(draw, check, font_check)
        draw.text((cx - cw // 2, cy - ch // 2), check, font=font_check, fill=(255, 255, 255))

        # Feature text — vertically center beside the circle
        fh = th(draw, feature, font_feat)
        draw.text((200, cy - fh // 2), feature, font=font_feat, fill=(255, 255, 255))

    # Footer line 1
    font_footer1 = fr(38)
    footer1 = "Instant Download  ·  Lifetime Access  ·  Free Updates"
    fw1 = tw(draw, footer1, font_footer1)
    draw.text(((W - fw1) // 2, 1900), footer1, font=font_footer1,
              fill=(200, 200, 200))

    # Footer line 2 — URL in slightly lighter product color
    font_footer2 = fr(34)
    footer2 = "nasritools.etsy.com"
    fw2 = tw(draw, footer2, font_footer2)
    url_color = mix(color, (255, 255, 255), 0.3)
    draw.text(((W - fw2) // 2, 1950), footer2, font=font_footer2, fill=url_color)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

# ---------------------------------------------------------------------------
# Image generator 2: Compatibility (rank 3)
# ---------------------------------------------------------------------------

def gen_compatibility(p):
    W, H = 2000, 2000
    color = p["color"]
    light = p["light"]
    bg = (247, 249, 252)

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Top accent bar
    draw.rectangle([0, 0, W, 12], fill=color)

    # Heading
    font_heading = fb(100)
    draw.text((100, 40), "WORKS ON EVERYTHING", font=font_heading, fill=(28, 30, 38))

    # Subtitle
    font_sub = fr(50)
    subtitle = "No software to install. Open your browser — you’re ready."
    draw.text((100, 195), subtitle, font=font_sub, fill=(90, 95, 110))

    # 4 compatibility cards in 2×2 grid
    card_w, card_h = 900, 500
    icon_area_h = 140
    positions = [(100, 320), (1060, 320), (100, 880), (1060, 880)]

    cards = [
        {"abbr": "GS", "title": "Google Sheets", "desc": "100% FREE — all features work"},
        {"abbr": "XL", "title": "Microsoft Excel", "desc": "Fully compatible"},
        {"abbr": "\U0001f4bb", "title": "Mac & PC",       "desc": "Works in any browser"},
        {"abbr": "\U0001f4f1", "title": "iPhone & Android","desc": "Free Google Sheets app"},
    ]

    font_abbr  = fb(56)
    font_title = fb(52)
    font_desc  = fr(44)

    for (cx, cy), card in zip(positions, cards):
        # Card white background
        draw.rectangle([cx, cy, cx + card_w, cy + card_h], fill=(255, 255, 255))
        # 4px product-color border
        for offset in range(4):
            draw.rectangle(
                [cx + offset, cy + offset, cx + card_w - offset, cy + card_h - offset],
                outline=color,
            )

        # Icon area (light color background at top of card)
        draw.rectangle([cx, cy, cx + card_w, cy + icon_area_h], fill=light)

        # Abbreviation centered in icon area
        abw = tw(draw, card["abbr"], font_abbr)
        abh = th(draw, card["abbr"], font_abbr)
        draw.text(
            (cx + (card_w - abw) // 2, cy + (icon_area_h - abh) // 2),
            card["abbr"], font=font_abbr, fill=color,
        )

        # Title below icon area
        tw_ = tw(draw, card["title"], font_title)
        draw.text(
            (cx + (card_w - tw_) // 2, cy + icon_area_h + 24),
            card["title"], font=font_title, fill=(28, 30, 38),
        )

        # Description
        dw = tw(draw, card["desc"], font_desc)
        title_h = th(draw, card["title"], font_title)
        draw.text(
            (cx + (card_w - dw) // 2, cy + icon_area_h + 24 + title_h + 20),
            card["desc"], font=font_desc, fill=(90, 95, 110),
        )

    # Footer URL
    font_url = fr(38)
    url_text = "nasritools.etsy.com"
    uw = tw(draw, url_text, font_url)
    draw.text(((W - uw) // 2, 1900), url_text, font=font_url, fill=color)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

# ---------------------------------------------------------------------------
# Image generator 3: How It Works (rank 4)
# ---------------------------------------------------------------------------

def gen_how_it_works(p):
    W, H = 2000, 2000
    color = p["color"]
    bg = color

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Dark diagonal accent in top-right corner
    darker = mix(color, (0, 0, 0), 0.30)
    # Draw a dark triangle in top-right
    draw.polygon([(W, 0), (W - 600, 0), (W, 600)], fill=darker)

    # Heading
    font_heading = fb(100)
    draw.text((100, 80), "READY IN 2 MINUTES", font=font_heading, fill=(255, 255, 255))

    # Subtitle (white at ~80% opacity: mix with bg color)
    font_sub = fr(52)
    subtitle = "From purchase to using it — in under 120 seconds."
    sub_color = mix((255, 255, 255), color, 0.20)
    draw.text((100, 225), subtitle, font=font_sub, fill=sub_color)

    # 3 steps — 3 equal columns
    col_w = 620
    left_margin = 70
    step_top = 400

    steps = [
        {"num": "1", "title": "PURCHASE",  "desc": ["Click buy — instant", "confirmation"]},
        {"num": "2", "title": "OPEN LINK", "desc": ["PDF arrives instantly with", "your Google Sheets link"]},
        {"num": "3", "title": "START",     "desc": ["File → Make a Copy", "→ yours forever"]},
    ]

    font_num   = fb(100)
    font_step  = fb(72)
    font_sdesc = fr(50)
    circle_r = 90  # radius of the number circle

    for i, step in enumerate(steps):
        col_cx = left_margin + i * col_w + col_w // 2  # center x of column

        # Large number circle (white bg, product-color text)
        circle_y = step_top + 40
        draw.ellipse(
            [col_cx - circle_r, circle_y, col_cx + circle_r, circle_y + 2 * circle_r],
            fill=(255, 255, 255),
        )
        nw = tw(draw, step["num"], font_num)
        nh = th(draw, step["num"], font_num)
        draw.text(
            (col_cx - nw // 2, circle_y + circle_r - nh // 2),
            step["num"], font=font_num, fill=color,
        )

        # Step title
        title_y = circle_y + 2 * circle_r + 40
        stw = tw(draw, step["title"], font_step)
        draw.text((col_cx - stw // 2, title_y), step["title"], font=font_step, fill=(255, 255, 255))

        # Description lines
        desc_color = mix((255, 255, 255), color, 0.15)
        title_h = th(draw, step["title"], font_step)
        desc_y = title_y + title_h + 20
        for line in step["desc"]:
            lw = tw(draw, line, font_sdesc)
            draw.text((col_cx - lw // 2, desc_y), line, font=font_sdesc, fill=desc_color)
            desc_y += th(draw, line, font_sdesc) + 10

    # Divider line
    draw.rectangle([100, 1480, W - 100, 1482], fill=(255, 255, 255))

    # Trust badges
    font_trust = fr(52)
    badges = ["✓ Instant Delivery", "✓ Lifetime Access",
              "✓ Free Updates", "✓ 24h Support"]

    # Measure total width to center them
    gap = 60
    badge_widths = [tw(draw, b, font_trust) for b in badges]
    total_w = sum(badge_widths) + gap * (len(badges) - 1)
    bx = (W - total_w) // 2
    by = 1540

    for b, bw in zip(badges, badge_widths):
        draw.text((bx, by), b, font=font_trust, fill=(255, 255, 255))
        bx += bw + gap

    # URL at bottom
    font_url = fr(42)
    url_text = "nasritools.etsy.com"
    url_color = mix((255, 255, 255), color, 0.40)
    uw = tw(draw, url_text, font_url)
    draw.text(((W - uw) // 2, 1880), url_text, font=font_url, fill=url_color)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

# ---------------------------------------------------------------------------
# Upload helper
# ---------------------------------------------------------------------------

def upload_image(token, lid, buf, rank):
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}/images",
        headers=auth_headers(token),
        files={"image": ("image.jpg", buf, "image/jpeg")},
        data={"rank": rank, "overwrite": "true"},
        timeout=60,
    )
    return r.ok, r.status_code

# ---------------------------------------------------------------------------
# Fetch active listings
# ---------------------------------------------------------------------------

def fetch_all_listings(token):
    """Return all active listings for the shop (handles pagination)."""
    listings = []
    offset = 0
    limit = 100
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": limit, "offset": offset},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        listings.extend(results)
        if len(results) < limit:
            break
        offset += limit
        time.sleep(0.5)
    return listings


def find_listing(listings, keywords):
    """Return the first listing whose title contains ALL keywords (case-insensitive)."""
    kw_lower = [k.lower() for k in keywords]
    for listing in listings:
        title = listing.get("title", "").lower()
        if all(k in title for k in kw_lower):
            return listing
    return None

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  Etsy Extra Images Generator")
    print("=" * 60)

    token = get_token()
    print("[*] Token loaded/refreshed.")

    print("[*] Fetching active listings...")
    listings = fetch_all_listings(token)
    print(f"    Found {len(listings)} active listings.")

    generators = [
        (2, "What's Included",  gen_whats_included),
        (3, "Compatibility",    gen_compatibility),
        (4, "How It Works",     gen_how_it_works),
    ]

    success_total = 0
    fail_total = 0

    for idx, product in enumerate(PRODUCTS, start=1):
        print(f"\n[{idx:02d}/10] {product['label']}")
        print(f"       Searching for keywords: {product['search_kw']}")

        listing = find_listing(listings, product["search_kw"])
        if listing is None:
            print(f"       [!] No listing matched. Skipping.")
            fail_total += 1
            continue

        lid = listing["listing_id"]
        title = listing.get("title", "")
        print(f"       Matched: [{lid}] {title[:70]}")

        # Refresh token before a batch of uploads to be safe
        token = get_token()

        for rank, label, gen_fn in generators:
            print(f"       Generating rank {rank} ({label}) ...", end=" ", flush=True)
            buf = gen_fn(product)
            ok, status = upload_image(token, lid, buf, rank)
            if ok:
                print(f"OK (HTTP {status})")
                success_total += 1
            else:
                print(f"FAILED (HTTP {status})")
                fail_total += 1
            time.sleep(1)

    print("\n" + "=" * 60)
    print(f"  Done.  {success_total} uploads succeeded, {fail_total} issues.")
    print("=" * 60)


if __name__ == "__main__":
    main()
