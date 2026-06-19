"""
NasriTools - Shop Section Organizer
Creates 6 themed sections and assigns all active listings automatically.
Run: python organize_sections.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

# Order matters — first match wins
SECTION_DEFS = [
    {"title": "Bundle Sets",          "kw": ["bundle"]},
    {"title": "Finance Templates",    "kw": ["budget", "invoice", "finance", "money", "tax"]},
    {"title": "Health & Fitness",     "kw": ["workout", "meal", "habit", "gym", "nutrition", "diet", "fitness"]},
    {"title": "Business Templates",   "kw": ["content creator", "freelancer", "business", "marketing", "social media"]},
    {"title": "Student Templates",    "kw": ["student", "gpa", "grade", "college", "university", "homework"]},
    {"title": "Planner Templates",    "kw": ["planner", "goals", "weekly", "schedule", "wedding", "productivity"]},
]


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


def get_existing_sections(token):
    r = requests.get(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/sections",
        headers=auth_headers(token), timeout=30,
    )
    if r.ok:
        return {s["title"]: s["shop_section_id"] for s in r.json().get("results", [])}
    print(f"  [warn] Could not fetch sections: {r.status_code} {r.text[:100]}")
    return {}


def create_section(token, title):
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/sections",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"title": title},
        timeout=30,
    )
    if r.ok:
        return r.json().get("shop_section_id")
    print(f"  [warn] Create section failed: {r.text[:100]}")
    return None


def assign_section(token, listing_id, section_id):
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"shop_section_id": section_id},
        timeout=30,
    )
    return r.ok


def fetch_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings


def match_section(title_lower):
    for sec in SECTION_DEFS:
        if any(kw in title_lower for kw in sec["kw"]):
            return sec["title"]
    return SECTION_DEFS[-1]["title"]


def main():
    token = get_token()

    print(f"\n{'='*60}")
    print(f"  NasriTools - Shop Section Organizer")
    print(f"{'='*60}\n")

    print("  Loading existing sections…")
    section_map = get_existing_sections(token)
    print(f"  Found {len(section_map)} existing sections\n")

    for sdef in SECTION_DEFS:
        title = sdef["title"]
        if title not in section_map:
            print(f"  Creating: {title}…", end=" ")
            sid = create_section(token, title)
            if sid:
                section_map[title] = sid
                print("✓")
            time.sleep(0.5)
            token = get_token()
        else:
            print(f"  Exists: {title}")

    print()
    print("  Fetching all active listings…")
    listings = fetch_all_listings(token)
    token = get_token()
    print(f"  Found {len(listings)} listings\n")

    ok = 0
    for lst in listings:
        lid   = lst["listing_id"]
        title = (lst.get("title") or "")
        sec   = match_section(title.lower())
        sid   = section_map.get(sec)

        if not sid:
            print(f"  [skip] no section ID for: {title[:50]}")
            continue

        success = assign_section(token, lid, sid)
        mark    = "✓" if success else "✗"
        print(f"  {mark} [{sec[:22]:<22}] {title[:48]}")
        if success:
            ok += 1
        time.sleep(0.4)
        token = get_token()

    print(f"\n{'='*60}")
    print(f"  Done: {ok}/{len(listings)} listings assigned to sections")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
