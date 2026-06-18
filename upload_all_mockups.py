"""
NasriTools - Upload Mockups to ALL Etsy Listings
Fetches every active listing, finds matching mockup file, uploads as image #2
Run: python upload_all_mockups.py
"""
import json, os, re, time, requests
from pathlib import Path

CLIENT_ID   = "pluc0garrgcjzhim0hawxf0k"
SECRET      = "hc89hlqkd6"
SHOP_ID     = 66526082
TOKEN_FILE  = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE   = Path(os.path.expanduser("~")) / "etsy_all_mockups_done.json"
MOCKUPS_DIR = Path(os.path.expanduser("~")) / "nasri_mockups"

STOP_WORDS = {
    "google", "sheets", "template", "spreadsheet", "and", "the",
    "a", "an", "for", "to", "with", "in", "of", "your", "my",
    "free", "best", "simple", "easy", "complete",
}


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


def auth_headers(token):
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}


def fetch_all_listings(token):
    listings, offset, limit = [], 0, 100
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": limit, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(0.5)
    return listings


def title_to_slug(title):
    """'Profit Loss Tracker Google Sheets Template' → 'profit_loss_tracker'"""
    title = title.split("|")[0].strip()
    words = re.sub(r'[^a-z0-9 ]', '', title.lower()).split()
    words = [w for w in words if w not in STOP_WORDS and w]
    return "_".join(words[:5])


def find_mockup(slug):
    """Find the best matching mockup file for a given slug."""
    exact = MOCKUPS_DIR / f"{slug}_mockup.jpg"
    if exact.exists():
        return exact
    # Fuzzy: try removing last word progressively
    parts = slug.split("_")
    for n in range(len(parts) - 1, 0, -1):
        candidate = MOCKUPS_DIR / f"{'_'.join(parts[:n])}_mockup.jpg"
        if candidate.exists():
            return candidate
    return None


def upload_image(token, listing_id, img_path, rank=2):
    with open(img_path, "rb") as f:
        r = requests.post(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images",
            headers=auth_headers(token),
            files={"image": (img_path.name, f, "image/jpeg")},
            data={"rank": rank, "overwrite": "true"},
            timeout=60,
        )
    return r


def main():
    done  = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Upload Mockups to ALL Listings")
    print(f"  Already done: {len(done)}")
    print(f"{'='*65}\n")

    print("  Fetching all active listings...")
    listings = fetch_all_listings(token)
    total    = len(listings)
    print(f"  Found {total} listings\n")

    ok = 0; skipped_no_file = 0

    for i, listing in enumerate(listings, 1):
        lid   = str(listing["listing_id"])
        title = listing.get("title", "")

        if lid in done:
            print(f"[{i:03d}/{total}] SKIP (done): {title[:55]}")
            ok += 1
            continue

        slug     = title_to_slug(title)
        mockup   = find_mockup(slug)

        if not mockup:
            print(f"[{i:03d}/{total}] NO FILE ({slug}): {title[:50]}")
            skipped_no_file += 1
            continue

        print(f"[{i:03d}/{total}] {title[:55]}")
        print(f"    file: {mockup.name}")

        r = upload_image(token, lid, mockup, rank=2)
        time.sleep(1)

        if r.ok:
            ok += 1
            done[lid] = {"title": title[:60], "file": mockup.name}
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"    uploaded: OK")
        else:
            print(f"    ERROR {r.status_code}: {r.text[:120]}")

        if i % 10 == 0:
            token = get_token()

    print(f"\n{'='*65}")
    print(f"  Done: {ok}/{total} mockups uploaded")
    print(f"  No matching file: {skipped_no_file}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
