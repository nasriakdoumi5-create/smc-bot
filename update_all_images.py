"""
update_all_images.py
Replaces the MAIN image (rank 1) on every live listing with the new
browser-rendered hero design.

Matching: reads each listing's xlsx filename to find its slug
(same method as update_all_files.py), cached in files_updated.json.

Run:  python update_all_images.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
OUTPUT     = Path(__file__).parent / "output"
MAP_FILE   = Path(__file__).parent / "files_updated.json"   # listing_id -> slug
DONE_FILE  = Path(__file__).parent / "images_updated.json"

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
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset}, timeout=30)
        if not r.ok:
            print(f"  Error: {r.status_code} {r.text[:200]}")
            break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings

def slug_for(lid, token, cache):
    if str(lid) in cache:
        return cache[str(lid)]
    r = requests.get(f"{API}/shops/{SHOP_ID}/listings/{lid}/files",
                     headers=auth_headers(token), timeout=30)
    if not r.ok:
        return None
    files = r.json().get("results", [])
    xlsx = next((f for f in files if f.get("filename", "").endswith(".xlsx")), None)
    if not xlsx:
        return None
    slug = xlsx["filename"][:-5]
    cache[str(lid)] = slug
    MAP_FILE.write_text(json.dumps(cache, indent=2))
    time.sleep(0.4)
    return slug

def main():
    print("=" * 65)
    print("  NasriTools — Replace main image on ALL listings")
    print("=" * 65)

    cache = json.loads(MAP_FILE.read_text()) if MAP_FILE.exists() else {}
    done  = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}

    token    = get_token()
    listings = get_all_listings(token)
    total    = len(listings)
    print(f"[*] {total} listings found\n")

    updated = skipped = failed = nomatch = 0

    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        title = l.get("title", "")[:38]

        if str(lid) in done:
            skipped += 1
            print(f"  [{idx:3}/{total}] SKIP (done) {title}")
            continue

        token = get_token()
        slug  = slug_for(lid, token, cache)
        hero  = OUTPUT / slug / f"{slug}_01_hero.jpg" if slug else None

        if not slug or not hero.exists():
            print(f"  [{idx:3}/{total}] — no hero for {slug or '?'} | {title}")
            nomatch += 1
            continue

        print(f"  [{idx:3}/{total}] {slug:35}", end=" ", flush=True)

        with open(hero, "rb") as fh:
            r = requests.post(
                f"{API}/shops/{SHOP_ID}/listings/{lid}/images",
                headers=auth_headers(token),
                files={"image": (hero.name, fh, "image/jpeg")},
                data={"rank": 1, "overwrite": "true"},
                timeout=120,
            )
        if r.ok:
            print("✓")
            updated += 1
            done[str(lid)] = slug
            DONE_FILE.write_text(json.dumps(done, indent=2))
        else:
            print(f"✗ {r.status_code}: {r.text[:80]}")
            failed += 1

        time.sleep(0.8)

    print(f"\n{'=' * 65}")
    print(f"  Updated  : {updated}")
    print(f"  Skipped  : {skipped} (already done — safe to re-run)")
    print(f"  No match : {nomatch}")
    print(f"  Failed   : {failed}")
    print(f"{'=' * 65}")
    if failed:
        print("  Re-run the script — it continues where it stopped.")

if __name__ == "__main__":
    main()
