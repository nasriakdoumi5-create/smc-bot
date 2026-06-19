"""
NasriTools - Listing Manager
Fetches all active listings, scores them by relevance to the 5 core systems,
deactivates weak/off-niche listings, and generates a prioritized action report.
Run: python manage_listings.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
REPORT_FILE = Path(os.path.expanduser("~")) / "nasri_listing_audit.json"

# Core products to ALWAYS keep active
CORE_LISTINGS = {
    4487745643, 4487740567, 4487742011, 4487743321, 4487744011,
    4487745211, 4487744321, 4487742911, 4487743721, 4487742511,
    # Bundles
    4524283814, 4524276503, 4524276527, 4524276553, 4524283886,
}

# Keywords that indicate a listing fits our 5 systems
SYSTEM_KEYWORDS = {
    "finance":     ["budget", "expense", "invoice", "finance", "money", "savings",
                    "income", "tax", "financial", "net worth", "accounting"],
    "health":      ["workout", "fitness", "gym", "meal", "nutrition", "habit",
                    "health", "exercise", "calories", "diet", "wellness"],
    "business":    ["content", "creator", "marketing", "freelance", "client",
                    "business", "invoice", "proposal", "social media", "brand"],
    "productivity":["planner", "weekly", "daily", "schedule", "goals", "productivity",
                    "task", "time blocking", "priority", "to do", "routine"],
    "student":     ["student", "study", "grade", "gpa", "college", "university",
                    "homework", "assignment", "school", "academic"],
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
            "x-api-key": CLIENT_ID}


def fetch_all_listings(token):
    listings = []
    offset   = 0
    limit    = 100
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": limit, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            print(f"  [error] fetch listings {r.status_code}: {r.text[:120]}")
            break
        data = r.json()
        batch = data.get("results", [])
        listings.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(0.5)
    return listings


def score_listing(listing):
    text = (
        (listing.get("title") or "") + " " +
        (listing.get("description") or "")
    ).lower()

    matched_systems = []
    for system, keywords in SYSTEM_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            matched_systems.append(system)

    return matched_systems


def deactivate_listing(token, listing_id):
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"state": "inactive"},
        timeout=30,
    )
    return r


def main():
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Listing Audit & Manager")
    print(f"{'='*65}\n")

    print("  Fetching all active listings…")
    listings = fetch_all_listings(token)
    print(f"  Found {len(listings)} active listings\n")

    report = {
        "keep_core":    [],
        "keep_system":  [],
        "deactivate":   [],
        "total":        len(listings),
    }

    to_deactivate = []

    for lst in listings:
        lid   = lst["listing_id"]
        title = lst.get("title", "")[:70]
        views = lst.get("views", 0)
        favs  = lst.get("num_favorers", 0)

        if lid in CORE_LISTINGS:
            report["keep_core"].append({"id": lid, "title": title})
            continue

        systems = score_listing(lst)

        if systems:
            report["keep_system"].append({
                "id": lid, "title": title,
                "systems": systems, "views": views, "favs": favs,
            })
        else:
            report["deactivate"].append({
                "id": lid, "title": title,
                "views": views, "favs": favs,
            })
            to_deactivate.append(lid)

    # Print summary
    print(f"  Core listings (always keep):  {len(report['keep_core'])}")
    print(f"  Fits a system (keep active):  {len(report['keep_system'])}")
    print(f"  Off-niche (to deactivate):    {len(report['deactivate'])}")
    print()

    if to_deactivate:
        print(f"  Deactivating {len(to_deactivate)} off-niche listings…")
        deactivated = 0
        for lid in to_deactivate:
            r = deactivate_listing(token, lid)
            time.sleep(0.8)
            status = "✓" if r.ok else f"✗ {r.status_code}"
            print(f"    {lid} → {status}")
            if r.ok:
                deactivated += 1
            token = get_token()
        print(f"\n  Deactivated: {deactivated}/{len(to_deactivate)}")
    else:
        print("  All listings already fit the core systems — nothing to deactivate.")

    # Save report
    REPORT_FILE.write_text(json.dumps(report, indent=2))
    print(f"\n  Full audit report saved to: {REPORT_FILE}")

    # Print off-niche titles for manual review
    if report["deactivate"]:
        print(f"\n  ── Deactivated Listings ──")
        for item in report["deactivate"]:
            print(f"    [{item['id']}] {item['title']} (views: {item['views']})")

    print(f"\n{'='*65}")
    print(f"  Audit complete.")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
