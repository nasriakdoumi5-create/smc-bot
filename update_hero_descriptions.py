"""
update_hero_descriptions.py
Replaces descriptions of the 5 Hero Products with premium, high-converting copy.
Target: Budget Tracker, Invoice Tracker, KPI Dashboard, Complete Life System, Finance Bundle
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

MARKER = "NASRITOOLS-HERO-V2"

HERO_DESCRIPTIONS = {
    "budget": """⚡ INSTANT DOWNLOAD — Budget Tracker — Know Exactly Where Your Money Goes

Stop wondering where your paycheck went. This Budget Tracker gives you a complete picture of your income, expenses, and savings — automatically.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WHAT'S INSIDE:

• Monthly Dashboard — Income vs. Expenses vs. Savings at a glance
• Expense Categories — Housing, food, transport, subscriptions, and more
• Annual Overview — See your full year on one screen
• Savings Goals Tracker — Track progress toward any financial goal
• Bill Tracker — Never miss a payment again
• Net Worth Calculator — Know exactly what you're worth

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 WHY THIS WORKS:
Most people overspend because they don't track. This template makes tracking take 5 minutes a week — not 5 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ KEY FEATURES:
• 100% Google Sheets — no software, no subscription
• Auto-calculating formulas — just enter your numbers
• Works on phone, tablet, and desktop
• Fully customizable — change any category, color, or label
• Instant download — ready in 2 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT — HOW TO ACCESS YOUR FILE:

Step 1: After purchase, open your Etsy receipt and click the download link
Step 2: The file opens in Google Sheets in your browser
Step 3: Click File → Make a Copy → save to your Google Drive
Step 4: The copy is 100% yours — start filling it in immediately

🔵 On Mobile: If the Etsy app doesn't show the file, open Etsy in your phone's browser (Chrome or Safari) instead of the app.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ FAQ:

Q: Do I need Microsoft Excel?
A: No. This is a Google Sheets file. You only need a free Google account.

Q: Can I use this on my phone?
A: Yes. Google Sheets works on iPhone and Android.

Q: Is this a one-time payment?
A: Yes. No subscription, no recurring fees. Buy once, use forever.

Q: Can I edit the categories?
A: Yes. Everything is fully editable — colors, categories, labels, everything.

Q: What if I need help?
A: Message us on Etsy — we reply within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ YOU MAY ALSO LIKE:
→ Complete Finance OS (5-Tool Bundle, Save 52%) — nasritools.etsy.com
→ Debt Payoff Planner — nasritools.etsy.com
→ Cash Flow Tracker — nasritools.etsy.com
→ Complete Life System (All 10 Tools) — nasritools.etsy.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<!-- NASRITOOLS-HERO-V2 -->
© NasriTools — Professional Google Sheets Templates
""",

    "invoice": """⚡ INSTANT DOWNLOAD — Invoice & Client Tracker — Never Lose Track of a Payment Again

Stop chasing clients and losing track of invoices. This tracker gives you a complete system to manage every client, every invoice, and every payment — in one Google Sheet.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WHAT'S INSIDE:

• Client Dashboard — All clients with contact info and project status
• Invoice Tracker — Invoice number, amount, due date, status (Paid/Pending/Overdue)
• Monthly Revenue Summary — Total billed and total received per month
• Annual Income Report — Tax-ready summary of all earnings
• Outstanding Payments — See exactly who owes you money
• Payment History — Complete record of all transactions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 WHY THIS WORKS:
Freelancers lose thousands every year by not tracking. This system shows you every outstanding invoice at a glance — so you always know who to follow up with.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ KEY FEATURES:
• 100% Google Sheets — works on any device
• Auto-calculating totals and summaries
• Status system: Paid ✓ | Pending ⏳ | Overdue ⚠️
• Works for freelancers, consultants, agencies, and small businesses
• Instant download — start in 2 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT — HOW TO ACCESS YOUR FILE:

