"""
NasriTools - Professional Bundle Cover Images (v2)
Clean result-focused design matching individual product image style.
Run: python generate_bundle_covers.py
"""
import io, json, os, time, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

BUNDLES = [
    {
        "listing_id": 4524283886,
        "headline1": "Total Financial Control.",
        "headline2": "Budget. Invoices. Goals.",
        "result": "Know where every euro goes. Get paid on time. Achieve every goal.",
        "badge": "3 SYSTEMS • SAVE 33%",
        "price": "€19.99  (worth €37)",
        "items": ["Budget & Expense System", "Invoice & Client System", "Goals & 90-Day System"],
        "bg":    (14, 35, 64),
        "mid":   (22, 58, 108),
        "accent":(41, 128, 185),
        "tag_c": (255, 200, 0),
    },
    {
        "listing_id": 4524724720,
        "headline1": "Transform Your Health.",
        "headline2": "Workout. Eat. Build Habits.",
        "result": "Track every session. Plan every meal. Build 30 habits — automatically.",
        "badge": "3 SYSTEMS • SAVE 50%",
        "price": "€17.99  (worth €36)",
        "items": ["Gym & Workout Tracking", "Weekly Meal Planning", "30-Day Habit Building"],
        "bg":    (10, 40, 20),
        "mid":   (18, 68, 34),
        "accent":(39, 174, 96),
        "tag_c": (255, 220, 0),
    },
    {
        "listing_id": 4524724758,
        "headline1": "Master Your Time.",
        "headline2": "Weekly. Academic. Goals.",
        "result": "Plan your perfect week. Ace every semester. Achieve every goal.",
        "badge": "3 SYSTEMS • SAVE 50%",
        "price": "€17.99  (worth €36)",
        "items": ["Weekly Productivity System", "Student Academic System", "Goals & 90-Day System"],
        "bg":    (30, 10, 50),
        "mid":   (55, 22, 90),
        "accent":(142, 68, 173),
        "tag_c": (255, 230, 0),
    },
    {
        "listing_id": 4524724798,
        "headline1": "Run Your Business.",
        "headline2": "Content. Invoices. Money.",
        "result": "Grow your audience. Get paid. Know your numbers — all in one system.",
        "badge": "3 SYSTEMS • SAVE 50%",
        "price": "€21.99  (worth €43)",
        "items": ["Content Creator System", "Invoice & Client System", "Budget & Expense System"],
        "bg":    (55, 25, 5),
        "mid":   (100, 45, 8),
        "accent":(211, 84, 0),
        "tag_c": (255, 240, 0),
    },
    {
        "listing_id": 4524724846,
        "headline1": "Systems That Run",
        "headline2": "Your Entire Life.",
        "result": "Finance. Health. Business. Planning. All 10 premium Google Sheets in one bundle.",
        "badge": "10 SYSTEMS • SAVE 65%",
        "price": "€39.99  (worth €120)",
        "items": [
            "Budget • Invoice • Goals",
            "Workout • Meals • Habits",
            "Content • Student • Weekly • Wedding",
        ],
        "bg":    (8, 8, 25),
        "mid":   (15, 15, 50),
        "accent":(52, 152, 219),
        "tag_c": (255, 200, 0),
        "is_ultimate": True,
    },
]

BOLD_FONTS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
REG_FONTS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]


def font(paths, size):
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(text, f, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=f) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


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


