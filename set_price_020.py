"""
set_price_020.py
Sets ALL active listings to EUR 0.20 (Etsy minimum).
Strategy: attract customers and reviews first, profit later.
"""
import json, os, time, requests
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

def set_price(token, lid, attempt=0):
    try:
        r = requests.patch(
            f"{API}/shops/{SHOP_ID}/listings/{lid}",
            headers={**auth_headers(token),
                     "Content-Type": "application/x-www-form-urlencoded"},
            data="price=0.20",
            timeout=30,
        )
        return r.ok, r.status_code
    except requests.exceptions.ConnectionError:
        if attempt < 3:
            time.sleep((attempt + 1) * 4)
            return set_price(token, lid, attempt + 1)
        return False, 0

def main():
    print("=" * 65)
    print("  NasriTools — Set ALL Prices to EUR 0.20")
    print("  Goal: attract customers & reviews first")
    print("=" * 65)

    token    = get_token()
    listings = get_all_listings(token)
    total    = len(listings)
    print(f"[*] {total} active listings found\n")

    ok = skip = fail = 0

    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        price = float(l.get("price", {}).get("amount", 0)) / float(l.get("price", {}).get("divisor", 100) or 100)
        title = l["title"][:45]

        print(f"  [{idx:3}/{total}] {title}...", end=" ", flush=True)

        if abs(price - 0.20) < 0.01:
            print("already 0.20 — skip")
            skip += 1
            time.sleep(0.1)
            continue

        print(f"({price:.2f} → 0.20)", end=" ", flush=True)
        token = get_token()
        r_ok, code = set_price(token, lid)

        if r_ok:
            print("OK ✅")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1

        time.sleep(0.8)

    print(f"\n{'=' * 65}")
    print(f"  Updated: {ok} | Already 0.20: {skip} | Failed: {fail}")
    print(f"  Total processed: {total}")
    print(f"{'=' * 65}")
    print()
    print("  Next step: collect reviews, then raise prices gradually.")

if __name__ == "__main__":
    main()
