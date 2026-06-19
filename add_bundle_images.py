"""
add_bundle_images.py
NasriTools Etsy shop — add feature card (rank 2) and product collage (rank 3)
to the 5 bundle listings.
"""

import os
import io
import json
import time
import math
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ─── Config ───────────────────────────────────────────────────────────────────
CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
SIZE       = 2000
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_bundle_images_done.json"

# ─── Bundle definitions ───────────────────────────────────────────────────────
BUNDLE_LISTINGS = {
    "finance_bundle": {
        "listing": 4524283814, "name": "Finance Bundle",
        "price": "€17.99", "save": "50%",
        "color": (31, 107, 59), "light": (220, 247, 233),
        "products": [
            ("Budget Tracker",  "Track income, expenses & savings"),
            ("Invoice Tracker", "Manage clients & payments"),
            ("Goals Planner",   "Annual goals & 90-day plans"),
        ],
    },
    "health_bundle": {
        "listing": 4524276503, "name": "Health Bundle",
        "price": "€16.99", "save": "50%",
        "color": (192, 57, 43), "light": (250, 219, 216),
        "products": [
            ("Workout Tracker", "Log sets, reps & personal records"),
            ("Meal Planner",    "7-day meals + grocery list"),
            ("Habit Tracker",   "Track 30 habits with streaks"),
        ],
    },
    "planner_bundle": {
        "listing": 4524276527, "name": "Planner Bundle",
        "price": "€16.99", "save": "50%",
        "color": (108, 52, 131), "light": (237, 228, 252),
        "products": [
            ("Weekly Planner",  "Time blocking & priority tasks"),
            ("Student Planner", "Assignments, grades & GPA"),
            ("Goals Planner",   "Annual goals & 90-day plans"),
        ],
    },
    "business_bundle": {
        "listing": 4524276553, "name": "Business Bundle",
        "price": "€21.99", "save": "50%",
        "color": (230, 126, 34), "light": (253, 235, 208),
        "products": [
            ("Content Creator Planner", "Content calendar & analytics"),
            ("Invoice Tracker",         "Clients, invoices & tax prep"),
            ("Goals Planner",           "Annual goals & milestones"),
        ],
    },
    "ultimate_bundle": {
        "listing": 4524283886, "name": "Ultimate Bundle",
        "price": "€39.99", "save": "65%",
        "color": (30, 100, 180), "light": (220, 235, 252),
        "products": [
            ("Budget Tracker",          "Income & expenses"),
            ("Habit Tracker",           "30 daily habits"),
            ("Meal Planner",            "7-day meals"),
            ("Wedding Planner",         "Budget & guests"),
            ("Workout Tracker",         "Gym log"),
            ("Content Creator",         "Content calendar"),
            ("Invoice Tracker",         "Clients & invoices"),
            ("Student Planner",         "Grades & GPA"),
            ("Goals Planner",           "Annual goals"),
            ("Weekly Planner",          "Time blocking"),
        ],
    },
}

# Emoji mapping (key = lower-cased product name, spaces/hyphens → underscores)
EMOJI_MAP = {
    "budget_tracker":           "💰",
    "habit_tracker":            "✅",
    "meal_planner":             "🥗",
    "wedding_planner":          "💍",
    "workout_tracker":          "💪",
    "content_creator_planner":  "📱",
    "content_creator":          "📱",
    "freelancer_invoice_tracker": "📄",
    "invoice_tracker":          "📄",
    "student_planner":          "🎓",
    "goals_planner":            "🎯",
    "weekly_planner":           "📅",
}

# Mini-card accent colours (used in the collage grid)
CARD_COLORS = {
    "budget_tracker":           (31,  107,  59),
    "habit_tracker":            (192,  57,  43),
    "meal_planner":             (39,  174, 141),
    "wedding_planner":          (210,  82, 162),
    "workout_tracker":          (192,  57,  43),
    "content_creator_planner":  (230, 126,  34),
    "content_creator":          (230, 126,  34),
    "freelancer_invoice_tracker":(52, 152, 219),
    "invoice_tracker":          (52,  152, 219),
    "student_planner":          (108,  52, 131),
    "goals_planner":            (30,  100, 180),
    "weekly_planner":           (108,  52, 131),
}

