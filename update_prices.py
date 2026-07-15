"""
update_prices.py  v2
Reprices all NasriTools listings to market tiers.
Verifies each update by reading back Etsy's response.

Tiers:
  BUNDLE_L  €19.99 — complete systems / large bundles (5+ products)
  BUNDLE_S   €9.99 — small bundles / kits (2-4 products)
  PREMIUM    €7.99 — advanced dashboards, CRM, full managers
  STANDARD   €4.99 — multi-feature planners & trackers
  BASIC      €2.99 — simple single-feature templates
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

BUNDLE_L = 19.99
BUNDLE_S =  9.99
PREMIUM  =  7.99
STANDARD =  4.99
BASIC    =  2.99

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

def detect_tier(title):
    t = title.lower()
    if any(x in t for x in [
        "complete system", "complete life", "complete finance", "complete business",
        "all-in-one", "all in one", "mega bundle", "ultimate bundle",
        "full bundle", "complete kit", "full system", "all 10", "all 5",
    ]):
        return BUNDLE_L, "BUNDLE_L"
    if any(x in t for x in [
        "bundle", " kit", " pack", "collection", "combo",
    ]):
        return BUNDLE_S, "BUNDLE_S"
    if any(x in t for x in [
        "dashboard", "crm", "kpi", "business intelligence",
        "restaurant manager", "hr system", "real estate analyzer",
        "investment tracker", "pipeline", "sales tracker",
        "ecommerce tracker", "pod tracker", "financial model",
        "cash flow forecast", "profit loss", "p&l",
        "complete", "advanced", "professional", "pro ",
        "automated", "full suite", "business manager",
        "freelance business", "startup financial",
    ]):
        return PREMIUM, "PREMIUM"
    if any(x in t for x in [
        "planner", "manager", "system", "tracker",
        "organizer", "calendar", "schedule",
        "invoice", "billing", "client tracker",
        "meal plan", "workout plan", "training plan",
        "content calendar", "social media",
        "budget planner", "expense tracker",
        "project tracker", "task manager",
        "inventory", "stock tracker",
        "travel planner", "event planner",
        "student planner", "study planner",
    ]):
        return STANDARD, "STANDARD"
    return BASIC, "BASIC"

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset}, timeout=30)
        if not r.ok:
            print(f"  Error fetching listings: {r.status_code} {r.text[:200]}")
            break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings

def update_price(token, lid, new_price):
    body = urllib.parse.urlencode({"price": f"{new_price:.2f}"})
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=body,
        timeout=30,
    )
    if not r.ok:
        return False, r.status_code, 0

    # Read the actual price Etsy stored in its response
    try:
        resp = r.json()
        price_raw = resp.get("price", {})
        actual = float(price_raw.get("amount", 0)) / max(price_raw.get("divisor", 100), 1)
    except Exception:
        actual = -1
    return True, r.status_code, actual

def main():
    print("=" * 65)
    print("  NasriTools — Price Updater v2")
    print("  Repricing all listings + verifying Etsy response")
    print("=" * 65)

    token    = get_token()
    listings = get_all_listings(token)
    total    = len(listings)
    print(f"[*] {total} listings found\n")

    updated = skipped = failed = mismatch = 0
    tier_counts = {}

    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        title = l.get("title", "")
        price_raw = l.get("price", {})
        current = float(price_raw.get("amount", 0)) / max(price_raw.get("divisor", 100), 1)

        new_price, tier = detect_tier(title)
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

        if abs(current - new_price) < 0.02:
            skipped += 1
            print(f"  [{idx:3}/{total}] SKIP  €{current:.2f} ({tier}): {title[:50]}")
            time.sleep(0.05)
            continue

        print(f"  [{idx:3}/{total}] [{tier:8}] €{current:.2f} → €{new_price:.2f} | {title[:35]}...", end=" ", flush=True)

        token = get_token()
        ok, code, actual = update_price(token, lid, new_price)

        if ok:
            if actual >= 0 and abs(actual - new_price) > 0.02:
                print(f"⚠ API stored €{actual:.2f} instead of €{new_price:.2f}!")
                mismatch += 1
            else:
                print(f"✓ (Etsy confirmed €{actual:.2f})")
                updated += 1
        else:
            print(f"✗ ({code})")
            failed += 1

        time.sleep(0.8)
        if idx % 20 == 0:
            token = get_token()

    tier_prices = {"BASIC": BASIC, "STANDARD": STANDARD, "PREMIUM": PREMIUM,
                   "BUNDLE_S": BUNDLE_S, "BUNDLE_L": BUNDLE_L}

    print(f"\n{'=' * 65}")
    print(f"  Updated OK : {updated}")
    print(f"  Skipped    : {skipped} (already correct)")
    print(f"  Mismatch   : {mismatch} (API accepted but stored wrong price)")
    print(f"  Failed     : {failed}")
    print(f"\n  Tier breakdown:")
    for tier, count in sorted(tier_counts.items()):
        print(f"    {tier:10} {count:3}  →  €{tier_prices.get(tier, 0):.2f}")
    print(f"{'=' * 65}")

if __name__ == "__main__":
    main()
