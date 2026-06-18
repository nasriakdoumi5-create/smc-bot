"""
NasriTools - Add Shop Sections & Move Listings
Creates 5 sections and assigns each of the 10 products to the right section
Run: python add_sections.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"

SECTIONS = [
    {"title": "Budget & Finance",    "slugs": ["budget_tracker", "freelancer_invoice_tracker"]},
    {"title": "Health & Fitness",    "slugs": ["habit_tracker", "workout_tracker", "meal_planner"]},
    {"title": "Business & Career",   "slugs": ["content_creator_planner", "freelancer_invoice_tracker"]},
    {"title": "Planners & Productivity", "slugs": ["weekly_planner", "goals_planner", "student_planner"]},
    {"title": "Life Events",         "slugs": ["wedding_planner"]},
]

SLUG_SECTION = {
    "budget_tracker":             "Budget & Finance",
    "habit_tracker":              "Health & Fitness",
    "meal_planner":               "Health & Fitness",
    "wedding_planner":            "Life Events",
    "workout_tracker":            "Health & Fitness",
    "content_creator_planner":    "Business & Career",
    "freelancer_invoice_tracker": "Budget & Finance",
    "student_planner":            "Planners & Productivity",
    "goals_planner":              "Planners & Productivity",
    "weekly_planner":             "Planners & Productivity",
}


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
    print(f"    ERROR creating section '{title}': {r.status_code} {r.text[:100]}")
    return None


def move_listing(token, listing_id, section_id):
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}",
        headers=auth_headers(token),
        json={"shop_section_id": section_id},
        timeout=15,
    )
    return r


def main():
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    token     = get_token()

    print(f"\n{'='*60}")
    print(f"  NasriTools - Add Shop Sections")
    print(f"{'='*60}\n")

    # Step 1: get or create sections
    print("  Fetching existing sections...")
    section_ids = get_existing_sections(token)
    print(f"  Found {len(section_ids)} existing sections")

    needed = {"Budget & Finance", "Health & Fitness", "Business & Career",
              "Planners & Productivity", "Life Events"}

    for title in needed:
        if title not in section_ids:
            print(f"  Creating: {title}")
            sid = create_section(token, title)
            if sid:
                section_ids[title] = sid
                print(f"    created (id={sid})")
            time.sleep(0.5)
        else:
            print(f"  Exists: {title} (id={section_ids[title]})")

    # Step 2: assign listings to sections
    print(f"\n  Assigning listings to sections...\n")
    ok = 0
    total = len(SLUG_SECTION)

    for i, (slug, section_title) in enumerate(SLUG_SECTION.items(), 1):
        lid = published.get(slug)
        if not lid:
            print(f"[{i:02d}/{total}] SKIP (no listing ID): {slug}")
            continue
        sid = section_ids.get(section_title)
        if not sid:
            print(f"[{i:02d}/{total}] SKIP (no section ID for '{section_title}'): {slug}")
            continue

        print(f"[{i:02d}/{total}] {slug} → {section_title}")
        r = move_listing(token, lid, sid)
        time.sleep(0.8)

        if r.ok:
            ok += 1
            print(f"    moved: OK")
        else:
            print(f"    ERROR {r.status_code}: {r.text[:150]}")

        if i % 5 == 0:
            token = get_token()

    print(f"\n{'='*60}")
    print(f"  Done: {ok}/{total} listings moved to sections")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
