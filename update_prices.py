"""
update_prices.py  v3
Reprices all NasriTools listings via the inventory endpoint.
(Etsy ignores listing-level price PATCH for listings with inventory.)
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

def update_via_inventory(token, lid, new_price):
    """Update price through the inventory endpoint (correct way for Etsy v3).
    Note: inventory endpoint is /listings/{lid}/inventory, NOT under /shops/."""
    inv_url = f"{API}/listings/{lid}/inventory"

    # 1. GET current inventory
    r = requests.get(inv_url, headers=auth_headers(token), timeout=30)
    if not r.ok:
        return False, f"GET inv {r.status_code}: {r.text[:80]}", 0

    inv = r.json()
    products = inv.get("products", [])
    if not products:
        return False, "no products in inventory", 0

    # 2. Rebuild a clean payload with ONLY the writable fields.
    #    PUT expects price as a plain float, not the money object GET returns.
    clean_products = []
    for product in products:
        clean_offerings = []
        for offering in product.get("offerings", []):
            clean_offerings.append({
                "price": float(new_price),
                "quantity": offering.get("quantity", 998),
                "is_enabled": offering.get("is_enabled", True),
            })
        clean_props = []
        for pv in product.get("property_values", []):
            clean_props.append({
                "property_id": pv.get("property_id"),
                "value_ids": pv.get("value_ids", []),
                "values": pv.get("values", []),
            })
        clean_products.append({
            "sku": product.get("sku", "") or "",
            "property_values": clean_props,
            "offerings": clean_offerings,
        })

    # 3. PUT inventory back
    payload = {
        "products": clean_products,
        "price_on_property": inv.get("price_on_property", []),
        "quantity_on_property": inv.get("quantity_on_property", []),
        "sku_on_property": inv.get("sku_on_property", []),
    }
    r2 = requests.put(
        inv_url,
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if not r2.ok:
        return False, f"PUT {r2.status_code}: {r2.text[:120]}", 0

    # 4. Read back the actual stored price
    try:
        resp = r2.json()
        prods = resp.get("products", [])
        pr = prods[0]["offerings"][0]["price"] if prods else {}
        actual = float(pr.get("amount", 0)) / max(pr.get("divisor", 100), 1)
    except Exception:
        actual = -1
    return True, "ok", actual

def main():
    print("=" * 65)
    print("  NasriTools — Price Updater v3 (inventory endpoint)")
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

        print(f"  [{idx:3}/{total}] [{tier:8}] €{current:.2f} → €{new_price:.2f} | {title[:33]}...", end=" ", flush=True)

        token = get_token()
        ok, msg, actual = update_via_inventory(token, lid, new_price)

        if ok:
            if actual >= 0 and abs(actual - new_price) > 0.02:
                print(f"⚠ still €{actual:.2f}! ({msg})")
                mismatch += 1
            else:
                print(f"✓ €{actual:.2f}")
                updated += 1
        else:
            print(f"✗ {msg}")
            failed += 1

        time.sleep(1.0)
        if idx % 15 == 0:
            token = get_token()

    tier_prices = {"BASIC": BASIC, "STANDARD": STANDARD, "PREMIUM": PREMIUM,
                   "BUNDLE_S": BUNDLE_S, "BUNDLE_L": BUNDLE_L}

    print(f"\n{'=' * 65}")
    print(f"  Updated OK : {updated}")
    print(f"  Skipped    : {skipped} (already correct)")
    print(f"  Mismatch   : {mismatch}")
    print(f"  Failed     : {failed}")
    print(f"\n  Tier breakdown:")
    for tier, count in sorted(tier_counts.items()):
        print(f"    {tier:10} {count:3}  →  €{tier_prices.get(tier, 0):.2f}")
    print(f"{'=' * 65}")

if __name__ == "__main__":
    main()