WHITE  = (255, 255, 255)
GRAY   = (120, 120, 130)
YELLOW = (255, 215,   0)

# ─── Font helpers ─────────────────────────────────────────────────────────────

def load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        # Windows
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        # macOS
        "/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def load_font_regular(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()

# ─── Drawing utilities ────────────────────────────────────────────────────────

def draw_rounded_rect(draw: ImageDraw.ImageDraw,
                      xy: tuple, radius: int,
                      fill: tuple, outline: tuple = None,
                      outline_width: int = 2) -> None:
    """Draw a filled rounded rectangle. xy = (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = xy
    # Ensure x0 < x1 and y0 < y1
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill,
                            outline=outline, width=outline_width if outline else 0)


def draw_circle(draw: ImageDraw.ImageDraw,
                cx: int, cy: int, r: int, fill: tuple) -> None:
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


def centered_text(draw: ImageDraw.ImageDraw,
                  text: str, font: ImageFont.FreeTypeFont,
                  cx: int, y: int, fill: tuple) -> None:
    """Draw text horizontally centred at cx, top-aligned at y."""
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((cx - w // 2, y), text, font=font, fill=fill)


def text_width(draw: ImageDraw.ImageDraw,
               text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_height(draw: ImageDraw.ImageDraw,
                text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]

# ─── Feature card ─────────────────────────────────────────────────────────────

def make_feature_card(bundle: dict) -> Image.Image:
    img  = Image.new("RGB", (SIZE, SIZE), bundle["light"])
    draw = ImageDraw.Draw(img)

    color = bundle["color"]
    light = bundle["light"]
    name  = bundle["name"]
    save  = bundle["save"]
    products = bundle["products"]

    # ── Top 500 px: solid colour header ──────────────────────────────────────
    draw.rectangle([0, 0, SIZE, 500], fill=color)

    # Bundle name
    font_title = load_font(90)
    centered_text(draw, name, font_title, SIZE // 2, 120, WHITE)

    # "SAVE X%" badge — yellow circle, top-right corner
    badge_cx, badge_cy, badge_r = SIZE - 160, 160, 115
    draw_circle(draw, badge_cx, badge_cy, badge_r, YELLOW)
    font_badge_top  = load_font(38)
    font_badge_pct  = load_font(60)
    centered_text(draw, "SAVE", font_badge_top,  badge_cx, badge_cy - 60, (50, 50, 50))
    centered_text(draw, save,   font_badge_pct,  badge_cx, badge_cy - 18, (50, 50, 50))

    # "✔ WHAT'S INCLUDED"
    font_section = load_font(52)
    centered_text(draw, "✔  WHAT'S INCLUDED", font_section, SIZE // 2, 390, WHITE)

    # ── Product cards ────────────────────────────────────────────────────────
    n        = len(products)
    card_h   = 180
    margin_x = 80
    pad_y    = 40          # gap between cards
    # Available vertical space: 500 → 1880 (leaving 120 px for the bottom strip)
    area_top    = 540
    area_bottom = 1880
    total_h = n * card_h + (n - 1) * pad_y
    start_y = area_top + (area_bottom - area_top - total_h) // 2

    font_prod_name = load_font(48)
    font_prod_desc = load_font_regular(36)

    for i, (prod_name, prod_desc) in enumerate(products):
        cy = start_y + i * (card_h + pad_y)
        # White shadow card
        draw_rounded_rect(draw,
                          (margin_x + 6, cy + 6, SIZE - margin_x + 6, cy + card_h + 6),
                          radius=24, fill=(200, 210, 200))
        draw_rounded_rect(draw,
                          (margin_x, cy, SIZE - margin_x, cy + card_h),
                          radius=24, fill=WHITE)

        # Colour left accent bar
        draw_rounded_rect(draw,
                          (margin_x, cy, margin_x + 10, cy + card_h),
                          radius=5, fill=color)

        # Product name
        draw.text((margin_x + 40, cy + 22), prod_name,
                  font=font_prod_name, fill=color)
        # Description
        draw.text((margin_x + 40, cy + 90), prod_desc,
                  font=font_prod_desc, fill=GRAY)

        # Small checkmark icon on the right
        font_check = load_font(52)
        check_x = SIZE - margin_x - 70
        draw.text((check_x, cy + 60), "✓", font=font_check, fill=color)

    # ── Bottom strip (last 120 px) ────────────────────────────────────────────
    draw.rectangle([0, SIZE - 120, SIZE, SIZE], fill=color)
    font_footer = load_font_regular(38)
    centered_text(draw,
                  "Instant Download  •  Google Sheets  •  nasritools.etsy.com",
                  font_footer, SIZE // 2, SIZE - 88, WHITE)

    return img

# ─── Product collage ──────────────────────────────────────────────────────────

def _product_key(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def make_collage(bundle: dict) -> Image.Image:
    img  = Image.new("RGB", (SIZE, SIZE), (245, 245, 248))
    draw = ImageDraw.Draw(img)

    color    = bundle["color"]
    name     = bundle["name"]
    products = bundle["products"]
    n        = len(products)

    # ── Title bar ────────────────────────────────────────────────────────────
    title_h = 140
    draw.rectangle([0, 0, SIZE, title_h], fill=color)
    font_title = load_font(72)
    title_text = f"{name}  •  {n} Templates"
    centered_text(draw, title_text, font_title, SIZE // 2, 34, WHITE)

    # ── Grid layout ──────────────────────────────────────────────────────────
    # Keep cols ≤ 4 and rows ≤ 4; prefer square-ish grids
    if n <= 2:
        cols, rows = n, 1
    elif n <= 4:
        cols, rows = 2, math.ceil(n / 2)
    elif n <= 6:
        cols, rows = 3, math.ceil(n / 3)
    else:
        cols = 4
        rows = math.ceil(n / cols)

    margin    = 60
    gap       = 28
    footer_h  = 100
    grid_top  = title_h + margin
    grid_bot  = SIZE - footer_h - margin
    grid_w    = SIZE - 2 * margin
    grid_h    = grid_bot - grid_top

    card_w = (grid_w - gap * (cols - 1)) // cols
    card_h = (grid_h - gap * (rows - 1)) // rows

    font_emoji = load_font(80)
    font_name  = load_font(max(28, min(46, card_w // 7)))
    font_small = load_font_regular(28)

    for idx, (prod_name, prod_desc) in enumerate(products):
        row = idx // cols
        col = idx % cols

        x0 = margin + col * (card_w + gap)
        y0 = grid_top + row * (card_h + gap)
        x1 = x0 + card_w
        y1 = y0 + card_h

        key = _product_key(prod_name)
        card_color = CARD_COLORS.get(key, color)
        emoji      = EMOJI_MAP.get(key, "📋")

        # Shadow
        draw_rounded_rect(draw,
                          (x0 + 5, y0 + 5, x1 + 5, y1 + 5),
                          radius=22,
                          fill=(180, 185, 195))
        # Card background
        draw_rounded_rect(draw, (x0, y0, x1, y1), radius=22, fill=card_color)

        # Lighter overlay strip at bottom 35% of card
        overlay_top = y0 + int(card_h * 0.62)
        r_card, g_card, b_card = card_color
        overlay_col = (min(r_card + 40, 255),
                       min(g_card + 40, 255),
                       min(b_card + 40, 255))
        draw_rounded_rect(draw,
                          (x0, overlay_top, x1, y1),
                          radius=22, fill=overlay_col)
        # Fix the seam left by the rounded corner at overlay_top
        draw.rectangle([x0, overlay_top, x1, overlay_top + 22], fill=overlay_col)
        # Re-draw the main color above the seam
        draw.rectangle([x0, overlay_top, x1, overlay_top + 2], fill=card_color)

        # Emoji centred in top 60% of card
        emoji_y = y0 + int(card_h * 0.08)
        try:
            centered_text(draw, emoji, font_emoji, (x0 + x1) // 2, emoji_y, WHITE)
        except Exception:
            pass  # some environments can't render emoji in TrueType; skip gracefully

        # Product name
        name_y = overlay_top + 12
        centered_text(draw, prod_name, font_name, (x0 + x1) // 2, name_y, WHITE)

        # Short description (truncate if too wide)
        desc_y = name_y + text_height(draw, prod_name, font_name) + 8
        desc = prod_desc if text_width(draw, prod_desc, font_small) <= (card_w - 20) else prod_desc[:30] + "…"
        centered_text(draw, desc, font_small, (x0 + x1) // 2, desc_y, WHITE)

    # ── Footer ────────────────────────────────────────────────────────────────
    font_footer = load_font_regular(38)
    centered_text(draw, "nasritools.etsy.com",
                  font_footer, SIZE // 2, SIZE - footer_h + 22, GRAY)

    return img

# ─── Auth / token helpers ─────────────────────────────────────────────────────

def load_token() -> dict:
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE) as f:
            return json.load(f)
    raise FileNotFoundError(f"Token file not found: {TOKEN_FILE}")


def save_token(token: dict) -> None:
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f, indent=2)


def refresh_token(token: dict) -> dict:
    resp = requests.post(
        "https://api.etsy.com/v3/public/oauth/token",
        data={
            "grant_type":    "refresh_token",
            "client_id":     CLIENT_ID,
            "refresh_token": token["refresh_token"],
        },
    )
    resp.raise_for_status()
    new_token = resp.json()
    # Carry forward refresh_token if not returned
    if "refresh_token" not in new_token:
        new_token["refresh_token"] = token["refresh_token"]
    save_token(new_token)
    return new_token


def get_token() -> dict:
    token = load_token()
    # Refresh if access_token missing or token is expiring (best-effort)
    expires_at = token.get("expires_at", 0)
    if time.time() > expires_at - 60:
        try:
            token = refresh_token(token)
        except Exception as e:
            print(f"  [warn] Token refresh failed ({e}); using existing token.")
    return token


def auth_headers(token: dict) -> dict:
    return {
        "Authorization": f"Bearer {token['access_token']}",
        "x-api-key":     CLIENT_ID + ":" + SECRET,
    }

# ─── Upload helper ────────────────────────────────────────────────────────────

def image_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def upload_image(token: dict, listing_id: int, img: Image.Image, rank: int) -> bool:
    url = (
        f"https://openapi.etsy.com/v3/application/shops/{SHOP_ID}"
        f"/listings/{listing_id}/images"
    )
    img_bytes = image_to_bytes(img)
    files = {
        "image": ("image.jpg", img_bytes, "image/jpeg"),
    }
    data = {
        "rank":      str(rank),
        "overwrite": "true",
    }
    resp = requests.post(url, headers=auth_headers(token), files=files, data=data)
    if resp.status_code in (200, 201):
        return True
    print(f"    [error] HTTP {resp.status_code}: {resp.text[:300]}")
    return False

# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    # Load done state
    done: dict = {}
    if DONE_FILE.exists():
        with open(DONE_FILE) as f:
            done = json.load(f)

    token = get_token()

    for key, bundle in BUNDLE_LISTINGS.items():
        listing_id = bundle["listing"]
        label      = f"[{key}]"

        # ── Feature card (rank 2) ─────────────────────────────────────────────
        fc_key = f"{key}_feature"
        if done.get(fc_key):
            print(f"{label} Feature card already uploaded, skipping.")
        else:
            print(f"{label} Uploading feature card (rank 2)…", end=" ", flush=True)
            try:
                fc_img = make_feature_card(bundle)
                ok = upload_image(token, listing_id, fc_img, rank=2)
                if ok:
                    print("✓")
                    done[fc_key] = True
                else:
                    print("✗")
            except Exception as e:
                print(f"✗  ({e})")

        # ── Collage (rank 3) ──────────────────────────────────────────────────
        cl_key = f"{key}_collage"
        if done.get(cl_key):
            print(f"{label} Collage already uploaded, skipping.")
        else:
            print(f"{label} Uploading product collage (rank 3)…", end=" ", flush=True)
            try:
                cl_img = make_collage(bundle)
                ok = upload_image(token, listing_id, cl_img, rank=3)
                if ok:
                    print("✓")
                    done[cl_key] = True
                else:
                    print("✗")
            except Exception as e:
                print(f"✗  ({e})")

        # Save progress after each bundle
        with open(DONE_FILE, "w") as f:
            json.dump(done, f, indent=2)

        time.sleep(1)

    print("\nAll done. State saved to:", DONE_FILE)


if __name__ == "__main__":
    main()
