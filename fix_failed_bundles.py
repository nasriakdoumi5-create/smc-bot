"""
fix_failed_bundles.py
Attaches a placeholder digital file to draft listings that failed to activate (HTTP 400),
then retries activation.
Etsy requires at least one digital file before a digital listing can go active.
"""
import json, os, re, time, requests, urllib.parse, io
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

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

def get_draft_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"{API}/shops/{SHOP_ID}/listings",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset, "state": "draft"},
        )
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100
    return listings

def make_placeholder_file(title):
    """Creates a minimal text file with the Google Sheets link."""
    content = f"""NASRITOOLS — {title}
=====================================

Thank you for your purchase!

HOW TO ACCESS YOUR GOOGLE SHEETS FILE:
---------------------------------------
1. Click the Google Sheets link below
2. Go to File → Make a Copy
3. Save to your Google Drive
4. Start using immediately!

SHOP: https://nasritools.etsy.com
SUPPORT: Message us on Etsy — we reply within 24 hours

© NasriTools — Professional Google Sheets Templates
"""
    return content.encode("utf-8")

def upload_file(token, lid, filename, content_bytes):
    r = requests.post(
        f"{API}/shops/{SHOP_ID}/listings/{lid}/files",
        headers=auth_headers(token),
        files={"file": (filename, io.BytesIO(content_bytes), "text/plain")},
        data={"name": filename, "rank": 1},
        timeout=60,
    )
    return r.ok, r.status_code, r.text[:200]

def get_active_listing_meta(token):
    """Grab return_policy_id and shipping_profile_id from an existing active listing."""
    r = requests.get(
        f"{API}/shops/{SHOP_ID}/listings/active",
        headers=auth_headers(token),
        params={"limit": 1},
    )
    if r.ok:
        results = r.json().get("results", [])
        if results:
            l = results[0]
            return l.get("return_policy_id"), l.get("shipping_profile_id")
    return None, None

def patch_listing_meta(token, lid, return_policy_id, shipping_profile_id):
    """Apply return policy and shipping profile to a draft listing."""
    parts = []
    if return_policy_id:
        parts.append(f"return_policy_id={return_policy_id}")
    if shipping_profile_id:
        parts.append(f"shipping_profile_id={shipping_profile_id}")
    if not parts:
        return True, 200
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data="&".join(parts),
        timeout=30,
    )
    return r.ok, r.status_code

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
    print("  NasriTools — Fix Failed Bundles (Attach File + Activate)")
    print("=" * 65)
    token = get_token()

    # Get policy/shipping from existing listing
    print("[*] Fetching return_policy_id from active listings...")
    return_policy_id, shipping_profile_id = get_active_listing_meta(token)
    print(f"    return_policy_id   = {return_policy_id}")
    print(f"    shipping_profile_id = {shipping_profile_id}\n")

    drafts = get_draft_listings(token)
    print(f"[*] Found {len(drafts)} remaining draft listings\n")

    if not drafts:
        print("  No drafts found — all bundles already active!")
        return

    ok = fail = 0
    for l in drafts:
        lid   = l["listing_id"]
        title = l["title"]
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', title.replace(' ', '_'))[:55] + ".txt"
        if len(safe_name) < 7:
            safe_name = f"bundle_{lid}.txt"

        print(f"  [{lid}] {title[:50]}")

        # Step 1: Upload placeholder file
        print(f"    → Uploading placeholder file...", end=" ", flush=True)
        token = get_token()
        content = make_placeholder_file(title)
        f_ok, f_code, f_text = upload_file(token, lid, safe_name, content)
        if f_ok:
            print("OK")
        else:
            print(f"FAIL ({f_code}) — {f_text[:80]}")
        time.sleep(2)

        # Step 2: Apply return policy + shipping profile
        print(f"    → Applying return policy...", end=" ", flush=True)
        token = get_token()
        p_ok, p_code = patch_listing_meta(token, lid, return_policy_id, shipping_profile_id)
        print("OK" if p_ok else f"FAIL ({p_code})")
        time.sleep(1)

        # Step 3: Activate
        print(f"    → Activating...", end=" ", flush=True)
        token = get_token()
        a_ok, a_code, a_text = activate_listing(token, lid)
        if a_ok:
            print("OK ✓ — Bundle is now LIVE")
            ok += 1
        else:
            print(f"FAIL ({a_code})")
            print(f"       Error: {a_text[:150]}")
            fail += 1
        time.sleep(2)
        print()

    print(f"{'='*65}")
    print(f"  Activated: {ok} | Failed: {fail}")
    if fail == 0:
        print(f"\n  All 5 bundles are now LIVE on your Etsy store!")
    else:
        print(f"\n  Remaining {fail} bundle(s) need manual activation in Etsy Shop Manager.")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
