"""
activate_bundles.py
Finds all draft listings and activates them (state: draft → active).
Run after create_premium_bundles.py and upload_thumbnails.py.
"""
import json, os, time, requests, urllib.parse
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

def get_draft_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"{API}/shops/{SHOP_ID}/listings",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset, "state": "draft"},
        )
        if not r.ok:
            print(f"  [WARN] Draft fetch: HTTP {r.status_code}")
            break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100
    return listings

def activate_listing(token, lid):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data="state=active",
        timeout=30,
    )
    return r.ok, r.status_code

def main():
    print("=" * 65)
    print("  NasriTools — Activate All Draft Listings")
    print("=" * 65)
    token = get_token()
    drafts = get_draft_listings(token)
    print(f"[*] Found {len(drafts)} draft listings\n")

    if not drafts:
        print("  No drafts found — all listings already active.")
        return

    ok = fail = 0
    for l in drafts:
        lid   = l["listing_id"]
        title = l["title"]
        print(f"  [ACT]  {title[:55]}...", end=" ", flush=True)
        token = get_token()
        r_ok, code = activate_listing(token, lid)
        if r_ok:
            print("OK")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1
        time.sleep(1)

    print(f"\n{'='*65}")
    print(f"  Activated: {ok} | Failed: {fail}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
