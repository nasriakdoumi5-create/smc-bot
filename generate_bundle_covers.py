"""
NasriTools - Professional Bundle Cover Images
Generates high-quality 2000x2000px bundle listing images and uploads them.
Run: python generate_bundle_covers.py
"""
import io, json, os, time, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

# All 5 bundles including the Finance one already active
BUNDLES = [
    {
        "listing_id": 4524283886,
        "name": "Complete Finance Control System",
        "subtitle": "Budget + Invoices + Goals",
        "save_pct": "Save 33%",
        "price": "€19.99",
        "individual": "€37",
        "items": [
            ("💰", "Budget & Expense System", "Track every euro automatically"),
            ("📄", "Invoice & Client System", "Get paid on time every time"),
            ("🎯", "Goals & 90-Day Action System", "Achieve more in less time"),
        ],
        "bg": (15, 52, 96),       # deep navy
        "accent": (41, 128, 185), # blue
        "light": (214, 234, 248),
    },
    {
        "listing_id": 4524724720,
        "name": "Complete Health Transformation System",
        "subtitle": "Workout + Meals + Habits",
        "save_pct": "Save 50%",
        "price": "€17.99",
        "individual": "€36",
        "items": [
            ("💪", "Gym & Workout Tracking", "Log sessions. Track PRs. See progress."),
            ("🥗", "Weekly Meal Planning", "7-day meals + auto grocery list"),
            ("✅", "30-Day Habit Building", "30 habits. Auto streaks. Daily wins."),
        ],
        "bg": (11, 61, 35),       # deep green
        "accent": (39, 174, 96),  # green
        "light": (212, 248, 232),
    },
    {
        "listing_id": 4524724758,
        "name": "Complete Planning & Productivity System",
        "subtitle": "Weekly + Student + Goals",
        "save_pct": "Save 50%",
        "price": "€17.99",
        "individual": "€36",
        "items": [
            ("📅", "Weekly Productivity System", "Time blocking. Priorities. Done."),
            ("🎓", "Student Academic System", "GPA tracked. Zero missed deadlines."),
            ("🎯", "Goals & 90-Day Action System", "Break big goals into weekly steps"),
        ],
        "bg": (44, 20, 66),       # deep purple
        "accent": (108, 52, 131), # purple
        "light": (237, 228, 252),
    },
    {
        "listing_id": 4524724798,
        "name": "Complete Creator Business System",
        "subtitle": "Content + Invoices + Budget",
        "save_pct": "Save 50%",
        "price": "€21.99",
        "individual": "€43",
        "items": [
            ("📱", "Content Creator Business", "Plan months of content in one weekend"),
            ("📄", "Invoice & Client System", "Get paid on time. Every time."),
            ("💰", "Budget & Expense System", "Know where every euro goes"),
        ],
        "bg": (98, 44, 5),        # deep orange
        "accent": (230, 126, 34), # orange
        "light": (254, 243, 224),
    },
    {
        "listing_id": 4524724846,
        "name": "The Complete Life System",
        "subtitle": "All 10 Google Sheets | Save 65%",
        "save_pct": "Save 65%",
        "price": "€39.99",
        "individual": "€120",
        "items": [
            ("💰", "Finance (Budget + Invoice + Goals)", "Complete financial control"),
            ("💪", "Health (Workout + Meals + Habits)", "Total health transformation"),
            ("🚀", "Business (Content + Planning)", "Creator & productivity systems"),
            ("📅", "Planning (Weekly + Student)", "Academic & personal success"),
            ("💍", "Wedding Planner", "Your perfect wedding, organized"),
        ],
        "bg": (10, 10, 40),       # deep dark blue
        "accent": (41, 128, 185), # blue
        "light": (214, 234, 248),
        "is_ultimate": True,
    },
]

FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_REG_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_font(paths, size):
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


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


def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                           outline=outline, width=width)


