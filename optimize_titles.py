"""
optimize_titles.py
Ensures every listing title starts with the highest-volume search keyword.
Etsy's algorithm weights the FIRST 3 words of the title most heavily.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

# Primary keyword that MUST appear first in the title (highest search volume)
PRIME_KEYWORD = {
    "budget":      "Budget Tracker Spreadsheet",
    "invoice":     "Invoice Template Google Sheets",
    "kpi":         "Business Dashboard Google Sheets",
    "fitness":     "Workout Tracker Spreadsheet",
    "meal":        "Meal Planner Spreadsheet",
    "habit":       "Habit Tracker Spreadsheet",
    "goals":       "Goal Planner Spreadsheet",
    "student":     "Student Planner Spreadsheet",
    "event":       "Event Planner Spreadsheet",
    "content":     "Content Calendar Spreadsheet",
    "project":     "Project Tracker Spreadsheet",
    "inventory":   "Inventory Tracker Spreadsheet",
    "realestate":  "Real Estate Spreadsheet",
    "hr":          "HR Template Google Sheets",
    "restaurant":  "Restaurant Spreadsheet Template",
    "travel":      "Travel Planner Spreadsheet",
    "planner":     "Planner Spreadsheet Template",
    "bundle":      "Google Sheets Bundle",
    "productivity":"Productivity Tracker Spreadsheet",
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
    if any(x in t for x in ["bundle", "complete system", "kit", "pack", "all-in-one", "all in one"]):
        return "bundle"
    if any(x in t for x in ["budget", "expense", "spending", "financial", "money", "cash flow"]):
        return "budget"
    if any(x in t for x in ["invoice", "freelanc", "billing", "client tracker", "payment tracker"]):
        return "invoice"
    if any(x in t for x in ["kpi", "dashboard", "sales tracker", "revenue", "pipeline", "crm", "startup"]):
        return "kpi"
    if any(x in t for x in ["workout", "fitness", "gym", "exercise", "weight loss", "training log"]):
        return "fitness"
    if any(x in t for x in ["meal", "food", "recipe", "nutrition", "grocery", "diet"]):
        return "meal"
    if any(x in t for x in ["habit", "routine", "morning routine", "evening routine"]):
        return "habit"
    if any(x in t for x in ["goal", "vision", "dream", "bucket list", "achievement"]):
        return "goals"
    if any(x in t for x in ["student", "school", "study", "college", "class", "assignment", "grade"]):
        return "student"
    if any(x in t for x in ["wedding", "event planner", "party", "birthday"]):
        return "event"
    if any(x in t for x in ["content", "social media", "instagram", "youtube", "tiktok", "creator"]):
        return "content"
    if any(x in t for x in ["project", "task manager", "team", "agile", "sprint", "gantt"]):
        return "project"
    if any(x in t for x in ["inventory", "stock", "ecommerce", "etsy shop", "etsy seller", "pod tracker", "print on demand"]):
        return "inventory"
    if any(x in t for x in ["real estate", "property", "rental", "lease"]):
        return "realestate"
    if any(x in t for x in ["hr ", "employee", "onboard", "hiring", "recruitment"]):
        return "hr"
    if any(x in t for x in ["restaurant", "cafe", "menu cost", "food business"]):
        return "restaurant"
    if any(x in t for x in ["travel", "trip", "vacation", "itinerary", "packing list"]):
        return "travel"
    if any(x in t for x in ["weekly planner", "monthly planner", "daily planner"]):
        return "planner"
    return "productivity"

def already_starts_correctly(title, prime):
    """Check if first few words already contain the prime keyword."""
    return title.lower().startswith(prime.lower())

def rebuild_title(current_title, prime):
    """
    Prepend the prime keyword if it's not already first.
    Keep all existing keyword segments, trim to 140 chars.
    """
    if already_starts_correctly(current_title, prime):
        return None  # no change needed

    # Split existing title on | and clean up
    parts = [p.strip() for p in current_title.split("|") if p.strip()]

    # Remove any part that duplicates the prime keyword
    prime_lower = prime.lower()
    filtered = [p for p in parts if prime_lower not in p.lower()]

    # Build new title: prime first, then the rest
    new_parts = [prime] + filtered
    new_title = " | ".join(new_parts)

    # Trim to 140 chars (Etsy limit) — cut at last | boundary
    if len(new_title) > 140:
        new_title = new_title[:140].rsplit(" | ", 1)[0]

    return new_title if new_title != current_title else None

def update_title(token, lid, new_title):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data="title=" + urllib.parse.quote(new_title),
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
    print("  NasriTools — Title SEO Optimizer")
    print("  Puts the #1 search keyword first in every title")
    print("=" * 65)

    token    = get_token()
    listings = get_all_listings(token)
    total    = len(listings)
    print(f"[*] {total} listings found\n")

    updated = skipped = fail = 0

    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        title = l.get("title", "")
        ptype = detect_type(title)
        prime = PRIME_KEYWORD.get(ptype, PRIME_KEYWORD["productivity"])

        new_title = rebuild_title(title, prime)

        if new_title is None:
            skipped += 1
            print(f"  [{idx:3}/{total}] SKIP (already correct): {title[:50]}")
            time.sleep(0.05)
            continue

        print(f"  [{idx:3}/{total}] [{ptype:12}] {title[:35]}...")
        print(f"          → {new_title[:60]}...", end=" ", flush=True)

        token = get_token()
        ok, code = update_title(token, lid, new_title)

        if ok:
            print("OK")
            updated += 1
        else:
            print(f"FAIL ({code})")
            fail += 1

        time.sleep(0.8)
        if idx % 20 == 0:
            token = get_token()

    print(f"\n{'=' * 65}")
    print(f"  Updated  : {updated}")
    print(f"  Skipped  : {skipped} (already correct)")
    print(f"  Failed   : {fail}")
    print(f"{'=' * 65}")

if __name__ == "__main__":
    main()
