"""
NasriTools - Upload images + digital file to Etsy draft listings
Run from: C:\Users\nasri\smc-bot
Usage:    python nasritools/upload_assets.py

Reads:  ~/etsy_published.json  (slug -> listing_id)
Reads:  output/{slug}/         (images + xlsx)
Saves:  ~/etsy_uploaded.json   (progress)
"""
import json, time, os, requests
from pathlib import Path

CLIENT_ID   = "pluc0garrgcjzhim0hawxf0k"
SECRET      = "hc89hlqkd6"
API         = "https://api.etsy.com/v3/application"
SHOP_ID     = 66526082
TOKEN_FILE  = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE    = Path(os.path.expanduser("~")) / "etsy_published.json"
DONE_FILE   = Path(os.path.expanduser("~")) / "etsy_uploaded.json"
OUTPUT_DIR  = Path(__file__).parent.parent / "output"

IMAGE_SLOTS = ["_01_hero", "_02_included", "_03_how", "_04_features", "_05_cta"]


def get_token():
    token = json.loads(TOKEN_FILE.read_text())
    if time.time() >= token.get("expires_at", 0):
        print("  Refreshing token...")
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": token["refresh_token"],
        })
        r.raise_for_status()
        token = r.json()
        token["expires_at"] = time.time() + token.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(token, indent=2))
        print("  Token refreshed")
    return token


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token['access_token']}",
        "x-api-key": f"{CLIENT_ID}:{SECRET}",
    }


def upload_image(listing_id, img_path, rank, token):
    with open(img_path, "rb") as f:
        r = requests.post(
            f"{API}/shops/{SHOP_ID}/listings/{listing_id}/images",
            headers=auth_headers(token),
            data={"rank": rank, "overwrite": "true"},
            files={"image": (img_path.name, f, "image/jpeg")},
        )
    return r


def upload_file(listing_id, file_path, token):
    with open(file_path, "rb") as f:
        r = requests.post(
            f"{API}/shops/{SHOP_ID}/listings/{listing_id}/files",
            headers=auth_headers(token),
            files={"file": (file_path.name, f, "application/octet-stream")},
        )
    return r


def main():
    print()
    print("=" * 55)
    print("  NasriTools - Upload Images + Files")
    print("=" * 55)

    if not PUB_FILE.exists():
        print(f"ERROR: {PUB_FILE} not found. Run publish_now.py first.")
        return

    published = json.loads(PUB_FILE.read_text())
    done = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}

    token = get_token()

    items = list(published.items())
    total = len(items)
    print(f"\n  Listings  : {total}")
    print(f"  Done      : {len(done)}")
    print(f"  Remaining : {total - len(done)}")
    print()

    for i, (slug, listing_id) in enumerate(items, 1):
        if slug in done:
            print(f"  [{i:3d}/{total}] SKIP: {slug}")
            continue

        folder = OUTPUT_DIR / slug
        if not folder.exists():
            print(f"  [{i:3d}/{total}] MISS folder: {slug}")
            continue

        print(f"  [{i:3d}/{total}] {slug}")

        # Refresh token every 50 items
        if i % 50 == 0:
            token = get_token()

        errors = []

        # Upload 5 images
        for rank, slot in enumerate(IMAGE_SLOTS, 1):
            img = folder / f"{slug}{slot}.jpg"
            if not img.exists():
                print(f"    img{rank}: NOT FOUND ({img.name})")
                continue
            r = upload_image(listing_id, img, rank, token)
            if r.ok:
                print(f"    img{rank}: OK")
            else:
                print(f"    img{rank}: ERR {r.status_code}: {r.text[:80]}")
                errors.append(f"img{rank}")
            time.sleep(0.5)

        # Upload digital file (.xlsx)
        xlsx = folder / f"{slug}.xlsx"
        if xlsx.exists():
            r = upload_file(listing_id, xlsx, token)
            if r.ok:
                print(f"    file: OK ({xlsx.name})")
            else:
                print(f"    file: ERR {r.status_code}: {r.text[:80]}")
                errors.append("xlsx")
            time.sleep(0.5)
        else:
            print(f"    file: NOT FOUND ({xlsx.name})")

        if not errors:
            done[slug] = listing_id
            DONE_FILE.write_text(json.dumps(done, indent=2))

        time.sleep(0.3)

    print()
    print("=" * 55)
    print(f"  Completed : {len(done)}/{total}")
    if len(done) < total:
        print(f"  Remaining : {total - len(done)} (re-run to retry)")
    print(f"  Progress  : {DONE_FILE}")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()
