"""
NasriTools - Generate Promotional Videos for 5 Bundle Listings
Creates a 12-second MP4 video for each bundle and uploads to Etsy.
Run: python generate_bundle_videos.py
"""
import json, os, time, requests, io, math, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

try:
    import cv2
    import numpy as np
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python-headless", "numpy"])
    import cv2
    import numpy as np

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_bundle_videos_done.json"

W, H   = 1920, 1080
FPS    = 30
TOTAL  = 12 * FPS  # 360 frames

BUNDLES = [
    {
        "listing": 4524283814,
        "name": "Finance Bundle",
        "subtitle": "Budget Tracker + Invoice Tracker + Goals Planner",
        "count": "3 Premium Templates",
        "price": "€17.99",
        "save": "Save 50%",
        "color": (31, 107, 59),
        "light": (220, 247, 233),
        "emoji": "💰",
        "products": ["Budget Tracker", "Invoice Tracker", "Goals Planner"],
        "descs": ["Track income & expenses", "Manage clients & payments", "Annual goals & plans"],
    },
    {
        "listing": 4524276503,
        "name": "Health Bundle",
        "subtitle": "Workout Tracker + Meal Planner + Habit Tracker",
        "count": "3 Premium Templates",
        "price": "€16.99",
        "save": "Save 50%",
        "color": (192, 57, 43),
        "light": (253, 228, 224),
        "emoji": "💪",
        "products": ["Workout Tracker", "Meal Planner", "Habit Tracker"],
        "descs": ["Log every gym session", "7-day meals + grocery list", "Track 30 daily habits"],
    },
    {
        "listing": 4524276527,
        "name": "Planner Bundle",
        "subtitle": "Weekly Planner + Student Planner + Goals Planner",
        "count": "3 Premium Templates",
        "price": "€16.99",
        "save": "Save 50%",
        "color": (108, 52, 131),
        "light": (237, 228, 252),
        "emoji": "📅",
        "products": ["Weekly Planner", "Student Planner", "Goals Planner"],
        "descs": ["Time blocking & tasks", "Grades, GPA & schedule", "Annual goals & milestones"],
    },
    {
        "listing": 4524276553,
        "name": "Business Bundle",
        "subtitle": "Content Creator + Invoice Tracker + Goals Planner",
        "count": "3 Premium Templates",
        "price": "€21.99",
        "save": "Save 50%",
        "color": (230, 126, 34),
        "light": (254, 243, 224),
        "emoji": "💼",
        "products": ["Content Creator Planner", "Invoice Tracker", "Goals Planner"],
        "descs": ["Content calendar & analytics", "Clients & tax prep", "Annual goals & milestones"],
    },
    {
        "listing": 4524283886,
        "name": "Ultimate Bundle",
        "subtitle": "All 10 Google Sheets Templates",
        "count": "10 Premium Templates",
        "price": "€39.99",
        "save": "Save 65%",
        "color": (30, 100, 180),
        "light": (220, 235, 252),
        "emoji": "⭐",
        "products": [
            "Budget Tracker", "Habit Tracker", "Meal Planner", "Wedding Planner",
            "Workout Tracker", "Content Creator", "Invoice Tracker",
            "Student Planner", "Goals Planner", "Weekly Planner",
        ],
        "descs": [
            "Track income & expenses", "30 daily habits", "7-day meals", "Budget & guests",
            "Gym log", "Content calendar", "Clients & invoices",
            "Grades & GPA", "Annual goals", "Time blocking",
        ],
    },
]


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


def load_font(size):
    for f in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def load_font_reg(size):
    for f in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


def ease_out(t):
    return 1 - (1 - t) ** 3


