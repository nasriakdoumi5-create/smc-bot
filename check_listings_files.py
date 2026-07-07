"""
check_listings_files.py
Checks all active listings for missing or empty download files.
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
        time.sleep(0.3)
    return listings

def get_listing_files(token, lid):
    r = requests.get(
        f"{API}/shops/{SHOP_ID}/listings/{lid}/files",
        headers=auth_headers(token),
        timeout=20
    )
    if r.ok:
        return r.json().get("results", [])
    return None

def main():
    print("=" * 65)
    print("  NasriTools — Check All Listings for Missing Files")
    print("=" * 65)

    token    = get_token()
    listings = get_all_listings(token)
    total    = len(listings)
    print(f"[*] {total} active listings found\n")

    no_files   = []
    has_files  = []
    api_errors = []

    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        title = l["title"][:50]

        print(f"  [{idx:3}/{total}] {title}...", end=" ", flush=True)

        token = get_token()
        files = get_listing_files(token, lid)

        if files is None:
            print("API ERROR")
            api_errors.append((lid, title))
        elif len(files) == 0:
            print("NO FILES ⚠️")
            no_files.append((lid, title))
        else:
            print(f"OK ({len(files)} file{'s' if len(files)>1 else ''})")
            has_files.append((lid, title, len(files)))

        time.sleep(0.5)

    print(f"\n{'=' * 65}")
    print(f"  OK (has files)  : {len(has_files)}")
    print(f"  NO FILES ⚠️     : {len(no_files)}")
    print(f"  API errors      : {len(api_errors)}")
    print(f"{'=' * 65}")

    if no_files:
        print(f"\n  ⚠️  LISTINGS WITH NO FILES ({len(no_files)}):")
        for lid, title in no_files:
            print(f"    [{lid}] {title}")
        print(f"\n  Fix: Go to each listing in Etsy Shop Manager")
        print(f"  and upload the Google Sheets file.")

    if api_errors:
        print(f"\n  ❌ API ERRORS ({len(api_errors)}):")
        for lid, title in api_errors:
            print(f"    [{lid}] {title}")

if __name__ == "__main__":
    main()
