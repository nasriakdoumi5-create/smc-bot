"""
rewrite_descriptions.py
Rewrites all listing descriptions with a proven conversion structure:
hook → what you get → features → how it works → why us → FAQ.
Run:  python rewrite_descriptions.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

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

# ---------------------------------------------------------------
# Per-type content: hook + benefit bullets
# ---------------------------------------------------------------
TYPES = {
    "budget": (
        "Stop wondering where your money goes. This budget tracker shows you every euro — automatically.",
        ["Monthly & yearly budget overview with auto-calculating totals",
         "Expense categories that update charts in real time",
         "Income vs. spending dashboard — see your savings rate instantly",
         "Works in any currency — just type your numbers"],
    ),
    "invoice": (
        "Send professional invoices in 2 minutes — no design skills, no expensive software.",
        ["Clean, client-ready invoice layout you can brand with your logo",
         "Auto-calculating totals, tax and discounts — zero formula editing",
         "Client & payment tracker included so nothing slips through",
         "Print-ready and PDF-export friendly"],
    ),
    "dashboard": (
        "See your entire business on one screen — sales, costs, profit, trends.",
        ["KPI dashboard with auto-updating charts and reports",
         "Track revenue, expenses and margins month by month",
         "Spot your best products and biggest costs at a glance",
         "Built for non-analysts — enter numbers, get insights"],
    ),
    "fitness": (
        "Plan workouts, log progress, and actually see results — all in one sheet.",
        ["Workout planner with sets, reps and weight tracking",
         "Progress charts that update as you log sessions",
         "Body measurements & goals tracker included",
         "Use it at the gym from your phone"],
    ),
    "meal": (
        "Plan a week of meals in 10 minutes — and never ask 'what's for dinner?' again.",
        ["Weekly & monthly meal planner with auto grocery list",
         "Recipe library you build once and reuse forever",
         "Budget-friendly: plan around what you already have",
         "Works on phone — take your grocery list to the store"],
    ),
    "habit": (
        "Build habits that stick — with a tracker you'll actually enjoy opening.",
        ["Daily habit grid with streak tracking",
         "Monthly progress charts that keep you motivated",
         "Flexible: track 5 habits or 50",
         "Morning routine & evening review sections"],
    ),
    "planner": (
        "Your day, week and month — organized in one clean, calming space.",
        ["Daily, weekly & monthly views that stay in sync",
         "Priority & task sections so big things get done first",
         "Goal tracking built in — connect daily work to yearly goals",
         "Undated: start any day, reuse every year"],
    ),
    "project": (
        "Run projects like a pro — tasks, deadlines, owners and progress in one view.",
        ["Task board with status, priority and due-date tracking",
         "Auto progress bars per project and per person",
         "Timeline view to spot bottlenecks before they hurt",
         "Perfect for freelancers, teams and agencies"],
    ),
    "content": (
        "Plan a month of content in one sitting — and never miss a posting day again.",
        ["Content calendar for all platforms in one view",
         "Idea bank so you never run out of post ideas",
         "Status workflow: idea → draft → scheduled → posted",
         "Performance tracker to double down on what works"],
    ),
    "inventory": (
        "Know exactly what's in stock, what's selling, and what to reorder — instantly.",
        ["Real-time stock levels with low-stock alerts",
         "Sales & cost tracking with automatic profit per item",
         "Supplier & reorder management in one place",
         "Built for small shops, Etsy sellers and ecommerce"],
    ),
    "student": (
        "Every class, deadline and grade — organized so you can focus on learning.",
        ["Class schedule & assignment tracker with due-date alerts",
         "Grade calculator that shows where you stand in every course",
         "Study planner with spaced-repetition friendly layout",
         "Semester overview on one page"],
    ),
    "travel": (
        "Plan your whole trip in one sheet — itinerary, budget, packing, bookings.",
        ["Day-by-day itinerary planner with times and locations",
         "Trip budget tracker — flights, stays, food, activities",
         "Packing checklist you'll reuse for every trip",
         "Booking & confirmation organizer"],
    ),
    "real estate": (
        "Analyze any property in minutes — cash flow, ROI, and whether it's worth it.",
        ["Rental income & expense analyzer with auto ROI",
         "Mortgage & cash flow calculator built in",
         "Compare multiple properties side by side",
         "Used by investors and first-time buyers alike"],
    ),
    "hr": (
        "Onboard, track and manage your team — without expensive HR software.",
        ["Employee database with roles, dates and documents",
         "Onboarding checklist so no step gets missed",
         "Leave & attendance tracking with auto balances",
         "Built for small businesses and startups"],
    ),
    "wedding": (
        "Plan your perfect day without the overwhelm — budget, guests, timeline, vendors.",
        ["Wedding budget tracker with category breakdowns",
         "Guest list & RSVP manager with seating notes",
         "Vendor comparison and payment schedule",
         "Countdown timeline so nothing is left to the last week"],
    ),
    "bundle": (
        "Everything you need in one purchase — and one price that beats buying separately.",
        ["Multiple complete templates in a single download",
         "Consistent design — everything works the same way",
         "Save 60%+ versus buying each template alone",
         "Lifetime access to every file included"],
    ),
}

GENERIC = (
    "A clean, powerful Google Sheets template that does the work for you.",
    ["Auto-calculating formulas — enter your data, get instant results",
     "Clear dashboard layout that anyone can use",
     "Fully customizable — colors, categories, columns",
     "Works on phone, tablet and desktop"],
)

def detect_type(title):
    t = title.lower()
    order = [
        ("bundle",      ["bundle", "all-in-one", "complete system", "complete life", " kit", " pack"]),
        ("real estate", ["real estate", "property", "rental", "mortgage"]),
        ("wedding",     ["wedding"]),
        ("hr",          ["hr ", "employee", "onboarding", "recruitment", "hiring"]),
        ("invoice",     ["invoice", "billing"]),
        ("budget",      ["budget", "expense", "spending", "money", "cash flow", "debt", "savings", "finance"]),
        ("dashboard",   ["dashboard", "kpi", "crm", "sales tracker", "business manager", "pipeline", "profit"]),
        ("fitness",     ["workout", "fitness", "gym", "exercise", "weight loss", "training"]),
        ("meal",        ["meal", "recipe", "grocery", "nutrition", "food"]),
        ("habit",       ["habit", "routine", "streak"]),
        ("project",     ["project", "task manager", "gantt", "sprint", "agile", "to-do", "todo"]),
        ("content",     ["content", "social media", "instagram", "youtube", "tiktok", "posting"]),
        ("inventory",   ["inventory", "stock", "ecommerce", "etsy shop", "pod "]),
        ("student",     ["student", "school", "study", "college", "grade", "academic"]),
        ("travel",      ["travel", "trip", "vacation", "itinerary", "packing"]),
        ("planner",     ["planner", "calendar", "schedule", "organizer", "diary", "journal"]),
    ]
    for key, words in order:
        if any(w in t for w in words):
            return key
    return None

def build_description(title):
    ptype = detect_type(title)
    hook, bullets = TYPES.get(ptype, GENERIC) if ptype else GENERIC
    name = title.split("|")[0].strip()

    lines = [
        f"★ {name} — Google Sheets Template ★",
        "",
        hook,
        "",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "✅ WHAT YOU GET",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
    ]
    lines += [f"• {b}" for b in bullets]
    lines += [
        "• Instant digital download — ready in 2 minutes",
        "• Lifetime access & free updates",
        "",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "⚡ HOW IT WORKS",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "1. Purchase & download the PDF",
        "2. Click the link inside",
        "3. File → Make a Copy — the template is yours forever",
        "",
        "No software to install. Works with any free Google account,",
        "on phone, tablet and desktop.",
        "",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "🧡 WHY NASRITOOLS",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "• Buy once, own forever — NO subscriptions, ever",
        "• No sign-ups, no watermarks, no locked cells you can't edit",
        "• Fast support — I personally reply to every message",
        "",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "❓ FAQ",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "Q: Do I need Excel?",
        "A: No — this works in Google Sheets, which is 100% free.",
        "",
        "Q: Can I customize it?",
        "A: Yes! Colors, categories, columns — everything is editable.",
        "",
        "Q: Is this a one-time payment?",
        "A: Yes. Buy once, use forever. No hidden fees.",
        "",
        "Q: Can I use it on my phone?",
        "A: Yes — via the free Google Sheets app (iOS & Android).",
        "",
        "─────────────────────",
        "Instant download • Lifetime access • Made with care by NasriTools",
    ]
    return "\n".join(lines)

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset}, timeout=30)
        if not r.ok:
            print(f"  Error fetching listings: {r.status_code} {r.text[:200]}")
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
    print("  NasriTools — Description Rewriter")
    print("=" * 65)

    token    = get_token()
    listings = get_all_listings(token)
    total    = len(listings)
    print(f"[*] {total} listings found\n")

    updated = failed = 0
    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        title = l.get("title", "")
        desc  = build_description(title)

        print(f"  [{idx:3}/{total}] {title[:48]}...", end=" ", flush=True)

        token = get_token()
        r = requests.patch(
            f"{API}/shops/{SHOP_ID}/listings/{lid}",
            headers={**auth_headers(token),
                     "Content-Type": "application/x-www-form-urlencoded"},
            data={"description": desc},
            timeout=30,
        )
        if r.ok:
            print("✓")
            updated += 1
        else:
            print(f"✗ {r.status_code}: {r.text[:80]}")
            failed += 1

        time.sleep(0.8)

    print(f"\n{'=' * 65}")
    print(f"  Updated : {updated}")
    print(f"  Failed  : {failed}")
    print(f"{'=' * 65}")

if __name__ == "__main__":
    main()
