"""
NasriTools - Complete All Setup Steps
Runs 5 steps in sequence:
  1. Update shop announcement & sale message
  2. Generate logo (500x500 JPEG)
  3. Generate banner (3360x840 JPEG)
  4. Upload logo to Etsy
  5. SEO update for remaining ~90 products

Run: python complete_all.py
"""
import json
import os
import time
import requests
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://api.etsy.com/v3/application"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"
DATA_FILE  = Path(os.path.expanduser("~")) / "smc-bot" / "nasritools" / "listings_data.json"
IMG_DIR    = Path(os.path.expanduser("~")) / "nasri_hero_images"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_complete_all.json"
SEO_DONE_FILE = Path(os.path.expanduser("~")) / "etsy_seo_improved.json"

# ── Auth helpers ───────────────────────────────────────────────────────────────
def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0):
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type":    "refresh_token",
            "client_id":     CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
        print("  Token refreshed.")
    return t


def etsy_auth(t):
    return {
        "Authorization": "Bearer " + t["access_token"],
        "x-api-key":     CLIENT_ID + ":" + SECRET,
        "Content-Type":  "application/json",
    }


# ── Step 1: Update shop text ───────────────────────────────────────────────────
def step1_update_shop_text(token):
    print("\n[STEP 1/5] Updating shop announcement...")
    payload = {
        "announcement": (
            "🌟 Welcome to NasriTools — 100+ Professional Google Sheets & Excel Templates!\n\n"
            "✅ Auto-calculating dashboards — no formulas to set up\n"
            "✅ Fill yellow cells only — ready in minutes\n"
            "✅ Works in Google Sheets & Excel\n"
            "✅ One-time purchase — yours forever, no subscriptions\n"
            "✅ Instant download after purchase\n\n"
            "📦 100+ templates across 10 categories:\n"
            "Budgeting • Business • Investing • Health • Productivity\n"
            "E-Commerce • Content Creation • Home & Lifestyle • Education • Specialty\n\n"
            "💬 Questions? Message us — we respond within 24 hours.\n"
            "⭐ Love your template? Leave a review — it helps our small shop grow!"
        ),
        "sale_message": (
            "🎉 Thank you for your purchase from NasriTools!\n\n"
            "Your template is ready to download immediately.\n\n"
            "HOW TO USE:\n"
            "1. Download your .xlsx file from your Etsy account (Purchases & Reviews)\n"
            "2. Open in Google Sheets: File → Import → Upload the file\n"
            "   OR open directly in Microsoft Excel\n"
            "3. Fill the YELLOW cells with your data\n"
            "4. The dashboard updates automatically!\n\n"
            "💡 PRO TIP: Make a copy of the file before editing to keep a clean backup.\n\n"
            "Need help? Message us anytime — we respond within 24 hours.\n\n"
            "⭐ Enjoying your template? Please leave a 5-star review — it takes 30 seconds "
            "and helps our small shop grow!\n\n"
            "Thank you,\n"
            "Nasri — NasriTools"
        ),
    }
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}",
        headers=etsy_auth(token),
        json=payload,
        timeout=30,
    )
    if r.ok:
        print("  Shop announcement + sale message: OK")
    else:
        print(f"  ERROR: {r.status_code} — {r.text[:200]}")
    return r.ok


