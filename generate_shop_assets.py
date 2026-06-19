"""
NasriTools - Generate Shop Branding Assets
Creates: Logo (500x500), Banner (3360x840), and uploads both to Etsy shop.
Also updates shop About section.
Run: python generate_shop_assets.py
"""
import json, os, time, requests, io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

# Brand colors
BRAND_COLOR  = (30, 100, 180)   # Primary blue
BRAND_LIGHT  = (220, 235, 252)
BRAND_ACCENT = (255, 180, 0)    # Gold accent
WHITE        = (255, 255, 255)
DARK         = (20, 30, 45)


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
            "x-api-key": CLIENT_ID}


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


# ── Logo (500x500, circular safe zone) ───────────────────────────────────────

def make_logo() -> Image.Image:
    S = 500
    img  = Image.new("RGB", (S, S), BRAND_COLOR)
    draw = ImageDraw.Draw(img)

    # Large circle background fill
    r1 = S // 2
    draw.ellipse([0, 0, S, S], fill=BRAND_COLOR)

    # Inner lighter circle ring
    r2 = 220
    cx, cy = S // 2, S // 2
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(40, 120, 200))

    # Grid icon (3×2 spreadsheet cells) — centred in top half
    gx, gy = cx - 75, cy - 105
    cw, ch = 50, 34
    gap    = 4
    cell_colors = [BRAND_ACCENT, WHITE, WHITE, WHITE, WHITE, WHITE]
    for i in range(2):
        for j in range(3):
            idx  = i * 3 + j
            bx   = gx + j * (cw + gap)
            by   = gy + i * (ch + gap)
            fill = cell_colors[idx]
            draw.rounded_rectangle([bx, by, bx + cw, by + ch], radius=5, fill=fill)

    # "N" letter below grid
    draw.text((cx, cy + 50), "N", font=load_font(110), fill=WHITE, anchor="mm")

    # "Tools" small text
    draw.text((cx, cy + 130), "Tools", font=load_font(44), fill=BRAND_ACCENT, anchor="mm")

    return img


# ── Banner (3360x840) ─────────────────────────────────────────────────────────

