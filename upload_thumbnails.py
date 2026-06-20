"""
upload_thumbnails.py
Uploads generated thumbnails to matching Etsy listings automatically.
Matches thumbnail filename to listing title keyword.
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
THUMB_DIR  = Path(__file__).parent / "thumbnails"

# thumbnail filename → keywords to match in listing title
THUMB_MAP = {
    "hero_budget_tracker.png":      ["budget tracker", "budget & expense", "budget spreadsheet"],
    "hero_invoice_tracker.png":     ["invoice tracker", "invoice & client", "freelancer invoice"],
    "hero_kpi_dashboard.png":       ["kpi dashboard"],
    "hero_complete_life.png":       ["complete life system", "all 10 templa"],
    "hero_finance_bundle.png":      ["finance bundle", "finance os", "budget + invoice"],
    "hero_workout_tracker.png":     ["workout tracker", "workout & fitness"],
    "hero_habit_tracker.png":       ["habit tracker", "30-day habit"],
    "hero_weekly_planner.png":      ["weekly planner", "weekly productivity"],
    "bundle_freelancer_kit.png":    ["freelancer os", "invoice + time", "freelancer complete"],
    "bundle_health_os.png":         ["complete health os", "workout + meal"],
    "bundle_business_starter.png":  ["business starter kit", "kpi dashboard + sales"],
    "bundle_productivity_os.png":   ["productivity os", "weekly planner + goals"],
}

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
    # Active listings
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset})
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100
    # Draft listings
    offset = 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset, "state": "draft"})
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100
    return listings

def match_listing(title_lower, keywords):
    return any(k in title_lower for k in keywords)

def upload_image(token, lid, image_path, rank=1):
    with open(image_path, "rb") as f:
        r = requests.post(
            f"{API}/shops/{SHOP_ID}/listings/{lid}/images",
            headers=auth_headers(token),
            files={"image": (image_path.name, f, "image/png")},
            data={"rank": rank},
            timeout=60,
        )
    return r.ok, r.status_code

def main():
    print("=" * 65)
    print("  NasriTools — Auto Upload Thumbnails to Etsy")
    print("=" * 65)

    if not THUMB_DIR.exists():
        print(f"  [ERR] thumbnails/ folder not found.")
        print(f"        Run: python generate_thumbnails.py first")
        return

    available = {f.name: f for f in THUMB_DIR.glob("*.png")}
    print(f"[*] Found {len(available)} thumbnails in {THUMB_DIR}\n")

    token = get_token()
    listings = get_all_listings(token)
    print(f"[*] Found {len(listings)} listings (active + draft)\n")

    ok = skip = fail = 0

    for thumb_name, keywords in THUMB_MAP.items():
        if thumb_name not in available:
            print(f"  [MISS] {thumb_name} — not found in thumbnails/")
            skip += 1
            continue

        # Find matching listing
        matched = None
        for l in listings:
            if match_listing(l["title"].lower(), keywords):
                matched = l
                break

        if not matched:
            print(f"  [SKIP] {thumb_name} — no listing matched keywords: {keywords[:2]}")
            skip += 1
            continue

        lid   = matched["listing_id"]
        title = matched["title"]
        img_path = available[thumb_name]

        print(f"  [UP]   {thumb_name} → {title[:40]}...", end=" ", flush=True)
        token = get_token()
        r_ok, code = upload_image(token, lid, img_path, rank=1)
        if r_ok:
            print("OK")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1
        time.sleep(1.5)

    print(f"\n{'='*65}")
    print(f"  Uploaded: {ok} | Skipped: {skip} | Failed: {fail}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
