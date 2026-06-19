"""
NasriTools - Bundle Cover Images (v3)
Matches the visual style of individual product images: circle-centered design,
large bold result text, benefit pill, footer bar.
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
        "color":  (20, 90, 50),
        "light":  (220, 247, 233),
        "emoji":  "💰",
        "line1":  "Total Financial Control.",
        "line2":  "Budget. Invoices. Goals.",
        "badge_top":  "3 SYSTEMS BUNDLE",
        "badge_bot":  "€19.99  ·  Save 33%",
        "items":  ["Budget & Expense System", "Invoice & Client System", "Goals & 90-Day System"],
    },
    {
        "listing_id": 4524724720,
        "color":  (25, 110, 55),
        "light":  (212, 248, 232),
        "emoji":  "💪",
        "line1":  "Transform Your Health.",
        "line2":  "Workout. Eat. Build Habits.",
        "badge_top":  "3 SYSTEMS BUNDLE",
        "badge_bot":  "€17.99  ·  Save 50%",
        "items":  ["Gym & Workout Tracking", "Weekly Meal Planning", "30-Day Habit Building"],
    },
    {
        "listing_id": 4524724758,
        "color":  (72, 30, 110),
        "light":  (237, 228, 252),
        "emoji":  "📅",
        "line1":  "Master Your Time.",
        "line2":  "Weekly. Academic. Goals.",
        "badge_top":  "3 SYSTEMS BUNDLE",
        "badge_bot":  "€17.99  ·  Save 50%",
        "items":  ["Weekly Productivity System", "Student Academic System", "Goals & 90-Day System"],
    },
    {
        "listing_id": 4524724798,
        "color":  (140, 50, 10),
        "light":  (254, 235, 220),
        "emoji":  "🚀",
        "line1":  "Run Your Business.",
        "line2":  "Content. Invoices. Budget.",
        "badge_top":  "3 SYSTEMS BUNDLE",
        "badge_bot":  "€21.99  ·  Save 50%",
        "items":  ["Content Creator System", "Invoice & Client System", "Budget & Expense System"],
    },
    {
        "listing_id": 4524724846,
        "color":  (15, 25, 80),
        "light":  (220, 230, 255),
        "emoji":  "⭐",
        "line1":  "Systems That Run",
        "line2":  "Your Entire Life.",
        "badge_top":  "10 SYSTEMS BUNDLE",
        "badge_bot":  "€39.99  ·  Save 65%",
        "items":  ["Finance · Health · Business", "Planning · Student · Content", "+ 4 More Premium Systems"],
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
EMOJI_FONTS = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/noto/NotoColorEmoji.ttf",
]


def _font(paths, size):
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fb(size): return _font(BOLD_FONTS, size)
def fr(size): return _font(REG_FONTS, size)


def darken(c, f=0.80):
    return tuple(max(0, int(x * f)) for x in c)


def lighten(c, f=1.18):
    return tuple(min(255, int(x * f)) for x in c)


def centered_text(draw, text, font, cx, y, fill):
    bb = draw.textbbox((0, 0), text, font=font)
    w = bb[2] - bb[0]
    draw.text((cx - w // 2, y), text, font=font, fill=fill)
    return bb[3] - bb[1]


def wrap(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bb = draw.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    r = min(radius, (x1-x0)//2, (y1-y0)//2)
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    draw.ellipse([x0, y0, x0+2*r, y0+2*r], fill=fill)
    draw.ellipse([x1-2*r, y0, x1, y0+2*r], fill=fill)
    draw.ellipse([x0, y1-2*r, x0+2*r, y1], fill=fill)
    draw.ellipse([x1-2*r, y1-2*r, x1, y1], fill=fill)


def draw_emoji(img, emoji_char, cx, cy, size):
    for p in EMOJI_FONTS:
        if not Path(p).exists():
            continue
        try:
            ef = ImageFont.truetype(p, size)
            tmp = Image.new("RGBA", (size*2, size*2), (0, 0, 0, 0))
            td = ImageDraw.Draw(tmp)
            td.text((0, 0), emoji_char, font=ef, embedded_color=True)
            bb = tmp.getbbox()
            if bb:
                tmp = tmp.crop(bb).resize((size, size), Image.LANCZOS)
            img.paste(tmp, (cx - size//2, cy - size//2), tmp)
            return
        except Exception:
            continue


def generate(b):
    W, H = 2000, 2000
    color = b["color"]
    light = b["light"]

    img  = Image.new("RGB", (W, H), color)
    draw = ImageDraw.Draw(img)

    cx = W // 2
    cy = H // 2

    # ── Large background circle (slightly lighter) ────────────────────
    cr = 820
    draw.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=lighten(color, 1.15))

    # ── Inner circle ring accent ──────────────────────────────────────
    cr2 = 760
    draw.ellipse([cx-cr2, cy-cr2, cx+cr2, cy+cr2], fill=lighten(color, 1.10))

    # ── Brand top-left ────────────────────────────────────────────────
    draw.text((60, 58), "NasriTools", font=fr(44), fill=light)

    # ── "BUNDLE" badge top-right ──────────────────────────────────────
    badge_f = fb(38)
    badge_txt = b["badge_top"]
    bb = draw.textbbox((0, 0), badge_txt, font=badge_f)
    bw = bb[2] - bb[0]
    pad = 36
    bx0 = W - bw - pad*2 - 60
    bx1 = W - 60
    by0 = 42
    by1 = by0 + 72
    rounded_rect(draw, (bx0, by0, bx1, by1), 20, light)
    draw.text((bx0 + pad, by0 + 16), badge_txt, font=badge_f, fill=color)

    # ── Emoji centered in upper part of circle ────────────────────────
    emoji_y = cy - 340
    draw_emoji(img, b["emoji"], cx, emoji_y, 140)

    # ── Main headline (2 large lines) ────────────────────────────────
    f_head = fb(86)
    line_h = 100
    text_y = cy - 220

    for line in [b["line1"], b["line2"]]:
        centered_text(draw, line, f_head, cx, text_y, (255, 255, 255))
        text_y += line_h

    # ── What's included — 3 items ─────────────────────────────────────
    f_items = fr(38)
    item_y = text_y + 30
    for item in b["items"]:
        centered_text(draw, "•  " + item, f_items, cx, item_y, light)
        item_y += 56

    # ── Price / save badge (pill) ─────────────────────────────────────
    f_price = fb(44)
    price_txt = b["badge_bot"]
    pbb = draw.textbbox((0, 0), price_txt, font=f_price)
    pw = pbb[2] - pbb[0]
    pp = 50
    pill_w = pw + pp*2
    pill_h = 80
    pill_x0 = cx - pill_w//2
    pill_y0 = item_y + 40
    rounded_rect(draw, (pill_x0, pill_y0, pill_x0+pill_w, pill_y0+pill_h), 40, (255, 255, 255))
    draw.text((pill_x0 + pp, pill_y0 + 16), price_txt, font=f_price, fill=color)

    # ── Bottom feature strip ──────────────────────────────────────────
    strip_y = H - 150
    draw.rectangle([0, strip_y, W, H], fill=darken(color, 0.75))

    f_strip = fr(34)
    footer = "Instant Download  ·  Google Sheets & Excel  ·  Lifetime Access  ·  No Subscription"
    centered_text(draw, footer, f_strip, cx, strip_y + 56, (255, 255, 255))

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
    print(f"  NasriTools - Bundle Covers v3 (circle-style, brand-consistent)")
    print(f"{'='*65}\n")

    ok = 0
    for i, b in enumerate(BUNDLES, 1):
        lid = b["listing_id"]
        print(f"[{i}/5] {b['line1']} {b['line2']}")
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
