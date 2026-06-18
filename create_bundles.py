"""
NasriTools - Create Bundle Listings on Etsy
Creates 5 discounted bundles (3-template packs + 1 ultimate pack)
Bundles are created as drafts — user adds the delivery file then activates them
Run: python create_bundles.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_bundles_created.json"

BUNDLES = [
    {
        "key": "finance_bundle",
        "title": "Finance Bundle | Budget Tracker + Invoice Tracker + Goals Planner | 3 Google Sheets Templates | Save 50%",
        "included": [
            ("Budget Tracker",             "Track income, expenses & savings goals"),
            ("Freelancer Invoice Tracker", "Manage clients, invoices & payments"),
            ("Goals Planner",              "Annual goals, 90-day plans & milestones"),
        ],
        "individual_total": 37,
        "price": 17.99,
        "tags": [
            "finance bundle", "budget tracker", "invoice tracker",
            "google sheets bundle", "finance templates", "money tracker",
            "spreadsheet bundle", "digital bundle", "personal finance",
            "goal planner", "instant download", "digital download",
            "template bundle",
        ],
        "section": "Budget & Finance",
    },
    {
        "key": "health_bundle",
        "title": "Health Bundle | Workout Tracker + Meal Planner + Habit Tracker | 3 Google Sheets Templates | Save 50%",
        "included": [
            ("Workout Tracker", "Log sets, reps, weight & track personal records"),
            ("Meal Planner",    "7-day meal planning + auto grocery list"),
            ("Habit Tracker",   "Track 30 daily habits with streak counter"),
        ],
        "individual_total": 36,
        "price": 16.99,
        "tags": [
            "health bundle", "workout tracker", "meal planner",
            "habit tracker", "fitness bundle", "google sheets bundle",
            "wellness templates", "health templates", "digital bundle",
            "spreadsheet bundle", "instant download", "digital download",
            "template bundle",
        ],
        "section": "Health & Fitness",
    },
    {
        "key": "planner_bundle",
        "title": "Planner Bundle | Weekly Planner + Student Planner + Goals Planner | 3 Google Sheets Templates | Save 50%",
        "included": [
            ("Weekly Planner",  "Time blocking, priority tasks & weekly schedule"),
            ("Student Planner", "Assignments, grades, GPA & exam prep"),
            ("Goals Planner",   "Annual goals, 90-day plans & milestones"),
        ],
        "individual_total": 36,
        "price": 16.99,
        "tags": [
            "planner bundle", "weekly planner", "student planner",
            "goal planner", "productivity bundle", "google sheets bundle",
            "planner templates", "digital bundle", "spreadsheet bundle",
            "academic planner", "instant download", "digital download",
            "template bundle",
        ],
        "section": "Planners & Productivity",
    },
    {
        "key": "business_bundle",
        "title": "Business Bundle | Content Creator + Freelancer Invoice + KPI Dashboard | 3 Google Sheets Templates | Save 50%",
        "included": [
            ("Content Creator Planner",    "Content calendar, analytics & brand deals"),
            ("Freelancer Invoice Tracker", "Clients, invoices, income & tax prep"),
            ("KPI Dashboard",              "Business metrics, charts & performance"),
        ],
        "individual_total": 46,
        "price": 21.99,
        "tags": [
            "business bundle", "content creator", "invoice tracker",
            "kpi dashboard", "freelancer bundle", "google sheets bundle",
            "business templates", "digital bundle", "spreadsheet bundle",
            "entrepreneur tools", "instant download", "digital download",
            "template bundle",
        ],
        "section": "Business & Career",
    },
    {
        "key": "ultimate_bundle",
        "title": "Ultimate Google Sheets Bundle | 10 Templates | Budget + Habits + Workout + Wedding + More | Save 65%",
        "included": [
            ("Budget Tracker",             "Income, expenses & savings goals"),
            ("Habit Tracker",              "30 daily habits with streak counter"),
            ("Meal Planner",               "7-day meals + auto grocery list"),
            ("Wedding Planner",            "Budget, guests, vendors & timeline"),
            ("Workout Tracker",            "Sets, reps, weight & personal records"),
            ("Content Creator Planner",    "Content calendar, analytics & brand deals"),
            ("Freelancer Invoice Tracker", "Clients, invoices & tax prep"),
            ("Student Planner",            "Assignments, grades & exam prep"),
            ("Goals Planner",              "Annual goals & 90-day action plan"),
            ("Weekly Planner",             "Time blocking & priority tasks"),
        ],
        "individual_total": 121,
        "price": 39.99,
        "tags": [
            "ultimate bundle", "google sheets bundle", "template bundle",
            "spreadsheet bundle", "mega bundle", "digital bundle",
            "all templates", "complete bundle", "google sheets",
            "instant download", "digital download", "productivity bundle",
            "best value",
        ],
        "section": "Planners & Productivity",
    },
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


def get_taxonomy_and_section(token, published):
    """Fetch taxonomy_id from an existing listing."""
    lid = next(iter(published.values()), None)
    if not lid:
        return 1, None
    r = requests.get(
        f"https://api.etsy.com/v3/application/listings/{lid}",
        headers=auth_headers(token),
        timeout=15,
    )
    if r.ok:
        data = r.json()
        return data.get("taxonomy_id", 1), data.get("shop_section_id")
    return 1, None


def get_section_id(token, section_title):
    r = requests.get(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/sections",
        headers=auth_headers(token),
        timeout=15,
    )
    if r.ok:
        for s in r.json().get("results", []):
            if s["title"] == section_title:
                return s["shop_section_id"]
    return None


def build_description(bundle):
    lines = []
    pct   = int((1 - bundle["price"] / bundle["individual_total"]) * 100)
    lines.append(f"🎯 {bundle['title'].split('|')[0].strip().upper()}")
    lines.append(f"Save {pct}% vs buying individually — {len(bundle['included'])} templates in one purchase!\n")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("✅ WHAT'S INCLUDED:\n")
    for i, (name, desc) in enumerate(bundle["included"], 1):
        lines.append(f"{i}. {name}")
        lines.append(f"   → {desc}\n")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"💰 INDIVIDUAL TOTAL: €{bundle['individual_total']:.2f}")
    lines.append(f"🏷️  BUNDLE PRICE:     €{bundle['price']:.2f}  (SAVE {pct}%)\n")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("📥 HOW IT WORKS:\n")
    lines.append("1. Purchase this bundle")
    lines.append("2. You'll receive a Google Sheets link to all templates")
    lines.append("3. Make a copy to your Google Drive — it's yours forever\n")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("⚡ FEATURES OF ALL TEMPLATES:\n")
    lines.append("• Works on Google Sheets & Microsoft Excel")
    lines.append("• Fully customizable — edit colors, text & layout")
    lines.append("• Auto-calculating formulas built in")
    lines.append("• Step-by-step setup instructions included")
    lines.append("• Lifetime access — yours forever after purchase")
    lines.append("• No subscription, no app needed\n")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("💬 QUESTIONS? Message us anytime — we reply within 24 hours.")
    lines.append("\nnasritools.etsy.com")
    return "\n".join(lines)


def create_listing(token, bundle, taxonomy_id, section_id):
    description = build_description(bundle)
    payload = {
        "quantity":    999,
        "title":       bundle["title"][:140],
        "description": description,
        "price":       bundle["price"],
        "who_made":    "i_did",
        "when_made":   "2020_2024",
        "taxonomy_id": taxonomy_id,
        "type":        "download",
        "tags":        bundle["tags"][:13],
        "state":       "draft",
    }
    if section_id:
        payload["shop_section_id"] = section_id

    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings",
        headers=auth_headers(token),
        json=payload,
        timeout=30,
    )
    return r


def main():
    done      = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    token     = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Create Bundle Listings [{len(BUNDLES)} bundles]")
    print(f"  Already done: {len(done)}")
    print(f"{'='*65}\n")

    taxonomy_id, _ = get_taxonomy_and_section(token, published)
    print(f"  Using taxonomy_id: {taxonomy_id}\n")

    ok = 0
    for i, bundle in enumerate(BUNDLES, 1):
        if bundle["key"] in done:
            print(f"[{i}/{len(BUNDLES)}] SKIP (done): {bundle['key']}")
            ok += 1
            continue

        section_id = get_section_id(token, bundle["section"])
        print(f"[{i}/{len(BUNDLES)}] Creating: {bundle['key']}")
        print(f"    Price: €{bundle['price']}  (was €{bundle['individual_total']})")

        r = create_listing(token, bundle, taxonomy_id, section_id)
        time.sleep(1)

        if r.ok:
            lid = r.json().get("listing_id")
            ok += 1
            done[bundle["key"]] = lid
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"    Created as DRAFT ✓  (listing_id: {lid})")
            print(f"    URL: https://www.etsy.com/your/shops/me/listing-editor/edit/{lid}")
        else:
            print(f"    ERROR {r.status_code}: {r.text[:200]}")

    print(f"\n{'='*65}")
    print(f"  Done: {ok}/{len(BUNDLES)} bundle drafts created")
    print(f"\n  NEXT STEP:")
    print(f"  For each bundle, open the URL above in Etsy and:")
    print(f"  1. Upload a PDF/file with Google Sheets links")
    print(f"  2. Click 'Publish' to make it active")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
