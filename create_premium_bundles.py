"""
create_premium_bundles.py
Creates 4 new premium OS bundles with updated pricing and full descriptions.
These replace/complement the old basic bundles with better positioning.
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
        "title": "Complete Finance OS | Budget + Invoice + Cash Flow + Profit + Debt Google Sheets Bundle",
        "price": 49.99,
        "tags": [
            "finance bundle", "budget spreadsheet", "invoice tracker",
            "cash flow tracker", "profit loss tracker", "debt payoff planner",
            "google sheets bundle", "finance template", "spreadsheet bundle",
            "personal finance", "budget planner", "financial tracker", "money system"
        ],
        "description": """⚡ INSTANT DOWNLOAD — Complete Finance OS — 5 Systems in One Bundle

Stop buying finance tools one by one. Get every spreadsheet you need to manage your money like a CFO — for one simple price.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WHAT'S INCLUDED (5 Systems):

1. Budget & Expense Tracker — Track income, expenses, and savings automatically
2. Invoice & Client Tracker — Manage clients, invoices, and payment status
3. Cash Flow Forecast — See your money flow 12 months ahead
4. Profit & Loss Tracker — Know exactly if your finances are growing
5. Debt Payoff Planner — Eliminate debt faster with snowball strategy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Individual value: €105+ | You pay: €49.99 | You save: 52%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ KEY FEATURES:
• 100% Google Sheets — works on any device, no software needed
• Auto-calculating formulas — just enter your numbers
• Mobile-friendly — works on phone and tablet
• Lifetime access — buy once, use forever
• No subscription fees

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT — HOW TO ACCESS YOUR FILE:

Step 1: After purchase, open your Etsy receipt and click the download link
Step 2: The file opens in Google Sheets (free Google account required)
Step 3: Click File → Make a Copy → saved to your Google Drive
Step 4: Start using immediately — fully editable

🔵 On Mobile: If the Etsy app doesn't show the download, open Etsy in your phone browser (Chrome/Safari) instead of the app.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ FAQ:
Q: Do I need Microsoft Excel? A: No — Google Sheets only. Free Google account required.
Q: Can I use this on my phone? A: Yes. Google Sheets works on iPhone and Android.
Q: Is this a one-time payment? A: Yes. No subscription, no recurring fees.
Q: What if I need help? A: Message us on Etsy — we reply within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ YOU MAY ALSO LIKE:
→ Complete Life System (All 10 Tools) — nasritools.etsy.com
→ Business Starter Kit Bundle — nasritools.etsy.com
→ Freelancer OS Bundle — nasritools.etsy.com

© NasriTools — Professional Google Sheets Templates
""",
    },
    {
        "title": "Freelancer OS | Invoice + Time Tracking + Content Planner + Social Media Google Sheets Bundle",
        "price": 39.99,
        "tags": [
            "freelancer tools", "invoice tracker", "time tracking spreadsheet",
            "content planner", "social media tracker", "freelance bundle",
            "google sheets bundle", "client tracker", "creator tools",
            "freelance template", "income tracker", "business tracker", "work planner"
        ],
        "description": """⚡ INSTANT DOWNLOAD — Freelancer OS — Run Your Entire Freelance Business in Google Sheets

No expensive software needed. Everything a freelancer needs — clients, invoices, time, content, income — in one bundle.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WHAT'S INCLUDED (5 Systems):

1. Invoice & Client Tracker — Track clients, invoices, payment status
2. Time Tracking Timesheet — Log hours by project, auto-calculate earnings
3. Content Creator Planner — Plan and schedule content across platforms
4. Social Media Analytics — Track followers, engagement, and growth
5. Annual Income Summary — Tax-ready income report

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Individual value: €86+ | You pay: €39.99 | You save: 53%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ PERFECT FOR: Freelancers, consultants, content creators, virtual assistants, graphic designers, copywriters

