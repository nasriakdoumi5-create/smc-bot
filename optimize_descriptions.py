"""
NasriTools - Optimize Descriptions for ALL 119 Etsy Listings
Generates and applies professional SEO-optimized descriptions via Etsy API v3.

Run: python optimize_descriptions.py
"""
import json
import os
import time
import urllib.parse
from pathlib import Path

import requests

# ── Credentials ────────────────────────────────────────────────────────────────

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_desc_done.json"

# ── Category definitions ────────────────────────────────────────────────────────

CATEGORIES = {
    "bundle": {
        "keywords": ["bundle", "system pack", "complete pack", "collection", "mega pack",
                     "ultimate pack", "full pack", "all-in-one"],
        "bullets": [
            "Multiple professional templates included",
            "All sheets auto-linked and synced",
            "Works on phone, tablet & desktop",
            "Instant download — all files in one purchase",
            "Lifetime access — buy once, use forever",
            "Fully customizable to your needs",
        ],
        "target": (
            "People who want a complete, done-for-you system\n"
            "→ Entrepreneurs managing multiple areas of life\n"
            "→ Busy professionals who value their time\n"
            "→ Anyone who wants every tool in one place"
        ),
    },
    "finance": {
        "keywords": ["budget", "expense", "finance", "financial", "money", "savings",
                     "net worth", "cash flow", "income", "spending", "wealth"],
        "bullets": [
            "Monthly budget dashboard — see everything at a glance",
            "12 monthly sheets — full-year tracking",
            "50+ expense categories — covers every spending area",
            "Savings goal tracker with progress bar",
            "Bill payment tracker with due dates",
            "Net worth calculator — assets vs liabilities",
        ],
        "target": (
            "Freelancers tracking income & business expenses\n"
            "→ Families managing household budgets\n"
            "→ Anyone wanting full financial clarity\n"
            "→ People trying to save more and spend less"
        ),
    },
    "invoice": {
        "keywords": ["invoice", "billing", "freelancer finance", "client tracker",
                     "payment tracker", "revenue tracker", "freelance tracker"],
        "bullets": [
            "Client database — all contacts in one place",
            "Invoice tracker with status (paid / pending / overdue)",
            "Auto revenue totals — monthly & annual summaries",
            "Time tracking per project with rate calculator",
            "Full payment history per client",
            "Overdue alerts — never miss a late payment again",
        ],
        "target": (
            "Freelancers who bill clients and need to stay organized\n"
            "→ Consultants and independent contractors\n"
            "→ Agencies tracking multiple client accounts\n"
            "→ Anyone who is self-employed"
        ),
    },
    "kpi": {
        "keywords": ["kpi", "dashboard", "performance", "metrics", "business tracker",
                     "revenue tracking", "growth tracker", "analytics", "crm", "sales tracker",
                     "pipeline", "business dashboard"],
        "bullets": [
            "Live KPI dashboard — all metrics in one view",
            "Revenue & growth tracking (month over month)",
            "Team performance metrics by person or department",
            "Monthly targets vs actual — spot gaps instantly",
            "Visual charts that auto-update when you enter data",
            "Pipeline tracking from lead to closed deal",
        ],
        "target": (
            "Business owners who want data-driven decisions\n"
            "→ Managers tracking team and company performance\n"
            "→ Entrepreneurs monitoring growth and revenue\n"
            "→ E-commerce sellers analyzing store metrics"
        ),
    },
    "fitness": {
        "keywords": ["fitness", "workout", "gym", "exercise", "calorie", "nutrition",
                     "body", "weight loss", "muscle", "training", "health tracker",
                     "meal plan", "diet", "sleep", "macro", "cardio", "sport"],
        "bullets": [
            "Workout logging — sets, reps & weight per session",
            "Auto streak counter — stay motivated every day",
            "Progress charts — see strength gains visually",
            "Nutrition & calorie tracker with macro breakdown",
            "Sleep tracker — rest is part of the plan",
            "Body measurements log — track every change",
        ],
        "target": (
            "Gym-goers who want to track and beat their records\n"
            "→ People building healthy habits and routines\n"
            "→ Fitness enthusiasts following a structured program\n"
            "→ Anyone who wants results, not just effort"
        ),
    },
    "productivity": {
        "keywords": ["productivity", "planner", "habit", "weekly", "goal", "schedule",
                     "task", "routine", "student", "to-do", "todo", "project", "time",
                     "daily", "organizer", "work", "study", "academic", "assignment",
                     "event", "wedding", "content creator", "social media", "rental",
                     "property", "meal", "crm", "contact"],
        "bullets": [
            "Weekly overview Mon-Sun — plan your entire week in one view",
            "Daily priority lists — focus on what actually matters",
            "Monthly goals tracker — stay aligned with big-picture goals",
            "Habit tracker — build streaks and routines that stick",
            "Focus time blocks — protect deep work hours",
            "Review & reflection sections — improve week over week",
        ],
        "target": (
            "Students juggling classes, assignments and exams\n"
            "→ Professionals who want more productive weeks\n"
            "→ Entrepreneurs managing business and personal goals\n"
            "→ Anyone who wants to plan better and stress less"
        ),
    },
}

