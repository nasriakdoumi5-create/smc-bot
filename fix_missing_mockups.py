"""
NasriTools - Fix Missing Mockups (Download from Etsy + Create Mockup)
For every listing still missing a mockup:
  1. Downloads its primary image from Etsy
  2. Creates a laptop-frame mockup
  3. Uploads it as image #2
Run: python fix_missing_mockups.py
"""
import json, os, re, time, hashlib, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

CLIENT_ID   = "pluc0garrgcjzhim0hawxf0k"
SECRET      = "hc89hlqkd6"
SHOP_ID     = 66526082
TOKEN_FILE  = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE   = Path(os.path.expanduser("~")) / "etsy_all_mockups_done.json"
MOCKUPS_DIR = Path(os.path.expanduser("~")) / "nasri_mockups"
MOCKUPS_DIR.mkdir(exist_ok=True)

SIZE = 2000
PALETTES = [
    ((34, 139, 87),  (220, 247, 233)),
    ((108, 67, 176), (237, 228, 252)),
    ((214, 90, 49),  (252, 232, 224)),
    ((185, 50, 100), (252, 225, 237)),
    ((30, 100, 180), (220, 235, 252)),
    ((200, 60, 60),  (252, 225, 225)),
    ((20, 120, 140), (215, 242, 246)),
    ((50, 130, 70),  (220, 245, 225)),
    ((160, 100, 20), (252, 243, 218)),
    ((80, 80, 160),  (230, 230, 252)),
    ((120, 40, 120), (245, 220, 245)),
    ((40, 100, 140), (215, 235, 250)),
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


def fetch_all_listings(token):
    listings, offset, limit = [], 0, 100
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": limit, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(0.4)
    return listings


def get_listing_primary_image_url(token, listing_id):
    r = requests.get(
        f"https://api.etsy.com/v3/application/listings/{listing_id}/images",
        headers=auth_headers(token),
        timeout=15,
    )
    if r.ok:
        imgs = r.json().get("results", [])
        if imgs:
            imgs.sort(key=lambda x: x.get("rank", 99))
            return imgs[0].get("url_fullxfull") or imgs[0].get("url_570xN")
    return None


def download_image_to_pil(url):
    r = requests.get(url, timeout=30)
    if r.ok:
        return Image.open(BytesIO(r.content)).convert("RGB")
    return None


def load_font(size):
    for f in ["C:/Windows/Fonts/arialbd.ttf",
              "C:/Windows/Fonts/arial.ttf",
              "C:/Windows/Fonts/calibrib.ttf"]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def color_for_title(title):
    idx = int(hashlib.md5(title.encode()).hexdigest()[:4], 16) % len(PALETTES)
    return PALETTES[idx][0]


def clean_label(title):
    label = title.split("|")[0].strip()
    for s in ["Google Sheets Template", "Google Sheets", "Spreadsheet Template",
              "Spreadsheet", "Template"]:
        label = label.replace(s, "").strip()
    return label[:50]


def draw_laptop(draw, img, screen_img, cx, cy, lw, lh, color):
    r, g, b = color
    body_h = int(lh * 0.07)
    body_y = cy + lh // 2
    bx0 = cx - int(lw * 0.55); bx1 = cx + int(lw * 0.55)
    draw.rounded_rectangle([bx0, body_y, bx1, body_y + body_h], radius=8, fill=(180, 180, 185))
    draw.rectangle([bx0 + 20, body_y, bx1 - 20, body_y + 4], fill=(210, 210, 215))
    lx0 = cx - lw // 2; lx1 = cx + lw // 2
    ly0 = cy - lh // 2; ly1 = cy + lh // 2
    draw.rounded_rectangle([lx0, ly0, lx1, ly1], radius=18, fill=(195, 195, 200))
    pad = 10
    draw.rounded_rectangle([lx0 + pad, ly0 + pad, lx1 - pad, ly1 - pad], radius=12, fill=(30, 30, 35))
    sp = 22
    sx0 = lx0 + sp; sy0 = ly0 + sp; sx1 = lx1 - sp; sy1 = ly1 - sp
    sw = sx1 - sx0; sh = sy1 - sy0
    screen_resized = screen_img.resize((sw, sh), Image.LANCZOS)
    img.paste(screen_resized, (sx0, sy0))
    glare = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glare)
    for i in range(60):
        alpha = max(0, 30 - i)
        gd.line([(0, i), (i, 0)], fill=(255, 255, 255, alpha), width=1)
    img.paste(glare, (sx0, sy0), glare)
    draw.rounded_rectangle([sx0 - 2, sy0 - 2, sx1 + 2, sy1 + 2], radius=4,
                            outline=(r, g, b, 180), width=3)
    draw.ellipse([cx - 4, ly0 + 14 - 4, cx + 4, ly0 + 14 + 4], fill=(50, 50, 55))


