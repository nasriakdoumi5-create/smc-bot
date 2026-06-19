#!/usr/bin/env python3
"""
generate_system_images.py
Generates and uploads 3 listing images per product for NasriTools Etsy store.
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
CLIENT_ID = "pluc0garrgcjzhim0hawxf0k"
SECRET = "hc89hlqkd6"
SHOP_ID = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE = Path(os.path.expanduser("~")) / "etsy_system_images_done.json"

# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
PRODUCTS = [
    {
        "name": "Budget Tracker", "search_kw": ["budget", "tracker"],
        "color": (31, 107, 59), "light": (220, 247, 233), "emoji": "💰",
        "result_line1": "Know where every euro goes.",
        "result_line2": "Automatically.",
        "pain": "Do you check your balance and feel surprised every time?",
        "solution": "This system tracks every expense, calculates your budget, and shows you exactly where your money went — without any manual math.",
        "before": ["Guess where money went", "Miss savings goals", "Stress at end of month", "No financial clarity"],
        "after": ["Every euro tracked automatically", "Savings goals on autopilot", "Full control in 5 minutes", "Crystal clear finances"],
        "benefit": "Users save €200+ extra per month",
    },
    {
        "name": "Habit Tracker", "search_kw": ["habit", "tracker"],
        "color": (192, 57, 43), "light": (253, 228, 224), "emoji": "✅",
        "result_line1": "Never break the chain.",
        "result_line2": "30 habits. Automatic streaks.",
        "pain": "Do you start habits and give up after 3 days?",
        "solution": "This system tracks 30 habits simultaneously, counts your streaks automatically, and shows your progress visually every day.",
        "before": ["Start habits, give up fast", "No streak visibility", "Forget daily habits", "Zero momentum"],
        "after": ["30 habits tracked daily", "Auto streak counter", "Visual progress daily", "Unstoppable momentum"],
        "benefit": "Build life-changing routines in 30 days",
    },
    {
        "name": "Meal Planner", "search_kw": ["meal", "planner"],
        "color": (39, 174, 141), "light": (209, 250, 229), "emoji": "🥗",
        "result_line1": "Plan 7 days of meals",
        "result_line2": "in 15 minutes flat.",
        "pain": "Do you waste money on groceries and still have nothing to eat?",
        "solution": "This system plans your full week of meals, auto-generates your grocery list, and tracks your nutrition — all in one place.",
        "before": ["No meal plan = no idea what to eat", "Overspend on groceries", "Unhealthy last-minute choices", "Food waste every week"],
        "after": ["Full week planned in 15 min", "Auto grocery list", "Nutrition tracked", "Save €80+ weekly"],
        "benefit": "Save €80+ on groceries every week",
    },
    {
        "name": "Wedding Planner", "search_kw": ["wedding", "planning"],
        "color": (210, 82, 162), "light": (252, 228, 243), "emoji": "💍",
        "result_line1": "Plan your perfect wedding.",
        "result_line2": "Budget. Guests. Vendors. Timeline.",
        "pain": "Is wedding planning making you anxious and overwhelmed?",
        "solution": "This system organizes every detail of your wedding — budget, guest list, vendors, and timeline — in one beautiful spreadsheet.",
        "before": ["Overwhelmed by planning", "Budget spiraling out of control", "Vendor chaos", "Forgetting important details"],
        "after": ["Every detail organized", "Budget tracked to the cent", "All vendors in one place", "Stress-free planning"],
        "benefit": "Plan your dream wedding stress-free",
    },
    {
        "name": "Workout Tracker", "search_kw": ["workout", "tracker"],
        "color": (192, 57, 43), "light": (253, 228, 224), "emoji": "💪",
        "result_line1": "See your strength grow",
        "result_line2": "every single session.",
        "pain": "Are you going to the gym but not sure if you're actually improving?",
        "solution": "This system logs every rep, set, and weight. It tracks your personal records, auto-generates progress charts, and shows you exactly how much stronger you've gotten.",
        "before": ["No idea if improving", "Forget last week's weights", "No PR tracking", "Random workouts"],
        "after": ["Every rep logged", "PRs tracked automatically", "Progress charts auto-generated", "Structured training"],
        "benefit": "Beat your PRs every single week",
    },
    {
        "name": "Content Creator Planner", "search_kw": ["content", "creator"],
        "color": (230, 126, 34), "light": (254, 243, 224), "emoji": "📱",
        "result_line1": "From posting randomly",
        "result_line2": "to growing systematically.",
        "pain": "Are you creating content without a strategy and wondering why you're not growing?",
        "solution": "This system plans your content calendar, tracks your analytics, manages brand deals, and shows you what's working — all in Google Sheets.",
        "before": ["Post randomly, no strategy", "No analytics tracking", "Miss brand deal deadlines", "Burnout from no system"],
        "after": ["3 months planned in one weekend", "Analytics tracked weekly", "Brand deals managed", "Consistent growth"],
        "benefit": "Grow your audience 3x faster",
    },
    {
        "name": "Invoice Tracker", "search_kw": ["invoice", "tracker"],
        "color": (52, 152, 219), "light": (214, 234, 248), "emoji": "📄",
        "result_line1": "Stop chasing invoices.",
        "result_line2": "Get paid on time. Every time.",
        "pain": "Do you have unpaid invoices you've been following up on for weeks?",
        "solution": "This system tracks every client, invoice, and payment. It shows you what's paid, pending, and overdue — and calculates your total revenue automatically.",
        "before": ["Chase unpaid invoices", "Forget client follow-ups", "Tax season is a nightmare", "No revenue visibility"],
        "after": ["All invoices tracked", "Payment status at a glance", "Tax prep ready", "Revenue calculated auto"],
        "benefit": "Never lose money to disorganization again",
    },
    {
        "name": "Student Planner", "search_kw": ["student", "planner"],
        "color": (108, 52, 131), "light": (237, 228, 252), "emoji": "🎓",
        "result_line1": "Ace your semester.",
        "result_line2": "GPA tracked. Deadlines met.",
        "pain": "Are you missing deadlines and watching your GPA drop?",
        "solution": "This system tracks all your assignments, calculates your GPA automatically, schedules your study time, and gives you a countdown to every exam.",
        "before": ["Miss assignment deadlines", "GPA dropping unexpectedly", "Study time wasted", "Exam panic every time"],
        "after": ["Zero missed deadlines", "GPA calculated live", "Optimized study schedule", "Exam ready every time"],
        "benefit": "Improve your GPA by 0.5+ points",
    },
    {
        "name": "Goals Planner", "search_kw": ["annual", "goal"],
        "color": (30, 100, 180), "light": (220, 235, 252), "emoji": "🎯",
        "result_line1": "Stop setting goals.",
        "result_line2": "Start achieving them.",
        "pain": "Do you set goals every January and forget them by February?",
        "solution": "This system breaks your annual goals into 90-day sprints and weekly actions, tracks your progress percentage, and shows you exactly what to do this week.",
        "before": ["Set goals, forget by Feb", "No weekly action plan", "Progress invisible", "Goals feel overwhelming"],
        "after": ["Goals broken into weekly steps", "90-day sprint plan", "Progress tracked %", "Clear next actions always"],
        "benefit": "Achieve more in 90 days than most do in a year",
    },
    {
        "name": "Weekly Planner", "search_kw": ["weekly", "planner"],
        "color": (108, 52, 131), "light": (237, 228, 252), "emoji": "📅",
        "result_line1": "Plan your perfect week",
        "result_line2": "in 15 minutes every Sunday.",
        "pain": "Do you end every week feeling like you accomplished nothing?",
        "solution": "This system uses time-blocking to help you schedule your highest-priority tasks, protect your focus time, and plan your energy levels throughout the day.",
        "before": ["Week ends with nothing done", "Reactive, not proactive", "Priority tasks always delayed", "Constant overwhelm"],
        "after": ["Week planned in 15 minutes", "Time-blocked for deep work", "Top 3 priorities always done", "Calm and in control"],
        "benefit": "Get 2x more done with 50% less stress",
    },
]

# ---------------------------------------------------------------------------
# Font paths
# ---------------------------------------------------------------------------
FONT_BOLD_CANDIDATES = [
    "arialbd.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
FONT_REGULAR_CANDIDATES = [
    "arial.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]
FONT_ITALIC_CANDIDATES = [
    "ariali.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf",
]
EMOJI_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/noto-emoji/NotoColorEmoji.ttf",
]


def _load_font(candidates, size):
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def font_bold(size):
    return _load_font(FONT_BOLD_CANDIDATES, size)


def font_regular(size):
    return _load_font(FONT_REGULAR_CANDIDATES, size)


def font_italic(size):
    return _load_font(FONT_ITALIC_CANDIDATES, size)


def _emoji_font_path():
    for p in EMOJI_FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_rounded_rect(draw, xy, radius, fill):
    """Draw a filled rounded rectangle. xy = (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = xy
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    draw.ellipse([x0, y0, x0 + 2 * r, y0 + 2 * r], fill=fill)
    draw.ellipse([x1 - 2 * r, y0, x1, y0 + 2 * r], fill=fill)
    draw.ellipse([x0, y1 - 2 * r, x0 + 2 * r, y1], fill=fill)
    draw.ellipse([x1 - 2 * r, y1 - 2 * r, x1, y1], fill=fill)


def wrap_text(text, font, max_width, draw):
    """Split text into lines that fit within max_width pixels."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered_text(draw, text, font, cx, y, fill):
    """Draw text centered horizontally around cx at vertical position y."""
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((cx - w // 2, y), text, font=font, fill=fill)
    return bbox[3] - bbox[1]  # return height


def draw_centered_multiline(draw, lines, font, cx, y_start, fill, line_spacing=10):
    """Draw multiple lines of text centered. Returns the y after the last line."""
    y = y_start
    for line in lines:
        h = draw_centered_text(draw, line, font, cx, y, fill)
        y += h + line_spacing
    return y


def draw_emoji(img, emoji_char, xy, size):
    """
    Attempt to render an emoji onto img at position xy=(x, y) with given size.
    Uses NotoColorEmoji if available. Silently skips on failure.
    """
    emoji_path = _emoji_font_path()
    if emoji_path is None:
        return
    try:
        # NotoColorEmoji uses a fixed size of 109; we scale after rendering
        efont = ImageFont.truetype(emoji_path, size)
        tmp = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        td.text((0, 0), emoji_char, font=efont, embedded_color=True)
        # Crop to bounding box of actual content
        bbox = tmp.getbbox()
        if bbox:
            tmp = tmp.crop(bbox)
            tmp = tmp.resize((size, size), Image.LANCZOS)
        x, y = xy
        img.paste(tmp, (x - size // 2, y - size // 2), tmp)
    except Exception:
        pass


def darken_color(color, factor=0.85):
    return tuple(max(0, int(c * factor)) for c in color)


def lighten_color(color, factor=1.15):
    return tuple(min(255, int(c * factor)) for c in color)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def auth_headers(token):
    return {
        "Authorization": "Bearer " + token["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }


def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post(
            "https://api.etsy.com/v3/public/oauth/token",
            data={
                "grant_type": "refresh_token",
                "client_id": CLIENT_ID,
                "refresh_token": t["refresh_token"],
            },
        )
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t


# ---------------------------------------------------------------------------
# Listing discovery
# ---------------------------------------------------------------------------

def fetch_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            print(f"  Warning: listings fetch failed: {r.status_code} {r.text[:200]}")
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings


def find_listing_id(active_listings, keywords):
    for lst in active_listings:
        title = (lst.get("title") or "").lower()
        if all(kw.lower() in title for kw in keywords):
            return lst["listing_id"]
    return None


# ---------------------------------------------------------------------------
# Image generation — Image 1: Result-Focused Thumbnail
# ---------------------------------------------------------------------------

def generate_image1(product):
    W, H = 2000, 2000
    color = product["color"]
    light = product["light"]

    img = Image.new("RGB", (W, H), color)
    draw = ImageDraw.Draw(img)

    # Decorative circle
    circle_radius = 700
    cx, cy = W // 2, H // 2
    draw.ellipse(
        [cx - circle_radius, cy - circle_radius, cx + circle_radius, cy + circle_radius],
        fill=lighten_color(color, 1.12),
    )

    # Brand text top-left
    brand_font = font_regular(40)
    draw.text((60, 55), "NasriTools", font=brand_font, fill=light)

    # Emoji centered near top area
    emoji_y = 430
    draw_emoji(img, product["emoji"], (cx, emoji_y), 130)

    # Result text — two large bold lines
    result_font = font_bold(76)
    line1 = product["result_line1"]
    line2 = product["result_line2"]

    # Measure and wrap each line
    draw_dummy = ImageDraw.Draw(img)
    lines1 = wrap_text(line1, result_font, W - 200, draw_dummy)
    lines2 = wrap_text(line2, result_font, W - 200, draw_dummy)

    total_lines = lines1 + lines2
    line_h = 90  # approx line height for 76px font
    total_text_h = len(total_lines) * line_h
    text_start_y = cy - total_text_h // 2 - 40

    y = text_start_y
    for line in total_lines:
        draw_centered_text(draw, line, result_font, cx, y, (255, 255, 255))
        y += line_h

    # Benefit pill badge
    benefit_text = product["benefit"]
    badge_font = font_bold(36)
    b_bbox = draw.textbbox((0, 0), benefit_text, font=badge_font)
    bw = b_bbox[2] - b_bbox[0]
    bh = b_bbox[3] - b_bbox[1]
    pad_x, pad_y = 50, 22
    badge_w = bw + pad_x * 2
    badge_h = bh + pad_y * 2
    badge_x0 = cx - badge_w // 2
    badge_y0 = y + 40
    badge_x1 = badge_x0 + badge_w
    badge_y1 = badge_y0 + badge_h
    draw_rounded_rect(draw, (badge_x0, badge_y0, badge_x1, badge_y1), 40, (255, 255, 255))
    draw.text(
        (badge_x0 + pad_x, badge_y0 + pad_y),
        benefit_text,
        font=badge_font,
        fill=color,
    )

    # Bottom strip (last 120px)
    strip_color = darken_color(color, 0.80)
    draw.rectangle([0, H - 120, W, H], fill=strip_color)

    strip_font = font_regular(34)
    footer_text = "nasritools.etsy.com  |  Google Sheets  |  Instant Download"
    draw_centered_text(draw, footer_text, strip_font, cx, H - 90, (255, 255, 255))

    name_font = font_regular(28)
    draw.text((40, H - 90), product["name"], font=name_font, fill=(255, 255, 255, 180))

    return img


# ---------------------------------------------------------------------------
# Image generation — Image 2: Value Hook
# ---------------------------------------------------------------------------

def generate_image2(product):
    W, H = 2000, 2000
    color = product["color"]
    light = product["light"]

    img = Image.new("RGB", (W, H), light)
    draw = ImageDraw.Draw(img)

    # Header strip: top 400px solid product color
    header_h = 400
    draw.rectangle([0, 0, W, header_h], fill=color)

    # Emoji in header
    draw_emoji(img, product["emoji"], (W // 2, 90), 100)

    # "Are you still..." italic
    italic_font = font_italic(42)
    draw_centered_text(draw, "Are you still...", italic_font, W // 2, 190, (255, 255, 255))

    # Pain question bold white
    pain_font = font_bold(58)
    draw_dummy = ImageDraw.Draw(img)
    pain_lines = wrap_text(product["pain"], pain_font, W - 160, draw_dummy)
    pain_y = 250
    for pl in pain_lines:
        draw_centered_text(draw, pl, pain_font, W // 2, pain_y, (255, 255, 255))
        pain_y += 70

    # White middle section background already set (light color acts as bg, but middle is white)
    # Draw white rectangle from 400 to 1880
    draw.rectangle([0, header_h, W, H - 120], fill=(255, 255, 255))

    # "THERE'S A BETTER WAY." bold, colored
    better_font = font_bold(56)
    y_cursor = header_h + 70
    draw_centered_text(draw, "THERE'S A BETTER WAY.", better_font, W // 2, y_cursor, color)
    y_cursor += 80

    # Horizontal divider
    draw.rectangle([100, y_cursor, W - 100, y_cursor + 4], fill=color)
    y_cursor += 40

    # Solution text
    sol_font = font_regular(38)
    sol_lines = wrap_text(product["solution"], sol_font, W - 240, draw_dummy)
    for sl in sol_lines:
        draw.text((120, y_cursor), sl, font=sol_font, fill=(50, 50, 50))
        y_cursor += 55

    # Benefit badge
    y_cursor += 40
    badge_font = font_bold(38)
    benefit_text = product["benefit"]
    b_bbox = draw.textbbox((0, 0), benefit_text, font=badge_font)
    bw = b_bbox[2] - b_bbox[0]
    bh = b_bbox[3] - b_bbox[1]
    pad_x, pad_y = 60, 28
    badge_w = bw + pad_x * 2
    badge_h = bh + pad_y * 2
    badge_x0 = W // 2 - badge_w // 2
    badge_y0 = y_cursor
    badge_x1 = badge_x0 + badge_w
    badge_y1 = badge_y0 + badge_h
    draw_rounded_rect(draw, (badge_x0, badge_y0, badge_x1, badge_y1), 45, color)
    draw.text((badge_x0 + pad_x, badge_y0 + pad_y), benefit_text, font=badge_font, fill=(255, 255, 255))

    # Bottom strip
    draw.rectangle([0, H - 120, W, H], fill=color)
    footer_font = font_regular(36)
    draw_centered_text(draw, "nasritools.etsy.com", footer_font, W // 2, H - 88, (255, 255, 255))

    return img


# ---------------------------------------------------------------------------
# Image generation — Image 3: Before / After
# ---------------------------------------------------------------------------

def generate_image3(product):
    W, H = 2000, 2000
    color = product["color"]

    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # TOP HEADER 200px
    header_h = 200
    draw.rectangle([0, 0, W, header_h], fill=color)
    header_font = font_bold(52)
    header_text = f"THE {product['name'].upper()} TRANSFORMATION"
    draw_centered_text(draw, header_text, header_font, W // 2, 70, (255, 255, 255))

    # Content area: 200 to 1800
    content_top = header_h
    content_bottom = 1800
    content_h = content_bottom - content_top

    # Left half: before (red)
    left_bg = (254, 226, 226)   # light red
    dark_red = (153, 27, 27)
    draw.rectangle([0, content_top, 960, content_bottom], fill=left_bg)

    # Right half: after (green)
    right_bg = (220, 252, 231)  # light green
    dark_green = (21, 128, 61)
    draw.rectangle([1040, content_top, W, content_bottom], fill=right_bg)

    # Center gap white divider
    draw.rectangle([960, content_top, 1040, content_bottom], fill=(255, 255, 255))

    # Arrow in center
    arrow_cx = W // 2
    arrow_cy = (content_top + content_bottom) // 2
    arrow_size = 60
    draw.ellipse(
        [arrow_cx - arrow_size, arrow_cy - arrow_size, arrow_cx + arrow_size, arrow_cy + arrow_size],
        fill=color,
    )
    # Draw "→" text
    arrow_font = font_bold(60)
    draw.text((arrow_cx - 22, arrow_cy - 32), "→", font=arrow_font, fill=(255, 255, 255))

    # BEFORE label
    label_font = font_bold(52)
    draw.text((80, content_top + 40), "BEFORE", font=label_font, fill=dark_red)

    # AFTER label
    draw.text((1100, content_top + 40), "AFTER", font=label_font, fill=dark_green)

    # Before bullet cards
    card_font = font_bold(34)
    card_y = content_top + 130
    card_spacing = 130
    for item in product["before"]:
        # White card
        card_x0 = 40
        card_x1 = 940
        card_y1 = card_y + 90
        draw_rounded_rect(draw, (card_x0, card_y, card_x1, card_y1), 16, (255, 255, 255))
        # Red x prefix
        draw.text((card_x0 + 20, card_y + 22), "✗", font=card_font, fill=(220, 38, 38))
        # Item text — wrap if needed
        item_lines = wrap_text(item, card_font, card_x1 - card_x0 - 90, draw)
        text_y = card_y + 22
        for il in item_lines[:2]:
            draw.text((card_x0 + 70, text_y), il, font=card_font, fill=(30, 30, 30))
            text_y += 40
        card_y += card_spacing

    # After bullet cards
    card_y = content_top + 130
    for item in product["after"]:
        card_x0 = 1060
        card_x1 = 1960
        card_y1 = card_y + 90
        draw_rounded_rect(draw, (card_x0, card_y, card_x1, card_y1), 16, (255, 255, 255))
        # Green checkmark prefix
        draw.text((card_x0 + 20, card_y + 22), "✓", font=card_font, fill=(22, 163, 74))
        item_lines = wrap_text(item, card_font, card_x1 - card_x0 - 90, draw)
        text_y = card_y + 22
        for il in item_lines[:2]:
            draw.text((card_x0 + 70, text_y), il, font=card_font, fill=(30, 30, 30))
            text_y += 40
        card_y += card_spacing

    # BOTTOM STRIP 1800-2000
    draw.rectangle([0, 1800, W, H], fill=color)
    bottom_font = font_bold(40)
    draw_centered_text(draw, product["benefit"], bottom_font, W // 2, 1825, (255, 255, 255))
    footer_font = font_regular(32)
    draw_centered_text(draw, "nasritools.etsy.com", footer_font, W // 2, 1900, (255, 255, 255))

    return img


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

def upload_image(token, listing_id, img_pil, rank):
    buf = io.BytesIO()
    img_pil.save(buf, format="JPEG", quality=92)
    buf.seek(0)

    url = f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images"
    headers = auth_headers(token)

    r = requests.post(
        url,
        headers=headers,
        files={"image": (f"image_rank{rank}.jpg", buf, "image/jpeg")},
        data={"rank": rank, "overwrite": "true"},
        timeout=60,
    )
    return r


# ---------------------------------------------------------------------------
# Done-state helpers
# ---------------------------------------------------------------------------

def load_done():
    if DONE_FILE.exists():
        try:
            return json.loads(DONE_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_done(done):
    DONE_FILE.write_text(json.dumps(done, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    done = load_done()

    print("Fetching token...")
    token = get_token()

    print("Fetching active listings...")
    active_listings = fetch_all_listings(token)
    print(f"  Found {len(active_listings)} active listings.")

    image_generators = {
        1: generate_image1,
        2: generate_image2,
        3: generate_image3,
    }

    for product in PRODUCTS:
        name = product["name"]
        print(f"\n--- {name} ---")

        listing_id = find_listing_id(active_listings, product["search_kw"])
        if listing_id is None:
            print(f"  SKIP: no listing found for keywords {product['search_kw']}")
            continue

        print(f"  Listing ID: {listing_id}")

        for rank in [1, 2, 3]:
            done_key = f"{listing_id}_{rank}"
            if done.get(done_key):
                print(f"  Rank {rank}: already done, skipping.")
                continue

            print(f"  Rank {rank}: generating image...", end=" ", flush=True)
            try:
                img = image_generators[rank](product)
            except Exception as e:
                print(f"FAILED to generate: {e}")
                continue

            print("uploading...", end=" ", flush=True)

            # Refresh token before each upload to be safe
            try:
                token = get_token()
            except Exception as e:
                print(f"Token refresh failed: {e}")
                continue

            try:
                r = upload_image(token, listing_id, img, rank)
                if r.ok:
                    print("OK")
                    done[done_key] = True
                    save_done(done)
                else:
                    print(f"FAILED ({r.status_code}): {r.text[:300]}")
            except Exception as e:
                print(f"FAILED (exception): {e}")

        time.sleep(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
