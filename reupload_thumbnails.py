"""
reupload_thumbnails.py
Re-uploads all thumbnails to the CORRECT listings by exact ID.
Use this after regenerating thumbnails with generate_thumbnails.py.
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
THUMB_DIR  = Path(__file__).parent / "thumbnails"

# EXACT mapping: thumbnail → listing ID
# Add or update IDs here if needed
UPLOAD_MAP = [
    # Hero Products (existing listings)
    ("hero_budget_tracker.png",   None, ["budget tracker", "budget & expense", "monthly budget & expense"]),
    ("hero_invoice_tracker.png",  None, ["invoice tracker", "invoice & client", "freelancer invoice"]),
    ("hero_kpi_dashboard.png",    None, ["kpi dashboard"]),
    ("hero_complete_life.png",    None, ["complete life system"]),
    ("hero_workout_tracker.png",  None, ["workout tracker google sheets template"]),
    ("hero_habit_tracker.png",    None, ["habit tracker google sheets"]),
    ("hero_weekly_planner.png",   None, ["weekly productivity system", "weekly planner google"]),
    # Finance Bundle (existing)
    ("hero_finance_bundle.png",   None, ["finance bundle google sheets"]),
    # New Premium Bundles (by ID)
    ("bundle_freelancer_kit.png",    None, ["freelancer os", "invoice + time tracking", "invoice + time"]),
    ("bundle_health_os.png",         4525136928, None),
    ("bundle_business_starter.png",  4525136952, None),
    ("bundle_productivity_os.png",   4525136964, None),
    ("hero_finance_bundle.png",      4525136892, None),  # Complete Finance OS
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

def delete_existing_images(token, lid):
    """Remove existing listing images so we can re-upload cleanly."""
    r = requests.get(f"{API}/listings/{lid}/images", headers=auth_headers(token))
    if r.ok:
        for img in r.json().get("results", []):
            img_id = img.get("listing_image_id")
            if img_id:
                requests.delete(
                    f"{API}/shops/{SHOP_ID}/listings/{lid}/images/{img_id}",
                    headers=auth_headers(token), timeout=15
                )

def upload_image(token, lid, image_path):
    with open(image_path, "rb") as f:
        r = requests.post(
            f"{API}/shops/{SHOP_ID}/listings/{lid}/images",
            headers=auth_headers(token),
            files={"image": (image_path.name, f, "image/png")},
            data={"rank": 1},
            timeout=60,
        )
    return r.ok, r.status_code, r.text[:150]

def find_listing_id(listings, keywords):
    for l in listings:
        tl = l["title"].lower()
        if any(k.lower() in tl for k in keywords):
            return l["listing_id"]
    return None

def main():
    print("=" * 65)
    print("  NasriTools — Re-Upload Thumbnails (Correct Mapping)")
    print("=" * 65)

    if not THUMB_DIR.exists():
        print(f"  thumbnails/ folder not found. Run generate_thumbnails.py first.")
        return

    token = get_token()
    listings = get_all_listings(token)
    print(f"[*] {len(listings)} active listings\n")

    ok = skip = fail = 0

    for thumb_name, fixed_id, keywords in UPLOAD_MAP:
        img_path = THUMB_DIR / thumb_name
        if not img_path.exists():
            print(f"  [MISS] {thumb_name}")
            skip += 1
            continue

        # Resolve listing ID
        if fixed_id:
            lid = fixed_id
        elif keywords:
            lid = find_listing_id(listings, keywords)
            if not lid:
                print(f"  [SKIP] {thumb_name} — no listing matched {keywords[:1]}")
                skip += 1
                continue
        else:
            skip += 1
            continue

        print(f"  [UP]  {thumb_name} → ID {lid}...", end=" ", flush=True)
        token = get_token()

        # Delete old images first
        delete_existing_images(token, lid)
        time.sleep(0.5)

        token = get_token()
        r_ok, code, text = upload_image(token, lid, img_path)
        if r_ok:
            print("OK")
            ok += 1
        else:
            print(f"FAIL ({code}) {text[:60]}")
            fail += 1
        time.sleep(1.2)

    print(f"\n{'='*65}")
    print(f"  Uploaded: {ok} | Skipped: {skip} | Failed: {fail}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
