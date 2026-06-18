"""
NasriTools - SEO Tag Updater for ALL Active Listings
Fetches every active listing and assigns 13 optimized tags by title keywords
Run: python update_all_tags.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_tags_done.json"

# (keywords, 13 tags) — first match wins — every tag ≤ 20 chars
TAG_RULES = [
    (["student", "academic", "college", "university", "gpa", "homework", "exam", "grade", "class schedule"],
     ["student planner", "academic planner", "assignment tracker",
      "grade tracker", "study planner", "gpa tracker",
      "exam planner", "class schedule", "homework tracker",
      "back to school", "google sheets", "instant download",
      "digital download"]),

    (["wedding", "bride", "groom", "rsvp", "seating chart"],
     ["wedding planner", "wedding budget", "guest list",
      "wedding checklist", "vendor tracker", "seating chart",
      "rsvp tracker", "wedding template", "bride to be gift",
      "wedding timeline", "google sheets", "instant download",
      "digital download"]),

    (["travel", "trip", "vacation", "itinerary", "packing"],
     ["travel planner", "trip planner", "vacation planner",
      "itinerary sheet", "packing list", "travel budget",
      "travel tracker", "trip budget", "travel organizer",
      "travel checklist", "google sheets", "instant download",
      "digital download"]),

    (["meal", "food", "grocery", "nutrition", "diet", "recipe", "calorie"],
     ["meal planner", "weekly meal plan", "grocery list",
      "meal prep planner", "food planner", "recipe organizer",
      "pantry tracker", "nutrition tracker", "dinner planner",
      "meal tracker", "google sheets", "instant download",
      "digital download"]),

    (["workout", "gym", "fitness", "exercise", "strength", "cardio", "running", "weight loss"],
     ["workout tracker", "gym log", "exercise tracker",
      "fitness planner", "strength tracker", "cardio log",
      "body measurement", "pr tracker", "fitness template",
      "weight training", "google sheets", "instant download",
      "digital download"]),

    (["habit", "routine", "streak", "wellness", "mindfulness", "meditation"],
     ["habit tracker", "daily habits", "routine tracker",
      "streak counter", "self improvement", "wellness tracker",
      "morning routine", "productivity", "goal tracker",
      "habit planner", "google sheets", "instant download",
      "digital download"]),

    (["trading", "stock", "options", "crypto", "forex", "portfolio", "investment"],
     ["trading tracker", "stock tracker", "investment log",
      "portfolio track", "trade journal", "options trading",
      "crypto tracker", "stock portfolio", "trading journal",
      "market tracker", "google sheets", "instant download",
      "digital download"]),

    (["amazon", "fba", "shopify", "dropshipping"],
     ["amazon fba", "amazon seller", "fba tracker",
      "product tracker", "amazon tracker", "inventory track",
      "listing tracker", "sales tracker", "amazon revenue",
      "fba spreadsheet", "google sheets", "instant download",
      "digital download"]),

    (["etsy seller", "etsy shop", "etsy tracker", "etsy revenue"],
     ["etsy seller", "etsy tracker", "shop tracker",
      "product tracker", "etsy analytics", "shop revenue",
      "listing tracker", "sales tracker", "shop income",
      "etsy template", "google sheets", "instant download",
      "digital download"]),

    (["ecommerce", "online store", "product research", "dropship"],
     ["ecommerce tracker", "product research", "online store",
      "store tracker", "product tracker", "sales tracker",
      "inventory track", "ecommerce sheet", "revenue tracker",
      "store analytics", "google sheets", "instant download",
      "digital download"]),

    (["real estate", "property", "rental", "mortgage", "landlord"],
     ["real estate", "property tracker", "rental income",
      "mortgage track", "property manager", "landlord track",
      "rental property", "property income", "real estate crm",
      "investment prop", "google sheets", "instant download",
      "digital download"]),

    (["startup", "business plan", "business model", "break even", "venture"],
     ["startup planner", "business plan", "startup finance",
      "business model", "startup tracker", "revenue model",
      "business canvas", "startup template", "cash flow plan",
      "investor sheet", "google sheets", "instant download",
      "digital download"]),

    (["profit", "loss", "revenue", "cash flow", "accounting", "balance sheet"],
     ["profit loss tracker", "revenue tracker", "financial report",
      "accounting sheet", "profit tracker", "income tracker",
      "cash flow", "business finance", "financial model",
      "pl template", "google sheets", "instant download",
      "digital download"]),

    (["invoice", "billing", "payment", "receipt"],
     ["invoice tracker", "client tracker", "freelance invoice",
      "payment tracker", "income tracker", "tax tracker",
      "client database", "freelance tools", "billing tracker",
      "invoice template", "google sheets", "instant download",
      "digital download"]),

    (["budget", "expense", "spending", "household", "saving"],
     ["budget tracker", "expense tracker", "monthly budget",
      "personal finance", "budget spreadsheet", "income tracker",
      "financial tracker", "money tracker", "household budget",
      "spending tracker", "google sheets", "instant download",
      "digital download"]),

    (["kpi", "dashboard", "metrics", "performance report"],
     ["kpi dashboard", "business metrics", "kpi tracker",
      "performance kpi", "metrics tracker", "business report",
      "kpi template", "dashboard sheet", "analytics sheet",
      "data tracker", "google sheets", "instant download",
      "digital download"]),

    (["crm", "lead", "sales pipeline", "customer", "contact manager"],
     ["crm template", "client tracker", "lead tracker",
      "sales tracker", "customer crm", "sales pipeline",
      "contact manager", "deal tracker", "sales template",
      "client manager", "google sheets", "instant download",
      "digital download"]),

    (["hr", "employee", "payroll", "attendance", "onboarding", "staff"],
     ["hr tracker", "employee tracker", "payroll tracker",
      "time off tracker", "hr spreadsheet", "staff tracker",
      "attendance log", "performance log", "employee log",
      "onboarding track", "google sheets", "instant download",
      "digital download"]),

    (["project", "task", "deadline", "gantt", "milestone", "team"],
     ["project tracker", "project planner", "task tracker",
      "deadline tracker", "team tracker", "project template",
      "task manager", "project log", "gantt chart",
      "milestone track", "google sheets", "instant download",
      "digital download"]),

    (["youtube", "podcast", "video", "subscriber", "channel"],
     ["youtube tracker", "channel tracker", "video planner",
      "youtube growth", "subscriber track", "content creator",
      "video tracker", "youtube planner", "channel growth",
      "youtube analytics", "google sheets", "instant download",
      "digital download"]),

    (["social media", "instagram", "twitter", "tiktok", "content calendar",
      "influencer", "posting", "content creator", "content repurposing"],
     ["content planner", "social media plan", "content calendar",
      "creator planner", "posting schedule", "influencer",
      "analytics tracker", "brand deals", "content creator",
      "digital planner", "google sheets", "instant download",
      "digital download"]),

    (["seo", "marketing", "keyword", "backlink", "email list"],
     ["seo tracker", "marketing plan", "keyword tracker",
      "backlink log", "seo template", "marketing tracker",
      "email marketing", "content tracker", "seo spreadsheet",
      "digital marketing", "google sheets", "instant download",
      "digital download"]),

    (["freelancer", "freelance", "contractor"],
     ["freelancer tracker", "client tracker", "income tracker",
      "project tracker", "freelance planner", "invoice template",
      "tax tracker", "client database", "payment tracker",
      "freelance tools", "google sheets", "instant download",
      "digital download"]),

    (["financial", "tax", "accounting", "money", "net worth", "retirement"],
     ["financial tracker", "income tracker", "tax tracker",
      "money tracker", "personal finance", "net worth tracker",
      "finance planner", "retirement plan", "financial sheet",
      "budget template", "google sheets", "instant download",
      "digital download"]),

    (["goal", "vision", "action plan", "objective", "90 day"],
     ["goal planner", "goal tracker", "annual goals",
      "action plan", "milestone tracker", "vision board",
      "self improvement", "90 day plan", "goal spreadsheet",
      "productivity plan", "google sheets", "instant download",
      "digital download"]),

    (["weekly planner", "daily planner", "time block", "schedule"],
     ["weekly planner", "time blocking", "weekly schedule",
      "productivity", "task planner", "to do list",
      "daily planner", "time management", "priority list",
      "week planner", "google sheets", "instant download",
      "digital download"]),

    (["home", "cleaning", "moving", "household chore"],
     ["home organizer", "household planner", "cleaning tracker",
      "home manager", "moving checklist", "home budget",
      "home tracker", "personal planner", "household tracker",
      "home checklist", "google sheets", "instant download",
      "digital download"]),
]

DEFAULT_TAGS = [
    "spreadsheet template", "google sheets", "digital planner",
    "productivity tool", "instant download", "digital download",
    "planner template", "organizer sheet", "tracker template",
    "google template", "digital template", "organization tool",
    "google spreadsheet",
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


def fetch_all_listings(token):
    listings, offset, limit = [], 0, 100
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": limit, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            print(f"  Error fetching listings: {r.status_code} {r.text[:100]}")
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(0.5)
    return listings


def pick_tags(title):
    t = title.lower()
    for keywords, tags in TAG_RULES:
        if any(kw in t for kw in keywords):
            return tags
    return DEFAULT_TAGS


def main():
    done  = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - SEO Tag Update (ALL Listings)")
    print(f"  Already done: {len(done)}")
    print(f"{'='*65}\n")

    print("  Fetching all active listings...")
    listings = fetch_all_listings(token)
    total    = len(listings)
    print(f"  Found {total} listings\n")

    ok = 0
    for i, listing in enumerate(listings, 1):
        lid   = str(listing["listing_id"])
        title = listing.get("title", "")

        if lid in done:
            print(f"[{i:03d}/{total}] SKIP: {title[:55]}")
            ok += 1
            continue

        tags = pick_tags(title)
        print(f"[{i:03d}/{total}] {title[:55]}")

        r = requests.patch(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}",
            headers=auth_headers(token),
            json={"tags": tags},
            timeout=30,
        )
        time.sleep(0.8)

        if r.ok:
            ok += 1
            done[lid] = title[:60]
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"    → {tags[0]}, {tags[1]}, {tags[2]} ...")
        else:
            print(f"    ERROR {r.status_code}: {r.text[:120]}")

        if i % 10 == 0:
            token = get_token()

    print(f"\n{'='*65}")
    print(f"  Done: {ok}/{total} listings updated with SEO tags")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
