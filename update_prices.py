"""
update_prices.py
Updates strategic prices per the Premium Positioning plan.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

# keyword → (new_price_cents, currency)
PRICE_MAP = [
    (["kpi dashboard", "kpi spread"],              2499, "EUR"),
    (["complete life system", "all 10 templa"],    5499, "EUR"),
    (["finance bundle", "budget + invoice"],        4999, "EUR"),
    (["restaurant manager", "restaurant tracker"], 2999, "EUR"),
    (["real estate deal", "real estate tracker"],  2499, "EUR"),
    (["startup financial"],                         2499, "EUR"),
    (["construction"],                              2499, "EUR"),
    (["law firm"],                                  2499, "EUR"),
    (["amazon fba"],                                2499, "EUR"),
    (["budget tracker", "budget & expense",
      "budget spreadsheet"],                        1999, "EUR"),
]

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
                         params={"limit": 100, "offset": offset})
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100
    return listings

def get_target_price(title_lower):
    for keywords, cents, currency in PRICE_MAP:
        if any(k in title_lower for k in keywords):
            return cents, currency
    return None, None

def update_price(token, lid, price_cents, currency):
    data = urllib.parse.urlencode({
        "price": str(price_cents / 100),
    })
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=data, timeout=30,
    )
    return r.ok, r.status_code

def main():
    print("=" * 65)
    print("  NasriTools — Strategic Price Update")
    print("=" * 65)
    token = get_token()
    listings = get_all_listings(token)
    print(f"[*] Found {len(listings)} listings\n")

    ok = skip = fail = 0
    for l in listings:
        lid   = l["listing_id"]
        title = l["title"]
        tl    = title.lower()

        price_raw = l.get("price", {})
        if isinstance(price_raw, dict):
            current = float(price_raw.get("amount", 0)) / max(price_raw.get("divisor", 100), 1)
        else:
            current = float(price_raw or 0)

        target_cents, currency = get_target_price(tl)
        if target_cents is None:
            skip += 1
            continue

        target = target_cents / 100
        if abs(current - target) < 0.01:
            print(f"  [SAME]  €{current:.2f}  {title[:45]}")
            skip += 1
            continue

        print(f"  [FIX]   €{current:.2f} → €{target:.2f}  {title[:40]} ...", end=" ", flush=True)
        token = get_token()
        r_ok, code = update_price(token, lid, target_cents, currency)
        if r_ok:
            print("OK")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1
        time.sleep(0.8)

    print(f"\n{'='*65}")
    print(f"  Updated: {ok} | Skipped/Same: {skip} | Failed: {fail}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
