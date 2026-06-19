"""
NasriTools - Generate "How to Use" Step Guide Images (rank 5)
3-step visual guide for all 10 main product listings.
Run: python generate_how_to_use.py
"""
import json, os, time, requests, io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_howto_done.json"
SIZE       = 2000

PRODUCTS = [
    {"listing": 4487745643, "name": "Budget Tracker",               "color": (31,  107,  59), "light": (220, 247, 233), "emoji": "💰"},
    {"listing": 4487740567, "name": "Habit Tracker",                "color": (192,  57,  43), "light": (253, 228, 224), "emoji": "✅"},
    {"listing": 4487742011, "name": "Meal Planner",                 "color": (39,  174, 141), "light": (209, 250, 229), "emoji": "🥗"},
    {"listing": 4487743321, "name": "Wedding Planner",              "color": (210,  82, 162), "light": (252, 228, 243), "emoji": "💍"},
    {"listing": 4487744011, "name": "Workout Tracker",              "color": (192,  57,  43), "light": (253, 228, 224), "emoji": "💪"},
    {"listing": 4487745211, "name": "Content Creator Planner",      "color": (230, 126,  34), "light": (254, 243, 224), "emoji": "📱"},
    {"listing": 4487744321, "name": "Freelancer Invoice Tracker",   "color": (52,  152, 219), "light": (214, 234, 248), "emoji": "📄"},
    {"listing": 4487742911, "name": "Student Planner",              "color": (108,  52, 131), "light": (237, 228, 252), "emoji": "🎓"},
    {"listing": 4487743721, "name": "Goals Planner",                "color": (30,  100, 180), "light": (220, 235, 252), "emoji": "🎯"},
    {"listing": 4487742511, "name": "Weekly Planner",               "color": (108,  52, 131), "light": (237, 228, 252), "emoji": "📅"},
]

