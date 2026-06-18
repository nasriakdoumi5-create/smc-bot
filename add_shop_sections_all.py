"""
NasriTools - Auto-Organize ALL Listings into Shop Sections
Creates 6 sections and assigns every active listing based on title keywords
Run: python add_shop_sections_all.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_sections_done.json"

# Ordered priority — first match wins
SECTION_RULES = [
    ("Students & Education", [
        "student", "academic", "college", "university", "gpa",
        "homework", "exam", "grade", "class schedule", "school",
    ]),
    ("Life Events", [
        "wedding", "bride", "groom", "travel", "vacation",
        "itinerary", "baby shower", "moving", "event planner",
    ]),
    ("Health & Fitness", [
        "workout", "gym", "fitness", "exercise", "meal plan",
        "nutrition", "habit tracker", "meditation", "yoga",
        "running", "calorie", "weight loss", "body measurement",
    ]),
    ("Budget & Finance", [
        "budget", "expense", "profit", "loss", "invoice",
        "revenue", "cash flow", "trading", "stock", "crypto",
        "amazon fba", "fba", "ecommerce", "financial model",
        "accounting", "tax", "mortgage", "debt", "savings",
        "net worth", "payroll", "startup", "break even",
    ]),
    ("Business & Career", [
        "kpi", "project tracker", "crm", "freelancer", "freelance",
        "social media", "marketing", "hr ", "employee", "sales",
        "lead tracker", "influencer", "youtube", "instagram",
        "podcast", "seo", "analytics", "content creator",
        "content calendar", "posting", "brand", "client tracker",
    ]),
    ("Planners & Productivity", []),   # catches everything else
]

SECTIONS_TO_CREATE = [
    "Budget & Finance",
    "Health & Fitness",
    "Business & Career",
    "Planners & Productivity",
    "Students & Education",
    "Life Events",
]


def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0):
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
        "Content-Type": "application/json",
    }


def get_existing_sections(token):
    r = requests.get(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/sections",
        headers=auth_headers(token),
        timeout=15,
    )
    if r.ok:
        return {s["title"]: s["shop_section_id"] for s in r.json().get("results", [])}
    print(f"  Warning: could not fetch sections: {r.status_code}")
    return {}


def create_section(token, title):
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/sections",
        headers=auth_headers(token),
        json={"title": title},
        timeout=15,
    )
    if r.ok:
        return r.json().get("shop_section_id")
    print(f"  Error creating '{title}': {r.status_code} {r.text[:100]}")
    return None


def fetch_all_listings(token):
    listings, offset, limit = [], 0, 100
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": limit, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(0.5)
    return listings


def pick_section(title):
    t = title.lower()
    for section_name, keywords in SECTION_RULES:
        if not keywords:
            return section_name      # default / catchall
        if any(kw in t for kw in keywords):
            return section_name
    return "Planners & Productivity"


def main():
    done  = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Auto-Organize ALL Listings into Sections")
    print(f"  Already done: {len(done)}")
    print(f"{'='*65}\n")

    # ── Step 1: ensure all sections exist ──────────────────
    print("  Checking / creating shop sections...")
    section_ids = get_existing_sections(token)

    for title in SECTIONS_TO_CREATE:
        if title not in section_ids:
            print(f"  + Creating: {title}")
            sid = create_section(token, title)
            if sid:
                section_ids[title] = sid
                print(f"    ✓ created (id={sid})")
            time.sleep(0.5)
        else:
            print(f"  ✓ Exists:  {title} (id={section_ids[title]})")

    # ── Step 2: fetch all listings ──────────────────────────
    print(f"\n  Fetching all active listings...")
    listings = fetch_all_listings(token)
    total    = len(listings)
    print(f"  Found {total} listings\n")

    # ── Step 3: assign each to a section ───────────────────
    ok = 0
    counts = {s: 0 for s in SECTIONS_TO_CREATE}

    for i, listing in enumerate(listings, 1):
        lid   = str(listing["listing_id"])
        title = listing.get("title", "")

        if lid in done:
            print(f"[{i:03d}/{total}] SKIP: {title[:55]}")
            ok += 1
            continue

        section_name = pick_section(title)
        sid = section_ids.get(section_name)
        if not sid:
            print(f"[{i:03d}/{total}] NO SECTION ID for '{section_name}': {title[:40]}")
            continue

        print(f"[{i:03d}/{total}] {title[:50]}")
        print(f"    → {section_name}")

        r = requests.patch(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}",
            headers=auth_headers(token),
            json={"shop_section_id": sid},
            timeout=20,
        )
        time.sleep(0.8)

        if r.ok:
            ok += 1
            counts[section_name] = counts.get(section_name, 0) + 1
            done[lid] = {"title": title[:60], "section": section_name}
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"    ✓ moved")
        else:
            print(f"    ERROR {r.status_code}: {r.text[:100]}")

        if i % 10 == 0:
            token = get_token()

    # ── Summary ────────────────────────────────────────────
    print(f"\n{'='*65}")
    print(f"  Done: {ok}/{total} listings organized")
    print(f"  Section breakdown:")
    for sec, cnt in counts.items():
        if cnt:
            print(f"    {sec}: {cnt}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
