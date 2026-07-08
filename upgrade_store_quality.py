"""
upgrade_store_quality.py
Fixes ALL listings:
1. Replaces 3 wasted generic tags with niche long-tail tags
2. Rewrites first 2 lines of description with product-specific hooks
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
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}

def detect_type(title):
    t = title.lower()
    if any(x in t for x in ["bundle", "complete", "system", "os", "kit", "pack"]):
        return "bundle"
    if any(x in t for x in ["budget", "expense", "spending", "financial", "money", "cash flow"]):
        return "budget"
    if any(x in t for x in ["invoice", "client", "freelanc", "billing", "payment"]):
        return "invoice"
    if any(x in t for x in ["kpi", "business", "sales", "revenue", "pipeline", "crm", "startup"]):
        return "kpi"
    if any(x in t for x in ["workout", "fitness", "gym", "exercise", "weight", "training"]):
        return "fitness"
    if any(x in t for x in ["meal", "food", "recipe", "nutrition", "grocery", "diet"]):
        return "meal"
    if any(x in t for x in ["habit", "routine", "daily", "morning", "evening"]):
        return "habit"
    if any(x in t for x in ["goal", "vision", "dream", "bucket", "achievement"]):
        return "goals"
    if any(x in t for x in ["student", "school", "study", "college", "class", "assignment", "grade"]):
        return "student"
    if any(x in t for x in ["wedding", "event", "party", "birthday"]):
        return "event"
    if any(x in t for x in ["content", "social media", "instagram", "youtube", "tiktok", "creator"]):
        return "content"
    if any(x in t for x in ["project", "task", "team", "agile", "sprint", "gantt"]):
        return "project"
    if any(x in t for x in ["inventory", "stock", "product", "ecommerce", "shop tracker"]):
        return "inventory"
    if any(x in t for x in ["real estate", "property", "rental", "lease"]):
        return "realestate"
    if any(x in t for x in ["hr", "employee", "onboard", "hiring", "recruitment"]):
        return "hr"
    if any(x in t for x in ["restaurant", "cafe", "menu", "food business"]):
        return "restaurant"
    if any(x in t for x in ["travel", "trip", "vacation", "itinerary", "packing"]):
        return "travel"
    if any(x in t for x in ["weekly planner", "monthly planner", "daily planner", "planner"]):
        return "planner"
    return "productivity"

# Niche replacement tags (replaces: google sheets, instant download, digital download)
NICHE_TAGS = {
    "budget":      ["personal finance tracker", "monthly budget planner", "money saving tracker"],
    "invoice":     ["freelancer invoice template", "client billing tracker", "self employed invoice"],
    "kpi":         ["business performance tracker", "startup metrics dashboard", "sales kpi template"],
    "fitness":     ["gym progress tracker", "workout log template", "fitness journal spreadsheet"],
    "meal":        ["weekly meal prep planner", "grocery list template", "nutrition tracker spreadsheet"],
    "habit":       ["daily habit tracker template", "morning routine planner", "self improvement tracker"],
    "goals":       ["annual goals planner", "vision board spreadsheet", "goal setting template"],
    "student":     ["student study planner", "college assignment tracker", "academic grade tracker"],
    "event":       ["wedding budget planner", "event planning spreadsheet", "wedding checklist template"],
    "content":     ["content calendar template", "social media planner spreadsheet", "instagram post planner"],
    "project":     ["project management template", "task tracker spreadsheet", "team productivity planner"],
    "inventory":   ["inventory management template", "stock tracker spreadsheet", "product inventory sheet"],
    "realestate":  ["real estate deal tracker", "rental property spreadsheet", "property analysis template"],
    "hr":          ["employee onboarding template", "hr management spreadsheet", "hiring tracker google sheets"],
    "restaurant":  ["restaurant management spreadsheet", "menu cost calculator", "food business tracker"],
    "travel":      ["travel itinerary template", "vacation budget planner", "trip planning spreadsheet"],
    "planner":     ["weekly planner template", "productivity planner spreadsheet", "daily schedule template"],
    "bundle":      ["google sheets bundle template", "productivity bundle spreadsheet", "all in one planner bundle"],
    "productivity": ["productivity planner template", "time management spreadsheet", "daily task tracker"],
}

# First 2 lines of description (product-specific hook)
DESC_HOOKS = {
    "budget":      "Stop guessing where your money goes. This budget tracker auto-calculates every expense, shows your spending patterns, and tells you exactly how much you can save — all inside Google Sheets.\n\nNo subscriptions. No app. Just open, enter your numbers, and see your finances clearly in under 2 minutes.",
    "invoice":     "Never chase a late payment again. This invoice tracker keeps every client, payment, and deadline in one place — so you always know who owes you and how much.\n\nBuilt for freelancers who want to look professional without paying for expensive billing software.",
    "kpi":         "Your business is growing — but are your numbers telling the full story? This KPI dashboard gives you real-time visibility into revenue, costs, and performance in one clean Google Sheet.\n\nSet up in minutes. No formulas needed. No coding. Just plug in your data and see the truth.",
    "fitness":     "Most people quit because they never see progress. This workout tracker logs every session, tracks your strength gains over time, and shows you exactly how far you've come.\n\nWorks for any training style — gym, home, cardio, or lifting. Open it on your phone between sets.",
    "meal":        "Meal planning shouldn't take longer than cooking. This planner builds your weekly menu, generates your grocery list automatically, and tracks your nutrition goals — all in one sheet.\n\nSave money on food, reduce waste, and eat better starting this week.",
    "habit":       "The difference between where you are and where you want to be is your daily habits. This tracker makes them visible, measurable, and actually achievable.\n\nTrack up to 20 habits per month. See your streaks. Build momentum that lasts.",
    "goals":       "Goals without a system stay wishes. This planner breaks your big goals into monthly milestones, weekly actions, and daily priorities — so you make progress every single day.\n\nUsed by people who are serious about results, not just motivation.",
    "student":     "Juggling classes, assignments, and deadlines is overwhelming. This student planner puts everything in one place — your schedule, grades, study sessions, and to-do list.\n\nSpend less time organizing and more time actually studying.",
    "event":       "Planning an event without a system leads to stress, overspending, and things falling through the cracks. This planner tracks every task, vendor, cost, and deadline in one sheet.\n\nStay on budget. Stay on schedule. Enjoy the day you actually planned for.",
    "content":     "Posting without a plan wastes hours and gets no results. This content calendar helps you plan, batch, and schedule content across all platforms in one organized Google Sheet.\n\nKnow exactly what to post, when, and why — every single week.",
    "project":     "Projects fail when tasks fall through the cracks. This tracker gives every task an owner, deadline, and status — so nothing gets lost and nothing is late.\n\nWorks for teams, freelancers, and solo founders managing multiple projects at once.",
    "inventory":   "Running out of stock — or overstocking — costs money. This inventory tracker gives you real-time visibility into every product, quantity, and reorder point.\n\nSimple enough to use daily. Powerful enough to manage hundreds of SKUs.",
    "realestate":  "Analyzing deals by gut feeling is how investors lose money. This spreadsheet runs the numbers automatically — cash flow, ROI, cap rate, and more — so you make data-driven decisions.\n\nWorks for buy-and-hold, flips, and rental properties.",
    "hr":          "Onboarding new employees shouldn't feel chaotic. This HR template tracks every step of the process — from offer letter to first 90 days — so nothing gets missed.\n\nProfessional, organized, and ready to use from day one.",
    "restaurant":  "Food costs, labor, and waste are eating your restaurant's profit. This tracker shows you exactly where the money goes — so you can fix it before it becomes a crisis.\n\nBuilt for restaurant owners who want real numbers, not guesses.",
    "travel":      "Bad trips happen when you don't plan. This travel planner organizes your itinerary, budget, packing list, and bookings in one place — so you arrive relaxed, not stressed.\n\nWorks for solo travel, couples, families, and group trips.",
    "planner":     "A cluttered week starts with no plan. This weekly planner gives every hour a purpose — your priorities, tasks, habits, and appointments all in one clean Google Sheet.\n\nSpend 10 minutes planning Sunday night and save hours every week.",
    "bundle":      "Why buy one tool when you can have a complete system? This bundle gives you multiple professional Google Sheets templates that work together — for budgeting, tracking, planning, and growing.\n\nEverything auto-calculates. Everything auto-links. Set up once, use it for years.",
    "productivity": "Feeling busy but not productive? This template helps you focus on what actually moves the needle — tasks, priorities, and time blocks — all in one clean Google Sheet.\n\nNo more lost to-do lists. No more end-of-day regret. Just clear, focused work.",
}

WASTE_TAGS = {"google sheets", "instant download", "digital download",
              "google sheet", "digital product", "spreadsheet template",
              "instant access", "digital file"}

def fix_tags(current_tags, ptype):
    replacement = NICHE_TAGS.get(ptype, NICHE_TAGS["productivity"])
    new_tags = []
    replaced = 0
    replace_list = list(replacement)

    for tag in current_tags:
        if tag.lower() in WASTE_TAGS and replaced < len(replace_list):
            new_tags.append(replace_list[replaced])
            replaced += 1
        else:
            new_tags.append(tag)

    # If we didn't find waste tags, append at end (up to 13 max)
    while replaced < len(replace_list) and len(new_tags) < 13:
        new_tags.append(replace_list[replaced])
        replaced += 1

    return new_tags[:13]

def fix_description(current_desc, ptype):
    hook = DESC_HOOKS.get(ptype, DESC_HOOKS["productivity"])
    # Find where the bullet points start (lines starting with ✅ or •)
    lines = current_desc.split("\n")
    bullet_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith(("✅", "•", "→", "-", "*", "✓")):
            bullet_start = i
            break

    if bullet_start > 0:
        bullets = "\n".join(lines[bullet_start:])
        return hook + "\n\n" + bullets
    else:
        # No bullets found, just prepend hook
        return hook + "\n\n" + current_desc

def update_listing(token, lid, new_tags, new_desc):
    import urllib.parse
    data = "tags[]=" + "&tags[]=".join(urllib.parse.quote(t) for t in new_tags)
    data += "&description=" + urllib.parse.quote(new_desc)
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token),
                 "Content-Type": "application/x-www-form-urlencoded"},
        data=data,
        timeout=30,
    )
    return r.ok, r.status_code

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset,
                                 "includes": ["tags"]}, timeout=30)
        if not r.ok:
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
    print("  NasriTools — Full Store Quality Upgrade")
    print("  Fixing: tags + description hooks on all listings")
    print("=" * 65)

    token    = get_token()
    listings = get_all_listings(token)
    total    = len(listings)
    print(f"[*] {total} listings found\n")

    ok = fail = 0

    for idx, l in enumerate(listings, 1):
        lid   = l["listing_id"]
        title = l.get("title", "")
        desc  = l.get("description", "")
        tags  = l.get("tags", [])

        ptype = detect_type(title)
        new_tags = fix_tags(tags, ptype)
        new_desc = fix_description(desc, ptype)

        print(f"  [{idx:3}/{total}] [{ptype:12}] {title[:40]}...", end=" ", flush=True)

        token = get_token()
        success, code = update_listing(token, lid, new_tags, new_desc)

        if success:
            print("OK")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1

        time.sleep(0.8)
        if idx % 20 == 0:
            token = get_token()

    print(f"\n{'=' * 65}")
    print(f"  Updated: {ok} | Failed: {fail}")
    print(f"{'=' * 65}")

if __name__ == "__main__":
    main()
