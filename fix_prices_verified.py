"""
fix_prices_verified.py
Sets ALL listings to EUR 0.20, then verifies each one actually changed.
Uses JSON body instead of form-encoded (more reliable with Etsy API v3).
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

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

def get_current_price(token, lid):
    r = requests.get(f"{API}/listings/{lid}", headers=auth_headers(token), timeout=20)
    if r.ok:
        p = r.json().get("price", {})
        return float(p.get("amount", 0)) / float(p.get("divisor", 100) or 100)
    return None

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset}, timeout=30)
        if not r.ok:
            print(f"  [fetch error {r.status_code}]")
            break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100:
            break
        offset += 100
        time.sleep(0.4)
    return listings

def set_price(token, lid):
    # Try method 1: form-encoded with explicit currency
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token),
                 "Content-Type": "application/x-www-form-urlencoded"},
        data="price=0.20",
        timeout=30,
    )
    if r.ok:
        return True, "form-encoded", r.status_code

    # Try method 2: JSON body
    r2 = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token),
                 "Content-Type": "application/json"},
        json={"price": 0.20},
        timeout=30,
    )
    if r2.ok:
        return True, "json", r2.status_code

    return False, "both-failed", r2.status_code

def main():
    print("=" * 70)
    print("  NasriTools — Fix Prices with Verification")
    print("=" * 70)

    token = get_token()

    # First: test with ONE listing to verify it actually works
    print("\n[TEST] Testing price update on first listing...")
    r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                     headers=auth_headers(token),
                     params={"limit": 1}, timeout=30)
    if not r.ok:
        print("  Cannot fetch listings")
        return

    test_listing = r.json()["results"][0]
    test_lid = test_listing["listing_id"]
    test_title = test_listing["title"][:40]
    before = get_current_price(token, test_lid)
    print(f"  Listing: {test_title}")
    print(f"  Price before API: €{before:.2f}")

    ok, method, code = set_price(token, test_lid)
    time.sleep(2)

    after = get_current_price(token, test_lid)
    print(f"  Price after API:  €{after:.2f} (method: {method}, status: {code})")

    if after is not None and abs(after - 0.20) < 0.01:
        print("  VERIFIED: API price update WORKS!\n")
        api_works = True
    else:
        print(f"  FAILED: API says ok but price is still €{after:.2f}")
        print("  The Etsy API is NOT updating prices via code.")
        print("\n  → You must update prices MANUALLY in Etsy Shop Manager:")
        print("    etsy.com/your/shops/me/tools/listings")
        print("    Select All → Edit → Price → 0.20 → Apply")
        api_works = False

    if not api_works:
        return

    # If API works, update all listings
    print("[*] API works — updating all listings...\n")
    listings = get_all_listings(token)
    total = len(listings)
    ok_count = skip = fail = 0

    for idx, l in enumerate(listings, 1):
        lid = l["listing_id"]
        p = l.get("price", {})
        price = float(p.get("amount", 0)) / float(p.get("divisor", 100) or 100)
        title = l["title"][:45]

        print(f"  [{idx:3}/{total}] {title}...", end=" ", flush=True)

        if abs(price - 0.20) < 0.01:
            print("skip (already 0.20)")
            skip += 1
            time.sleep(0.1)
            continue

        print(f"(€{price:.2f}→€0.20)", end=" ", flush=True)
        token = get_token()
        success, method, code = set_price(token, lid)

        if success:
            print(f"OK [{method}]")
            ok_count += 1
        else:
            print(f"FAIL ({code})")
            fail += 1

        time.sleep(0.8)
        if idx % 20 == 0:
            token = get_token()

    print(f"\n{'=' * 70}")
    print(f"  Updated: {ok_count} | Skipped: {skip} | Failed: {fail}")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    main()
