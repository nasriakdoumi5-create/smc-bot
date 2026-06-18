"""
NasriTools - Generate Bundle Images + Publish 5 Bundle Listings
Creates a promotional image for each bundle then publishes them on Etsy
Run: python publish_bundles.py
"""
import json, os, time, requests, hashlib
from pathlib import Path
from io import BytesIO
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

SIZE = 2000

BUNDLES = [
    {
        "key":      "finance_bundle",
        "listing":  4524283814,
        "name":     "Finance Bundle",
        "subtitle": "Budget Tracker + Invoice Tracker + Goals Planner",
        "count":    "3 Templates",
        "price":    "€17.99",
        "color":    (31, 107, 59),
        "light":    (220, 247, 233),
        "icon":     "💰",
    },
    {
        "key":      "health_bundle",
        "listing":  4524276503,
        "name":     "Health Bundle",
        "subtitle": "Workout Tracker + Meal Planner + Habit Tracker",
        "count":    "3 Templates",
        "price":    "€16.99",
        "color":    (192, 57, 43),
        "light":    (253, 228, 224),
        "icon":     "💪",
    },
    {
        "key":      "planner_bundle",
        "listing":  4524276527,
        "name":     "Planner Bundle",
        "subtitle": "Weekly Planner + Student Planner + Goals Planner",
        "count":    "3 Templates",
        "price":    "€16.99",
        "color":    (108, 52, 131),
        "light":    (237, 228, 252),
        "icon":     "📅",
    },
    {
        "key":      "business_bundle",
        "listing":  4524276553,
        "name":     "Business Bundle",
        "subtitle": "Content Creator + Invoice Tracker + Goals Planner",
        "count":    "3 Templates",
        "price":    "€21.99",
        "color":    (230, 126, 34),
        "light":    (254, 243, 224),
        "icon":     "💼",
    },
    {
        "key":      "ultimate_bundle",
        "listing":  4524283886,
        "name":     "Ultimate Bundle",
        "subtitle": "All 10 Google Sheets Templates",
        "count":    "10 Templates",
        "price":    "€39.99",
        "color":    (30, 100, 180),
        "light":    (220, 235, 252),
        "icon":     "⭐",
    },
]


def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0):
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
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
              "C:/Windows/Fonts/arialbd.ttf",
              "C:/Windows/Fonts/calibrib.ttf"]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def make_bundle_image(bundle):
    color = bundle["color"]
    light = bundle["light"]
    r, g, b = color

    img  = Image.new("RGB", (SIZE, SIZE), light)
    draw = ImageDraw.Draw(img)

    # Top banner
    draw.rectangle([0, 0, SIZE, 600], fill=color)

    # Decorative circles
    for cx, cy, rad in [(1750, 80, 300), (100, 500, 180), (1900, 580, 120)]:
        ov = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=(255, 255, 255, 18))
        img  = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        draw = ImageDraw.Draw(img)

    # SALE badge
    badge_x, badge_y, badge_r = SIZE - 200, 80, 110
    draw.ellipse([badge_x-badge_r, badge_y-badge_r, badge_x+badge_r, badge_y+badge_r],
                 fill=(255, 220, 0))
    draw.text((badge_x, badge_y - 18), "SAVE", font=load_font(36),
              fill=(80, 40, 0), anchor="mm")
    draw.text((badge_x, badge_y + 22), "50%+", font=load_font(46),
              fill=(180, 40, 0), anchor="mm")

    # Icon
    draw.text((SIZE // 2, 130), bundle["icon"], font=load_font(90),
              fill=(255, 255, 255), anchor="mm")

    # Title
    draw.text((SIZE // 2, 280), bundle["name"].upper(),
              font=load_font(90), fill=(255, 255, 255), anchor="mm")

    # Subtitle
    draw.text((SIZE // 2, 390), bundle["subtitle"],
              font=load_font(46), fill=(255, 255, 220), anchor="mm")

    # Divider
    draw.rectangle([SIZE // 2 - 200, 450, SIZE // 2 + 200, 456],
                   fill=(255, 255, 255))

    # Count pill
    pw, ph = 340, 80
    px = SIZE // 2 - pw // 2
    draw.rounded_rectangle([px, 480, px + pw, 480 + ph], radius=40,
                            fill=(255, 255, 255))
    draw.text((SIZE // 2, 520), bundle["count"],
              font=load_font(48), fill=color, anchor="mm")

    # Features block
    features = [
        "✔  Instant Digital Download",
        "✔  Works on Google Sheets & Excel",
        "✔  Fully Customizable — Edit Anything",
        "✔  Auto-Calculating Formulas Built In",
        "✔  Lifetime Access — Yours Forever",
        "✔  No Subscription, No App Needed",
    ]
    f_feat = load_font(46)
    fy = 670
    for feat in features:
        fw, fh = 1400, 90
        fx = (SIZE - fw) // 2
        draw.rounded_rectangle([fx, fy, fx + fw, fy + fh], radius=14,
                                fill=(255, 255, 255))
        draw.text((fx + 40, fy + fh // 2), feat, font=f_feat,
                  fill=(40, 40, 40), anchor="lm")
        fy += 106

    # Price block
    price_y = fy + 30
    draw.rounded_rectangle([SIZE // 2 - 220, price_y, SIZE // 2 + 220, price_y + 110],
                            radius=24, fill=color)
    draw.text((SIZE // 2, price_y + 35), "Bundle Price",
              font=load_font(36), fill=(255, 255, 220), anchor="mm")
    draw.text((SIZE // 2, price_y + 82), bundle["price"],
              font=load_font(56), fill=(255, 255, 255), anchor="mm")

    # Bottom strip
    strip_y = SIZE - 130
    draw.rectangle([0, strip_y, SIZE, SIZE], fill=color)
    draw.text((SIZE // 2, strip_y + 42),
              "Instant Download  •  Google Sheets  •  100% Customizable",
              font=load_font(38), fill=(255, 255, 255), anchor="mm")
    draw.text((SIZE // 2, strip_y + 92), "nasritools.etsy.com",
              font=load_font(32), fill=(255, 255, 200), anchor="mm")

    return img


def upload_image(token, listing_id, img):
    buf = BytesIO()
    img.save(buf, "JPEG", quality=94)
    buf.seek(0)
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images",
        headers=auth_headers(token),
        files={"image": ("bundle_cover.jpg", buf, "image/jpeg")},
        data={"rank": 1, "overwrite": "true"},
        timeout=60,
    )
    return r


def publish_listing(token, listing_id):
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"state": "active"},
        timeout=30,
    )
    return r


def main():
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Publish Bundle Listings")
    print(f"{'='*65}\n")

    ok = 0
    for bundle in BUNDLES:
        lid = bundle["listing"]
        print(f"  [{bundle['name']}]  listing {lid}")

        # Generate image
        print(f"    Generating cover image...", end=" ")
        img = make_bundle_image(bundle)
        print("✓")

        # Upload image
        print(f"    Uploading image...", end=" ")
        r = upload_image(token, lid, img)
        time.sleep(1.5)
        if r.ok:
            print("✓")
        else:
            print(f"✗  {r.status_code}: {r.text[:100]}")
            continue

        # Publish
        print(f"    Publishing...", end=" ")
        rp = publish_listing(token, lid)
        time.sleep(1)
        if rp.ok:
            ok += 1
            print(f"✓  LIVE → https://www.etsy.com/listing/{lid}")
        else:
            print(f"✗  {rp.status_code}: {rp.text[:100]}")

        print()

    print(f"{'='*65}")
    print(f"  Done: {ok}/{len(BUNDLES)} bundles published")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
