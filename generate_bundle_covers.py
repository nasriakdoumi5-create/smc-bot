"""
NasriTools - Bundle Cover Images (v5-scenic)
Premium mountain gradient style — inspired by high-end travel/product design.
Run: python generate_bundle_covers.py
"""
import io, json, os, time, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

# ── Mountain silhouettes (normalized x,y coords — shared across bundles) ─────
PEAKS_BACK = [
    (0, 1), (0.05, 0.74), (0.14, 0.80), (0.22, 0.73), (0.31, 0.78),
    (0.42, 0.71), (0.52, 0.76), (0.62, 0.72), (0.71, 0.77),
    (0.82, 0.73), (0.91, 0.79), (1, 1),
]
PEAKS_MID = [
    (0, 1), (0.06, 0.80), (0.17, 0.86), (0.27, 0.79), (0.37, 0.84),
    (0.48, 0.78), (0.59, 0.83), (0.69, 0.79), (0.79, 0.84),
    (0.90, 0.80), (1, 1),
]
PEAKS_FRONT = [
    (0, 1), (0.10, 0.87), (0.22, 0.92), (0.34, 0.86), (0.45, 0.91),
    (0.56, 0.85), (0.67, 0.90), (0.78, 0.85), (0.89, 0.90),
    (1, 1),
]

# ── Bundle data ───────────────────────────────────────────────────────────────
BUNDLES = [
    {
        "listing_id": 4524283886,
        "sky_top":    (88, 145, 232),
        "sky_bot":    (28, 68, 168),
        "mtn_back":   (20, 48, 128),
        "mtn_mid":    (12, 32, 96),
        "mtn_front":  (6, 16, 62),
        "accent":     (145, 205, 255),
        "badge":      "3 SYSTEMS  ·  SAVE 33%",
        "line1":      "Total Financial Control.",
        "line2":      "Budget. Invoices. Goals.",
        "result":     "Know where every euro goes. Get paid on time. Achieve every goal.",
        "price":      "€19.99",
        "worth":      "worth €37",
        "items":      ["Budget & Expense System", "Invoice & Client System", "Goals & 90-Day System"],
    },
    {
        "listing_id": 4524724720,
        "sky_top":    (232, 112, 50),
        "sky_bot":    (172, 65, 18),
        "mtn_back":   (135, 50, 13),
        "mtn_mid":    (100, 35, 8),
        "mtn_front":  (65, 20, 4),
        "accent":     (255, 205, 128),
        "badge":      "3 SYSTEMS  ·  SAVE 50%",
        "line1":      "Transform Your Health.",
        "line2":      "Workout. Eat. Build Habits.",
        "result":     "Track every session. Plan every meal. Build 30 habits — automatically.",
        "price":      "€17.99",
        "worth":      "worth €36",
        "items":      ["Gym & Workout Tracking", "Weekly Meal Planning", "30-Day Habit Building"],
    },
    {
        "listing_id": 4524724758,
        "sky_top":    (152, 82, 228),
        "sky_bot":    (85, 28, 158),
        "mtn_back":   (62, 18, 120),
        "mtn_mid":    (42, 11, 88),
        "mtn_front":  (24, 5, 56),
        "accent":     (215, 168, 255),
        "badge":      "3 SYSTEMS  ·  SAVE 50%",
        "line1":      "Master Your Time.",
        "line2":      "Weekly. Academic. Goals.",
        "result":     "Plan your perfect week. Ace every semester. Achieve every goal.",
        "price":      "€17.99",
        "worth":      "worth €36",
        "items":      ["Weekly Productivity System", "Student Academic System", "Goals & 90-Day System"],
    },
    {
        "listing_id": 4524724798,
        "sky_top":    (218, 155, 32),
        "sky_bot":    (158, 102, 10),
        "mtn_back":   (122, 76, 7),
        "mtn_mid":    (90, 54, 4),
        "mtn_front":  (58, 33, 2),
        "accent":     (255, 222, 108),
        "badge":      "3 SYSTEMS  ·  SAVE 50%",
        "line1":      "Run Your Business.",
        "line2":      "Content. Invoices. Budget.",
        "result":     "Grow your audience. Get paid. Know your numbers — all in one system.",
        "price":      "€21.99",
        "worth":      "worth €43",
        "items":      ["Content Creator System", "Invoice & Client System", "Budget & Expense System"],
    },
    {
        "listing_id": 4524724846,
        "sky_top":    (28, 138, 102),
        "sky_bot":    (10, 82, 60),
        "mtn_back":   (7, 60, 44),
        "mtn_mid":    (4, 43, 31),
        "mtn_front":  (2, 26, 19),
        "accent":     (105, 235, 188),
        "badge":      "10 SYSTEMS  ·  SAVE 65%",
        "line1":      "Systems That Run",
        "line2":      "Your Entire Life.",
        "result":     "Finance. Health. Business. Planning. All 10 premium Google Sheets.",
        "price":      "€39.99",
        "worth":      "worth €120",
        "items":      ["Finance + Health + Business", "Planning + Student + Content", "Wedding + Goals + Weekly"],
    },
]

