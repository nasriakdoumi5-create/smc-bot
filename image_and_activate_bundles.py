"""
NasriTools - Generate images + activate 4 missing bundles.
Run: python image_and_activate_bundles.py
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
        "listing_id": 4524724720,
        "name": "Health Transformation System",
        "tagline": "Workout + Meals + Habits",
        "items": ["Gym & Workout Tracking System", "Weekly Meal Planning System", "30-Day Habit Building System"],
        "color": (39, 174, 96),
        "light": (212, 248, 232),
        "emoji": "💪",
        "price": "€17.99",
        "save": "Save 50%",
    },
    {
        "listing_id": 4524724758,
        "name": "Planning & Productivity System",
        "tagline": "Weekly + Student + Goals",
        "items": ["Weekly Productivity System", "Student Academic Success System", "Annual Goals & 90-Day Action System"],
        "color": (108, 52, 131),
        "light": (237, 228, 252),
        "emoji": "📅",
        "price": "€17.99",
        "save": "Save 50%",
    },
    {
        "listing_id": 4524724798,
        "name": "Creator Business System",
        "tagline": "Content + Invoices + Budget",
        "items": ["Content Creator Business System", "Freelancer Invoice & Client System", "Monthly Budget & Expense System"],
        "color": (230, 126, 34),
        "light": (254, 243, 224),
        "emoji": "🚀",
        "price": "€21.99",
        "save": "Save 50%",
    },
    {
        "listing_id": 4524724846,
        "name": "The Complete Life System",
        "tagline": "All 10 Google Sheets Templates",
        "items": ["Finance", "Health", "Business", "Planning", "+ 6 more"],
        "color": (41, 128, 185),
        "light": (214, 234, 248),
        "emoji": "⭐",
        "price": "€39.99",
        "save": "Save 65%",
    },
]

FONT_BOLD = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
FONT_REG = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]


def load_font(candidates, size):
    for p in candidates:
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


def generate_bundle_image(bundle):
    W, H = 2000, 2000
    img  = Image.new("RGB", (W, H), bundle["light"])
    draw = ImageDraw.Draw(img)

    # Dark header band
    r, g, b = bundle["color"]
    draw.rectangle([(0, 0), (W, 520)], fill=bundle["color"])

    # Subtle diagonal accent
    dark = (max(0, r - 40), max(0, g - 40), max(0, b - 40))
    draw.polygon([(W - 400, 0), (W, 0), (W, 520), (W - 200, 520)], fill=dark)

    # BUNDLE badge
    f_bold = load_font(FONT_BOLD, 52)
    f_reg  = load_font(FONT_REG, 44)
    f_lg   = load_font(FONT_BOLD, 88)
    f_xl   = load_font(FONT_BOLD, 68)
    f_sm   = load_font(FONT_REG, 38)
    f_tiny = load_font(FONT_REG, 32)

    draw.text((80, 55), "NASRITOOLS  BUNDLE", font=f_bold, fill=(255, 255, 255, 180))

    # Save badge
    bw, bh = 220, 80
    draw.rounded_rectangle([(W - bw - 60, 42), (W - 60, 42 + bh)],
                           radius=12, fill=(255, 255, 255))
    draw.text((W - bw - 60 + 20, 50), bundle["save"],
              font=load_font(FONT_BOLD, 38), fill=bundle["color"])

    # Emoji + name
    draw.text((80, 140), bundle["emoji"] + "  " + bundle["name"],
              font=f_lg, fill=(255, 255, 255))

    # Tagline
    draw.text((85, 270), bundle["tagline"], font=f_xl, fill=(255, 255, 255, 210))

    # Price
    draw.text((85, 395), bundle["price"] + "  •  Instant Download",
              font=f_reg, fill=(255, 255, 255, 200))

    # Divider
    draw.rectangle([(80, 560), (W - 80, 568)], fill=bundle["color"])

    # "WHAT'S INCLUDED" label
    draw.text((80, 600), "WHAT'S INCLUDED:", font=load_font(FONT_BOLD, 54), fill=bundle["color"])

    # Items list
    y = 695
    for item in bundle["items"]:
        # Bullet
        draw.ellipse([(80, y + 14), (110, y + 44)], fill=bundle["color"])
        draw.text((135, y), item, font=f_xl, fill=(30, 30, 30))
        y += 110

    # Bottom value bar
    draw.rectangle([(0, H - 240), (W, H)], fill=bundle["color"])
    draw.text((80, H - 185),
              "Works on Google Sheets (FREE) & Microsoft Excel",
              font=f_sm, fill=(255, 255, 255))
    draw.text((80, H - 130),
              "Instant download  •  Lifetime access  •  No subscription",
              font=f_sm, fill=(255, 255, 255, 200))
    draw.text((80, H - 72), "nasritools.etsy.com",
              font=f_tiny, fill=(255, 255, 255, 160))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    buf.seek(0)
    return buf


def upload_image(token, listing_id, img_buf):
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images",
        headers=auth_headers(token),
        files={"image": ("bundle_cover.jpg", img_buf, "image/jpeg")},
        data={"rank": 1, "overwrite": "true"},
        timeout=60,
    )
    return r.ok, r.status_code, r.text[:200]


def activate(token, listing_id):
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"state": "active"}, timeout=30,
    )
    return r.ok, r.status_code, r.text[:200]


def main():
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Image + Activate 4 Bundles")
    print(f"{'='*65}\n")

    ok = 0
    for i, bundle in enumerate(BUNDLES, 1):
        lid  = bundle["listing_id"]
        name = bundle["name"]
        print(f"[{i}/4] {name}  [{lid}]")

        print(f"  Generating image…", end=" ", flush=True)
        img_buf = generate_bundle_image(bundle)
        print("done")

        token = get_token()
        print(f"  Uploading image…", end=" ", flush=True)
        img_ok, img_code, img_txt = upload_image(token, lid, img_buf)
        print(f"{'✓' if img_ok else f'✗ {img_code}: {img_txt}'}")
        time.sleep(1.5)

        if not img_ok:
            continue

        token = get_token()
        print(f"  Activating…", end=" ", flush=True)
        act_ok, act_code, act_txt = activate(token, lid)
        print(f"{'✓' if act_ok else f'✗ {act_code}: {act_txt}'}")

        if act_ok:
            ok += 1
            print(f"  → https://www.etsy.com/listing/{lid}")
        print()
        time.sleep(1.5)
        token = get_token()

    print(f"{'='*65}")
    print(f"  Done: {ok}/4 bundles live")
    if ok < 4:
        print(f"\n  For any remaining drafts, open Etsy Shop Manager →")
        print(f"  Listings → Drafts → manually publish.")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
