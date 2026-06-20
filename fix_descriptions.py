"""
fix_descriptions.py
Prepends mobile warning + Make a Copy instructions to ALL active listing descriptions.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

WARNING_BLOCK = """⚠️ IMPORTANT — HOW TO ACCESS YOUR FILE
━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Works on: Desktop, Laptop, Tablet, Phone (via Google Sheets app)
📱 After purchase: Open your confirmation email on any device
🔗 Click the link in the PDF → File → Make a Copy → Done!

⚠️ NOTE: The Etsy mobile app does not show digital downloads.
Open etsy.com in your phone browser instead, go to Your Account → Purchases → Download.
━━━━━━━━━━━━━━━━━━━━━━━━━

"""

MARKER = "⚠️ IMPORTANT — HOW TO ACCESS YOUR FILE"

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
            params={"limit": 100, "offset": offset, "includes": ["description"]},
        )
        if not r.ok:
            print(f"  Error fetching listings: HTTP {r.status_code}")
            break
        data = r.json()
        results = data.get("results", [])
        listings.extend(results)
        if len(results) < 100:
            break
        offset += 100
    return listings

def update_description(token, lid, description):
    payload = {"description": description}
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode(payload),
        timeout=30,
    )
    return r.ok, r.status_code

def main():
    print("=" * 65)
    print("  NasriTools — Fix Descriptions (Mobile Warning + Make a Copy)")
    print("=" * 65)

    token = get_token()
    print("[*] Token OK")

    listings = get_all_listings(token)
    print(f"[*] Found {len(listings)} active listings\n")

    ok_count = 0
    skip_count = 0
    fail_count = 0

    for l in listings:
        lid   = l["listing_id"]
        title = l["title"][:45]
        desc  = l.get("description", "") or ""

        if MARKER in desc:
            print(f"  [SKIP] Already updated: {title[:40]}")
            skip_count += 1
            continue

        new_desc = WARNING_BLOCK + desc

        print(f"  [UPDATE] {title[:40]} ...", end=" ", flush=True)
        token = get_token()
        ok, code = update_description(token, lid, new_desc)
        if ok:
            print(f"OK (HTTP {code})")
            ok_count += 1
        else:
            print(f"FAILED (HTTP {code})")
            fail_count += 1
        time.sleep(1.5)

    print(f"\n{'='*65}")
    print(f"  Updated: {ok_count}  |  Skipped: {skip_count}  |  Failed: {fail_count}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
