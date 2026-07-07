"""
delete_empty_listings.py
Deactivates the 3 listings that have no download files.
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

TO_DELETE = [
    (4525136916, "Invoice Tracker Bundle Google Sheets"),
    (4525136952, "KPI Dashboard Bundle Google Sheets"),
    (4525136964, "Weekly Planner Bundle Google Sheets"),
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

def deactivate_listing(token, lid):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token),
                 "Content-Type": "application/x-www-form-urlencoded"},
        data="state=inactive",
        timeout=30,
    )
    return r.ok, r.status_code

def main():
    print("=" * 55)
    print("  Deactivating 3 listings with no files")
    print("=" * 55)

    token = get_token()

    for lid, title in TO_DELETE:
        print(f"\n  [{lid}] {title[:45]}")
        print(f"  Deactivating...", end=" ", flush=True)
        ok, code = deactivate_listing(token, lid)
        if ok:
            print(f"DEACTIVATED ✓")
        else:
            print(f"FAILED ({code})")
        time.sleep(1)

    print(f"\n{'=' * 55}")
    print("  Done — listings hidden from store.")

if __name__ == "__main__":
    main()