def generate_bundle_image(bundle):
    W, H = 2000, 2000
    is_ultimate = bundle.get("is_ultimate", False)

    img  = Image.new("RGB", (W, H), bundle["bg"])
    draw = ImageDraw.Draw(img)

    accent = bundle["accent"]
    light  = bundle["light"]
    ar, ag, ab = accent
    bg = bundle["bg"]

    # ── Subtle grid pattern ──────────────────────────────────────
    for x in range(0, W, 80):
        draw.line([(x, 0), (x, H)], fill=(ar, ag, ab, 12), width=1)
    for y in range(0, H, 80):
        draw.line([(0, y), (W, y)], fill=(ar, ag, ab, 12), width=1)

    # ── Top gradient bar ─────────────────────────────────────────
    for i in range(300):
        alpha = int(255 * (1 - i / 300))
        r = min(255, ar + int((255 - ar) * i / 600))
        g = min(255, ag + int((255 - ag) * i / 600))
        b = min(255, ab + int((255 - ab) * i / 600))
        draw.line([(0, i), (W, i)], fill=(r, g, b))

    # ── Brand + badge row ─────────────────────────────────────────
    fb_sm = load_font(FONT_BOLD_PATHS, 42)
    fb_xs = load_font(FONT_BOLD_PATHS, 36)
    fr_sm = load_font(FONT_REG_PATHS, 36)

    draw.text((70, 40), "NASRITOOLS", font=fb_sm, fill=(255, 255, 255, 160))

    # Save badge
    badge_txt = bundle["save_pct"]
    bw = 260 if is_ultimate else 230
    draw_rounded_rect(draw, [W - bw - 50, 32, W - 50, 100], radius=16, fill=(255, 220, 0))
    draw.text((W - bw - 50 + 22, 42), badge_txt,
              font=load_font(FONT_BOLD_PATHS, 40), fill=(30, 30, 30))

    # ── Main title ────────────────────────────────────────────────
    fb_xl = load_font(FONT_BOLD_PATHS, 80 if is_ultimate else 90)
    fb_lg = load_font(FONT_BOLD_PATHS, 60)

    name_lines = bundle["name"].split(" | ") if " | " in bundle["name"] else [bundle["name"]]
    y_title = 130
    for line in name_lines[:2]:
        draw.text((70, y_title), line, font=fb_xl, fill=(255, 255, 255))
        y_title += 95

    # Subtitle
    draw.text((72, y_title + 8), bundle["subtitle"],
              font=load_font(FONT_BOLD_PATHS, 56), fill=(ar + 80, ag + 80, ab + 80))
    y_title += 80

    # ── Price banner ───────────────────────────────────────────────
    price_y = y_title + 30
    draw_rounded_rect(draw, [70, price_y, 650, price_y + 90], radius=14, fill=accent)
    draw.text((90, price_y + 12), f"BUNDLE PRICE: {bundle['price']}",
              font=load_font(FONT_BOLD_PATHS, 46), fill=(255, 255, 255))

    draw.text((670, price_y + 18),
              f"(individually {bundle['individual']})",
              font=load_font(FONT_REG_PATHS, 38), fill=(180, 200, 220))

    # ── Divider ────────────────────────────────────────────────────
    div_y = price_y + 130
    draw.rectangle([(70, div_y), (W - 70, div_y + 3)], fill=accent)

    # ── Items / What's included ────────────────────────────────────
    draw.text((70, div_y + 22),
              "WHAT'S INCLUDED:" if not is_ultimate else "ALL 10 SYSTEMS:",
              font=load_font(FONT_BOLD_PATHS, 50), fill=light)

    y_item = div_y + 100
    card_h = 155 if is_ultimate else 175
    card_gap = 20 if is_ultimate else 24

    for emoji, title, desc in bundle["items"]:
        # Card background
        draw_rounded_rect(draw, [70, y_item, W - 70, y_item + card_h],
                          radius=20, fill=(255, 255, 255, 18))
        draw_rounded_rect(draw, [70, y_item, W - 70, y_item + card_h],
                          radius=20, fill=None,
                          outline=(ar, ag, ab, 80), width=2)

        # Emoji circle
        circle_cx = 148
        circle_r = 44
        draw.ellipse([(circle_cx - circle_r, y_item + 18),
                      (circle_cx + circle_r, y_item + 18 + circle_r * 2)],
                     fill=accent)
        em_font = load_font(FONT_BOLD_PATHS, 40)
        draw.text((circle_cx - 20, y_item + 26), emoji, font=em_font, fill=(255, 255, 255))

        # Title + desc
        draw.text((215, y_item + 18),
                  title, font=load_font(FONT_BOLD_PATHS, 46 if not is_ultimate else 42),
                  fill=(255, 255, 255))
        draw.text((215, y_item + 78 if not is_ultimate else y_item + 70),
                  desc, font=load_font(FONT_REG_PATHS, 34),
                  fill=(180, 200, 220))

        y_item += card_h + card_gap

    # ── Bottom strip ───────────────────────────────────────────────
    strip_y = H - 170
    draw.rectangle([(0, strip_y), (W, H)], fill=accent)

    features = [
        "⚡ Instant Download",
        "✅ Google Sheets (FREE) + Excel",
        "♾️ Lifetime Access",
        "🔒 Buy Once — Yours Forever",
    ]
    fx = 70
    fy = strip_y + 28
    f_feat = load_font(FONT_BOLD_PATHS, 38)
    f_feat2 = load_font(FONT_REG_PATHS, 34)
    for feat in features[:2]:
        draw.text((fx, fy), feat, font=f_feat, fill=(255, 255, 255))
        fx += 520
    fx = 70
    fy += 70
    for feat in features[2:]:
        draw.text((fx, fy), feat, font=f_feat, fill=(255, 255, 255, 210))
        fx += 520

    # Site URL
    draw.text((W - 380, strip_y + 110), "nasritools.etsy.com",
              font=load_font(FONT_REG_PATHS, 30), fill=(255, 255, 255, 160))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=94)
    buf.seek(0)
    return buf


def upload_image(token, listing_id, img_buf, rank=1):
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images",
        headers=auth_headers(token),
        files={"image": ("bundle_cover.jpg", img_buf, "image/jpeg")},
        data={"rank": rank, "overwrite": "true"},
        timeout=60,
    )
    return r.ok, r.status_code


def main():
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Professional Bundle Cover Images")
    print(f"  Generating for all 5 bundles")
    print(f"{'='*65}\n")

    ok = 0
    for i, bundle in enumerate(BUNDLES, 1):
        lid  = bundle["listing_id"]
        name = bundle["name"]
        print(f"[{i}/5] {name[:55]}…")
        print(f"  Generating 2000×2000px cover…", end=" ", flush=True)

        try:
            img_buf = generate_bundle_image(bundle)
            print("done")
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        token = get_token()
        print(f"  Uploading to listing {lid}…", end=" ", flush=True)
        img_ok, code = upload_image(token, lid, img_buf, rank=1)
        print(f"{'✓' if img_ok else f'✗ ({code})'}")

        if img_ok:
            ok += 1
            print(f"  → https://www.etsy.com/listing/{lid}")
        print()
        time.sleep(2)
        token = get_token()

    print(f"{'='*65}")
    print(f"  Done: {ok}/5 bundle images updated")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
