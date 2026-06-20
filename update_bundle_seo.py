"""
update_bundle_seo.py
Updates SEO (title + description + tags) for all 5 bundle listings
using listing_id directly — no keyword search needed.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

BUNDLES = [
    {
        "listing_id": 4524283886,
        "title": "Finance Bundle Google Sheets | Budget + Invoice + Goals Tracker | 3 Templates | Save 33% | Instant Download",
        "tags": ["finance bundle", "budget tracker", "invoice tracker", "google sheets", "goals planner", "finance templates", "freelancer tools", "digital download", "money tracker", "business finance", "spreadsheet bundle", "personal finance", "instant download"],
        "description": """Take total control of your finances — in one bundle.

This Finance Bundle gives you 3 of our most powerful Google Sheets templates at a 33% discount. Everything you need to track your money, get paid on time, and reach every financial goal.

━━━━━━━━━━━━━━━━━━━━━━━━━
📦 WHAT'S IN THE BUNDLE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Budget & Expense Tracker
   → Monthly dashboard, daily log, savings goals, 12-month summary

✅ Invoice & Client Manager
   → Track paid/pending/overdue, client CRM, tax prep sheet

✅ Goals & 90-Day Action Planner
   → Annual goals dashboard, weekly action steps, auto progress %

━━━━━━━━━━━━━━━━━━━━━━━━━
💰 BUNDLE VALUE
━━━━━━━━━━━━━━━━━━━━━━━━━

Individual price: €37  →  Bundle: €19.99  (Save 33%)

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click each Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Do I get all 3 templates at once?
A: Yes. You receive all 3 template links in one PDF instantly.

Q: Is this a physical product?
A: No. This is a digital download — instant access after purchase.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

→ See all templates: nasritools.etsy.com""",
    },
    {
        "listing_id": 4524724720,
        "title": "Health Bundle Google Sheets | Workout + Meal Planner + Habit Tracker | 3 Templates | Save 50% | Instant Download",
        "tags": ["health bundle", "workout tracker", "meal planner", "habit tracker", "google sheets", "fitness templates", "health planner", "digital download", "gym tracker", "nutrition planner", "habit builder", "spreadsheet bundle", "instant download"],
        "description": """Transform your health — one system at a time.

This Health Bundle gives you 3 of our most powerful Google Sheets templates at a 50% discount. Track every workout, plan every meal, and build 30 habits automatically.

━━━━━━━━━━━━━━━━━━━━━━━━━
📦 WHAT'S IN THE BUNDLE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Gym & Workout Tracker
   → Exercise log, PR tracker, volume calculator, progress charts

✅ Weekly Meal Planner
   → 7-day plan, auto grocery list, calorie counter, pantry tracker

✅ 30-Day Habit Builder
   → Track 20 habits daily, auto streak counter, visual dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━
💰 BUNDLE VALUE
━━━━━━━━━━━━━━━━━━━━━━━━━

Individual price: €36  →  Bundle: €17.99  (Save 50%)

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click each Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Do I get all 3 templates at once?
A: Yes. You receive all 3 template links in one PDF instantly.

Q: Is this a physical product?
A: No. This is a digital download — instant access after purchase.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

→ See all templates: nasritools.etsy.com""",
    },
    {
        "listing_id": 4524724758,
        "title": "Productivity Bundle Google Sheets | Weekly Planner + Student + Goals Tracker | 3 Templates | Save 50% | Instant Download",
        "tags": ["productivity bundle", "weekly planner", "student planner", "goals tracker", "google sheets", "productivity templates", "time management", "digital download", "academic planner", "study planner", "goal planner", "spreadsheet bundle", "instant download"],
        "description": """Master your time. Ace your semester. Reach every goal.

This Productivity Bundle gives you 3 of our most powerful Google Sheets templates at a 50% discount. Plan your perfect week, track your grades, and achieve every goal you set.

━━━━━━━━━━━━━━━━━━━━━━━━━
📦 WHAT'S IN THE BUNDLE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Weekly Productivity System
   → Time-blocking, top 3 priorities, task tracker, weekly review

✅ Student Academic Planner
   → Assignment tracker, live GPA calculator, exam countdown

✅ Goals & 90-Day Action Planner
   → Annual dashboard, 90-day sprints, auto progress %

━━━━━━━━━━━━━━━━━━━━━━━━━
💰 BUNDLE VALUE
━━━━━━━━━━━━━━━━━━━━━━━━━

Individual price: €36  →  Bundle: €17.99  (Save 50%)

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click each Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Do I get all 3 templates at once?
A: Yes. You receive all 3 template links in one PDF instantly.

