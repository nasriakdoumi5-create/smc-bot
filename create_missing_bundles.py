"""
NasriTools - Create Missing Bundle Listings
Creates the 4 missing bundles: Health, Planner, Business, Ultimate.
(Finance Bundle already exists at listing 4524283886)
Run: python create_missing_bundles.py
"""
import io, json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_missing_bundles.json"

BUNDLES = [
    {
        "key": "health_bundle",
        "title": "Complete Health Transformation System | Workout + Meals + Habits | 3 Google Sheets | Instant Download",
        "included": [
            ("Gym & Workout Tracking System",  "Log every session, track PRs, see progress automatically"),
            ("Weekly Meal Planning System",    "Plan 7 days of meals in 15 min + auto grocery list"),
            ("30-Day Habit Building System",   "Track 30 habits simultaneously with auto streak counter"),
        ],
        "individual_total": 36,
        "price": 17.99,
        "tags": [
            "health bundle", "workout tracker", "meal planner",
            "habit tracker", "fitness bundle", "google sheets bundle",
            "wellness tracker", "health system", "fitness system",
            "workout meal habits", "instant download", "digital download",
            "health templates",
        ],
        "section": "Health & Fitness",
    },
    {
        "key": "planner_bundle",
        "title": "Complete Planning & Productivity System | Weekly + Student + Goals | 3 Google Sheets | Instant Download",
        "included": [
            ("Weekly Productivity System",         "Time blocking, priorities & energy management"),
            ("Student Academic Success System",    "Grades, GPA, assignments & exam prep"),
            ("Annual Goals & 90-Day Action System","Break big goals into weekly steps"),
        ],
        "individual_total": 36,
        "price": 17.99,
        "tags": [
            "planner bundle", "weekly planner", "student planner",
            "goal planner", "productivity bundle", "google sheets bundle",
            "planning system", "productivity system", "life planner",
            "student goals weekly", "instant download", "digital download",
            "planner templates",
        ],
        "section": "Planners & Productivity",
    },
    {
        "key": "business_bundle",
        "title": "Complete Creator Business System | Content + Invoices + Budget | 3 Google Sheets | Instant Download",
        "included": [
            ("Content Creator Business System",  "Content calendar, analytics & brand deal tracker"),
            ("Freelancer Invoice & Client System","Invoices, clients, payments & tax prep"),
            ("Monthly Budget & Expense System",   "Track income, expenses & savings goals"),
        ],
        "individual_total": 43,
        "price": 21.99,
        "tags": [
            "creator business bundle", "content creator", "invoice tracker",
            "budget tracker", "freelancer bundle", "google sheets bundle",
            "business system", "creator tools", "entrepreneur bundle",
            "content invoice budget", "instant download", "digital download",
            "business templates",
        ],
        "section": "Business & Career",
    },
    {
        "key": "ultimate_bundle",
        "title": "The Complete Life System | All 10 Google Sheets | Finance Health Business Planning | Save 50%",
        "included": [
            ("Monthly Budget & Expense System",        "Track income, expenses & savings"),
            ("30-Day Habit Building System",           "30 habits + auto streaks"),
            ("Weekly Meal Planning System",            "7-day meals + grocery list"),
            ("Complete Wedding Planning System",       "Budget, guests, vendors & timeline"),
            ("Gym & Workout Tracking System",          "Sessions, PRs & progress charts"),
            ("Content Creator Business System",        "Content calendar & brand deals"),
            ("Freelancer Invoice & Client System",     "Clients, invoices & tax prep"),
            ("Student Academic Success System",        "Grades, GPA & study schedule"),
            ("Annual Goals & 90-Day Action System",    "Goals → weekly steps"),
            ("Weekly Productivity System",             "Time blocking & priorities"),
        ],
        "individual_total": 120,
        "price": 39.99,
        "tags": [
            "ultimate bundle", "complete life system", "google sheets bundle",
            "all templates", "mega bundle", "10 templates",
            "finance health business", "complete bundle", "google sheets",
            "best value bundle", "instant download", "digital download",
            "productivity bundle",
        ],
        "section": "Bundle Sets",
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
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}


def fetch_sections(token):
    r = requests.get(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/sections",
        headers=auth_headers(token), timeout=15,
    )
    return {s["title"]: s["shop_section_id"] for s in r.json().get("results", [])} if r.ok else {}


def get_taxonomy_id(token):
    r = requests.get(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
        headers=auth_headers(token), params={"limit": 1}, timeout=15,
    )
    if r.ok:
        results = r.json().get("results", [])
        if results:
            return results[0].get("taxonomy_id", 2078)
    return 2078


def build_description(bundle):
    pct = int((1 - bundle["price"] / bundle["individual_total"]) * 100)
    lines = [
        f"Get {len(bundle['included'])} premium Google Sheets systems at {pct}% off.",
        f"Individual value: €{bundle['individual_total']:.2f} — yours for €{bundle['price']:.2f}.\n",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "✅ WHAT'S INCLUDED:\n",
    ]
    for i, (name, desc) in enumerate(bundle["included"], 1):
        lines.append(f"{i}. {name}")
        lines.append(f"   → {desc}\n")
    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "📥 HOW IT WORKS:\n",
        "1. Purchase — you'll receive instant access",
        "2. Open the Google Sheets link in your confirmation",
        "3. File > Make a Copy → yours forever\n",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "⚡ ALL TEMPLATES INCLUDE:\n",
        "• Works on Google Sheets (FREE) & Microsoft Excel",
        "• Auto-calculating formulas — no manual math",
        "• Fully customizable colors, text & layout",
        "• Step-by-step setup guide included",
        "• Lifetime access — buy once, use forever",
        "• No subscription, no app, no extra cost\n",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "💬 Questions? Message us — we reply within 24 hours. ♥",
        "\nnasritools.etsy.com | Systems That Run Your Life",
    ]
    return "\n".join(lines)


