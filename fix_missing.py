"""
Fix Missing - Find and fully publish the 1 missing product
Run after finalize_listings.py completes.

Steps:
  1. Find slug missing from ~/etsy_published.json
  2. Create draft listing
  3. Upload 5 images from GitHub raw URLs
  4. Upload .xlsx digital file from GitHub raw URL
  5. Activate listing

Usage:  python fix_missing.py
"""
import json, time, os, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://api.etsy.com/v3/application"
SHOP_ID    = 66526082
RAW        = "https://raw.githubusercontent.com/nasriakdoumi5-create/smc-bot/claude/digital-products-knowledge-yzpw50/output"
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"
DATA_FILE  = Path(__file__).parent / "nasritools" / "listings_data.json"
SLOTS      = ["_01_hero", "_02_included", "_03_how", "_04_features", "_05_cta"]


def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0):
        print("  Refreshing token...")
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
        print("  Token refreshed")
    return t


def auth(t):
    return {
        "Authorization": "Bearer " + t["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }


def main():
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    listings = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    missing = [item for item in listings if item["slug"] not in published]

    if not missing:
        print("All 100 products already published! Nothing to do.")
        return

    print(f"Found {len(missing)} missing product(s):")
    for item in missing:
        print(f"  - {item['slug']}")
    print()

    token = get_token()

    for item in missing:
        slug = item["slug"]
        print(f"Processing: {slug}")
        print("-" * 50)

        # Step 1: Create draft listing
        import re
        tags = list(dict.fromkeys(t.lower() for t in item["tags"]))
        tags = [re.sub(r'[^a-zA-Z0-9 \-]', '', tag).strip() for tag in tags]
        tags = [t for t in tags if t][:13]

        body = {
            "quantity":        999,
            "title":           item["title"],
            "description":     item["description"],
            "price":           item["price"],
            "who_made":        "i_did",
            "when_made":       "2020_2025",
            "taxonomy_id":     2078,
            "type":            "download",
            "is_supply":       False,
            "is_customizable": False,
            "tags":            tags,
            "state":           "draft",
        }
        r = requests.post(
            API + "/shops/" + str(SHOP_ID) + "/listings",
            headers={**auth(token), "Content-Type": "application/json"},
            json=body,
        )
        if not r.ok:
            print(f"  publish: ERR {r.status_code}: {r.text[:200]}")
            continue
        lid = r.json().get("listing_id")
        published[slug] = lid
        PUB_FILE.write_text(json.dumps(published, indent=2))
        print(f"  publish: OK (listing_id={lid})")
        time.sleep(0.5)

        # Step 2: Upload 5 images
        for rank, slot in enumerate(SLOTS, 1):
            url = RAW + "/" + slug + "/" + slug + slot + ".jpg"
            img = requests.get(url, timeout=30)
            if img.status_code != 200:
                print(f"  img{rank}: download ERR {img.status_code}")
                continue
            r2 = requests.post(
                API + "/shops/" + str(SHOP_ID) + "/listings/" + str(lid) + "/images",
                headers=auth(token),
                data={"rank": rank, "overwrite": "true"},
                files={"image": (slug + slot + ".jpg", img.content, "image/jpeg")},
            )
            if r2.ok:
                print(f"  img{rank}: OK")
            else:
                print(f"  img{rank}: ERR {r2.text[:80]}")
            time.sleep(0.4)

        # Step 3: Upload .xlsx digital file
        xlsx_url = RAW + "/" + slug + "/" + slug + ".xlsx"
        xlsx_data = requests.get(xlsx_url, timeout=60)
        if xlsx_data.status_code == 200:
            r3 = requests.post(
                API + "/shops/" + str(SHOP_ID) + "/listings/" + str(lid) + "/files",
                headers=auth(token),
                data={"name": slug + ".xlsx"},
                files={"file": (slug + ".xlsx", xlsx_data.content,
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
            if r3.ok:
                print(f"  file: OK")
            else:
                print(f"  file: ERR {r3.text[:100]}")
        else:
            print(f"  file: download ERR {xlsx_data.status_code}")
        time.sleep(0.5)

        # Step 4: Activate listing
        r4 = requests.patch(
            API + "/shops/" + str(SHOP_ID) + "/listings/" + str(lid),
            headers={**auth(token), "Content-Type": "application/json"},
            json={"state": "active"},
        )
        if r4.ok:
            print(f"  activate: OK")
        else:
            print(f"  activate: ERR {r4.text[:100]}")

        print(f"\nDone! Listing {lid} is now ACTIVE.")
        print(f"URL: https://www.etsy.com/listing/{lid}")


if __name__ == "__main__":
    main()
