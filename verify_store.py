"""
verify_store.py
Reads LIVE data back from Etsy and proves whether prices + descriptions
were really updated. No changes are made — read-only.
Run:  python verify_store.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

MARKER = "WHY NASRITOOLS"   # only exists in the new descriptions

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
    return {
        "Authorization": "Bearer " + token["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset}, timeout=30)
        if not r.ok:
            print(f"  Error: {r.status_code} {r.text[:200]}")
            break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings

def main():
    print("=" * 65)
    print("  NasriTools — LIVE Store Verification (read-only)")
    print("=" * 65)

    token    = get_token()
    listings = get_all_listings(token)
    total    = len(listings)
    print(f"[*] {total} listings fetched LIVE from Etsy\n")

    price_buckets = {}
    old_price = 0
    new_desc = 0
    old_desc_items = []

    for l in listings:
        price_raw = l.get("price", {})
        price = float(price_raw.get("amount", 0)) / max(price_raw.get("divisor", 100), 1)
        key = f"€{price:.2f}"
        price_buckets[key] = price_buckets.get(key, 0) + 1
        if price < 2.5:
            old_price += 1

        desc = l.get("description", "")
        if MARKER in desc:
            new_desc += 1
        else:
            old_desc_items.append(l.get("title", "")[:55])

    print("  ─── PRICES (live from Etsy) ───")
    for k in sorted(price_buckets, key=lambda x: float(x[1:])):
        print(f"    {k:8} × {price_buckets[k]}")
    if old_price == 0:
        print("    ✅ NO listing is below €2.50 — old prices are GONE")
    else:
        print(f"    ❌ {old_price} listings still under €2.50!")

    print("\n  ─── DESCRIPTIONS (live from Etsy) ───")
    print(f"    New format : {new_desc}/{total}")
    if new_desc == total:
        print("    ✅ ALL descriptions contain the new structure")
    else:
        print(f"    ❌ {total - new_desc} still have OLD descriptions:")
        for t in old_desc_items[:10]:
            print(f"       - {t}")

    # Show one real example straight from Etsy
    sample = listings[0]
    print("\n  ─── SAMPLE (first listing, straight from Etsy) ───")
    print(f"    Title : {sample.get('title','')[:60]}")
    pr = sample.get("price", {})
    print(f"    Price : €{float(pr.get('amount',0))/max(pr.get('divisor',100),1):.2f}")
    print(f"    Desc  : {sample.get('description','')[:150]}...")
    print("=" * 65)

if __name__ == "__main__":
    main()
