"""
delete_all_listings.py
Deletes EVERY listing in the shop (active, inactive, draft, expired) so you
can relaunch with a clean, focused catalogue.

⚠️  PERMANENT. Deleted listings cannot be recovered.
    Listing fees already charged are NOT refunded.

Safety: you must type  DELETE ALL  to proceed.
Progress is saved to deleted_listings.json — safe to re-run if interrupted.

Run:  python delete_all_listings.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
LOG_FILE   = Path(__file__).parent / "deleted_listings.json"

STATES = ["active", "inactive", "draft", "expired", "sold_out"]

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

def fetch_state(token, state):
    out, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings",
                         headers=auth_headers(token),
                         params={"state": state, "limit": 100, "offset": offset},
                         timeout=30)
        if not r.ok:
            if r.status_code != 404:
                print(f"    ({state}: {r.status_code})")
            break
        batch = r.json().get("results", [])
        out.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
        time.sleep(0.4)
    return out

def main():
    print("=" * 62)
    print("  NasriTools — DELETE ALL LISTINGS")
    print("=" * 62)

    token = get_token()

    print("\n  Scanning the shop...")
    all_listings, seen = [], set()
    for state in STATES:
        found = fetch_state(token, state)
        new = [l for l in found if l["listing_id"] not in seen]
        for l in new:
            seen.add(l["listing_id"])
        all_listings.extend(new)
        print(f"    {state:10} {len(found):4}")
        time.sleep(0.3)

    total = len(all_listings)
    if total == 0:
        print("\n  Shop is already empty — nothing to delete.")
        return

    print(f"\n  TOTAL TO DELETE: {total} listings")
    print("\n  ⚠️  This is PERMANENT. Listings cannot be recovered.")
    print("     Listing fees already charged are NOT refunded.")
    print("     (If you only want them hidden, they are already inactive —")
    print("      inactive listings cost nothing and can be reactivated.)")
    print("\n  Type exactly:  DELETE ALL")
    answer = input("  > ").strip()

    if answer != "DELETE ALL":
        print("\n  Cancelled — nothing was deleted.")
        return

    done = json.loads(LOG_FILE.read_text()) if LOG_FILE.exists() else {}
    ok = failed = skipped = 0

    print()
    for i, l in enumerate(all_listings, 1):
        lid   = l["listing_id"]
        title = l.get("title", "")[:44]

        if str(lid) in done:
            skipped += 1
            continue

        token = get_token()
        r = requests.delete(f"{API}/listings/{lid}",
                            headers=auth_headers(token), timeout=30)
        if r.ok or r.status_code == 404:
            print(f"  [{i:3}/{total}] ✓ {title}")
            done[str(lid)] = title
            LOG_FILE.write_text(json.dumps(done, indent=2, ensure_ascii=False))
            ok += 1
        else:
            print(f"  [{i:3}/{total}] ✗ {r.status_code} {title}")
            failed += 1
        time.sleep(0.6)

    print(f"\n{'=' * 62}")
    print(f"  Deleted : {ok}")
    print(f"  Skipped : {skipped} (already done)")
    print(f"  Failed  : {failed}")
    print(f"{'=' * 62}")
    if failed:
        print("  Re-run to retry the failures — progress is saved.")
    else:
        print("  Shop is clean. Next:  python publish_premium.py")

if __name__ == "__main__":
    main()
