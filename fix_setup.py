"""
fix_setup.py
Fixes two errors from setup_shop_complete.py:
  1. Sections: renames existing sections instead of creating new ones (bypasses limit)
  2. Sale message: uses correct field name
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

TARGET_SECTIONS = [
    ("Finance & Budget",  ["budget","finance","expense","cash","debt","savings","income","stock","trading"]),
    ("Business & KPIs",   ["kpi","dashboard","business","sales","marketing","crm","employee","hr","project","inventory","restaurant","etsy shop","real estate","va tracker","pod"]),
    ("Freelancer Tools",  ["invoice","freelancer","billing","time track","client","content planner","social media","job application","freelance"]),
    ("Health & Fitness",  ["workout","fitness","health","meal","weight","sleep","habit","calories","exercise","nutrition","mental health","water","pet"]),
    ("Planners & Goals",  ["planner","productivity","goal","weekly","daily","schedule","task","study","life","journal","routine","focus","event","car"]),
    ("Bundles & Systems", ["bundle","complete","system","os","starter kit","all-in-one","collection","mega","pack"]),
]

SALE_MESSAGE = """Thank you for your purchase!

HOW TO GET STARTED (2 minutes):
1. Download your file from this order page
2. Go to sheets.google.com
3. File → Import → Upload → select your file
4. Customize categories to match your life — done!

NEED HELP?
Message us on Etsy — we reply within 24 hours.
Happy to help with any customization.

LOVING IT?
A quick review helps us grow and helps other buyers.
It takes 30 seconds and means everything to a small shop.

More templates: nasritools.etsy.com
Use code WELCOME10 for 10% off your next order.

© NasriTools — Professional Google Sheets Templates"""


def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"]})
        r.raise_for_status(); t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def auth_headers(token):
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                        headers=auth_headers(token),
                        params={"limit": 100, "offset": offset}, timeout=30)
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100; time.sleep(0.3)
    return listings

def match_section_idx(title):
    tl = title.lower()
    for i, (name, keywords) in enumerate(TARGET_SECTIONS):
        if any(k in tl for k in keywords):
            return i
    return 4  # default: Planners & Goals


def step1_fix_sections(token):
    print("\n" + "─"*55)
    print("STEP 1 — Fix Sections (rename existing)")
    print("─"*55)

    # Get existing sections
    r = requests.get(f"{API}/shops/{SHOP_ID}/sections",
                    headers=auth_headers(token), timeout=30)
    if not r.ok:
        print(f"  Cannot fetch sections: {r.status_code}")
        return {}

    existing = r.json().get("results", [])
    print(f"  Found {len(existing)} existing sections:")
    for s in existing:
        print(f"    [{s['shop_section_id']}] '{s['title']}'")

    # Rename existing sections to our targets (reuse slots)
    section_ids = {}
    for i, (target_name, _) in enumerate(TARGET_SECTIONS):
        if i < len(existing):
            sid = existing[i]["shop_section_id"]
            old_name = existing[i]["title"]
            if old_name == target_name:
                print(f"  [skip] '{target_name}' already named correctly")
            else:
                token = get_token()
                r2 = requests.put(
                    f"{API}/shops/{SHOP_ID}/sections/{sid}",
                    headers={**auth_headers(token),
                             "Content-Type": "application/x-www-form-urlencoded"},
                    data=f"title={urllib.parse.quote(target_name, safe='')}",
                    timeout=30)
                if r2.ok:
                    print(f"  [rename] '{old_name}' → '{target_name}' (id={sid})")
                else:
                    print(f"  [fail] rename '{target_name}' ({r2.status_code}): {r2.text[:80]}")
                time.sleep(0.5)
            section_ids[i] = sid
        else:
            # Try to create a new section
            token = get_token()
            r2 = requests.post(
                f"{API}/shops/{SHOP_ID}/sections",
                headers={**auth_headers(token),
                         "Content-Type": "application/x-www-form-urlencoded"},
                data=f"title={urllib.parse.quote(target_name, safe='')}",
                timeout=30)
            if r2.ok:
                sid = r2.json().get("shop_section_id")
                print(f"  [create] '{target_name}' → id={sid}")
                section_ids[i] = sid
            else:
                print(f"  [fail] create '{target_name}': {r2.text[:80]}")
            time.sleep(1)

    return section_ids


def step2_assign_listings(token, section_ids, listings):
    print("\n" + "─"*55)
    print("STEP 2 — Assign Listings to Sections")
    print("─"*55)

    ok = skip = fail = 0
    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        title = l["title"]
        si    = match_section_idx(title)
        sid   = section_ids.get(si)

        if not sid:
            print(f"  [{idx:3}] {title[:40]}... → no section id, skip")
            skip += 1
            continue

        sec_name = TARGET_SECTIONS[si][0]
        token = get_token()
        r = requests.patch(
            f"{API}/shops/{SHOP_ID}/listings/{lid}",
            headers={**auth_headers(token),
                     "Content-Type": "application/x-www-form-urlencoded"},
            data=f"shop_section_id={sid}", timeout=30)

        status = "OK" if r.ok else f"FAIL({r.status_code})"
        print(f"  [{idx:3}/{len(listings)}] {title[:38]}... → {sec_name} {status}")
        if r.ok: ok += 1
        else: fail += 1
        time.sleep(0.5)

    print(f"\n  Assigned: {ok} OK | {skip} skipped | {fail} failed")


def step3_sale_message(token):
    print("\n" + "─"*55)
    print("STEP 3 — Sale Message")
    print("─"*55)

    token = get_token()
    fields = ["sale_message", "digital_sale_message"]
    for field in fields:
        r = requests.patch(
            f"{API}/shops/{SHOP_ID}",
            headers={**auth_headers(token),
                     "Content-Type": "application/x-www-form-urlencoded"},
            data=f"{field}={urllib.parse.quote(SALE_MESSAGE, safe='')}",
            timeout=30)
        if r.ok:
            print(f"  '{field}' updated ✅")
            break
        else:
            print(f"  '{field}' failed ({r.status_code}) — trying next...")
        time.sleep(1)


def main():
    print("=" * 55)
    print("  NasriTools — Fix Setup Errors")
    print("=" * 55)

    token    = get_token()
    listings = get_all_listings(token)
    print(f"[*] {len(listings)} listings")

    section_ids = step1_fix_sections(token)
    step2_assign_listings(token, section_ids, listings)
    step3_sale_message(token)

    print("\n" + "=" * 55)
    print("  Fix complete")
    print("=" * 55)

if __name__ == "__main__":
    main()