# ── Step 2: Generate logo ──────────────────────────────────────────────────────
def step2_generate_logo():
    print("\n[STEP 2/5] Generating logo (500x500)...")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  ERROR: Pillow not installed. Run: pip install Pillow")
        return None

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    logo_path = IMG_DIR / "nasritools_logo.jpg"

    W, H = 500, 500
    img  = Image.new("RGB", (W, H), color=(30, 58, 95))   # #1E3A5F
    draw = ImageDraw.Draw(img)

    # Subtle grid lines
    grid_color = (26, 51, 88)  # #1a3358
    for x in range(0, W, 50):
        draw.line([(x, 0), (x, H)], fill=grid_color, width=1)
    for y in range(0, H, 50):
        draw.line([(0, y), (W, y)], fill=grid_color, width=1)

    # Top + bottom gold strips
    gold = (255, 215, 0)
    draw.rectangle([(0, 0), (W, 8)],   fill=gold)
    draw.rectangle([(0, 480), (W, H)], fill=gold)

    # Load fonts (Windows paths first, fallback)
    def load_font(bold=True, size=50):
        win_bold  = ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"]
        win_reg   = ["C:/Windows/Fonts/arial.ttf",   "C:/Windows/Fonts/calibri.ttf"]
        paths = win_bold if bold else win_reg
        for p in paths:
            try:
                return ImageFont.truetype(p, size)
            except (IOError, OSError):
                pass
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()

    # Large "N"
    font_N     = load_font(bold=True,  size=220)
    font_nasri = load_font(bold=True,  size=52)
    font_tools = load_font(bold=True,  size=52)

    # Center "N" at (250, 200)
    bbox = draw.textbbox((0, 0), "N", font=font_N)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((250 - tw // 2, 200 - th // 2), "N", fill=(255, 255, 255), font=font_N)

    # "NASRI"
    bbox = draw.textbbox((0, 0), "NASRI", font=font_nasri)
    tw = bbox[2] - bbox[0]
    draw.text((250 - tw // 2, 355), "NASRI", fill=(255, 255, 255), font=font_nasri)

    # "TOOLS" in gold
    bbox = draw.textbbox((0, 0), "TOOLS", font=font_tools)
    tw = bbox[2] - bbox[0]
    draw.text((250 - tw // 2, 415), "TOOLS", fill=gold, font=font_tools)

    img.save(str(logo_path), "JPEG", quality=95)
    print(f"  Logo saved to: {logo_path}")
    return logo_path


# ── Step 3: Generate banner ────────────────────────────────────────────────────
def step3_generate_banner():
    print("\n[STEP 3/5] Generating banner (3360x840)...")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  ERROR: Pillow not installed. Run: pip install Pillow")
        return None

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    banner_path = IMG_DIR / "nasritools_banner.jpg"

    W, H   = 3360, 840
    NAVY   = (30,  58,  95)
    D_NAVY = (22,  45,  79)   # slightly darker #162D4F
    GOLD   = (255, 215,  0)
    WHITE  = (255, 255, 255)
    BLUE   = (80,  120, 180)
    PANEL_RIGHT_BG = (13, 30, 53)   # #0D1E35

    img  = Image.new("RGB", (W, H), color=NAVY)
    draw = ImageDraw.Draw(img)

    # Left dark panel
    draw.rectangle([(0, 0), (1400, H)], fill=D_NAVY)

    # Vertical texture lines (every 80px across whole image)
    tex_color = (26, 53, 88)   # #1a3558
    for x in range(0, W, 80):
        draw.line([(x, 0), (x, H)], fill=tex_color, width=1)

    # Gold bottom strip
    draw.rectangle([(0, 828), (W, H)], fill=GOLD)

    # ---- Font loader ----
    def load_font(bold=True, size=40):
        win_bold = ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"]
        win_reg  = ["C:/Windows/Fonts/arial.ttf",   "C:/Windows/Fonts/calibri.ttf"]
        paths = win_bold if bold else win_reg
        for p in paths:
            try:
                return ImageFont.truetype(p, size)
            except (IOError, OSError):
                pass
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()

    # ---- Left side text ----
    x0 = 80

    # y=120: "100+ Professional Templates"
    f85 = load_font(bold=True, size=85)
    draw.text((x0, 120), "100+ Professional Templates", fill=WHITE, font=f85)

    # y=230: "Google Sheets  &  Excel"
    f65 = load_font(bold=True, size=65)
    draw.text((x0, 230), "Google Sheets  &  Excel", fill=GOLD, font=f65)

    # y=320: separator line
    f30 = load_font(bold=False, size=30)
    draw.text((x0, 320), "━━━━━━━━━━━━━━━━━━━━━━━", fill=BLUE, font=f30)

    # y=380-560: checkmark features
    f42 = load_font(bold=False, size=42)
    features = [
        (380, "✓  Auto-calculating dashboards"),
        (440, "✓  Fill yellow cells only"),
        (500, "✓  Works in Google Sheets & Excel"),
        (560, "✓  One-time purchase — yours forever"),
    ]
    for fy, text in features:
        draw.text((x0, fy), text, fill=WHITE, font=f42)

    # y=640: URL in gold
    f38 = load_font(bold=False, size=38)
    draw.text((x0, 640), "nasritools.etsy.com", fill=GOLD, font=f38)

    # ---- Right panel box ----
    BOX_L, BOX_T, BOX_R, BOX_B = 1480, 80, 3280, 760
    box_w = BOX_R - BOX_L   # 1800
    box_cx = (BOX_L + BOX_R) // 2

    # Rounded rectangle (Pillow >= 8.2 supports radius)
    try:
        draw.rounded_rectangle(
            [(BOX_L, BOX_T), (BOX_R, BOX_B)],
            radius=20,
            fill=PANEL_RIGHT_BG,
            outline=GOLD,
            width=3,
        )
    except TypeError:
        # Fallback for older Pillow without rounded_rectangle
        draw.rectangle([(BOX_L, BOX_T), (BOX_R, BOX_B)], fill=PANEL_RIGHT_BG, outline=GOLD, width=3)

    # "SHOP NOW"
    f72 = load_font(bold=True, size=72)
    bb = draw.textbbox((0, 0), "SHOP NOW", font=f72)
    tw = bb[2] - bb[0]
    draw.text((box_cx - tw // 2, 130), "SHOP NOW", fill=GOLD, font=f72)

    # Separator
    f25 = load_font(bold=False, size=25)
    sep = "━━━━━━━━━━━━━━━━"
    bb = draw.textbbox((0, 0), sep, font=f25)
    tw = bb[2] - bb[0]
    draw.text((box_cx - tw // 2, 220), sep, fill=BLUE, font=f25)

    # Category pills
    CATEGORIES = [
        "Budget & Finance", "Business", "Investing", "Health", "Productivity",
        "E-Commerce", "Content Creator", "Home & Lifestyle", "Education", "Specialty",
    ]
    CAT_COLORS = {
        "Budget & Finance":  (41,  128, 185),
        "Business":          (39,  174,  96),
        "Investing":         (22,  160, 133),
        "Health":            (231,  76,  60),
        "Productivity":      (155,  89, 182),
        "E-Commerce":        (230, 126,  34),
        "Content Creator":   (52,  152, 219),
        "Home & Lifestyle":  (200, 160,  40),
        "Education":         (192,  57,  43),
        "Specialty":         (26,  188, 156),
    }
    f28 = load_font(bold=True, size=28)
    PILL_H   = 52
    PILL_PAD = 18   # horizontal padding each side
    PILL_GAP = 20
    rows = [CATEGORIES[:5], CATEGORIES[5:]]
    row_ys = [270, 380]

    for row_i, (row, ry) in enumerate(zip(rows, row_ys)):
        # Compute total row width to center it
        pill_widths = []
        for cat in row:
            bb = draw.textbbox((0, 0), cat, font=f28)
            tw = bb[2] - bb[0]
            pill_widths.append(tw + PILL_PAD * 2)
        total_w = sum(pill_widths) + PILL_GAP * (len(row) - 1)
        sx = box_cx - total_w // 2

        for cat, pw in zip(row, pill_widths):
            color = CAT_COLORS.get(cat, (80, 80, 80))
            try:
                draw.rounded_rectangle(
                    [(sx, ry), (sx + pw, ry + PILL_H)],
                    radius=14,
                    fill=color,
                )
            except TypeError:
                draw.rectangle([(sx, ry), (sx + pw, ry + PILL_H)], fill=color)

            bb = draw.textbbox((0, 0), cat, font=f28)
            tw_c = bb[2] - bb[0]
            th_c = bb[3] - bb[1]
            tx = sx + (pw - tw_c) // 2
            ty = ry + (PILL_H - th_c) // 2
            draw.text((tx, ty), cat, fill=WHITE, font=f28)
            sx += pw + PILL_GAP

    # Bottom of box: tagline
    f30 = load_font(bold=False, size=30)
    tagline = "Instant Download  •  No Subscription  •  Use Forever"
    bb = draw.textbbox((0, 0), tagline, font=f30)
    tw = bb[2] - bb[0]
    draw.text((box_cx - tw // 2, 660), tagline, fill=(170, 170, 200), font=f30)

    img.save(str(banner_path), "JPEG", quality=95)
    print(f"  Banner saved to: {banner_path}")
    print("  → Upload manually: Etsy → Shop Manager → Edit Shop → Cover photo")
    return banner_path


# ── Step 4: Upload logo to Etsy ────────────────────────────────────────────────
def step4_upload_logo(token, logo_path):
    print("\n[STEP 4/5] Uploading logo to Etsy...")
    if logo_path is None or not Path(logo_path).exists():
        print("  SKIP: logo file not found.")
        return

    logo_bytes = Path(logo_path).read_bytes()
    # Strip Content-Type so requests sets multipart boundary automatically
    headers = {
        "Authorization": "Bearer " + token["access_token"],
        "x-api-key":     CLIENT_ID + ":" + SECRET,
    }
    r = requests.put(
        f"{API}/shops/{SHOP_ID}/icon",
        headers=headers,
        files={"icon": ("nasritools_logo.jpg", logo_bytes, "image/jpeg")},
        timeout=60,
    )
    if r.status_code in (404, 405):
        print("  Logo upload not supported via API — upload manually from Etsy dashboard")
    elif r.ok:
        print("  Logo uploaded: OK")
    else:
        print(f"  ERROR: {r.status_code} — {r.text[:200]}")
        print("  → Upload manually: Etsy → Shop Manager → Edit Shop → Shop icon")


# ── Step 5: SEO update for remaining products ──────────────────────────────────
def generate_seo(slug, title, category):
    name      = slug.replace("_", " ").title()
    cat_short = category.split(" & ")[0].split(" ")[0]

    base      = title.split("|")[0].strip()
    new_title = f"{base} | {name} Spreadsheet | {cat_short} Template | Google Sheets"
    if len(new_title) > 140:
        new_title = new_title[:137] + "..."

    name_lower = name.lower()
    words      = slug.split("_")

    tags = [
        name_lower,
        f"{name_lower} google sheets",
        f"{name_lower} template",
        f"{name_lower} spreadsheet",
        f"{words[0]} tracker",
        f"google sheets {words[0]}",
        category.lower()[:20],
        "digital download",
        "instant download",
        "google sheets template",
        "spreadsheet template",
        f"{words[0]} planner",
        f"{cat_short.lower()} spreadsheet",
    ]

    seen       = set()
    clean_tags = []
    for t in tags:
        t = t[:20].strip()
        if t and t not in seen:
            seen.add(t)
            clean_tags.append(t)

    return new_title, clean_tags[:13]


def step5_seo_remaining(token, done):
    print("\n[STEP 5/5] Updating SEO for remaining products...")

    if not DATA_FILE.exists():
        print(f"  ERROR: DATA_FILE not found: {DATA_FILE}")
        return

    data      = json.loads(DATA_FILE.read_text())
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}

    # Already-done slugs from the initial top-10 SEO run
    seo_done_slugs = set()
    if SEO_DONE_FILE.exists():
        seo_done_slugs = set(json.loads(SEO_DONE_FILE.read_text()).keys())

    # Already done in this run
    already_done = set(done.get("seo", {}).keys())

    # Build slug → (title, category) map
    slug_map = {}
    for item in data:
        slug_map[item["slug"]] = {
            "title":    item.get("title", ""),
            "category": item.get("category", "General"),
        }

    # Filter: skip already done, skip top-10 SEO slugs
    to_update = []
    for item in data:
        slug = item["slug"]
        if slug in already_done:
            continue
        if slug in seo_done_slugs:
            continue
        lid = published.get(slug)
        if not lid:
            continue
        to_update.append(item)

    total = len(to_update)
    print(f"  Remaining to update: {total}")

    if "seo" not in done:
        done["seo"] = {}

    ok = 0
    for i, item in enumerate(to_update, 1):
        slug     = item["slug"]
        title    = item.get("title", "")
        category = item.get("category", "General")
        lid      = published.get(slug)

        if i % 20 == 0:
            token = get_token()

        new_title, tags = generate_seo(slug, title, category)

        r = requests.patch(
            f"{API}/shops/{SHOP_ID}/listings/{lid}",
            headers=etsy_auth(token),
            json={"title": new_title, "tags": tags},
            timeout=30,
        )
        time.sleep(0.6)

        if r.ok:
            ok += 1
            done["seo"][slug] = lid
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"  [{i:02d}/{total}] {slug} → updated: OK")
        else:
            print(f"  [{i:02d}/{total}] {slug} → ERROR: {r.text[:100]}")

    print(f"\n  SEO done: {ok}/{total} updated")
    return done


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  NasriTools - Complete All Setup Steps")
    print("=" * 60)

    done = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}

    token = get_token()

    # Step 1: Update shop text
    try:
        step1_update_shop_text(token)
    except Exception as e:
        print(f"  [STEP 1 ERROR] {e}")

    # Step 2: Generate logo
    logo_path = None
    try:
        logo_path = step2_generate_logo()
    except Exception as e:
        print(f"  [STEP 2 ERROR] {e}")

    # Step 3: Generate banner
    try:
        step3_generate_banner()
    except Exception as e:
        print(f"  [STEP 3 ERROR] {e}")

    # Step 4: Upload logo
    try:
        token = get_token()
        step4_upload_logo(token, logo_path)
    except Exception as e:
        print(f"  [STEP 4 ERROR] {e}")

    # Step 5: SEO update remaining products
    try:
        token = get_token()
        done  = step5_seo_remaining(token, done)
    except Exception as e:
        print(f"  [STEP 5 ERROR] {e}")

    # Final summary
    seo_count = len(done.get("seo", {})) if done else 0
    print("\n" + "=" * 60)
    print("  NasriTools Setup — Complete!")
    print(f"  SEO updates saved: {seo_count}")
    print(f"  Logo:   {IMG_DIR / 'nasritools_logo.jpg'}")
    print(f"  Banner: {IMG_DIR / 'nasritools_banner.jpg'}")
    print("  → Banner must be uploaded manually via Etsy → Edit Shop → Cover photo")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