def generate(b):
    W, H = 2000, 2000
    img  = Image.new("RGB", (W, H), b["bg"])
    draw = ImageDraw.Draw(img)
    acc  = b["accent"]
    mid  = b["mid"]
    is_u = b.get("is_ultimate", False)

    # ── Background: subtle diagonal gradient bands ────────────────
    for i in range(H):
        t = i / H
        r = int(b["bg"][0] * (1 - t) + mid[0] * t)
        g = int(b["bg"][1] * (1 - t) + mid[1] * t)
        bv= int(b["bg"][2] * (1 - t) + mid[2] * t)
        draw.line([(0, i), (W, i)], fill=(r, g, bv))

    # ── Accent top bar ────────────────────────────────────────────
    for i in range(12):
        alpha = 1 - i / 12
        c = tuple(int(acc[j] * alpha) for j in range(3))
        draw.line([(0, i), (W, i)], fill=c)

    # ── NASRITOOLS brand ──────────────────────────────────────────
    fb40 = font(BOLD_FONTS, 40)
    draw.text((80, 48), "NASRITOOLS", font=fb40, fill=(255, 255, 255, 120))

    # ── Badge (top right) ─────────────────────────────────────────
    fb42 = font(BOLD_FONTS, 42)
    badge_txt = b["badge"]
    bw = int(draw.textlength(badge_txt, font=fb42)) + 60
    bx = W - bw - 60
    draw.rounded_rectangle([bx, 32, W - 60, 102], radius=18, fill=b["tag_c"])
    draw.text((bx + 30, 42), badge_txt, font=fb42, fill=(20, 20, 20))

    # ── Accent horizontal divider under brand ─────────────────────
    draw.rectangle([(80, 118), (W - 80, 122)], fill=acc)

    # ── Main headline ─────────────────────────────────────────────
    fb100 = font(BOLD_FONTS, 108 if not is_u else 96)
    fb90  = font(BOLD_FONTS, 90 if not is_u else 82)

    draw.text((80, 145), b["headline1"], font=fb100, fill=(255, 255, 255))
    draw.text((82, 270 if not is_u else 258), b["headline2"], font=fb90, fill=acc)

    # ── Result statement ──────────────────────────────────────────
    fr50 = font(REG_FONTS, 52)
    y_res = 420 if not is_u else 390
    result_lines = wrap(b["result"], fr50, W - 160, draw)
    for line in result_lines[:3]:
        draw.text((80, y_res), line, font=fr50, fill=(200, 215, 235))
        y_res += 68

    # ── Price pill ────────────────────────────────────────────────
    y_price = y_res + 30
    fb50 = font(BOLD_FONTS, 52)
    pw = int(draw.textlength(b["price"], font=fb50)) + 80
    draw.rounded_rectangle([80, y_price, 80 + pw, y_price + 80], radius=16, fill=acc)
    draw.text((114, y_price + 13), b["price"], font=fb50, fill=(255, 255, 255))

    # ── What's included section ───────────────────────────────────
    y_inc = y_price + 130
    draw.rectangle([(80, y_inc), (W - 80, y_inc + 3)], fill=(255, 255, 255, 40))

    fb46 = font(BOLD_FONTS, 48)
    fr44 = font(REG_FONTS, 44)

    draw.text((80, y_inc + 18), "WHAT'S INCLUDED:", font=fb46, fill=(255, 255, 255, 160))
    y_inc += 90

    for item in b["items"]:
        # Bullet dot
        draw.ellipse([(80, y_inc + 14), (104, y_inc + 38)], fill=acc)
        draw.text((124, y_inc), item, font=fr44, fill=(230, 240, 255))
        y_inc += 70

    # ── Bottom feature strip ──────────────────────────────────────
    strip_y = H - 200
    draw.rectangle([(0, strip_y), (W, H)], fill=acc)

    feats = [
        "⚡ Instant Download",
        "✅ Google Sheets (FREE) & Excel",
        "♾️ Lifetime Access — Buy Once",
        "🔒 No Subscription Ever",
    ]
    fb38 = font(BOLD_FONTS, 38)
    x, y_f = 80, strip_y + 28
    for feat in feats[:2]:
        draw.text((x, y_f), feat, font=fb38, fill=(255, 255, 255))
        x += W // 2 - 40
    x, y_f = 80, strip_y + 106
    for feat in feats[2:]:
        draw.text((x, y_f), feat, font=fb38, fill=(255, 255, 255, 210))
        x += W // 2 - 40

    draw.text((W - 380, strip_y + 150), "nasritools.etsy.com",
              font=font(REG_FONTS, 30), fill=(255, 255, 255, 140))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf


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
    print(f"  NasriTools - Bundle Covers v2 (result-focused)")
    print(f"{'='*65}\n")

    ok = 0
    for i, b in enumerate(BUNDLES, 1):
        lid = b["listing_id"]
        print(f"[{i}/5] {b['headline1']} {b['headline2']}")
        print(f"  Generating…", end=" ", flush=True)
        try:
            buf = generate(b)
            print("done")
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        token = get_token()
        print(f"  Uploading to [{lid}]…", end=" ", flush=True)
        img_ok, code, txt = upload_image(token, lid, buf)
        print(f"{'✓' if img_ok else f'✗ {code}: {txt}'}")
        if img_ok:
            ok += 1
            print(f"  → https://www.etsy.com/listing/{lid}")
        print()
        time.sleep(2)
        token = get_token()

    print(f"{'='*65}")
    print(f"  Done: {ok}/5 covers updated")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
