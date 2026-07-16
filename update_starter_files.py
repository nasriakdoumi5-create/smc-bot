"""
update_starter_files.py
Replaces the xlsx on the LIVE Starter Budget Tracker listing
with the new quality version (v2).
Run:  python update_starter_files.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
LISTING_ID = 4538866889
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

SLUG   = "starter_budget_tracker"
FOLDER = Path(__file__).parent / "output" / SLUG
XLSX   = FOLDER / f"{SLUG}.xlsx"

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

def main():
    print("=" * 60)
    print("  Replacing xlsx on listing", LISTING_ID)
    print("=" * 60)
    token = get_token()

    # 1. List current files
    r = requests.get(f"{API}/shops/{SHOP_ID}/listings/{LISTING_ID}/files",
                     headers=auth_headers(token), timeout=30)
    if not r.ok:
        print(f"  ✗ list files: {r.status_code} {r.text[:200]}")
        return
    files = r.json().get("results", [])
    for f in files:
        print(f"  found: {f.get('filename')} (id {f.get('listing_file_id')})")

    # 2. Delete the old xlsx
    for f in files:
        if f.get("filename", "").endswith(".xlsx"):
            fid = f["listing_file_id"]
            r = requests.delete(
                f"{API}/shops/{SHOP_ID}/listings/{LISTING_ID}/files/{fid}",
                headers=auth_headers(token), timeout=30)
            print(f"  {'✓ deleted' if r.ok else '✗ delete failed'} {f['filename']}"
                  + ("" if r.ok else f" ({r.status_code}: {r.text[:120]})"))
            time.sleep(0.5)

    # 3. Upload the new xlsx
    with open(XLSX, "rb") as fh:
        r = requests.post(
            f"{API}/shops/{SHOP_ID}/listings/{LISTING_ID}/files",
            headers=auth_headers(token),
            files={"file": (XLSX.name, fh,
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"name": XLSX.name, "rank": 1},
            timeout=120,
        )
    if r.ok:
        print(f"  ✓ uploaded new {XLSX.name} ({XLSX.stat().st_size:,} bytes)")
        print(f"\n  Done → https://www.etsy.com/listing/{LISTING_ID}")
    else:
        print(f"  ✗ upload: {r.status_code} {r.text[:200]}")
    print("=" * 60)

if __name__ == "__main__":
    main()