STEPS = [
    {
        "num": "1",
        "title": "Purchase & Download",
        "desc": "After checkout, Etsy sends you\na download link instantly.",
        "icon": "🛒",
    },
    {
        "num": "2",
        "title": "Open in Google Sheets",
        "desc": "Click the file link, then choose\nFile → Make a Copy to your Drive.",
        "icon": "📋",
    },
    {
        "num": "3",
        "title": "Customize & Use",
        "desc": "Edit colors, add your data,\nand start tracking instantly!",
        "icon": "✏️",
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


def make_how_to_use(product):
    color = product["color"]
    light = product["light"]
    name  = product["name"]
    emoji = product["emoji"]
    r, g, b = color

    img  = Image.new("RGB", (SIZE, SIZE), light)
    draw = ImageDraw.Draw(img)

    # ── Header ────────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, SIZE, 500], fill=color)

    # Decorative circles
    for cx2, cy2, rad in [(1800, 100, 260), (80, 400, 160)]:
        ov = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.ellipse([cx2-rad, cy2-rad, cx2+rad, cy2+rad], fill=(255, 255, 255, 20))
        img  = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Emoji + name
    draw.text((SIZE // 2, 110), emoji, font=load_font(80), fill=(255, 255, 255), anchor="mm")
    draw.text((SIZE // 2, 240), name.upper(), font=load_font(88), fill=(255, 255, 255), anchor="mm")
    draw.text((SIZE // 2, 360), "HOW TO GET STARTED", font=load_font(52), fill=(255, 255, 200), anchor="mm")
    draw.rectangle([SIZE // 2 - 200, 415, SIZE // 2 + 200, 421], fill=(255, 255, 255))

    # ── 3 Steps ───────────────────────────────────────────────────────────────
    step_top  = 560
    step_h    = 380
    step_gap  = 40
    card_w    = SIZE - 160
    card_x    = 80

    for i, step in enumerate(STEPS):
        sy = step_top + i * (step_h + step_gap)

        # Card shadow
        draw.rounded_rectangle([card_x + 6, sy + 6, card_x + card_w + 6, sy + step_h + 6],
                                radius=28, fill=(180, 185, 195))
        # Card white background
        draw.rounded_rectangle([card_x, sy, card_x + card_w, sy + step_h],
                                radius=28, fill=(255, 255, 255))

        # Left accent
        draw.rounded_rectangle([card_x, sy, card_x + 14, sy + step_h],
                                radius=7, fill=color)

        # Number circle
        cx3 = card_x + 90
        cy3 = sy + step_h // 2
        draw.ellipse([cx3 - 55, cy3 - 55, cx3 + 55, cy3 + 55], fill=color)
        draw.text((cx3, cy3), step["num"], font=load_font(58), fill=(255, 255, 255), anchor="mm")

        # Step icon
        icon_x = card_x + 200
        draw.text((icon_x, sy + 60), step["icon"], font=load_font(70), fill=color, anchor="mm")

        # Step title
        title_x = card_x + 240
        draw.text((title_x, sy + 80), step["title"], font=load_font(58), fill=color)

        # Step description (multiline)
        desc_lines = step["desc"].split("\n")
        desc_y = sy + 165
        for line in desc_lines:
            draw.text((title_x, desc_y), line, font=load_font_reg(40), fill=(60, 60, 70))
            desc_y += 52

        # Right checkmark (for steps 1 & 2) or star (step 3)
        mark = "⭐" if i == 2 else "✓"
        check_x = card_x + card_w - 80
        draw.text((check_x, cy3), mark, font=load_font(60), fill=color, anchor="mm")

    # ── Bottom badge row ──────────────────────────────────────────────────────
    badge_y = step_top + 3 * (step_h + step_gap) + 20
    badges = [
        ("⚡", "Instant Download"),
        ("🔄", "Free to Edit"),
        ("♾️", "Lifetime Access"),
    ]
    bw = 380
    bx = (SIZE - 3 * bw - 2 * 60) // 2
    for icon2, label in badges:
        draw.rounded_rectangle([bx, badge_y, bx + bw, badge_y + 110],
                                radius=28, fill=color)
        draw.text((bx + bw // 2, badge_y + 32), icon2, font=load_font(36),
                  fill=(255, 255, 255), anchor="mm")
        draw.text((bx + bw // 2, badge_y + 76), label, font=load_font_reg(32),
                  fill=(255, 255, 220), anchor="mm")
        bx += bw + 60

    # ── Bottom strip ──────────────────────────────────────────────────────────
    draw.rectangle([0, SIZE - 110, SIZE, SIZE], fill=color)
    draw.text((SIZE // 2, SIZE - 65),
              "Questions? Message us on Etsy — we reply within 24h",
              font=load_font_reg(34), fill=(255, 255, 255), anchor="mm")

    return img


def upload_image(token, listing_id, img, rank=5):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=92)
    buf.seek(0)
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images",
        headers=auth_headers(token),
        files={"image": ("howto.jpg", buf, "image/jpeg")},
        data={"rank": rank, "overwrite": "true"},
        timeout=60,
    )
    return r


def main():
    done = {}
    if DONE_FILE.exists():
        done = json.loads(DONE_FILE.read_text())

    token = get_token()

    print(f"\n{'='*60}")
    print(f"  NasriTools - How To Use Images (rank 5)")
    print(f"{'='*60}\n")

    ok = 0
    for p in PRODUCTS:
        key = str(p["listing"])
        if done.get(key):
            print(f"  [{p['name']}] skipped (already done)")
            ok += 1
            continue

        print(f"  [{p['name']}] listing {p['listing']}", end=" ")
        img = make_how_to_use(p)
        r = upload_image(token, p["listing"], img, rank=5)
        time.sleep(1)
        if r.ok:
            print("✓")
            done[key] = True
            ok += 1
        else:
            print(f"✗  {r.status_code}: {r.text[:100]}")

        DONE_FILE.write_text(json.dumps(done, indent=2))
        token = get_token()

    print(f"\n{'='*60}")
    print(f"  Done: {ok}/{len(PRODUCTS)} how-to images uploaded")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