# Keyword detection priority order (bundle first to catch bundle listings early)
CATEGORY_PRIORITY = ["bundle", "invoice", "kpi", "finance", "fitness", "productivity"]

# ── Auth ────────────────────────────────────────────────────────────────────────

def get_token() -> dict:
    """Load token from file, refresh if expired."""
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post(
            "https://api.etsy.com/v3/public/oauth/token",
            data={
                "grant_type":    "refresh_token",
                "client_id":     CLIENT_ID,
                "refresh_token": t["refresh_token"],
            },
            timeout=30,
        )
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
        print("  [token refreshed]")
    return t


def auth_headers(token: dict) -> dict:
    return {
        "Authorization": "Bearer " + token["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }


# ── Listings ────────────────────────────────────────────────────────────────────

def fetch_all_active_listings(token: dict) -> list:
    """Fetch all active listings with pagination."""
    listings = []
    offset = 0
    limit = 100
    while True:
        r = requests.get(
            f"{API}/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": limit, "offset": offset},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        batch = data.get("results", [])
        listings.extend(batch)
        print(f"  Fetched {len(listings)} listings so far...")
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(0.5)
    return listings


# ── Category detection ──────────────────────────────────────────────────────────

def detect_category(title: str) -> str:
    """Return the best-matching category key for a listing title."""
    title_lower = title.lower()
    for cat in CATEGORY_PRIORITY:
        for kw in CATEGORIES[cat]["keywords"]:
            if kw in title_lower:
                return cat
    # Default fallback
    return "productivity"


# ── Description generator ───────────────────────────────────────────────────────

def generate_description(title: str, category: str) -> str:
    """Build a professional SEO-optimized description from the template."""
    cat = CATEGORIES[category]

    # Strip trailing noise like "| Digital Download", "| Google Sheets Template", etc.
    # and use the title as the product name
    product_name = title.strip()

    bullets_text = "\n".join(f"✅ {b}" for b in cat["bullets"])
    target_text  = cat["target"]

    description = (
        f"{product_name} — Professional Google Sheets Template\n"
        "\n"
        "✅ INSTANT DOWNLOAD — Start using in 2 minutes\n"
        "✅ Works FREE on Google Sheets + Microsoft Excel\n"
        "✅ Works on Phone, Tablet & Desktop — no app needed\n"
        "✅ No formula knowledge required — fully automated\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 WHAT'S INCLUDED:\n"
        f"{bullets_text}\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 HOW TO GET STARTED (2 minutes):\n"
        "1. Complete purchase → instant download link from Etsy\n"
        "2. Open sheets.google.com → File → Import → Upload your file\n"
        "3. Add your data and start tracking immediately\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 PERFECT FOR:\n"
        f"{target_text}\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "❓ NEED HELP?\n"
        "Message us on Etsy — we reply within 24 hours.\n"
        "We're happy to help customize anything for your needs.\n"
        "\n"
        "⭐ LOVING IT?\n"
        "A quick review takes 30 seconds and helps us grow as a small shop!\n"
        "\n"
        "© NasriTools — nasritools.etsy.com"
    )
    return description


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    # Load done set (list of listing IDs that were already processed)
    if DONE_FILE.exists():
        done: set = set(json.loads(DONE_FILE.read_text()))
    else:
        done: set = set()

    print(f"\n{'='*60}")
    print(f"  NasriTools - Optimize Descriptions  [all 119 listings]")
    print(f"  Already done: {len(done)}")
    print(f"{'='*60}\n")

    print("Fetching token...")
    token = get_token()

    print("Fetching all active listings...")
    try:
        listings = fetch_all_active_listings(token)
    except requests.HTTPError as exc:
        print(f"ERROR fetching listings: {exc}")
        return

    total = len(listings)
    print(f"\nFound {total} active listings. Starting updates...\n")

    ok   = 0
    fail = 0
    skip = 0

    for idx, listing in enumerate(listings, 1):
        lid   = listing["listing_id"]
        title = listing.get("title", "").strip()

        # Skip if already done
        if lid in done:
            print(f"[{idx:03d}/{total}] SKIP {lid} — {title[:55]}")
            skip += 1
            continue

        # Refresh token before every batch of 20
        if (idx - 1) % 20 == 0 and idx > 1:
            print(f"\n  [Refreshing token at listing {idx}...]\n")
            token = get_token()

        category    = detect_category(title)
        description = generate_description(title, category)

        r = requests.patch(
            f"{API}/shops/{SHOP_ID}/listings/{lid}",
            headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
            data=f"description={urllib.parse.quote(description, safe='')}",
            timeout=30,
        )

        time.sleep(0.8)

        short_title = title[:55] + ("..." if len(title) > 55 else "")
        if r.ok:
            ok += 1
            done.add(lid)
            DONE_FILE.write_text(json.dumps(sorted(done), indent=2))
            print(f"[{idx:03d}/{total}] [{category:12s}] {short_title} ... OK")
        else:
            fail += 1
            print(f"[{idx:03d}/{total}] [{category:12s}] {short_title} ... FAIL {r.status_code}: {r.text[:100]}")

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"  Updated : {ok}")
    print(f"  Failed  : {fail}")
    print(f"  Skipped : {skip}  (already done)")
    print(f"  Total   : {total}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
