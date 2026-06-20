"""
fix_budget_tracker_price.py
Lists all shop listings with prices, then fixes Budget Tracker if price is wrong.
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

CORRECT_PRICES = {
    "budget":     17.99,
    "invoice":    21.99,
    "workout":    12.99,
    "meal":       12.99,
    "habit":      16.99,
    "weekly":     12.99,
    "student":    16.99,
    "goals":      12.99,
    "content":    21.99,
    "wedding":    12.99,
}

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
    listings = []
    offset = 0
    while True:
        r = requests.get(
            f"{API}/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset},
        )
        if not r.ok:
            print(f"  Failed to fetch listings: HTTP {r.status_code}")
            break
        data = r.json()
        results = data.get("results", [])
        listings.extend(results)
        if len(results) < 100:
            break
        offset += 100
    return listings

def update_price(token, listing_id, price):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{listing_id}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=f"price={price:.2f}",
        timeout=30,
    )
    return r.ok, r.status_code

def get_price(listing):
    p = listing.get("price", {})
    return p.get("amount", 0) / max(p.get("divisor", 100), 1)

def main():
    print("=" * 65)
    print("  NasriTools — Price Checker & Fixer")
    print("=" * 65)

    token = get_token()
    print("[*] Token OK")

    listings = get_all_listings(token)
    print(f"[*] Found {len(listings)} active listings\n")

    print(f"{'ID':<14} {'Price':>8}  Title")
    print("-" * 65)
    problems = []
    for l in sorted(listings, key=lambda x: get_price(x)):
        lid   = l["listing_id"]
        title = l["title"][:50]
        price = get_price(l)
        flag  = " ⚠ WRONG!" if price < 5.0 else ""
        print(f"{lid:<14} €{price:>6.2f}  {title}{flag}")
        if price < 5.0:
            problems.append(l)

    if not problems:
        print("\n✅ All prices look correct.")
        return

    print(f"\n{'='*65}")
    print(f"  Found {len(problems)} listings with wrong price — fixing now...")
    print(f"{'='*65}\n")

    token = get_token()
    for l in problems:
        lid   = l["listing_id"]
        title = l["title"]
        old   = get_price(l)

        # Determine correct price from title keywords
        title_lower = title.lower()
        new_price = None
        for kw, price in CORRECT_PRICES.items():
            if kw in title_lower:
                new_price = price
                break

        if new_price is None:
            new_price = 17.99  # safe default

        print(f"  [{lid}] {title[:45]}")
        print(f"    Old: €{old:.2f}  →  New: €{new_price:.2f} ... ", end="", flush=True)
        ok, code = update_price(token, lid, new_price)
        print(f"{'OK' if ok else 'FAILED'} (HTTP {code})")
        time.sleep(1)

    print(f"\n{'='*65}")
    print(f"  Done.")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
