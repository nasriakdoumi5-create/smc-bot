"""
NasriTools - Publish listings to Etsy (metadata only, no file upload)
Run from your local machine:
    python nasritools/publish_only.py

Requirements: pip install requests
Token file:   C:/Users/nasri/etsy_token.json  (already saved)
"""
import json
import time
import os
from pathlib import Path

try:
    import requests
except ImportError:
    print("Run: pip install requests")
    exit(1)

# Config
CLIENT_ID     = "pluc0garrgcjzhim0hawxf0k"
SHARED_SECRET = "hc89hlqkd6"
API           = "https://api.etsy.com/v3/application"
TOKEN_FILE   = Path(os.path.expanduser("~")) / "etsy_token.json"
DATA_FILE    = Path(__file__).parent / "listings_data.json"
RESULTS_FILE = Path(os.path.expanduser("~")) / "etsy_published.json"
SHOP_ID_FILE = Path(os.path.expanduser("~")) / "etsy_shop_id.txt"


def load_token():
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(f"Token not found at {TOKEN_FILE}")
    token = json.loads(TOKEN_FILE.read_text())
    if time.time() >= token.get("expires_at", 0):
        print("  Token expired, refreshing...")
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type":    "refresh_token",
            "client_id":     CLIENT_ID,
            "refresh_token": token["refresh_token"],
        })
        r.raise_for_status()
        token = r.json()
        token["expires_at"] = time.time() + token.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(token, indent=2))
        print("  Token refreshed OK")
    return token


def h(token):
    return {
        "Authorization": f"Bearer {token['access_token']}",
        "x-api-key": CLIENT_ID,
    }


SHOP_ID = 66526082  # NasriTools


def get_shop_id(token):
    return SHOP_ID


def create_listing(shop_id, item, token):
    body = {
        "quantity":        999,
        "title":           item["title"],
        "description":     item["description"],
        "price":           item["price"],
        "who_made":        "i_did",
        "when_made":       "2020_2025",
        "taxonomy_id":     2078,
        "type":            "download",
        "is_supply":       False,
        "is_customizable": False,
        "tags":            item["tags"],
        "state":           "draft",
    }
    r = requests.post(
        f"{API}/shops/{shop_id}/listings",
        headers={**h(token), "Content-Type": "application/json"},
        json=body,
    )
    if not r.ok:
        print(f"    ERROR {r.status_code}: {r.text[:300]}")
        return None
    return r.json().get("listing_id")


def main():
    print()
    print("=" * 50)
    print("  NasriTools - Etsy Publisher")
    print("=" * 50)

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"listings_data.json not found at {DATA_FILE}")

    listings = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    print(f"\n  Products to publish: {len(listings)}")

    token = load_token()
    print("  Token loaded OK")

    shop_id = get_shop_id(token)
    print(f"  Shop ID: {shop_id}")

    results = {}
    if RESULTS_FILE.exists():
        results = json.loads(RESULTS_FILE.read_text())

    published = 0
    failed = []

    for i, item in enumerate(listings, 1):
        slug = item["slug"]
        if slug in results:
            print(f"  [{i:3d}/{len(listings)}] SKIP: {slug}")
            published += 1
            continue

        title_preview = item["title"][:50]
        print(f"  [{i:3d}/{len(listings)}] {title_preview}...")

        listing_id = create_listing(shop_id, item, token)
        if listing_id:
            results[slug] = listing_id
            RESULTS_FILE.write_text(json.dumps(results, indent=2))
            print(f"           OK listing_id={listing_id}")
            published += 1
        else:
            failed.append(slug)
            print(f"           FAILED")

        time.sleep(0.3)

    print()
    print("=" * 50)
    print(f"  Published : {published}/{len(listings)}")
    if failed:
        print(f"  Failed    : {len(failed)}")
        for s in failed:
            print(f"    - {s}")
    print(f"  Results   : {RESULTS_FILE}")
    print("=" * 50)
    print()


if __name__ == "__main__":
    main()