⚠️ HOW TO ACCESS:
Step 1: Etsy receipt → click download link
Step 2: File opens in Google Sheets → File → Make a Copy
Step 3: Start immediately

🔵 Mobile: Open Etsy in Chrome/Safari browser, not the app

✨ YOU MAY ALSO LIKE:
→ Complete Finance OS Bundle — nasritools.etsy.com
→ Complete Life System (All 10 Tools) — nasritools.etsy.com

© NasriTools — Professional Google Sheets Templates
""",
    },
    {
        "title": "Complete Health OS | Workout + Meal Planner + Habit + Sleep + Weight Loss Google Sheets Bundle",
        "price": 34.99,
        "tags": [
            "health bundle", "workout tracker", "meal planner",
            "habit tracker", "sleep tracker", "weight loss tracker",
            "google sheets bundle", "fitness bundle", "health spreadsheet",
            "wellness planner", "fitness planner", "health tracker", "body tracker"
        ],
        "description": """⚡ INSTANT DOWNLOAD — Complete Health OS — Transform Your Body and Habits

Everything you need to get fit, eat better, sleep deeper, and build lasting habits — in one Google Sheets bundle.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WHAT'S INCLUDED (5 Systems):

1. Workout Tracker — 12-week progressive training with auto-tracking
2. Meal Planner — Weekly meal planning + grocery list
3. Habit Tracker — Build any habit in 30 days with visual streaks
4. Sleep Tracker — Monitor sleep quality and patterns
5. Weight Loss Tracker — Track weight, BMI, body measurements

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Individual value: €75+ | You pay: €34.99 | You save: 53%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ PERFECT FOR: Anyone starting a fitness journey, meal preppers, habit-builders, weight loss tracking

⚠️ HOW TO ACCESS:
Step 1: Etsy receipt → click download link
Step 2: File opens in Google Sheets → File → Make a Copy
Step 3: Start immediately on any device

✨ YOU MAY ALSO LIKE:
→ Keto Diet Tracker — nasritools.etsy.com
→ Complete Life System — nasritools.etsy.com

© NasriTools — Professional Google Sheets Templates
""",
    },
    {
        "title": "Business Starter Kit | KPI Dashboard + Sales + Marketing ROI + Cash Flow + Profit Google Sheets",
        "price": 54.99,
        "tags": [
            "business bundle", "kpi dashboard", "sales tracker",
            "marketing tracker", "cash flow tracker", "profit loss tracker",
            "google sheets bundle", "business template", "analytics sheet",
            "business planner", "revenue tracker", "business spreadsheet", "performance tracker"
        ],
        "description": """⚡ INSTANT DOWNLOAD — Business Starter Kit — Run Your Business Like a CEO

No expensive CRM or BI software needed. Track KPIs, sales, marketing, cash flow, and profit — all in Google Sheets.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WHAT'S INCLUDED (5 Systems):

1. KPI Dashboard — All key business metrics on one screen with live charts
2. Sales Commission Tracker — Track deals, reps, and commissions
3. Marketing ROI Tracker — Measure every campaign and ad spend
4. Cash Flow Tracker — 12-month cash flow forecast
5. Profit & Loss Tracker — Monthly and annual P&L statement

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Individual value: €110+ | You pay: €54.99 | You save: 50%
vs. HubSpot/Salesforce: $100-300/month → you pay once, forever.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ PERFECT FOR: Small business owners, startups, sales managers, entrepreneurs replacing expensive SaaS tools

⚠️ HOW TO ACCESS:
Step 1: Etsy receipt → click download link
Step 2: File opens in Google Sheets → File → Make a Copy
Step 3: Start immediately — no setup required

✨ YOU MAY ALSO LIKE:
→ Complete Finance OS Bundle — nasritools.etsy.com
→ Complete Life System (All 10 Tools) — nasritools.etsy.com

