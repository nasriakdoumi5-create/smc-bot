"""
create_shop_sections.py
Creates 5 shop sections and assigns all listings to the right section.
Sections help Etsy SEO + buyer navigation.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

SECTIONS = [
    {
        "title": "Bundles — Save Up to 65%",
        "keywords": ["bundle", "complete life", "finance bundle", "health bundle",
                     "productivity bundle", "business bundle"],
    },
    {
        "title": "Finance & Budget",
        "keywords": ["budget", "expense", "invoice", "finance", "money", "profit",
                     "debt", "cash flow", "tax", "financial", "revenue", "payoff",
                     "startup financial", "nonprofit", "church budget", "emergency fund"],
    },
    {
        "title": "Health & Fitness",
        "keywords": ["workout", "meal", "habit", "fitness", "keto", "weight",
                     "sleep", "pregnancy", "marathon", "mental health", "baby"],
    },
    {
        "title": "Business & Freelance",
        "keywords": ["freelance", "invoice", "client", "marketing", "sales",
                     "content creator", "social media", "ecommerce", "dropshipping",
                     "restaurant", "hair salon", "law firm", "construction",
                     "supply chain", "inventory", "employee", "hr", "kpi",
                     "real estate", "print on demand", "virtual assistant",
                     "influencer", "musician", "artist", "author", "etsy shop"],
    },
    {
        "title": "Productivity & Planning",
        "keywords": ["planner", "weekly", "student", "goals", "productivity",
                     "time tracking", "project", "annual review", "certification",
                     "skill", "tutor", "online course", "job application",
                     "travel", "event", "family chores", "car maintenance",
                     "school supply", "thesis", "pet", "stock trading",
                     "options trading", "youtube", "content repurposing"],
    },
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
    return {
        "Authorization": "Bearer " + token["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }

def get_existing_sections(token):
    r = requests.get(
        f"{API}/shops/{SHOP_ID}/sections",
        headers=auth_headers(token),
    )
    if r.ok:
        return {s["title"]: s["shop_section_id"] for s in r.json().get("results", [])}
    return {}

def create_section(token, title):
    r = requests.post(
        f"{API}/shops/{SHOP_ID}/sections",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode({"title": title}),
        timeout=30,
    )
    if r.ok:
        return r.json().get("shop_section_id")
    print(f"    Failed to create section '{title}': HTTP {r.status_code} — {r.text[:100]}")
    return None

def assign_listing(token, lid, section_id):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=f"shop_section_id={section_id}",
        timeout=30,
    )
    return r.ok, r.status_code

def get_all_listings(token):
    listings = []
    offset = 0
    while True:
        r = requests.get(
            f"{API}/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset},
        )
        if not r.ok:
            break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100:
            break
        offset += 100
    return listings

def match_section(title, sections):
    title_lower = title.lower()
    for sec in sections:
        for kw in sec["keywords"]:
            if kw in title_lower:
                return sec["title"]
    return sections[-1]["title"]  # default: Productivity & Planning

def main():
    print("=" * 65)
    print("  NasriTools — Create Shop Sections & Assign Listings")
    print("=" * 65)

    token = get_token()
    print("[*] Token OK\n")

    # ── Step 1: Get or create sections ────────────────────────────────
    print("[1/2] Setting up sections...")
    existing = get_existing_sections(token)
    print(f"  Existing sections: {list(existing.keys()) or 'none'}")

    section_ids = {}
    for sec in SECTIONS:
        title = sec["title"]
        if title in existing:
            section_ids[title] = existing[title]
            print(f"  [EXISTS] {title}")
        else:
            token = get_token()
            sid = create_section(token, title)
            if sid:
                section_ids[title] = sid
                print(f"  [CREATED] {title} (id={sid})")
            time.sleep(0.5)

    # ── Step 2: Assign listings ────────────────────────────────────────
    print(f"\n[2/2] Assigning {len(section_ids)} sections to listings...")
    token = get_token()
    listings = get_all_listings(token)
    print(f"  Found {len(listings)} listings\n")

    counts = {s["title"]: 0 for s in SECTIONS}
    ok_total = fail_total = 0

    for l in listings:
        lid   = l["listing_id"]
        title = l["title"]
        sec_title = match_section(title, SECTIONS)
        sid = section_ids.get(sec_title)
        if not sid:
            print(f"  [SKIP] No section ID for '{sec_title}'")
            continue

        print(f"  [{sec_title[:20]:20}] {title[:38]} ...", end=" ", flush=True)
        token = get_token()
        ok, code = assign_listing(token, lid, sid)
        if ok:
            print(f"OK")
            ok_total += 1
            counts[sec_title] = counts.get(sec_title, 0) + 1
        else:
            print(f"FAIL ({code})")
            fail_total += 1
        time.sleep(0.8)

    print(f"\n{'='*65}")
    print(f"  Sections created/assigned:")
    for title, count in counts.items():
        print(f"    {title}: {count} listings")
    print(f"\n  Total: {ok_total} OK | {fail_total} failed")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