Step 1: Open your Etsy receipt → click the download link
Step 2: File opens in Google Sheets → File → Make a Copy
Step 3: Saved to your Google Drive — start using immediately

🔵 On Mobile: Use Chrome or Safari to open Etsy, not the app.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ FAQ:
Q: Do I need Microsoft Excel? A: No. Google Sheets only.
Q: Can I add unlimited clients? A: Yes. Add as many rows as needed.
Q: Is this a one-time payment? A: Yes. No subscription.
Q: What if I need help? A: Message us on Etsy — 24hr response.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ YOU MAY ALSO LIKE:
→ Freelancer OS Bundle (5 Tools, Save 53%) — nasritools.etsy.com
→ Cash Flow Tracker — nasritools.etsy.com
→ Complete Finance OS Bundle — nasritools.etsy.com

<!-- NASRITOOLS-HERO-V2 -->
© NasriTools — Professional Google Sheets Templates
""",

    "kpi": """⚡ INSTANT DOWNLOAD — KPI Dashboard — Your Entire Business on One Screen

Stop switching between spreadsheets to find your numbers. This KPI Dashboard puts every critical business metric — revenue, leads, conversion, expenses — on one auto-updating dashboard.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WHAT'S INSIDE:

• Executive Dashboard — All KPIs on one page with live charts
• Revenue Tracker — Monthly and annual revenue with trend lines
• Lead & Conversion Tracker — Track leads, demos, and close rates
• Expense Tracker — Business costs by category
• Team Performance — Track individual and team metrics
• Goal vs. Actual — See at a glance if you're on track

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 WHY THIS WORKS:
HubSpot costs $100/month. Salesforce costs $300/month. This KPI Dashboard does what most businesses need — for a one-time €24.99.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ KEY FEATURES:
• 100% Google Sheets — no software installation
• Auto-updating charts and graphs
• Customizable KPIs — add or remove any metric
• Works for any business type: SaaS, e-commerce, service, agency
• Instant download — ready in 2 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ HOW TO ACCESS YOUR FILE:

Step 1: Etsy receipt → click download link
Step 2: File opens in Google Sheets → File → Make a Copy
Step 3: Start using immediately — all formulas pre-built

🔵 Mobile: Open Etsy in Chrome/Safari, not the app.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ YOU MAY ALSO LIKE:
→ Business Starter Kit (5-Tool Bundle, Save 50%) — nasritools.etsy.com
→ Marketing ROI Tracker — nasritools.etsy.com
→ Sales Commission Tracker — nasritools.etsy.com

<!-- NASRITOOLS-HERO-V2 -->
© NasriTools — Professional Google Sheets Templates
""",

    "complete life": """⚡ INSTANT DOWNLOAD — Complete Life System — ALL 10 Templates in One File

Stop buying tools one by one. This is your complete life operating system — finance, fitness, habits, goals, health, planning — everything in one Google Sheets file.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WHAT'S INCLUDED — ALL 10 SYSTEMS:

1. Budget & Expense Tracker — Income, expenses, savings, net worth
2. Invoice & Client Tracker — Clients, invoices, payment status
3. Workout Tracker — 12-week progressive training system
4. Meal Planner — Weekly meals + grocery list
5. Habit Tracker — 30-day habit building with streaks
6. Weekly Planner — Time-blocking and priority system
7. Goals & Action Planner — 90-day goal system
8. Sleep Tracker — Sleep quality and pattern monitoring
9. Weight Loss Tracker — Body stats, BMI, progress
10. Annual Review Planner — Year reflection and design

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 THE MATH:
Individual value: €180+ | You pay: €54.99 | You save: 70%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ KEY FEATURES:
• All 10 systems in ONE Google Sheets file
• Everything interconnects — change one number, everything updates
• Works on phone, tablet, and desktop
• Fully customizable — make it your own
• Lifetime access — buy once, use forever

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ HOW TO ACCESS YOUR FILE:

Step 1: Etsy receipt → click download link
Step 2: File opens in Google Sheets → File → Make a Copy
Step 3: Yours forever — start using immediately

