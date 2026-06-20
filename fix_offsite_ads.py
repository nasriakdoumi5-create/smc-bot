"""
fix_offsite_ads.py
Checks listings priced under €20 and prints a report.
Etsy Offsite Ads: Etsy charges 12-15% commission on sales from offsite ads.
For listings priced under €20, the commission eats most of the margin.

NOTE: Etsy API does NOT allow toggling offsite ads per-listing via v3 API.
This script identifies affected listings and provides a manual fix guide.

To opt out of Offsite Ads (if your shop earned < $10,000/year):
  Etsy Shop Manager → Marketing → Offsite Ads → Toggle off
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

LOW_PRICE_THRESHOLD = 20.0  # EUR

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
    return {"Authorization": "Bearer " + token["access_token"], "x-api-key": CLIENT_ID + ":" + SECRET}

def get_all_listings(token):
    listings = []
    offset = 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token), params={"limit": 100, "offset": offset})
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100
    return listings

def main():
    print("=" * 65)
    print("  NasriTools — Offsite Ads Audit")
    print("=" * 65)
    token = get_token()
    listings = get_all_listings(token)
    print(f"[*] Found {len(listings)} listings\n")

    low_price = []
    ok_price  = []

    for l in listings:
        price_raw = l.get("price", {})
        if isinstance(price_raw, dict):
            price = float(price_raw.get("amount", 0)) / max(price_raw.get("divisor", 100), 1)
        else:
            price = float(price_raw or 0)

        title = l["title"]
        lid   = l["listing_id"]

        if price < LOW_PRICE_THRESHOLD:
            low_price.append((price, title, lid))
        else:
            ok_price.append((price, title, lid))

    print(f"  Listings UNDER €{LOW_PRICE_THRESHOLD} (offsite ads cost >12% margin):")
    print(f"  {'─'*60}")
    for price, title, lid in sorted(low_price):
        ad_cost = price * 0.15
        print(f"  €{price:5.2f}  [{lid}]  {title[:40]}  → ad cost ~€{ad_cost:.2f}")

    print(f"\n  Listings OVER €{LOW_PRICE_THRESHOLD} (offsite ads OK):")
    print(f"  {'─'*60}")
    for price, title, lid in sorted(ok_price):
        print(f"  €{price:5.2f}  {title[:50]}")

    print(f"\n{'='*65}")
    print(f"  LOW PRICE: {len(low_price)} listings | SAFE PRICE: {len(ok_price)} listings")
    print(f"{'='*65}")
    print("""
  ACTION REQUIRED (Manual):
  Etsy API v3 does NOT expose per-listing offsite ad toggle.

  Option A — Opt out entirely (recommended if < $10k/year):
    Etsy Shop Manager → Marketing → Offsite Ads → Turn off

  Option B — Raise prices on low listings to ≥ €20:
    Run: python fix_budget_tracker_price.py
    Or edit listings manually in Etsy Shop Manager.

  Option C — Leave it on (Etsy drives extra traffic; you pay only on sale).
""")

if __name__ == "__main__":
    main()
