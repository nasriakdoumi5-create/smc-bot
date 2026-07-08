"""
organize_store_sections.py
Clears old sections, creates 8 professional sections, assigns all 116 listings.
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

SECTIONS = [
    "Budget & Finance",
    "Business & Growth",
    "Health & Fitness",
    "Planners & Productivity",
    "Life & Events",
    "Content & Social Media",
    "Project Management",
    "Complete Bundles",
]

TYPE_TO_SECTION = {
    "budget":      "Budget & Finance",
    "invoice":     "Budget & Finance",
    "kpi":         "Business & Growth",
    "inventory":   "Business & Growth",
    "hr":          "Business & Growth",
    "restaurant":  "Business & Growth",
    "realestate":  "Business & Growth",
    "fitness":     "Health & Fitness",
    "meal":        "Health & Fitness",
    "planner":     "Planners & Productivity",
    "habit":       "Planners & Productivity",
    "goals":       "Planners & Productivity",
    "productivity":"Planners & Productivity",
    "student":     "Life & Events",
    "event":       "Life & Events",
    "travel":      "Life & Events",
    "content":     "Content & Social Media",
    "project":     "Project Management",
    "bundle":      "Complete Bundles",
}

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

def detect_type(title):
    t = title.lower()
    if any(x in t for x in ["bundle", "complete", "system", "os", "kit", "pack"]):
        return "bundle"
    if any(x in t for x in ["budget", "expense", "spending", "financial", "money", "cash flow"]):
        return "budget"
    if any(x in t for x in ["invoice", "client", "freelanc", "billing", "payment"]):
        return "invoice"
    if any(x in t for x in ["kpi", "business", "sales", "revenue", "pipeline", "crm", "startup"]):
        return "kpi"
    if any(x in t for x in ["workout", "fitness", "gym", "exercise", "weight", "training"]):
        return "fitness"
    if any(x in t for x in ["meal", "food", "recipe", "nutrition", "grocery", "diet"]):
        return "meal"
    if any(x in t for x in ["habit", "routine", "daily", "morning", "evening"]):
        return "habit"
    if any(x in t for x in ["goal", "vision", "dream", "bucket", "achievement"]):
        return "goals"
    if any(x in t for x in ["student", "school", "study", "college", "class", "assignment", "grade"]):
        return "student"
    if any(x in t for x in ["wedding", "event", "party", "birthday"]):
        return "event"
    if any(x in t for x in ["content", "social media", "instagram", "youtube", "tiktok", "creator"]):
        return "content"
    if any(x in t for x in ["project", "task", "team", "agile", "sprint", "gantt"]):
        return "project"
    if any(x in t for x in ["inventory", "stock", "product", "ecommerce", "shop tracker", "etsy shop", "etsy seller", "pod"]):
        return "inventory"
    if any(x in t for x in ["real estate", "property", "rental", "lease"]):
        return "realestate"
    if any(x in t for x in ["hr", "employee", "onboard", "hiring", "recruitment"]):
        return "hr"
    if any(x in t for x in ["restaurant", "cafe", "menu", "food business"]):
        return "restaurant"
    if any(x in t for x in ["travel", "trip", "vacation", "itinerary", "packing"]):
        return "travel"
    if any(x in t for x in ["weekly planner", "monthly planner", "daily planner", "planner"]):
        return "planner"
    return "productivity"

def get_existing_sections(token):
    r = requests.get(f"{API}/shops/{SHOP_ID}/sections",
                     headers=auth_headers(token), timeout=15)
    if r.ok:
        return r.json().get("results", [])
    return []

def delete_section(token, sid):
    r = requests.delete(f"{API}/shops/{SHOP_ID}/sections/{sid}",
                        headers=auth_headers(token), timeout=15)
    return r.ok, r.status_code

def create_section(token, title):
    r = requests.post(f"{API}/shops/{SHOP_ID}/sections",
                      headers={**auth_headers(token), "Content-Type": "application/json"},
                      json={"title": title}, timeout=15)
    if r.ok:
        return r.json().get("shop_section_id")
    print(f"    ERROR creating '{title}': {r.status_code} {r.text[:80]}")
    return None

def assign_section(token, lid, section_id):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=f"shop_section_id={section_id}",
        timeout=30,
    )
    return r.ok, r.status_code

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset}, timeout=30)
        if not r.ok:
            break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings

def main():
    print("=" * 65)
    print("  NasriTools — Organize Store into 8 Professional Sections")
    print("=" * 65)

    token = get_token()

    # Step 1: Get all existing sections
    print("\n[1] Getting existing sections...")
    existing = get_existing_sections(token)
    print(f"    Found {len(existing)} sections:")
    for s in existing:
        print(f"      [{s['shop_section_id']}] {s['title']}")

    # Step 2: Delete old sections that are NOT in our 8
    print(f"\n[2] Removing old sections (keeping only our 8)...")
    keep_titles = set(SECTIONS)
    section_ids = {}

    for s in existing:
        if s["title"] in keep_titles:
            section_ids[s["title"]] = s["shop_section_id"]
            print(f"    KEEP: {s['title']}")
        else:
            print(f"    DELETE: {s['title']}...", end=" ", flush=True)
            ok, code = delete_section(token, s["shop_section_id"])
            print("OK" if ok else f"FAIL ({code})")
            time.sleep(0.4)

    # Step 3: Create missing sections
    print(f"\n[3] Creating missing sections...")
    for title in SECTIONS:
        if title not in section_ids:
            print(f"    CREATE: {title}...", end=" ", flush=True)
            token = get_token()
            sid = create_section(token, title)
            if sid:
                section_ids[title] = sid
                print(f"OK (id={sid})")
            else:
                print("FAILED")
            time.sleep(0.5)
        else:
            print(f"    EXISTS: {title} (id={section_ids[title]})")

    print(f"\n    Active sections: {list(section_ids.keys())}")

    # Step 4: Get all listings
    print(f"\n[4] Fetching all listings...")
    token = get_token()
    listings = get_all_listings(token)
    total = len(listings)
    print(f"    {total} listings found\n")

    # Step 5: Assign each listing
    print("[5] Assigning listings to sections...\n")
    ok = fail = already = 0

    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        title = l.get("title", "")
        current_section = l.get("shop_section_id")

        ptype   = detect_type(title)
        section = TYPE_TO_SECTION.get(ptype, "Planners & Productivity")
        sid     = section_ids.get(section)

        if not sid:
            print(f"  [{idx:3}/{total}] SKIP (no section): {title[:45]}")
            continue

        if current_section == sid:
            already += 1
            print(f"  [{idx:3}/{total}] [{section[:20]:20}] {title[:35]}... already")
            time.sleep(0.05)
            continue

        print(f"  [{idx:3}/{total}] [{section[:20]:20}] {title[:35]}...", end=" ", flush=True)
        token = get_token()
        success, code = assign_section(token, lid, sid)

        if success:
            print("OK")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1

        time.sleep(0.5)
        if idx % 25 == 0:
            token = get_token()

    print(f"\n{'=' * 65}")
    print(f"  Sections ready   : {len(section_ids)}/8")
    print(f"  Assigned OK      : {ok}")
    print(f"  Already correct  : {already}")
    print(f"  Failed           : {fail}")
    print(f"{'=' * 65}")

if __name__ == "__main__":
    main()
