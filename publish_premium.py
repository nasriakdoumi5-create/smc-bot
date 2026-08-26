"""
publish_premium.py
Publishes the 7 premium products from DIGITAL_PRODUCTS/ to Etsy.
Each: draft listing → 3 images → demo video → xlsx file → activate.

Content source: DIGITAL_PRODUCTS/content/listings.json
Assets:         DIGITAL_PRODUCTS/files/  (matched by filename)

Pick which to publish with PUBLISH below.
Run:  python publish_premium.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
FILES      = Path(__file__).parent / "DIGITAL_PRODUCTS" / "files"
LISTINGS   = Path(__file__).parent / "DIGITAL_PRODUCTS" / "content" / "listings.json"
DONE_FILE  = Path(__file__).parent / "premium_published.json"
TAXONOMY   = 2078

# ── Which products to publish ────────────────────────────────────────────
# The launch plan (README) says: start with the 3 stars, watch 2 weeks, then
# the rest. Edit this list to control what goes live.
#   "ALL"   → publish all 7
#   "STARS" → Trading Journal, Business KPI, Budget Tracker
#   or list exact product names, e.g. ["Trading Journal"]
PUBLISH = "STARS"

STARS = ["Trading Journal", "Business KPI Dashboard", "Monthly Budget Tracker"]

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

def local(path_from_json):
    """Resolve a listings.json path to the real file by its basename."""
    name = str(path_from_json).replace("\\", "/").split("/")[-1]
    return FILES / name

def should_publish(name):
    if PUBLISH == "ALL":
        return True
    if PUBLISH == "STARS":
        return name in STARS
    return name in PUBLISH

def publish_one(p, token, done):
    name  = p["product"]
    title = p["title"][:140]
    tags  = [t.strip()[:20] for t in p.get("tags", [])[:13]]
    price = float(p["price"])
    xlsx  = local(p["file"])

    print(f"\n  ▶ {name}  (${price})")
    if not xlsx.exists():
        print(f"     ✗ missing file {xlsx.name}")
        return False

    # 1. create draft
    r = requests.post(
        f"{API}/shops/{SHOP_ID}/listings",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={
            "quantity": 999, "title": title, "description": p["description"],
            "price": price, "who_made": "i_did", "when_made": "2020_2025",
            "taxonomy_id": TAXONOMY, "type": "download",
            "is_supply": False, "is_digital": True, "tags": tags,
        }, timeout=30)
    if not r.ok:
        print(f"     ✗ create {r.status_code}: {r.text[:150]}")
        return False
    lid = r.json()["listing_id"]
    print(f"     ✓ listing {lid}")

    # 2. images
    for rank, img_path in enumerate(p.get("images", []), 1):
        img = local(img_path)
        if not img.exists():
            print(f"     ⚠ missing image {img.name}"); continue
        with open(img, "rb") as fh:
            ri = requests.post(
                f"{API}/shops/{SHOP_ID}/listings/{lid}/images",
                headers=auth_headers(token),
                files={"image": (img.name, fh, "image/png")},
                data={"rank": rank}, timeout=90)
        print(f"     {'✓' if ri.ok else '✗'} image {img.name}")
        time.sleep(0.5)

    # 3. video
    vid = local(p.get("video", ""))
    if vid.exists():
        with open(vid, "rb") as fh:
            rv = requests.post(
                f"{API}/shops/{SHOP_ID}/listings/{lid}/videos",
                headers=auth_headers(token),
                files={"video": (vid.name, fh, "video/mp4")},
                data={"name": vid.name}, timeout=180)
        print(f"     {'✓' if rv.ok else '✗'} video {vid.name}"
              + ("" if rv.ok else f" ({rv.status_code}: {rv.text[:80]})"))
        time.sleep(0.5)

    # 4. digital file
    with open(xlsx, "rb") as fh:
        rf = requests.post(
            f"{API}/shops/{SHOP_ID}/listings/{lid}/files",
            headers=auth_headers(token),
            files={"file": (xlsx.name, fh,
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"name": xlsx.name, "rank": 1}, timeout=120)
    print(f"     {'✓' if rf.ok else '✗'} file {xlsx.name}")
    if not rf.ok:
        return False

    # 5. activate
    token = get_token()
    ra = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token),
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"state": "active"}, timeout=30)
    if ra.ok:
        print(f"     ✓ LIVE → https://www.etsy.com/listing/{lid}")
    else:
        print(f"     ⚠ saved as DRAFT (activate manually) — {ra.status_code}")

    done[name] = lid
    DONE_FILE.write_text(json.dumps(done, indent=2))
    return True

def main():
    print("=" * 62)
    print("  NasriTools — Publish PREMIUM products")
    print(f"  Mode: {PUBLISH}")
    print("=" * 62)

    products = json.loads(LISTINGS.read_text(encoding="utf-8"))
    done = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    token = get_token()

    n = 0
    for p in products:
        name = p["product"]
        if not should_publish(name):
            continue
        if name in done:
            print(f"\n  ▶ {name}  SKIP (already published {done[name]})")
            continue
        token = get_token()
        if publish_one(p, token, done):
            n += 1
        time.sleep(1.0)

    print(f"\n{'=' * 62}")
    print(f"  Published this run: {n}")
    print(f"  Total done: {len(done)}")
    print(f"{'=' * 62}")

if __name__ == "__main__":
    main()
