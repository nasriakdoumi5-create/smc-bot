"""
Reactivate ALL inactive/draft listings in the shop.
Run: python reactivate_all.py
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

def fetch_inactive(token):
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings",
            headers=auth_headers(token),
            params={"state": "inactive", "limit": 100, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            print(f"  Fetch error: {r.status_code}")
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
        time.sleep(0.5)
    return listings

def main():
    token = get_token()
    print("\nFetching inactive listings...")
    listings = fetch_inactive(token)
    print(f"Found {len(listings)} inactive listings\n")

    ok = 0
    for i, lst in enumerate(listings, 1):
        lid   = lst["listing_id"]
        title = lst.get("title", "")[:50]
        print(f"[{i}/{len(listings)}] {title}...", end=" ", flush=True)

        token = get_token()
        r = requests.patch(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}",
            headers={**auth_headers(token), "Content-Type": "application/json"},
            json={"state": "active"},
            timeout=30,
        )
        if r.ok:
            print("OK")
            ok += 1
        else:
            print(f"FAIL {r.status_code}: {r.text[:80]}")
        time.sleep(0.5)

    print(f"\nReactivated: {ok}/{len(listings)}")

if __name__ == "__main__":
    main()
