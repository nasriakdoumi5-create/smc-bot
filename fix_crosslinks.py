"""
fix_crosslinks.py
Appends a "You May Also Like" section to every listing description,
linking to related product types in the same shop.
This boosts session length, reduces bounce rate, and improves Etsy SEO.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

MARKER = "✨ YOU MAY ALSO LIKE"

# Cross-link suggestions per product type
CROSSLINKS = {
    "budget": """✨ YOU MAY ALSO LIKE
→ Invoice & Client Tracker — nasritools.etsy.com
→ Profit & Loss Tracker — nasritools.etsy.com
→ Cash Flow Tracker — nasritools.etsy.com
→ Debt Payoff Planner — nasritools.etsy.com
Browse all Finance tools: nasritools.etsy.com/section/finance""",

    "invoice": """✨ YOU MAY ALSO LIKE
→ Budget & Expense Tracker — nasritools.etsy.com
→ Cash Flow Tracker — nasritools.etsy.com
→ Profit & Loss Tracker — nasritools.etsy.com
→ KPI Dashboard — nasritools.etsy.com
Browse all Business tools: nasritools.etsy.com/section/business""",

    "workout": """✨ YOU MAY ALSO LIKE
→ Meal Planner — nasritools.etsy.com
→ Habit Tracker — nasritools.etsy.com
→ Weight Loss Tracker — nasritools.etsy.com
→ Sleep Tracker — nasritools.etsy.com
Browse all Health tools: nasritools.etsy.com/section/health""",

    "meal": """✨ YOU MAY ALSO LIKE
→ Workout Tracker — nasritools.etsy.com
→ Keto Diet Tracker — nasritools.etsy.com
→ Weight Loss Tracker — nasritools.etsy.com
→ Habit Tracker — nasritools.etsy.com
Browse all Health tools: nasritools.etsy.com/section/health""",

    "habit": """✨ YOU MAY ALSO LIKE
→ Weekly Planner — nasritools.etsy.com
→ Goals & Action Planner — nasritools.etsy.com
→ Workout Tracker — nasritools.etsy.com
→ Sleep Tracker — nasritools.etsy.com
Browse all Productivity tools: nasritools.etsy.com/section/productivity""",

    "student": """✨ YOU MAY ALSO LIKE
→ Weekly Planner — nasritools.etsy.com
→ Goals & Action Planner — nasritools.etsy.com
→ Habit Tracker — nasritools.etsy.com
→ Project Tracker — nasritools.etsy.com
Browse all Productivity tools: nasritools.etsy.com/section/productivity""",

    "goals": """✨ YOU MAY ALSO LIKE
→ Weekly Planner — nasritools.etsy.com
→ Habit Tracker — nasritools.etsy.com
→ Project Tracker — nasritools.etsy.com
→ Student Planner — nasritools.etsy.com
Browse all Productivity tools: nasritools.etsy.com/section/productivity""",

    "content": """✨ YOU MAY ALSO LIKE
→ Social Media Planner — nasritools.etsy.com
→ Marketing ROI Tracker — nasritools.etsy.com
→ YouTube Tracker — nasritools.etsy.com
→ Invoice & Client Tracker — nasritools.etsy.com
Browse all Business tools: nasritools.etsy.com/section/business""",

    "wedding": """✨ YOU MAY ALSO LIKE
→ Budget & Expense Tracker — nasritools.etsy.com
→ Event Planner — nasritools.etsy.com
→ Travel Planner — nasritools.etsy.com
→ Goals & Action Planner — nasritools.etsy.com
Browse all Planners: nasritools.etsy.com/section/productivity""",

    "bundle": """✨ YOU MAY ALSO LIKE
→ Browse individual Finance trackers — nasritools.etsy.com
→ Browse Health & Fitness tools — nasritools.etsy.com
→ Browse Business templates — nasritools.etsy.com
→ Browse Productivity planners — nasritools.etsy.com
See all bundles: nasritools.etsy.com/section/bundles""",

    "weekly": """✨ YOU MAY ALSO LIKE
→ Goals & Action Planner — nasritools.etsy.com
→ Habit Tracker — nasritools.etsy.com
→ Project Tracker — nasritools.etsy.com
→ Student Planner — nasritools.etsy.com
Browse all Productivity tools: nasritools.etsy.com/section/productivity""",

    "profit": """✨ YOU MAY ALSO LIKE