def make_banner() -> Image.Image:
    W, H = 3360, 840
    img  = Image.new("RGB", (W, H), BRAND_COLOR)
    draw = ImageDraw.Draw(img)

    # Gradient-like right panel (lighter)
    r, g, b = BRAND_COLOR
    panel_col = (min(r + 20, 255), min(g + 20, 255), min(b + 20, 255))
    draw.rectangle([W // 2, 0, W, H], fill=panel_col)

    # Decorative circles (background)
    for cx2, cy2, rad, alpha in [
        (200, 100, 300, 18),
        (3200, 700, 250, 15),
        (1680, 420, 500, 10),
    ]:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.ellipse([cx2-rad, cy2-rad, cx2+rad, cy2+rad], fill=(255, 255, 255, alpha))
        img  = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Left half: brand name + tagline
    lx = 280

    # Shop name
    draw.text((lx, 180), "Nasri", font=load_font(220), fill=WHITE)
    draw.text((lx + 490, 215), "Tools", font=load_font(160), fill=BRAND_ACCENT)

    # Tagline
    draw.text((lx, 440),
              "Premium Google Sheets Templates", font=load_font(68), fill=WHITE)
    draw.text((lx, 530),
              "Budget • Habits • Business • Planning", font=load_font_reg(54), fill=(200, 225, 255))

    # Stat pills
    stats = [
        ("100+",   "Templates"),
        ("⭐ 5.0",  "Rating"),
        ("24h",    "Support"),
    ]
    px = lx
    py = 660
    for val, label in stats:
        pw = 280
        draw.rounded_rectangle([px, py, px + pw, py + 90], radius=24, fill=(255, 255, 255, 0))
        draw.rounded_rectangle([px, py, px + pw, py + 90], radius=24, outline=WHITE, width=2)
        draw.text((px + pw // 2, py + 30), val,   font=load_font(36),     fill=WHITE, anchor="mm")
        draw.text((px + pw // 2, py + 64), label, font=load_font_reg(28), fill=(200, 225, 255), anchor="mm")
        px += pw + 24

    # Right half: mini product showcase grid
    items = [
        ("💰", "Budget"),
        ("✅", "Habits"),
        ("💪", "Workout"),
        ("🎯", "Goals"),
        ("📅", "Planner"),
        ("🎓", "Student"),
    ]
    rx    = W // 2 + 160
    ry    = 100
    iw, ih = 360, 200
    igap  = 24
    item_colors = [
        (31,  107,  59),
        (192,  57,  43),
        (192,  57,  43),
        (30,  100, 180),
        (108,  52, 131),
        (108,  52, 131),
    ]
    for idx, (emoji, label) in enumerate(items):
        row = idx // 3
        col = idx % 3
        ix  = rx + col * (iw + igap)
        iy  = ry + row * (ih + igap)
        ic  = item_colors[idx]

        draw.rounded_rectangle([ix, iy, ix + iw, iy + ih], radius=20, fill=ic)
        draw.text((ix + iw // 2, iy + 65), emoji, font=load_font(60), fill=WHITE, anchor="mm")
        draw.text((ix + iw // 2, iy + 140), label, font=load_font(38), fill=WHITE, anchor="mm")

    return img


# ── Upload helpers ────────────────────────────────────────────────────────────

def img_to_bytes(img, fmt="JPEG", quality=92):
    buf = io.BytesIO()
    img.save(buf, fmt, quality=quality)
    buf.seek(0)
    return buf


def upload_logo(token, img):
    buf = img_to_bytes(img)
    r = requests.put(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/logo",
        headers=auth_headers(token),
        files={"image": ("logo.jpg", buf, "image/jpeg")},
        timeout=60,
    )
    return r


def upload_banner(token, img):
    buf = img_to_bytes(img)
    r = requests.put(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/banner",
        headers=auth_headers(token),
        files={"image": ("banner.jpg", buf, "image/jpeg")},
        data={"banner_type": "big_banner"},
        timeout=60,
    )
    return r


def update_about(token):
    about_text = (
        "Welcome to NasriTools — your go-to store for premium Google Sheets templates!\n\n"
        "We design beautiful, easy-to-use spreadsheet templates that help you stay organized, "
        "save money, and reach your goals — without the complexity.\n\n"
        "All templates work on Google Sheets (free!) and Microsoft Excel. "
        "No subscriptions, no apps to install — just download, make a copy, and start using.\n\n"
        "🔥 Popular templates:\n"
        "• Budget Tracker — track income, expenses & savings\n"
        "• Habit Tracker — build 30 daily habits with streaks\n"
        "• Workout Tracker — log every gym session\n"
        "• Goals Planner — annual goals & 90-day action plans\n"
        "• Content Creator Planner — plan posts across all platforms\n\n"
        "💡 Questions? Message us on Etsy — we reply within 24 hours.\n"
        "⭐ Loved your template? Please leave a review — it means the world to us!"
    )
    r = requests.put(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"story": about_text},
        timeout=30,
    )
    return r


# ── Save locally ──────────────────────────────────────────────────────────────

def save_locally(logo, banner):
    out = Path(os.path.expanduser("~")) / "nasri_assets"
    out.mkdir(exist_ok=True)
    logo.save(out / "nasritools_logo_500x500.jpg", "JPEG", quality=95)
    banner.save(out / "nasritools_banner_3360x840.jpg", "JPEG", quality=95)
    print(f"    Local copies saved to: {out}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    token = get_token()

    print(f"\n{'='*60}")
    print(f"  NasriTools - Shop Branding Assets")
    print(f"{'='*60}\n")

    # Logo
    print("  [1/3] Generating logo (500×500)…", end=" ")
    logo = make_logo()
    print("✓  →  Uploading…", end=" ")
    r = upload_logo(token, logo)
    if r.ok:
        print("✓")
    else:
        print(f"✗  {r.status_code}: {r.text[:150]}")
    time.sleep(2)

    # Banner
    token = get_token()
    print("  [2/3] Generating banner (3360×840)…", end=" ")
    banner = make_banner()
    print("✓  →  Uploading…", end=" ")
    r = upload_banner(token, banner)
    if r.ok:
        print("✓")
    else:
        print(f"✗  {r.status_code}: {r.text[:150]}")
    time.sleep(2)

    # About section
    token = get_token()
    print("  [3/3] Updating About section…", end=" ")
    r = update_about(token)
    if r.ok:
        print("✓")
    else:
        print(f"✗  {r.status_code}: {r.text[:150]}")

    # Save locally regardless
    save_locally(logo, banner)

    print(f"\n{'='*60}")
    print(f"  Shop assets complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