def build_delivery_file(bundle):
    lines = [
        f"NasriTools — {bundle['title'].split('|')[0].strip()}",
        "=" * 60,
        "",
        "Thank you for your purchase! Below are your Google Sheets links.",
        "Open each link → File → Make a Copy → it's yours forever.",
        "",
        "=" * 60,
        "YOUR TEMPLATES:",
        "=" * 60,
        "",
    ]
    for i, (name, desc) in enumerate(bundle["included"], 1):
        lines.append(f"{i}. {name}")
        lines.append(f"   {desc}")
        lines.append(f"   → Link: [UPDATE WITH ACTUAL GOOGLE SHEETS LINK]")
        lines.append("")
    lines += [
        "=" * 60,
        "NEED HELP?",
        "Message us on Etsy — we reply within 24 hours.",
        "nasritools.etsy.com",
        "",
        "⭐ Enjoying your templates? A quick review means the world to us!",
    ]
    return "\n".join(lines)


def upload_file(token, listing_id, bundle):
    content = build_delivery_file(bundle).encode("utf-8")
    fname   = f"{bundle['key']}_delivery.txt"
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/files",
        headers=auth_headers(token),
        files={"file": (fname, io.BytesIO(content), "text/plain")},
        data={"name": fname, "rank": 1},
        timeout=30,
    )
    return r.ok


def create_listing(token, bundle, taxonomy_id, section_id):
    payload = {
        "quantity":    999,
        "title":       bundle["title"][:140],
        "description": build_description(bundle),
        "price":       bundle["price"],
        "who_made":    "i_did",
        "when_made":   "2020_2026",
        "taxonomy_id": taxonomy_id,
        "type":        "download",
        "tags":        bundle["tags"][:13],
        "state":       "draft",
    }
    if section_id:
        payload["shop_section_id"] = section_id
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json=payload, timeout=30,
    )
    return r


def activate_listing(token, listing_id):
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"state": "active"}, timeout=30,
    )
    return r.ok


def main():
    done  = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Create Missing Bundle Listings")
    print(f"  Creating: Health, Planner, Business, Ultimate")
    print(f"{'='*65}\n")

    taxonomy_id = get_taxonomy_id(token)
    sections    = fetch_sections(token)
    print(f"  Taxonomy: {taxonomy_id}")
    print(f"  Sections found: {list(sections.keys())}\n")

    ok = 0
    for i, bundle in enumerate(BUNDLES, 1):
        key = bundle["key"]
        if key in done:
            print(f"[{i}/{len(BUNDLES)}] SKIP (already created): {key}  [{done[key]}]")
            ok += 1
            continue

        print(f"[{i}/{len(BUNDLES)}] Creating: {bundle['title'][:60]}…")

        section_id = sections.get(bundle["section"])
        token = get_token()

        r = create_listing(token, bundle, taxonomy_id, section_id)
        if not r.ok:
            print(f"  ERROR creating listing: {r.status_code}: {r.text[:200]}")
            continue

        lid = r.json().get("listing_id")
        print(f"  Draft created: [{lid}]")
        time.sleep(1)

        token = get_token()
        file_ok = upload_file(token, lid, bundle)
        print(f"  File uploaded: {'✓' if file_ok else '✗'}")
        time.sleep(1)

        if file_ok:
            token = get_token()
            act_ok = activate_listing(token, lid)
            print(f"  Activated:     {'✓' if act_ok else '✗ (remains as draft)'}")
        else:
            act_ok = False

        done[key] = lid
        DONE_FILE.write_text(json.dumps(done, indent=2))
        print(f"  → https://www.etsy.com/listing/{lid}\n")
        if act_ok:
            ok += 1
        time.sleep(1.5)
        token = get_token()

    print(f"{'='*65}")
    print(f"  Done: {ok}/{len(BUNDLES)} bundles created and activated")
    print(f"\n  IMPORTANT — Update delivery files with real Google Sheets links:")
    print(f"  Etsy → Shop Manager → Listings → Edit each bundle → Digital Files")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