def pil_to_cv(img):
    arr = np.array(img.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


# ── Section 1 (frames 0-89): Title reveal ────────────────────────────────────

def draw_title_frame(bundle, frame):
    prog = ease_out(frame / 89)
    color = bundle["color"]
    light = bundle["light"]
    r, g, b = color

    img  = Image.new("RGB", (W, H), color)
    draw = ImageDraw.Draw(img)

    # Pulsing background circle
    rad = int(lerp(200, 340, 0.5 + 0.5 * math.sin(frame * 0.12)))
    draw.ellipse([W // 2 - rad, H // 2 - rad, W // 2 + rad, H // 2 + rad],
                 fill=(min(r + 30, 255), min(g + 30, 255), min(b + 30, 255)))

    # Brand name slide in from left
    bx = int(lerp(-400, 60, prog))
    draw.text((bx, 60), "NasriTools", font=load_font(72), fill=(255, 255, 220))

    # Emoji fade in centred
    alpha_val = int(prog * 255)
    emoji_img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ed = ImageDraw.Draw(emoji_img)
    try:
        ed.text((100, 100), bundle["emoji"], font=load_font(120), anchor="mm",
                fill=(255, 255, 255, alpha_val))
    except Exception:
        ed.text((100, 100), bundle["emoji"], font=load_font(120), anchor="mm",
                fill=(255, 255, 255))
    img.paste(emoji_img, (W // 2 - 100, H // 2 - 250), emoji_img)

    draw = ImageDraw.Draw(img)

    # Bundle name slide from right
    nx = int(lerp(W + 100, W // 2, prog))
    draw.text((nx, H // 2 - 60), bundle["name"].upper(), font=load_font(96),
              fill=(255, 255, 255), anchor="mm")

    # Subtitle fade
    sub_alpha = int(lerp(0, 255, prog))
    draw.text((W // 2, H // 2 + 60), bundle["subtitle"],
              font=load_font_reg(46), fill=(255, 255, sub_alpha), anchor="mm")

    # Count pill
    if prog > 0.5:
        pill_prog = (prog - 0.5) * 2
        pw, ph = 340, 70
        px = W // 2 - pw // 2
        py = H // 2 + 140
        draw.rounded_rectangle([px, py, px + pw, py + ph], radius=35,
                                fill=(255, 255, 255))
        draw.text((W // 2, py + ph // 2), bundle["count"],
                  font=load_font(42), fill=color, anchor="mm")

    return img


# ── Section 2 (frames 90-209): Product cards scroll in ───────────────────────

def draw_products_frame(bundle, frame):
    local_f = frame - 90
    total_f = 120
    color   = bundle["color"]
    light   = bundle["light"]
    products = bundle["products"]
    descs    = bundle["descs"]
    n        = len(products)

    img  = Image.new("RGB", (W, H), light)
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([0, 0, W, 160], fill=color)
    draw.text((W // 2, 80), f"{bundle['name']} — What's Included",
              font=load_font(60), fill=(255, 255, 255), anchor="mm")

    # Determine grid
    if n <= 3:
        cols, rows_n = n, 1
    elif n <= 6:
        cols, rows_n = 3, 2
    else:
        cols, rows_n = 5, 2

    margin  = 60
    gap     = 24
    top     = 200
    bottom  = H - 100

    card_w = (W - 2 * margin - gap * (cols - 1)) // cols
    card_h = (bottom - top - gap * (rows_n - 1)) // rows_n

    EMOJI_MAP = {
        "Budget Tracker": "💰", "Habit Tracker": "✅", "Meal Planner": "🥗",
        "Wedding Planner": "💍", "Workout Tracker": "💪", "Content Creator": "📱",
        "Content Creator Planner": "📱", "Invoice Tracker": "📄",
        "Freelancer Invoice Tracker": "📄", "Student Planner": "🎓",
        "Goals Planner": "🎯", "Weekly Planner": "📅",
    }
    COLORS = [
        (31, 107, 59), (192, 57, 43), (39, 174, 141), (210, 82, 162),
        (192, 57, 43), (230, 126, 34), (52, 152, 219), (108, 52, 131),
        (30, 100, 180), (108, 52, 131),
    ]

    for idx, (prod, desc) in enumerate(zip(products, descs)):
        row = idx // cols
        col = idx % cols
        # Stagger animation: each card arrives with small delay
        delay = idx * (total_f / max(n, 1)) * 0.4
        prog  = ease_out(max(0, (local_f - delay) / (total_f * 0.6)))

        x0 = margin + col * (card_w + gap)
        y0 = top + row * (card_h + gap)
        x1 = x0 + card_w
        y1 = y0 + card_h

        # Slide in from bottom
        offset = int(lerp(200, 0, prog))
        y0 += offset
        y1 += offset

        if y0 > H:
            continue

        ic = COLORS[idx % len(COLORS)]
        # Shadow
        draw.rounded_rectangle([x0 + 4, y0 + 4, x1 + 4, y1 + 4], radius=18,
                                fill=(160, 165, 175))
        # Card
        draw.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=ic)
        # Bottom lighter panel
        panel_y = y0 + int(card_h * 0.55)
        pr, pg, pb = ic
        panel_col = (min(pr + 35, 255), min(pg + 35, 255), min(pb + 35, 255))
        draw.rounded_rectangle([x0, panel_y, x1, y1], radius=18, fill=panel_col)
        draw.rectangle([x0, panel_y, x1, panel_y + 20], fill=panel_col)
        draw.rectangle([x0, panel_y - 1, x1, panel_y + 1], fill=ic)

        # Emoji
        emoji = EMOJI_MAP.get(prod, "📋")
        try:
            draw.text(((x0 + x1) // 2, y0 + int(card_h * 0.3)),
                      emoji, font=load_font(52), fill=(255, 255, 255), anchor="mm")
        except Exception:
            pass

        # Name
        draw.text(((x0 + x1) // 2, panel_y + 28), prod,
                  font=load_font(max(20, card_w // 10)), fill=(255, 255, 255), anchor="mm")
        # Desc (truncate)
        desc_text = desc
        f_small = load_font_reg(22)
        while len(desc_text) > 2 and draw.textlength(desc_text, font=f_small) > card_w - 20:
            desc_text = desc_text[:-1]
        draw.text(((x0 + x1) // 2, panel_y + 62), desc_text,
                  font=f_small, fill=(255, 255, 255), anchor="mm")

    # Bottom price strip
    draw.rectangle([0, H - 90, W, H], fill=color)
    r2, g2, b2 = color
    draw.text((W // 2, H - 45),
              f"Bundle Price: {bundle['price']}  |  {bundle['save']}  |  Instant Download",
              font=load_font(40), fill=(255, 255, 220), anchor="mm")

    return img


# ── Section 3 (frames 210-299): Feature checklist ────────────────────────────

FEATURES = [
    "✔  Instant Digital Download — no waiting",
    "✔  Works on Google Sheets & Excel",
    "✔  Fully Customizable — edit everything",
    "✔  Auto-Calculating Formulas Built In",
    "✔  Lifetime Access — yours forever",
    "✔  No Subscription, No App Needed",
]


def draw_features_frame(bundle, frame):
    local_f = frame - 210
    color = bundle["color"]
    light = bundle["light"]

    img  = Image.new("RGB", (W, H), light)
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, W, 140], fill=color)
    draw.text((W // 2, 70), "Why Choose NasriTools?",
              font=load_font(62), fill=(255, 255, 255), anchor="mm")

    # Feature rows slide in from right, staggered
    fy = 200
    fh = 110
    for i, feat in enumerate(FEATURES):
        delay = i * 12
        prog  = ease_out(max(0, (local_f - delay) / 50))
        fx    = int(lerp(W + 100, 120, prog))

        # Guard: only draw if card is at least partially on-screen
        if fx >= W - 60:
            fy += fh + 20
            continue

        fw = min(W - fx - 60, W - 180)
        x1 = fx + fw
        y1 = fy + fh
        if fw > 0 and fh > 0:
            # Shadow
            draw.rounded_rectangle([fx + 4, fy + 4, x1 + 4, y1 + 4],
                                    radius=16, fill=(180, 185, 195))
            # Card
            draw.rounded_rectangle([fx, fy, x1, y1], radius=16, fill=(255, 255, 255))
            # Left bar
            lx1 = min(fx + 10, x1)
            draw.rounded_rectangle([fx, fy, lx1, y1], radius=8, fill=color)
            # Text
            draw.text((fx + 40, fy + fh // 2), feat,
                      font=load_font(38), fill=(40, 40, 50), anchor="lm")

        fy += fh + 20

    # Bottom
    draw.rectangle([0, H - 80, W, H], fill=color)
    draw.text((W // 2, H - 40), f"nasritools.etsy.com  •  Google Sheets Templates",
              font=load_font_reg(34), fill=(255, 255, 255), anchor="mm")

    return img


# ── Section 4 (frames 300-359): CTA ──────────────────────────────────────────

def draw_cta_frame(bundle, frame):
    local_f = frame - 300
    prog    = ease_out(local_f / 59)
    color   = bundle["color"]
    r, g, b = color
    pulse   = 0.5 + 0.5 * math.sin(local_f * 0.18)

    img  = Image.new("RGB", (W, H), color)
    draw = ImageDraw.Draw(img)

    # Pulsing circle
    rad = int(lerp(280, 380, pulse))
    pc  = (min(r + 40, 255), min(g + 40, 255), min(b + 40, 255))
    draw.ellipse([W // 2 - rad, H // 2 - rad, W // 2 + rad, H // 2 + rad], fill=pc)

    # Save badge
    badge_r = int(lerp(0, 110, ease_out(local_f / 30)))
    if badge_r > 5:
        draw.ellipse([W // 2 - badge_r, 80 - badge_r, W // 2 + badge_r, 80 + badge_r],
                     fill=(255, 215, 0))
        draw.text((W // 2, 60), bundle["save"], font=load_font(46),
                  fill=(60, 30, 0), anchor="mm")

    # Heading slide in
    hx = int(lerp(-500, W // 2, ease_out(min(1, local_f / 25))))
    draw.text((hx, H // 2 - 160), "GET THE BUNDLE TODAY",
              font=load_font(80), fill=(255, 255, 255), anchor="mm")

    # Price
    if local_f > 20:
        draw.text((W // 2, H // 2 - 60), bundle["price"],
                  font=load_font(120), fill=(255, 215, 0), anchor="mm")

    # CTA button
    if local_f > 30:
        btn_prog = ease_out((local_f - 30) / 25)
        bw, bh   = int(btn_prog * 560), 90
        bx       = W // 2 - bw // 2
        by       = H // 2 + 60
        if bw > 10:
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=45,
                                    fill=(255, 255, 255))
            if btn_prog > 0.7:
                draw.text((W // 2, by + bh // 2), "Add to Cart on Etsy →",
                          font=load_font(44), fill=color, anchor="mm")

    # Bottom strip
    draw.rectangle([0, H - 90, W, H], fill=(20, 20, 30))
    draw.text((W // 2, H - 45), "nasritools.etsy.com  •  Instant Download",
              font=load_font_reg(36), fill=(200, 225, 255), anchor="mm")

    return img


# ── Video builder ─────────────────────────────────────────────────────────────

def build_video(bundle):
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp.close()
    path = tmp.name

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out    = cv2.VideoWriter(path, fourcc, FPS, (W, H))

    for f in range(TOTAL):
        if f < 90:
            frame_img = draw_title_frame(bundle, f)
        elif f < 210:
            frame_img = draw_products_frame(bundle, f)
        elif f < 300:
            frame_img = draw_features_frame(bundle, f)
        else:
            frame_img = draw_cta_frame(bundle, f)

        out.write(pil_to_cv(frame_img))

    out.release()
    return path


def upload_video(token, listing_id, video_path):
    with open(video_path, "rb") as f:
        r = requests.post(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/videos",
            headers=auth_headers(token),
            files={"video": ("bundle_promo.mp4", f, "video/mp4")},
            data={"name": "Bundle Promo Video"},
            timeout=180,
        )
    return r


def main():
    done = {}
    if DONE_FILE.exists():
        done = json.loads(DONE_FILE.read_text())

    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Bundle Promo Videos")
    print(f"{'='*65}\n")

    ok = 0
    for bundle in BUNDLES:
        key = str(bundle["listing"])
        if done.get(key):
            print(f"  [{bundle['name']}] skipped (already done)")
            ok += 1
            continue

        print(f"  [{bundle['name']}] rendering {TOTAL} frames…", end=" ", flush=True)
        video_path = build_video(bundle)
        size_kb    = Path(video_path).stat().st_size // 1024
        print(f"✓ ({size_kb}KB)  uploading…", end=" ", flush=True)

        r = upload_video(token, bundle["listing"], video_path)
        os.unlink(video_path)
        time.sleep(3)

        if r.ok:
            print("✓")
            done[key] = True
            ok += 1
        else:
            print(f"✗  {r.status_code}: {r.text[:120]}")

        DONE_FILE.write_text(json.dumps(done, indent=2))
        token = get_token()

    print(f"\n{'='*65}")
    print(f"  Done: {ok}/{len(BUNDLES)} bundle videos uploaded")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