🔵 Mobile: Open Etsy in Chrome/Safari browser, not the app.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ FAQ:
Q: Do I need any special software? A: No. Free Google account only.
Q: Can I share with my family? A: Yes. Share your copy with anyone.
Q: Is this a one-time purchase? A: Yes. No subscription ever.
Q: What if I need help? A: Message us on Etsy — 24hr response.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ YOU MAY ALSO LIKE:
→ Complete Finance OS (5-Tool Bundle) — nasritools.etsy.com
→ Business Starter Kit Bundle — nasritools.etsy.com
→ Complete Health OS Bundle — nasritools.etsy.com

<!-- NASRITOOLS-HERO-V2 -->
© NasriTools — Professional Google Sheets Templates
""",

    "finance bundle": """⚡ INSTANT DOWNLOAD — Finance Bundle — 5 Finance Systems, One Price

Your complete personal and business finance toolkit. Budget, invoices, cash flow, profit, and debt — all in one Google Sheets bundle.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WHAT'S INCLUDED (5 Systems):

1. Budget & Expense Tracker — Track every euro in and out
2. Invoice & Client Tracker — Manage clients and payments
3. Cash Flow Forecast — See your money 12 months ahead
4. Profit & Loss Tracker — Know if you're actually growing
5. Debt Payoff Planner — Get debt-free faster

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Individual value: €105+ | You pay: €49.99 | You save: 52%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ KEY FEATURES:
• All 5 systems in separate, linked Google Sheets
• Auto-calculating — just enter numbers
• Works on any device — phone, tablet, desktop
• Lifetime access — no subscription

⚠️ HOW TO ACCESS:
Step 1: Etsy receipt → download link
Step 2: Google Sheets → File → Make a Copy
Step 3: Start immediately

✨ YOU MAY ALSO LIKE:
→ Complete Life System (All 10 Tools) — nasritools.etsy.com
→ Business Starter Kit Bundle — nasritools.etsy.com

<!-- NASRITOOLS-HERO-V2 -->
© NasriTools — Professional Google Sheets Templates
""",
}

HERO_KEYWORDS = {
    "budget": ["budget tracker", "budget & expense", "budget spreadsheet", "monthly budget"],
    "invoice": ["invoice tracker", "invoice & client", "freelancer invoice", "freelance invoice"],
    "kpi": ["kpi dashboard", "kpi spread"],
    "complete life": ["complete life system", "all 10 templa"],
    "finance bundle": ["finance bundle", "budget + invoice", "finance os"],
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

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset})
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100
    return listings

def get_hero_type(title_lower):
    for hero_type, keywords in HERO_KEYWORDS.items():
        if any(k in title_lower for k in keywords):
            return hero_type
    return None

def update_description(token, lid, desc):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode({"description": desc}), timeout=30,
    )
    return r.ok, r.status_code

def main():
    print("=" * 65)
    print("  NasriTools — Update Hero Product Descriptions (Premium V2)")
    print("=" * 65)
    token = get_token()
    listings = get_all_listings(token)
    print(f"[*] Found {len(listings)} listings\n")

    ok = skip = fail = 0
    for l in listings:
        lid   = l["listing_id"]
        title = l["title"]
        tl    = title.lower()
        desc  = l.get("description", "") or ""

        if MARKER in desc:
            skip += 1
            continue

        hero_type = get_hero_type(tl)
        if not hero_type:
            skip += 1
            continue

        new_desc = HERO_DESCRIPTIONS[hero_type]
        print(f"  [HERO-{hero_type.upper()[:8]:8}] {title[:40]} ...", end=" ", flush=True)
        token = get_token()
        r_ok, code = update_description(token, lid, new_desc)
        if r_ok:
            print("OK")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1
        time.sleep(1)

    print(f"\n{'='*65}")
    print(f"  Hero descriptions updated: {ok} | Skipped: {skip} | Failed: {fail}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
