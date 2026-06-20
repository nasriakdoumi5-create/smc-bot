"""
fix_missing_sections.py
Creates Finance & Budget and Bundles sections and assigns missing listings.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

FINANCE_KEYWORDS = [
    "budget", "expense", "invoice", "finance", "money", "profit",
    "debt", "cash flow", "tax", "financial", "revenue", "payoff",
    "startup financial", "nonprofit", "church budget", "emergency fund",
    "small business finance", "freelancer invoice", "freelance business"
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
        return {s["title"]: s["shop_section_id"] for s in r.json().get("results", [])}
    return {}

def create_section(token, title):
    r = requests.post(
        f"{API}/shops/{SHOP_ID}/sections",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode({"title": title}), timeout=30,
    )
    if r.ok:
        return r.json().get("shop_section_id")
    print(f"  Create failed: {r.status_code} {r.text[:120]}")
    return None

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
    print("  NasriTools — Fix Missing Sections (Finance + Bundles)")
    print("=" * 65)

    token = get_token()
    sections = get_sections(token)
    print(f"[*] Existing sections: {list(sections.keys())}\n")

    # Create missing sections
    needed = {
        "Finance and Budget": FINANCE_KEYWORDS,
        "Bundles Save Up to 65": BUNDLE_KEYWORDS,
    }

    section_ids = {}
    for title, kws in needed.items():
        if title in sections:
            section_ids[title] = sections[title]
            print(f"  [EXISTS] {title}")
        else:
            token = get_token()
            sid = create_section(token, title)
            if sid:
                section_ids[title] = sid
                print(f"  [CREATED] {title} (id={sid})")
            else:
                print(f"  [FAILED] Could not create: {title}")
            time.sleep(1)

    if not section_ids:
        print("\nNo sections could be created. Check API permissions.")
        return

    # Assign listings
    print(f"\n[*] Assigning listings to {len(section_ids)} sections...")
    token = get_token()
    listings = get_all_listings(token)

    finance_id = section_ids.get("Finance and Budget")
    bundle_id  = section_ids.get("Bundles Save Up to 65")

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

        print(f"  [{label}] {title[:45]} ...", end=" ", flush=True)
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
