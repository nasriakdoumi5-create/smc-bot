"""
fix_tags.py
Rewrites all listing tags using 80% long-tail strategy.
13 tags per listing: 3 high-volume + 10 long-tail converting keywords.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

# Tag sets per product type: 3 high-volume + 10 long-tail = 13 total
TAG_SETS = {
    "budget": [
        "google sheets", "budget planner", "expense tracker",
        "monthly budget", "budget spreadsheet", "household budget",
        "personal finance", "money tracker", "savings tracker",
        "budget template", "finance planner", "income tracker", "expense sheet"
    ],
    "invoice": [
        "invoice tracker", "client tracker", "business template",
        "freelance invoice", "invoice spreadsheet", "client manager",
        "payment tracker", "billing tracker", "freelancer tools",
        "revenue tracker", "tax prep sheet", "business tracker", "income tracker"
    ],
    "workout": [
        "workout tracker", "fitness tracker", "gym planner",
        "exercise log", "gym spreadsheet", "workout log",
        "fitness planner", "weight lifting", "progress tracker",
        "workout schedule", "exercise tracker", "gym template", "fitness sheet"
    ],
    "meal": [
        "meal planner", "meal prep", "grocery list",
        "weekly meal plan", "meal plan sheet", "grocery tracker",
        "food planner", "meal schedule", "nutrition tracker",
        "diet planner", "weekly menu", "food log", "meal planning"
    ],
    "habit": [
        "habit tracker", "daily planner", "goal tracker",
        "30 day habits", "streak tracker", "daily habits",
        "routine tracker", "habit log", "habit template",
        "daily routine", "behavior tracker", "morning routine", "productivity"
    ],
    "student": [
        "student planner", "gpa calculator", "study planner",
        "grade tracker", "assignment tracker", "exam tracker",
        "college planner", "academic planner", "semester planner",
        "course tracker", "study schedule", "homework tracker", "school planner"
    ],
    "goals": [
        "goal planner", "weekly planner", "productivity planner",
        "90 day planner", "goal tracker", "action planner",
        "weekly schedule", "time blocking", "priority planner",
        "task tracker", "goal setting", "life planner", "vision planner"
    ],
    "content": [
        "content planner", "social media planner", "creator tools",
        "content calendar", "instagram planner", "youtube tracker",
        "content schedule", "posting calendar", "influencer tools",
        "brand tracker", "analytics sheet", "creator template", "media planner"
    ],
    "wedding": [
        "wedding planner", "wedding budget", "wedding template",
        "wedding checklist", "guest list tracker", "vendor tracker",
        "seating chart", "bridal planner", "wedding organizer",
        "rsvp tracker", "wedding timeline", "wedding spreadsheet", "event planner"
    ],
    "bundle": [
        "template bundle", "google sheets bundle", "digital download",
        "spreadsheet bundle", "planner bundle", "template set",
        "life planner", "organizer bundle", "planner templates",
        "productivity bundle", "digital planner", "instant download", "sheets bundle"
    ],
    "weekly": [
        "weekly planner", "productivity planner", "time management",
        "weekly schedule", "time blocking", "task planner",
        "daily planner", "work planner", "priority planner",
        "monday planner", "weekly organizer", "schedule template", "planner sheet"
    ],
    "profit": [
        "profit loss tracker", "business finance", "income tracker",
        "revenue tracker", "expense report", "business tracker",
        "profit tracker", "financial report", "sales tracker",
        "monthly report", "profit spreadsheet", "business planner", "finance sheet"
    ],
    "cash": [
        "cash flow tracker", "business finance", "finance template",
        "cash flow sheet", "money tracker", "business budget",
        "income tracker", "expense tracker", "financial planner",
        "revenue tracker", "payment tracker", "accounting sheet", "finance planner"
    ],
    "kpi": [
        "kpi dashboard", "business tracker", "metrics tracker",
        "performance tracker", "business dashboard", "analytics sheet",
        "goal tracker", "team tracker", "work tracker",
        "sales dashboard", "data tracker", "reporting sheet", "business metrics"
    ],
    "social": [
        "social media planner", "content calendar", "instagram planner",
        "posting schedule", "content planner", "media tracker",
        "tiktok planner", "youtube planner", "brand planner",
        "influencer tools", "creator calendar", "marketing planner", "post tracker"
    ],
    "travel": [
        "travel planner", "trip planner", "vacation planner",
        "travel budget", "trip budget", "itinerary planner",
        "packing list", "travel template", "travel organizer",
        "holiday planner", "road trip planner", "travel tracker", "trip organizer"
    ],
    "project": [
        "project planner", "task manager", "project tracker",
        "work planner", "team planner", "deadline tracker",
        "milestone tracker", "project template", "task list",
        "action plan", "project schedule", "productivity sheet", "work tracker"
    ],
    "debt": [
        "debt payoff planner", "budget planner", "finance tracker",
        "debt tracker", "loan tracker", "payment planner",
        "debt snowball", "budget template", "money planner",
        "savings tracker", "financial planner", "payoff tracker", "debt free"
    ],
    "keto": [
        "keto tracker", "diet planner", "nutrition tracker",
        "keto meal plan", "low carb planner", "food tracker",
        "calorie tracker", "macro tracker", "keto template",
        "diet template", "meal planner", "food log", "health tracker"
    ],
    "weight": [
        "weight loss tracker", "fitness tracker", "health tracker",
        "body weight log", "weight log", "diet tracker",
        "calorie tracker", "bmi tracker", "body measurements",
        "fitness planner", "weight template", "progress tracker", "health planner"
    ],
    "sleep": [
        "sleep tracker", "health tracker", "wellness planner",
        "sleep log", "sleep journal", "daily routine",
        "habit tracker", "wellness tracker", "self care planner",
        "rest tracker", "sleep template", "health log", "wellness template"
    ],
    "stock": [
        "stock tracker", "investment tracker", "portfolio tracker",
        "stock journal", "trading log", "dividend tracker",
        "finance tracker", "investor sheet", "market tracker",
        "trade log", "investment planner", "portfolio sheet", "stock template"
    ],
    "ecommerce": [
        "ecommerce tracker", "online store tracker", "sales tracker",
        "product tracker", "inventory tracker", "store analytics",
        "revenue tracker", "shop tracker", "business template",
        "dropship tracker", "seller tools", "order tracker", "shop template"
    ],
    "real estate": [
        "real estate tracker", "property tracker", "investment tracker",
        "rental tracker", "property sheet", "house tracker",
        "real estate sheet", "landlord tools", "rental income",
        "investment sheet", "roi tracker", "property planner", "finance tracker"
    ],
    "marketing": [
        "marketing tracker", "roi tracker", "campaign tracker",
        "ad tracker", "marketing planner", "lead tracker",
        "sales tracker", "conversion tracker", "marketing sheet",
        "campaign sheet", "analytics tracker", "marketing template", "ad planner"
    ],
    "default": [
        "google sheets", "spreadsheet template", "digital download",
        "planner template", "tracker template", "instant download",
        "productivity sheet", "organizer template", "editable template",
        "business template", "google sheets template", "digital planner", "printable sheet"
    ],
}

KEYWORD_TO_TYPE = [
    (["budget", "expense", "spending", "financial"], "budget"),
    (["invoice", "client", "billing", "payment", "freelance business"], "invoice"),
    (["workout", "gym", "exercise", "fitness", "training", "marathon"], "workout"),
    (["meal", "food", "grocery", "nutrition", "recipe", "keto"], "meal"),
    (["habit", "streak", "routine", "30 day", "daily habit"], "habit"),
    (["student", "gpa", "grade", "assignment", "exam", "thesis", "school", "academic"], "student"),
    (["goal", "90 day", "planner", "productivity", "weekly plan", "action plan", "annual review", "certification", "skill"], "goals"),
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

def update_tags(token, lid, tags):
    tag_str = "&".join(f"tags[]={urllib.parse.quote(t, safe='')}" for t in tags[:13])
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=tag_str, timeout=30,
    )
    return r.ok, r.status_code

def main():
    print("=" * 65)
    print("  NasriTools — Fix Tags (80% Long-Tail Strategy)")
    print("=" * 65)
    token = get_token()
    listings = get_all_listings(token)
    print(f"[*] Found {len(listings)} listings\n")

    ok = fail = 0
    for l in listings:
        lid   = l["listing_id"]
        title = l["title"]
        tag_type = get_tag_type(title)
        tags = TAG_SETS.get(tag_type, TAG_SETS["default"])

        print(f"  [{tag_type:12}] {title[:40]} ...", end=" ", flush=True)
        token = get_token()
        r_ok, code = update_tags(token, lid, tags)
        if r_ok:
            print(f"OK")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1
        time.sleep(1)

    print(f"\n{'='*65}")
    print(f"  Tags updated: {ok} | Failed: {fail}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