# ── Fonts ─────────────────────────────────────────────────────────────────────
_BOLD = [
    # Windows
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
    "C:/Windows/Fonts/verdanab.ttf",
    "C:/Windows/Fonts/trebucbd.ttf",
    # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
_REG = [
    # Windows
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/verdana.ttf",
    "C:/Windows/Fonts/trebuc.ttf",
    # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]

def _f(p, s):
    for path in p:
        if Path(path).exists():
            return ImageFont.truetype(path, s)
    return ImageFont.load_default()

def fb(s): return _f(_BOLD, s)
def fr(s): return _f(_REG, s)

# ── Helpers ───────────────────────────────────────────────────────────────────
def mix(c1, c2, t):
    return tuple(int(c1[i]*(1-t) + c2[i]*t) for i in range(3))

def tw(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]

def wrap(draw, text, font, max_w):
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

def pill(draw, x0, y0, x1, y1, fill, radius=None):
    r = radius if radius is not None else (y1 - y0) // 2
    r = min(r, (x1-x0)//2, (y1-y0)//2)
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx, cy in [(x0,y0), (x1-2*r,y0), (x0,y1-2*r), (x1-2*r,y1-2*r)]:
        draw.ellipse([cx, cy, cx+2*r, cy+2*r], fill=fill)

def txt(draw, x, y, text, font, fill, shadow=True):
    """Draw text with optional drop shadow for readability."""
    if shadow:
        draw.text((x+3, y+3), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=fill)

# ── Generator ─────────────────────────────────────────────────────────────────
def generate(b):
    W, H = 2000, 2000
    img  = Image.new("RGB", (W, H), b["sky_bot"])
    draw = ImageDraw.Draw(img)

    # 1. Sky gradient (top → bottom)
    for y in range(H):
        draw.line([(0, y), (W, y)], fill=mix(b["sky_top"], b["sky_bot"], y/(H-1)))

    # 2. Soft glow / sun (very subtle — just atmosphere, not bright)
    gx, gy = W // 2, 500
    sky_mid = mix(b["sky_top"], b["sky_bot"], gy / H)
    for step in range(10, 0, -1):
        r   = int(420 * step / 10)
        t   = (10 - step) / 9
        col = mix(sky_mid, mix(sky_mid, (255, 255, 255), 0.12), t)
        draw.ellipse([gx-r, gy-r, gx+r, gy+r], fill=col)

    # 2b. Dark scrim over top text area
    for y in range(0, 1500):
        t     = max(0, 1 - y / 1500)
        sky_c = mix(b["sky_top"], b["sky_bot"], y / (H - 1))
        draw.line([(0, y), (W, y)], fill=mix(sky_c, (0, 0, 0), 0.32 * t))

    # 3. Mountain silhouette layers
    for peaks_norm, color in [
        (PEAKS_BACK,  b["mtn_back"]),
        (PEAKS_MID,   b["mtn_mid"]),
        (PEAKS_FRONT, b["mtn_front"]),
    ]:
        pts = [(int(x*W), int(y*H)) for x, y in peaks_norm]
        draw.polygon(pts, fill=color)

    # 4. Darken bottom edge
    for y in range(H - 140, H):
        t = (y - (H - 140)) / 140
        draw.line([(0, y), (W, y)], fill=mix(b["mtn_front"], (0, 0, 0), t * 0.45))

    # ── TEXT ──────────────────────────────────────────────────────────────────

    # Brand + badge (top bar)
    txt(draw, 80, 60, "NASRITOOLS", fb(48), (255, 255, 255))
    btxt = b["badge"]
    bf   = fb(42)
    bw_  = tw(draw, btxt, bf)
    bx0  = W - bw_ - 128
    pill(draw, bx0, 46, W - 64, 118, (255, 255, 255), 24)
    draw.text((bx0 + 36, 58), btxt, font=bf, fill=b["sky_bot"])

    # Divider
    draw.rectangle([80, 134, W - 80, 139], fill=mix(b["sky_top"], (255, 255, 255), 0.55))

    # Headline 1 — very large white
    h1f = fb(130)
    draw.text((84, 158), b["line1"], font=h1f, fill=(0, 0, 0))
    draw.text((80, 154), b["line1"], font=h1f, fill=(255, 255, 255))

    # Headline 2 — accent, large
    h2f = fb(108)
    draw.text((84, 318), b["line2"], font=h2f, fill=(0, 0, 0))
    draw.text((80, 314), b["line2"], font=h2f, fill=b["accent"])

    # Result statement
    rf     = fr(52)
    rlines = wrap(draw, b["result"], rf, W - 160)
    ry     = 480
    for line in rlines[:2]:
        txt(draw, 80, ry, line, rf, (255, 255, 255))
        ry += 66

    # Price pill
    pf   = fb(64)
    ptxt = b["price"]
    pw_  = tw(draw, ptxt, pf)
    wf   = fr(44)
    wtxt = "  ·  " + b["worth"]
    ww_  = tw(draw, wtxt, wf)
    pill(draw, 80, ry + 28, 80 + pw_ + ww_ + 96, ry + 132, (255, 255, 255), 34)
    draw.text((122, ry + 42), ptxt, font=pf, fill=b["sky_bot"])
    draw.text((122 + pw_, ry + 56), wtxt, font=wf, fill=mix(b["sky_bot"], (60, 60, 60), 0.3))
    ry += 160

    # Included items (larger)
    fi = fr(50)
    for item in b["items"]:
        draw.ellipse([80, ry + 12, 112, ry + 44], fill=(255, 255, 255))
        txt(draw, 130, ry, item, fi, (255, 255, 255))
        ry += 76

    # Footer
    ft = "Instant Download  ·  Google Sheets & Excel  ·  Lifetime Access"
    txt(draw, 80, H - 110, ft, fr(34), (255, 255, 255), shadow=False)
    url = "nasritools.etsy.com"
    uf  = fr(32)
    draw.text((W - tw(draw, url, uf) - 80, H - 66), url, font=uf,
              fill=mix((255, 255, 255), b["mtn_front"], 0.28))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf


# ── Etsy API ──────────────────────────────────────────────────────────────────
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
    print(f"  NasriTools - Bundle Covers v5-scenic (mountain gradient)")
    print(f"{'='*65}\n")

    ok = 0
    for i, b in enumerate(BUNDLES, 1):
        lid = b["listing_id"]
        print(f"[{i}/5] {b['line1']}")
        print(f"  Generating...", end=" ", flush=True)
        try:
            buf = generate(b)
            print("done")
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        token = get_token()
        print(f"  Uploading to [{lid}]...", end=" ", flush=True)
        ok_, code, txt = upload_image(token, lid, buf)
        print(f"{'OK' if ok_ else f'FAIL {code}: {txt}'}")
        if ok_:
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
