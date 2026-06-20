"""
assign_finance_bundles.py
Assigns Finance and Bundle listings to their existing sections.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

FINANCE_KEYWORDS = [
    "budget", "expense", "invoice", "finance", "profit", "debt", "cash flow",
    "tax", "financial", "revenue", "payoff", "nonprofit", "church budget",
    "emergency fund", "small business finance", "freelancer invoice",
    "freelance business", "startup financial"
]
BUNDLE_KEYWORDS = ["bundle", "complete life"]

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
    return {"Authorization": "Bearer " + token["access_token"], "x-api-key": CLIENT_ID + ":" + SECRET}

def get_sections(token):
    r = requests.get(f"{API}/shops/{SHOP_ID}/sections", headers=auth_headers(token))
    if r.ok:
        secs = r.json().get("results", [])
        print("  All sections:")
        for s in secs:
            print(f"    [{s['shop_section_id']}] {s['title']}")
        return {s["title"]: s["shop_section_id"] for s in secs}
    return {}

def assign_listing(token, lid, section_id):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=f"shop_section_id={section_id}", timeout=30,
    )
    return r.ok, r.status_code

def get_all_listings(token):
    listings = []
    offset = 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token), params={"limit": 100, "offset": offset})
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100
    return listings

def matches(title_lower, keywords):
    return any(kw in title_lower for kw in keywords)

def main():
    print("=" * 65)
    print("  NasriTools — Assign Finance & Bundle Listings to Sections")
    print("=" * 65)

    token = get_token()
    sections = get_sections(token)

    # Find the right section IDs
    finance_id = None
    bundle_id  = None
    for title, sid in sections.items():
        tl = title.lower()
        if "budget" in tl or "finance" in tl:
            finance_id = sid
        if "bundle" in tl:
            bundle_id = sid

    print(f"\n  Finance section ID: {finance_id}")
    print(f"  Bundle section ID:  {bundle_id}\n")

    if not finance_id and not bundle_id:
        print("  No matching sections found.")
        return

    listings = get_all_listings(token)
    print(f"  Found {len(listings)} listings\n")

    ok = fail = skip = 0
    for l in listings:
        lid   = l["listing_id"]
        title = l["title"]
        tl    = title.lower()

        if bundle_id and matches(tl, BUNDLE_KEYWORDS):
            sid = bundle_id
            label = "Bundle"
        elif finance_id and matches(tl, FINANCE_KEYWORDS):
            sid = finance_id
            label = "Finance"
        else:
            skip += 1
            continue

        print(f"  [{label:7}] {title[:45]} ...", end=" ", flush=True)
        token = get_token()
        r_ok, code = assign_listing(token, lid, sid)
        if r_ok:
            print("OK")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1
        time.sleep(0.8)

    print(f"\n{'='*65}")
    print(f"  Assigned: {ok} | Skipped: {skip} | Failed: {fail}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
