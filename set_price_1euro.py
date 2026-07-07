"""
set_price_1euro.py
Changes all listings priced at €0.20 to €1.00.
Listings already at €1.00+ are skipped untouched.
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
NEW_PRICE  = 1.00

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
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token),
                 "Content-Type": "application/x-www-form-urlencoded"},
        data=f"price={NEW_PRICE:.2f}",
        timeout=30,
    )
    if r.ok:
        return True, r.status_code
    # fallback: JSON body
    r2 = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token),
                 "Content-Type": "application/json"},
        json={"price": NEW_PRICE},
        timeout=30,
    )
    return r2.ok, r2.status_code

def main():
    print("=" * 65)
    print("  NasriTools — Set Prices to EUR 1.00")
    print("  Only listings at €0.20 will be updated")
    print("=" * 65)

    token    = get_token()
    listings = get_all_listings(token)
    total    = len(listings)
    print(f"[*] {total} active listings found\n")

    updated = skip_already = skip_higher = fail = 0

    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        p     = l.get("price", {})
        price = float(p.get("amount", 0)) / float(p.get("divisor", 100) or 100)
        title = l["title"][:48]

        print(f"  [{idx:3}/{total}] {title}...", end=" ", flush=True)

        if abs(price - NEW_PRICE) < 0.01:
            print("skip (already €1.00)")
            skip_already += 1
            time.sleep(0.1)
            continue

        if price > NEW_PRICE + 0.05:
            print(f"skip (€{price:.2f} — keeping higher price)")
            skip_higher += 1
            time.sleep(0.1)
            continue

        # price is ~€0.20 — update to €1.00
        print(f"(€{price:.2f} → €{NEW_PRICE:.2f})", end=" ", flush=True)
        token = get_token()
        ok, code = set_price(token, lid)

        if ok:
            print(f"OK")
            updated += 1
        else:
            print(f"FAIL ({code})")
            fail += 1

        time.sleep(0.8)
        if idx % 20 == 0:
            token = get_token()

    print(f"\n{'=' * 65}")
    print(f"  Updated to €1.00 : {updated}")
    print(f"  Already €1.00    : {skip_already}")
    print(f"  Kept higher price: {skip_higher}")
    print(f"  Failed           : {fail}")
    print(f"{'=' * 65}")
    print()
    print("  Etsy shows prices with 21% IVA — €1.00 appears as ~€1.21 to buyers.")

if __name__ == "__main__":
    main()