© NasriTools — Professional Google Sheets Templates
""",
    },
    {
        "title": "Productivity OS | Weekly Planner + Goals + Student Planner + Project Tracker Google Sheets Bundle",
        "price": 34.99,
        "tags": [
            "productivity bundle", "weekly planner", "goal planner",
            "student planner", "project tracker", "annual review",
            "google sheets bundle", "planner bundle", "productivity template",
            "time management", "task planner", "life planner", "organizer bundle"
        ],
        "description": """⚡ INSTANT DOWNLOAD — Productivity OS — Plan, Focus, and Achieve More

Stop scattered to-do lists. Build a complete productivity system with weekly planning, goal tracking, project management, and annual reviews.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WHAT'S INCLUDED (5 Systems):

1. Weekly Planner — Time-blocking, priorities, and task management
2. 90-Day Goals & Action Planner — Break big goals into daily actions
3. Student Academic Planner — Grades, assignments, exams, and GPA
4. Project Tracker — Milestones, deadlines, and task lists
5. Annual Review Planner — Reflect, plan, and design your year

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Individual value: €75+ | You pay: €34.99 | You save: 53%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ PERFECT FOR: Students, remote workers, freelancers, entrepreneurs, goal-setters

⚠️ HOW TO ACCESS:
Step 1: Etsy receipt → click download link
Step 2: File opens in Google Sheets → File → Make a Copy
Step 3: Start immediately on any device

✨ YOU MAY ALSO LIKE:
→ Complete Life System (All 10 Tools) — nasritools.etsy.com
→ Freelancer OS Bundle — nasritools.etsy.com

© NasriTools — Professional Google Sheets Templates
""",
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

def get_taxonomy_id(token):
    listings = []
    r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                     headers=auth_headers(token), params={"limit": 1})
    if r.ok:
        results = r.json().get("results", [])
        if results:
            return results[0].get("taxonomy_id", 2078)
    return 2078

def create_listing(token, bundle, taxonomy_id):
    tags = bundle["tags"][:13]
    parts = [
        f"title={urllib.parse.quote(bundle['title'][:140])}",
        f"description={urllib.parse.quote(bundle['description'])}",
        f"price={urllib.parse.quote(str(bundle['price']))}",
        f"quantity=999",
        f"who_made=i_did",
        f"when_made=made_to_order",
        f"taxonomy_id={taxonomy_id}",
        f"type=download",
        f"state=draft",
        f"should_auto_renew=true",
    ]
    for tag in tags:
        parts.append(f"tags[]={urllib.parse.quote(tag, safe='')}")

    r = requests.post(
        f"{API}/shops/{SHOP_ID}/listings",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data="&".join(parts),
        timeout=30,
    )
    return r.ok, r.status_code, r.json() if r.ok else r.text[:300]

def main():
    print("=" * 65)
    print("  NasriTools — Create Premium OS Bundles (New Strategy)")
    print("=" * 65)
    token = get_token()
    taxonomy_id = get_taxonomy_id(token)
    print(f"[*] Using taxonomy_id: {taxonomy_id}\n")

    ok = fail = 0
    for i, b in enumerate(BUNDLES, 1):
        print(f"[{i}/{len(BUNDLES)}] {b['title'][:55]}...")
        token = get_token()
        r_ok, code, result = create_listing(token, b, taxonomy_id)
        if r_ok:
            lid = result.get("listing_id", "?")
            print(f"  [OK] Draft created — ID: {lid}")
            print(f"       → etsy.com/your/shops/me/listing-editor/edit/{lid}")
            ok += 1
        else:
            print(f"  [FAIL] HTTP {code}: {result}")
            fail += 1
        time.sleep(2)

    print(f"\n{'='*65}")
    print(f"  Created: {ok} | Failed: {fail}")
    print(f"\n  NEXT STEPS:")
    print(f"  1. python generate_thumbnails.py  → generates images in ./thumbnails/")
    print(f"  2. Open each draft in Etsy Shop Manager")
    print(f"  3. Upload the matching thumbnail image")
    print(f"  4. Click Publish to make it active")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
