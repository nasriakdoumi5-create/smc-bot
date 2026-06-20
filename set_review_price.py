"""
set_review_price.py
Temporarily sets Budget Tracker to minimum price for friend reviews.
Run with --restore to bring original price back after getting reviews.
"""
import json, os, sys, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

REVIEW_PRICE  = 0.27   # minimum Etsy allows (~€0.05 after 75% coupon)
ORIGINAL_PRICE = 17.99  # restore after reviews

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

def get_listings(token):
    r = requests.get(
        f"{API}/shops/{SHOP_ID}/listings/active",
        headers=auth_headers(token),
        params={"limit": 100},
    )
    return r.json().get("results", [])

def set_price(token, lid, price):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=f"price={price:.2f}",
        timeout=30,
    )
    return r.ok, r.status_code

def get_price(l):
    p = l.get("price", {})
    return p.get("amount", 0) / max(p.get("divisor", 100), 1)

def main():
    restore = "--restore" in sys.argv
    target_price = ORIGINAL_PRICE if restore else REVIEW_PRICE
    mode = "RESTORE" if restore else "REVIEW MODE"

    print("=" * 55)
    print(f"  NasriTools — Budget Tracker Price ({mode})")
    print("=" * 55)

    token = get_token()
    listings = get_listings(token)

    found = False
    for l in listings:
        title = l["title"].lower()
        if "budget" in title and ("tracker" in title or "expense" in title):
            lid   = l["listing_id"]
            old   = get_price(l)
            print(f"\n  Found: {l['title'][:50]}")
            print(f"  [{lid}]  €{old:.2f} → €{target_price:.2f}")
            print(f"  Updating...", end=" ", flush=True)
            ok, code = set_price(token, lid, target_price)
            if ok:
                print(f"OK (HTTP {code})")
                if not restore:
                    print(f"\n  ✅ Price set to €{target_price:.2f}")
                    print(f"  With FRIENDS100 (75% off) = €{target_price*0.25:.2f} ≈ FREE")
                    print(f"\n  Share this link with friends:")
                    print(f"  nasritools.etsy.com?coupon=FRIENDS100")
                    print(f"\n  After 10 reviews, run:")
                    print(f"  python set_review_price.py --restore")
                else:
                    print(f"\n  ✅ Price restored to €{target_price:.2f}")
            else:
                print(f"FAILED (HTTP {code})")
            found = True
            break

    if not found:
        print("\n  ❌ Budget Tracker listing not found.")

    print("=" * 55)

if __name__ == "__main__":
    main()