→ Cash Flow Tracker — nasritools.etsy.com
→ Invoice & Client Tracker — nasritools.etsy.com
→ Budget & Expense Tracker — nasritools.etsy.com
→ KPI Dashboard — nasritools.etsy.com
Browse all Finance tools: nasritools.etsy.com/section/finance""",

    "cash": """✨ YOU MAY ALSO LIKE
→ Profit & Loss Tracker — nasritools.etsy.com
→ Budget & Expense Tracker — nasritools.etsy.com
→ Invoice & Client Tracker — nasritools.etsy.com
→ KPI Dashboard — nasritools.etsy.com
Browse all Finance tools: nasritools.etsy.com/section/finance""",

    "kpi": """✨ YOU MAY ALSO LIKE
→ Marketing ROI Tracker — nasritools.etsy.com
→ Sales Commission Tracker — nasritools.etsy.com
→ Profit & Loss Tracker — nasritools.etsy.com
→ Cash Flow Tracker — nasritools.etsy.com
Browse all Business tools: nasritools.etsy.com/section/business""",

    "social": """✨ YOU MAY ALSO LIKE
→ Content Creator Planner — nasritools.etsy.com
→ Marketing ROI Tracker — nasritools.etsy.com
→ YouTube Tracker — nasritools.etsy.com
→ Invoice & Client Tracker — nasritools.etsy.com
Browse all Business tools: nasritools.etsy.com/section/business""",

    "travel": """✨ YOU MAY ALSO LIKE
→ Budget & Expense Tracker — nasritools.etsy.com
→ Goals & Action Planner — nasritools.etsy.com
→ Weekly Planner — nasritools.etsy.com
→ Packing List Template — nasritools.etsy.com
Browse all Planners: nasritools.etsy.com/section/productivity""",

    "project": """✨ YOU MAY ALSO LIKE
→ Weekly Planner — nasritools.etsy.com
→ Goals & Action Planner — nasritools.etsy.com
→ KPI Dashboard — nasritools.etsy.com
→ Habit Tracker — nasritools.etsy.com
Browse all Productivity tools: nasritools.etsy.com/section/productivity""",

    "debt": """✨ YOU MAY ALSO LIKE
→ Budget & Expense Tracker — nasritools.etsy.com
→ Cash Flow Tracker — nasritools.etsy.com
→ Emergency Fund Tracker — nasritools.etsy.com
→ Profit & Loss Tracker — nasritools.etsy.com
Browse all Finance tools: nasritools.etsy.com/section/finance""",

    "keto": """✨ YOU MAY ALSO LIKE
→ Meal Planner — nasritools.etsy.com
→ Weight Loss Tracker — nasritools.etsy.com
→ Workout Tracker — nasritools.etsy.com
→ Habit Tracker — nasritools.etsy.com
Browse all Health tools: nasritools.etsy.com/section/health""",

    "weight": """✨ YOU MAY ALSO LIKE
→ Workout Tracker — nasritools.etsy.com
→ Meal Planner — nasritools.etsy.com
→ Keto Diet Tracker — nasritools.etsy.com
→ Habit Tracker — nasritools.etsy.com
Browse all Health tools: nasritools.etsy.com/section/health""",

    "sleep": """✨ YOU MAY ALSO LIKE
→ Habit Tracker — nasritools.etsy.com
→ Workout Tracker — nasritools.etsy.com
→ Mental Health Journal — nasritools.etsy.com
→ Daily Routine Planner — nasritools.etsy.com
Browse all Health tools: nasritools.etsy.com/section/health""",

    "stock": """✨ YOU MAY ALSO LIKE
→ Budget & Expense Tracker — nasritools.etsy.com
→ Cash Flow Tracker — nasritools.etsy.com
→ Profit & Loss Tracker — nasritools.etsy.com
→ Real Estate Tracker — nasritools.etsy.com
Browse all Finance tools: nasritools.etsy.com/section/finance""",

    "ecommerce": """✨ YOU MAY ALSO LIKE
→ Invoice & Client Tracker — nasritools.etsy.com
→ Profit & Loss Tracker — nasritools.etsy.com
→ Marketing ROI Tracker — nasritools.etsy.com
→ Cash Flow Tracker — nasritools.etsy.com
Browse all Business tools: nasritools.etsy.com/section/business""",

    "real estate": """✨ YOU MAY ALSO LIKE
→ Cash Flow Tracker — nasritools.etsy.com
→ Budget & Expense Tracker — nasritools.etsy.com
→ Profit & Loss Tracker — nasritools.etsy.com
→ Invoice & Client Tracker — nasritools.etsy.com
Browse all Finance tools: nasritools.etsy.com/section/finance""",

    "marketing": """✨ YOU MAY ALSO LIKE
