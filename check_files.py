"""
check_files.py
Read-only inventory: what does the buyer ACTUALLY receive
on every listing? Lists file names/types per listing.
Run:  python check_files.py
"""
import json, os, time, requests
from pathlib import Path
from collections import Counter

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
OUT_FILE   = Path(__file__).parent / "files_inventory.json"

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
            print(f"  Error: {r.status_code}")
            break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings

def main():
    print("=" * 70)
    print("  NasriTools — File Inventory (read-only)")
    print("=" * 70)

    token    = get_token()
    listings = get_all_listings(token)
    total    = len(listings)
    print(f"[*] {total} listings\n")

    inventory = {}
    ext_counter = Counter()
    empty = []

    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        title = l.get("title", "")

        token = get_token()
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/{lid}/files",
                         headers=auth_headers(token), timeout=30)
        files = r.json().get("results", []) if r.ok else []
        names = [f.get("filename", "?") for f in files]
        sizes = [f.get("size", 0) for f in files]

        inventory[str(lid)] = {"title": title, "files": names, "sizes": sizes}
        for n in names:
            ext = n.rsplit(".", 1)[-1].lower() if "." in n else "none"
            ext_counter[ext] += 1
        if not names:
            empty.append(title[:60])

        flist = ", ".join(f"{n} ({s//1024}KB)" for n, s in zip(names, sizes)) or "❌ NO FILES"
        print(f"  [{idx:3}/{total}] {title[:42]:44} → {flist[:70]}")
        time.sleep(0.4)

    OUT_FILE.write_text(json.dumps(inventory, indent=2, ensure_ascii=False))

    print(f"\n{'=' * 70}")
    print("  File types across all listings:")
    for ext, n in ext_counter.most_common():
        print(f"    .{ext:6} × {n}")
    print(f"\n  Listings with NO files at all: {len(empty)}")
    for t in empty[:15]:
        print(f"    ❌ {t}")
    print(f"\n  Full details saved → files_inventory.json")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    main()
