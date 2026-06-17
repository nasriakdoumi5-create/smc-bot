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


def get_shop_id(token):
    # Check cached shop ID first
    if SHOP_ID_FILE.exists():
        sid = SHOP_ID_FILE.read_text().strip()
        if sid.isdigit():
            return int(sid)

    # Try: user_id is the numeric prefix of the access token
    user_id = token["access_token"].split(".")[0]
    print(f"  Trying /users/{user_id}/shops ...")
    r = requests.get(f"{API}/users/{user_id}/shops", headers=h(token))
    print(f"    -> {r.status_code}")
    if r.ok:
        data = r.json()
        results = data.get("results", [])
        if results:
            sid = int(results[0]["shop_id"])
            SHOP_ID_FILE.write_text(str(sid))
            return sid

    # Try /users/me (needs profile_r scope, may fail)
    print("  Trying /users/me ...")
    r2 = requests.get(f"{API}/users/me", headers=h(token))
    print(f"    -> {r2.status_code}")
    if r2.ok:
        shop_id = r2.json().get("shop_id")
        if shop_id:
            SHOP_ID_FILE.write_text(str(shop_id))
            return int(shop_id)

    # Manual fallback
    print()
    print("  Could not find your shop automatically.")
    print()
    print("  To find your Etsy Shop ID:")
    print("  1. Open https://www.etsy.com/your/shops/me/tools/listings")
    print("  2. Look at the URL - it will show your shop name")
    print("  3. OR go to: https://www.etsy.com/shop/{YourShopName}/about")
    print("     and the shop ID appears in the page source as 'shop_id'")
    print()
    print("  You can also find it here:")
    print("  https://www.etsy.com/your/shops/me/dashboard")
    print("  The number in the URL after /shops/ is your shop ID.")
    print()
    val = input("  Enter your Etsy Shop ID (numbers only) or Shop Name: ").strip()

    if val.isdigit():
        sid = int(val)
        SHOP_ID_FILE.write_text(str(sid))
        return sid

    # Scrape shop_id from public Etsy page (no auth needed)
    import re
    print(f"  Fetching public page for shop '{val}' ...")
    try:
        rp = requests.get(
            f"https://www.etsy.com/shop/{val}/about",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        match = re.search(r'"shop_id"\s*:\s*(\d+)', rp.text)
        if match:
            sid = int(match.group(1))
            print(f"  Found shop_id={sid} from page")
            SHOP_ID_FILE.write_text(str(sid))
            return sid
        # Try alternate pattern
        match2 = re.search(r"shop_id['\"]?\s*[=:]\s*['\"]?(\d+)", rp.text)
        if match2:
            sid = int(match2.group(1))
            print(f"  Found shop_id={sid}")
            SHOP_ID_FILE.write_text(str(sid))
            return sid
    except Exception as e:
        print(f"  Page fetch failed: {e}")

    raise ValueError(
        f"Could not find shop_id for '{val}'.\n"
        "  Open https://www.etsy.com/shop/NasriTools/about in browser,\n"
        "  press Ctrl+U (View Source), Ctrl+F 'shop_id',\n"
        "  then re-run this script and enter the number directly."
    )


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
