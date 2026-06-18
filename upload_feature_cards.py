"""
NasriTools - Upload Feature Card Images to Etsy Listings
Adds feature card as image #3 for each of the 10 top products
Run: python upload_feature_cards.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID   = "pluc0garrgcjzhim0hawxf0k"
SECRET      = "hc89hlqkd6"
SHOP_ID     = 66526082
TOKEN_FILE  = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE    = Path(os.path.expanduser("~")) / "etsy_published.json"
DONE_FILE   = Path(os.path.expanduser("~")) / "etsy_features_uploaded.json"
CARDS_DIR   = Path(os.path.expanduser("~")) / "nasri_feature_cards"

PRODUCTS = [
    "budget_tracker", "habit_tracker", "meal_planner", "wedding_planner",
    "workout_tracker", "content_creator_planner", "freelancer_invoice_tracker",
    "student_planner", "goals_planner", "weekly_planner",
]

def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0):
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def etsy_headers(t):
    return {"Authorization": "Bearer " + t["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}

def upload_image(token, listing_id, img_path, rank=3):
    with open(img_path, "rb") as f:
        r = requests.post(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images",
            headers=etsy_headers(token),
            files={"image": (img_path.name, f, "image/jpeg")},
            data={"rank": rank, "overwrite": "true"},
            timeout=60,
        )
    return r

def main():
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    done      = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    token     = get_token()
    total     = len(PRODUCTS)

    print(f"\n{'='*60}")
    print(f"  NasriTools - Upload Feature Cards  [{total} products]")
    print(f"  Already done: {len(done)}")
    print(f"{'='*60}\n")

    ok = 0
    for i, slug in enumerate(PRODUCTS, 1):
        if slug in done:
            print(f"[{i:02d}/{total}] SKIP (done): {slug}"); ok += 1; continue

        lid = published.get(slug)
        if not lid:
            print(f"[{i:02d}/{total}] SKIP (no listing ID): {slug}"); continue

        card_path = CARDS_DIR / f"{slug}_features.jpg"
        if not card_path.exists():
            print(f"[{i:02d}/{total}] SKIP (card not found): {card_path.name}"); continue

        print(f"[{i:02d}/{total}] {slug}  (listing {lid})")
        r = upload_image(token, lid, card_path, rank=3)
        time.sleep(1)

        if r.ok:
            ok += 1; done[slug] = lid
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"    uploaded: OK")
        else:
            print(f"    ERROR {r.status_code}: {r.text[:120]}")

        if i % 5 == 0:
            token = get_token()

    print(f"\n{'='*60}")
    print(f"  Done: {ok}/{total} feature cards uploaded to Etsy")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
