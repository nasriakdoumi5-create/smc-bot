"""
Diagnostic: find all active listings and show bundle/system listings.
Run: python find_bundles.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"


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


def fetch_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset}, timeout=30,
        )
        if not r.ok:
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings


token = get_token()
listings = fetch_all_listings(token)
print(f"\nTotal active listings: {len(listings)}\n")

print("── Listings with 'bundle', 'system', '3 google', or 'all 10' ──")
for lst in sorted(listings, key=lambda x: x["listing_id"]):
    t = (lst.get("title") or "").lower()
    if any(kw in t for kw in ["bundle", "system", "3 google", "all 10"]):
        price = lst.get("price", {}).get("amount", 0) / 100 if lst.get("price") else 0
        print(f"  [{lst['listing_id']}] €{price:.2f}  {lst.get('title', '')[:80]}")

print("\n── All active listing IDs + titles ──")
for lst in sorted(listings, key=lambda x: x["listing_id"]):
    print(f"  [{lst['listing_id']}] {lst.get('title', '')[:75]}")
