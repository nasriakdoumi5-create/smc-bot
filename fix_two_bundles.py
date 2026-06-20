"""
fix_two_bundles.py
Uploads the correct thumbnail + activates the 2 remaining draft bundles by ID.
IDs from create_premium_bundles.py output:
  4525136928 = Complete Health OS
  4525136892 = Complete Finance OS
"""
import json, os, re, time, requests, urllib.parse, io
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
THUMB_DIR  = Path(__file__).parent / "thumbnails"

# Hardcoded by ID — no keyword matching needed
TARGETS = [
    {
        "listing_id": 4525136928,
        "title": "Complete Health OS",
        "thumbnail": "bundle_health_os.png",
    },
    {
        "listing_id": 4525136892,
        "title": "Complete Finance OS",
        "thumbnail": "hero_finance_bundle.png",
    },
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

def upload_image(token, lid, image_path):
    with open(image_path, "rb") as f:
        r = requests.post(
            f"{API}/shops/{SHOP_ID}/listings/{lid}/images",
            headers=auth_headers(token),
            files={"image": (image_path.name, f, "image/png")},
            data={"rank": 1},
            timeout=60,
        )
    return r.ok, r.status_code, r.text[:200]

def activate_listing(token, lid):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data="state=active",
        timeout=30,
    )
    return r.ok, r.status_code, r.text[:300]

def main():
    print("=" * 65)
    print("  NasriTools — Fix 2 Remaining Bundles (Image + Activate)")
    print("=" * 65 + "\n")

    token = get_token()
    ok = fail = 0

    for t in TARGETS:
        lid       = t["listing_id"]
        title     = t["title"]
        thumb_name = t["thumbnail"]
        thumb_path = THUMB_DIR / thumb_name

        print(f"  [{lid}] {title}")

        # Step 1: Upload image
        if not thumb_path.exists():
            print(f"    → ERROR: {thumb_path} not found — run generate_thumbnails.py first")
            fail += 1
            continue

        print(f"    → Uploading {thumb_name}...", end=" ", flush=True)
        token = get_token()
        i_ok, i_code, i_text = upload_image(token, lid, thumb_path)
        if i_ok:
            print("OK")
        else:
            print(f"FAIL ({i_code}) — {i_text[:80]}")
        time.sleep(2)

        # Step 2: Activate
        print(f"    → Activating...", end=" ", flush=True)
        token = get_token()
        a_ok, a_code, a_text = activate_listing(token, lid)
        if a_ok:
            print("OK ✓ — LIVE")
            ok += 1
        else:
            print(f"FAIL ({a_code})")
            print(f"       {a_text[:150]}")
            fail += 1
        time.sleep(2)
        print()

    print(f"{'='*65}")
    print(f"  Activated: {ok} | Failed: {fail}")
    if ok == 2:
        print(f"\n  All 5 bundles are now LIVE on nasritools.etsy.com!")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