def create_mockup(screen_img, title):
    color = color_for_title(title)
    label = clean_label(title)
    r, g, b = color
    img = Image.new("RGB", (SIZE, SIZE), (250, 250, 252))
    draw = ImageDraw.Draw(img)
    for y in range(SIZE):
        t = y / SIZE
        cr = int(240 + (r / 255 * 25) * t)
        cg = int(240 + (g / 255 * 25) * t)
        cb = int(240 + (b / 255 * 25) * t)
        draw.line([(0, y), (SIZE, y)], fill=(min(cr, 255), min(cg, 255), min(cb, 255)))
    for cx2, cy2, rad, alpha in [(200, 200, 300, 15), (1800, 300, 250, 12),
                                   (1850, 1800, 350, 10), (150, 1700, 280, 12)]:
        circle = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        cd = ImageDraw.Draw(circle)
        cd.ellipse([cx2 - rad, cy2 - rad, cx2 + rad, cy2 + rad], fill=(r, g, b, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), circle).convert("RGB")
        draw = ImageDraw.Draw(img)
    draw_laptop(draw, img, screen_img, SIZE // 2, SIZE // 2 - 60, 1180, 760, color)
    f_label = load_font(50)
    draw.text((SIZE // 2, 90), label, font=f_label, fill=(50, 50, 50), anchor="mm")
    draw.rectangle([SIZE // 2 - 200, 118, SIZE // 2 + 200, 122], fill=(r, g, b))
    features = ["Instant Download", "Works on Any Device", "100% Customizable"]
    pill_y = SIZE - 200; pill_w = 380; gap = 30
    total_w = len(features) * pill_w + (len(features) - 1) * gap
    start_x = (SIZE - total_w) // 2
    f_feat = load_font(32)
    for i, feat in enumerate(features):
        px = start_x + i * (pill_w + gap)
        draw.rounded_rectangle([px, pill_y, px + pill_w, pill_y + 64], radius=32, fill=(r, g, b))
        draw.text((px + pill_w // 2, pill_y + 32), feat, font=f_feat,
                  fill=(255, 255, 255), anchor="mm")
    f_brand = load_font(36)
    draw.text((SIZE // 2, SIZE - 80), "nasritools.etsy.com",
              font=f_brand, fill=(130, 130, 130), anchor="mm")
    return img


def upload_image(token, listing_id, img):
    buf = BytesIO()
    img.save(buf, "JPEG", quality=93)
    buf.seek(0)
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images",
        headers=auth_headers(token),
        files={"image": ("mockup.jpg", buf, "image/jpeg")},
        data={"rank": 2, "overwrite": "true"},
        timeout=60,
    )
    return r


def main():
    done  = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Fix Missing Mockups (download + create + upload)")
    print(f"  Already done: {len(done)}")
    print(f"{'='*65}\n")

    print("  Fetching all active listings...")
    listings = fetch_all_listings(token)
    total    = len(listings)
    print(f"  Found {total} listings\n")

    pending = [l for l in listings if str(l["listing_id"]) not in done]
    print(f"  Pending (no mockup yet): {len(pending)}\n")

    ok = 0
    for i, listing in enumerate(pending, 1):
        lid   = str(listing["listing_id"])
        title = listing.get("title", "")
        print(f"[{i:03d}/{len(pending)}] {title[:60]}")

        # Get primary image URL from Etsy
        img_url = get_listing_primary_image_url(token, lid)
        if not img_url:
            print(f"    SKIP — no image found on Etsy")
            continue

        # Download image
        screen = download_image_to_pil(img_url)
        if not screen:
            print(f"    SKIP — download failed")
            continue

        # Create mockup
        mockup_img = create_mockup(screen, title)

        # Upload to Etsy
        r = upload_image(token, lid, mockup_img)
        time.sleep(1.2)

        if r.ok:
            ok += 1
            done[lid] = {"title": title[:60], "source": "downloaded"}
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"    uploaded: OK")
        else:
            print(f"    ERROR {r.status_code}: {r.text[:120]}")

        if i % 10 == 0:
            token = get_token()

    print(f"\n{'='*65}")
    print(f"  Done: {ok}/{len(pending)} missing mockups fixed")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
