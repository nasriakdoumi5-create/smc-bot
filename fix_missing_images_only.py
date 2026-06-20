"""
fix_missing_images_only.py
Step 5 standalone — finds listings with 0 images and uploads from thumbnails/all/.
Has retry logic for network interruptions.
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
ALL_DIR    = Path("thumbnails/all")

def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at",0)-60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token",data={
            "grant_type":"refresh_token","client_id":CLIENT_ID,
            "refresh_token":t["refresh_token"]})
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time()+t.get("expires_in",3600)-60
        TOKEN_FILE.write_text(json.dumps(t,indent=2))
    return t

def auth_headers(token):
    return {"Authorization":"Bearer "+token["access_token"],
            "x-api-key":CLIENT_ID+":"+SECRET}

def api_get(token, url, **kwargs):
    """GET with 3 retries on connection error."""
    for attempt in range(3):
        try:
            return requests.get(url, headers=auth_headers(token), timeout=30, **kwargs)
        except requests.exceptions.ConnectionError:
            if attempt < 2:
                wait = (attempt+1)*4
                print(f"  [retry in {wait}s]", end=" ", flush=True)
                time.sleep(wait)
            else:
                raise

def api_post_file(token, url, img_path):
    """POST with 3 retries on connection error."""
    for attempt in range(3):
        try:
            with open(img_path,"rb") as f:
                return requests.post(url, headers=auth_headers(token),
                                     files={"image":(img_path.name,f,"image/png")},
                                     data={"rank":1}, timeout=60)
        except requests.exceptions.ConnectionError:
            if attempt < 2:
                wait = (attempt+1)*5
                print(f"  [retry in {wait}s]", end=" ", flush=True)
                time.sleep(wait)
            else:
                raise

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = api_get(token, f"{API}/shops/{SHOP_ID}/listings/active",
                    params={"limit":100,"offset":offset})
        if not r.ok: break
        results = r.json().get("results",[])
        listings.extend(results)
        if len(results)<100: break
        offset+=100
        time.sleep(0.5)
    return listings

def main():
    print("="*65)
    print("  NasriTools — Fix Missing 1st Images (Step 5 standalone)")
    print("="*65)

    if not ALL_DIR.exists():
        print(f"  ERROR: {ALL_DIR} not found. Run generate_all_thumbnails.py first.")
        return

    token    = get_token()
    listings = get_all_listings(token)
    print(f"[*] {len(listings)} active listings\n")

    ok = skip = fail = miss = 0

    for idx, l in enumerate(listings,1):
        lid = l["listing_id"]
        print(f"  [{idx:3}/{len(listings)}] {l['title'][:42]}...", end=" ", flush=True)

        # Check image count
        try:
            token = get_token()
            r = api_get(token, f"{API}/listings/{lid}/images")
            imgs = r.json().get("results",[]) if r.ok else []
        except Exception as e:
            print(f"CHECK-ERR ({e})")
            fail += 1
            time.sleep(2)
            continue

        if imgs:
            print(f"has {len(imgs)} image(s) — skip")
            skip += 1
            time.sleep(0.2)
            continue

        # Missing image — try to upload
        img_path = ALL_DIR / f"listing_{lid}.png"
        if not img_path.exists():
            print(f"no thumbnail file — skip")
            miss += 1
            continue

        print(f"MISSING → uploading...", end=" ", flush=True)
        try:
            token = get_token()
            r = api_post_file(token, f"{API}/shops/{SHOP_ID}/listings/{lid}/images", img_path)
            if r.ok:
                print("OK ✅")
                ok += 1
            else:
                print(f"FAIL ({r.status_code})")
                fail += 1
        except Exception as e:
            print(f"ERR ({e})")
            fail += 1
        time.sleep(1.5)

    print(f"\n{'='*65}")
    print(f"  Fixed: {ok} | Already had images: {skip} | No file: {miss} | Failed: {fail}")
    print(f"{'='*65}")

if __name__=="__main__":
    main()