Q: Is this a physical product?
A: No. This is a digital download — instant access after purchase.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

→ See all templates: nasritools.etsy.com""",
    },
    {
        "listing_id": 4524724798,
        "title": "Business Bundle Google Sheets | Content Creator + Invoice + Budget Tracker | 3 Templates | Save 50% | Instant Download",
        "tags": ["business bundle", "content creator", "invoice tracker", "budget tracker", "google sheets", "business templates", "freelancer tools", "digital download", "social media planner", "client tracker", "creator tools", "spreadsheet bundle", "instant download"],
        "description": """Run your entire business — in three Google Sheets.

This Business Bundle gives you 3 of our most powerful Google Sheets templates at a 50% discount. Grow your audience, manage your clients, and know your numbers at all times.

━━━━━━━━━━━━━━━━━━━━━━━━━
📦 WHAT'S IN THE BUNDLE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Content Creator Business System
   → 90-day content calendar, analytics tracker, brand deal CRM

✅ Invoice & Client Manager
   → Track paid/pending/overdue, client CRM, tax prep sheet

✅ Budget & Expense Tracker
   → Monthly dashboard, daily log, savings goals, 12-month summary

━━━━━━━━━━━━━━━━━━━━━━━━━
💰 BUNDLE VALUE
━━━━━━━━━━━━━━━━━━━━━━━━━

Individual price: €43  →  Bundle: €21.99  (Save 50%)

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click each Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Do I get all 3 templates at once?
A: Yes. You receive all 3 template links in one PDF instantly.

Q: Is this a physical product?
A: No. This is a digital download — instant access after purchase.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

→ See all templates: nasritools.etsy.com""",
    },
    {
        "listing_id": 4524724846,
        "title": "Complete Life System Google Sheets | All 10 Templates Bundle | Finance Health Business Planning | Save 65% | Instant Download",
        "tags": ["complete bundle", "google sheets bundle", "life planner", "all in one planner", "finance health", "productivity bundle", "digital download", "google sheets", "template bundle", "life system", "spreadsheet bundle", "10 templates", "instant download"],
        "description": """Every system you'll ever need — in one bundle.

This is our flagship product. The Complete Life System gives you all 10 of our premium Google Sheets templates at a 65% discount. Finance, health, business, productivity — everything runs on one system.

━━━━━━━━━━━━━━━━━━━━━━━━━
📦 ALL 10 TEMPLATES INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━

💰 FINANCE
✅ Budget & Expense Tracker
✅ Invoice & Client Manager
✅ Goals & 90-Day Action Planner

💪 HEALTH
✅ Gym & Workout Tracker
✅ Weekly Meal Planner
✅ 30-Day Habit Builder

💼 BUSINESS
✅ Content Creator Business System

🗓️ PLANNING
✅ Weekly Productivity System
✅ Student Academic Planner
✅ Wedding Planner

━━━━━━━━━━━━━━━━━━━━━━━━━
💰 BUNDLE VALUE
━━━━━━━━━━━━━━━━━━━━━━━━━

Individual price: €120  →  Bundle: €39.99  (Save 65%)

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click each Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Do I get all 10 templates at once?
A: Yes. You receive all 10 template links in one PDF instantly after purchase.

Q: Is this a physical product?
A: No. This is a digital download — instant access after purchase.

Q: Can I customize the templates?
A: Yes. Everything is fully editable — colors, categories, data.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

→ See all templates: nasritools.etsy.com""",
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


def update_listing(token, lid, title, description, tags):
    payload = {"title": title[:140], "description": description}
    base    = urllib.parse.urlencode(payload)
    tag_str = "&".join("tags[]=" + urllib.parse.quote(t, safe="") for t in tags[:13])
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=base + "&" + tag_str,
        timeout=30,
    )
    return r.ok, r.status_code


def main():
    print("=" * 60)
    print("  NasriTools — Bundle SEO Update (5 bundles)")
    print("=" * 60)
    token = get_token()
    ok = 0
    for i, b in enumerate(BUNDLES, 1):
        lid = b["listing_id"]
        print(f"\n[{i}/5] Listing {lid}")
        print(f"  Title: {b['title'][:60]}...")
        token = get_token()
        success, code = update_listing(token, lid, b["title"], b["description"], b["tags"])
        if success:
            print(f"  OK (HTTP {code})")
            ok += 1
        else:
            print(f"  FAILED (HTTP {code})")
        time.sleep(1)
    print(f"\n{'='*60}")
    print(f"  Done: {ok}/5 bundles updated")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