→ KPI Dashboard — nasritools.etsy.com
→ Social Media Planner — nasritools.etsy.com
→ Content Creator Planner — nasritools.etsy.com
→ Sales Commission Tracker — nasritools.etsy.com
Browse all Business tools: nasritools.etsy.com/section/business""",

    "default": """✨ YOU MAY ALSO LIKE
→ Budget & Expense Tracker — nasritools.etsy.com
→ Weekly Planner — nasritools.etsy.com
→ Habit Tracker — nasritools.etsy.com
→ Business Bundle (Save 65%) — nasritools.etsy.com
Browse all templates: nasritools.etsy.com""",
}

KEYWORD_TO_TYPE = [
    (["budget", "expense", "spending", "financial"], "budget"),
    (["invoice", "client", "billing", "payment", "freelance business"], "invoice"),
    (["workout", "gym", "exercise", "fitness", "training", "marathon"], "workout"),
    (["meal", "food", "grocery", "nutrition", "recipe"], "meal"),
    (["habit", "streak", "routine", "30 day", "daily habit"], "habit"),
    (["student", "gpa", "grade", "assignment", "exam", "thesis", "school", "academic"], "student"),
    (["goal", "90 day", "planner", "productivity", "weekly plan", "action plan", "annual review"], "goals"),
    (["content creator", "youtube", "instagram", "social media", "influencer", "tiktok", "posting"], "content"),
    (["wedding", "bride", "venue", "seating", "rsvp", "vendor"], "wedding"),
    (["bundle", "complete life", "all 10", "all templates"], "bundle"),
    (["weekly planner", "weekly productivity", "time block", "time management", "work planner"], "weekly"),
    (["profit loss", "profit & loss", "p&l"], "profit"),
    (["cash flow"], "cash"),
    (["kpi", "dashboard", "metrics", "performance"], "kpi"),
    (["social media", "content calendar", "posting calendar", "media planner"], "social"),
    (["travel", "trip", "vacation", "itinerary"], "travel"),
    (["project management", "project tracker", "milestone", "task manager"], "project"),
    (["debt payoff", "debt tracker", "loan tracker"], "debt"),
    (["keto", "low carb", "macro"], "keto"),
    (["weight loss", "body weight", "bmi", "measurements"], "weight"),
    (["sleep tracker", "sleep log"], "sleep"),
    (["stock", "trading", "portfolio", "dividend", "investment"], "stock"),
    (["ecommerce", "dropshipping", "online store", "etsy shop", "print on demand"], "ecommerce"),
    (["real estate", "property", "rental", "landlord"], "real estate"),
    (["marketing roi", "marketing tracker", "campaign", "ad tracker"], "marketing"),
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
    return {"Authorization": "Bearer " + token["access_token"], "x-api-key": CLIENT_ID + ":" + SECRET}

def get_all_listings(token):
    listings = []
    offset = 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token), params={"limit": 100, "offset": offset})
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100
    return listings

def get_tag_type(title):
    tl = title.lower()
    for keywords, tag_type in KEYWORD_TO_TYPE:
        if any(k in tl for k in keywords):
            return tag_type
    return "default"

def update_description(token, lid, desc):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode({"description": desc}), timeout=30,
    )
    return r.ok, r.status_code

def main():
    print("=" * 65)
    print("  NasriTools — Fix Cross-Links (You May Also Like)")
    print("=" * 65)
    token = get_token()

    # Fetch listings with descriptions
    print("[*] Fetching listings with descriptions...")
    listings = []
    offset = 0
    while True:
        r = requests.get(
            f"{API}/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset, "includes": "description"},
        )
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100

    print(f"[*] Found {len(listings)} listings\n")

    ok = skip = fail = 0
    for l in listings:
        lid   = l["listing_id"]
        title = l["title"]
        desc  = l.get("description", "") or ""

        if MARKER in desc:
            print(f"  [SKIP] {title[:50]}")
            skip += 1
            continue

        tag_type = get_tag_type(title)
        crosslink_block = CROSSLINKS.get(tag_type, CROSSLINKS["default"])
        new_desc = desc.rstrip() + "\n\n" + crosslink_block

        print(f"  [FIX]  {title[:45]} ...", end=" ", flush=True)
        token = get_token()
        r_ok, code = update_description(token, lid, new_desc)
        if r_ok:
            print("OK")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1
        time.sleep(0.8)

    print(f"\n{'='*65}")
    print(f"  Cross-links added: {ok} | Skipped: {skip} | Failed: {fail}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
