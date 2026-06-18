"""
NasriTools - Improve SEO for Top 10 Products
- Updates titles to lead with strongest search keyword
- Replaces all 13 tags with high-traffic long-tail keywords
- Uses PATCH endpoint to update each listing

Run: python improve_seo.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://api.etsy.com/v3/application"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_seo_improved.json"

# ── Top 10 products — optimized SEO ───────────────────
SEO_DATA = {
    "budget_tracker": {
        "title": "Budget Tracker Spreadsheet Google Sheets | Monthly Budget Planner | Expense Tracker Template | Bill Organizer",
        "tags": [
            "budget tracker",
            "google sheets budget",
            "monthly budget planner",
            "expense tracker",
            "budget spreadsheet",
            "bill tracker template",
            "personal finance",
            "money manager sheet",
            "household budget",
            "spending tracker",
            "financial planner",
            "savings tracker",
            "budget template"
        ]
    },
    "habit_tracker": {
        "title": "Habit Tracker Google Sheets | Daily Habit Planner Spreadsheet | Routine Tracker | Monthly Habit Log Template",
        "tags": [
            "habit tracker",
            "daily habit tracker",
            "habit planner",
            "routine tracker",
            "google sheets habits",
            "habit log template",
            "daily routine planner",
            "streak tracker",
            "30 day habit tracker",
            "monthly habit log",
            "wellness tracker",
            "productivity tracker",
            "habit spreadsheet"
        ]
    },
    "meal_planner": {
        "title": "Meal Planner Google Sheets | Weekly Meal Planning Spreadsheet | Grocery List Template | Dinner Planner",
        "tags": [
            "meal planner",
            "weekly meal planner",
            "meal planning spreadsheet",
            "grocery list template",
            "dinner planner",
            "meal prep planner",
            "google sheets meal",
            "family meal planner",
            "nutrition tracker",
            "recipe organizer",
            "menu planner weekly",
            "healthy eating planner",
            "food budget planner"
        ]
    },
    "wedding_planner": {
        "title": "Wedding Planner Spreadsheet Google Sheets | Wedding Budget Tracker | Guest List Template | Wedding Checklist",
        "tags": [
            "wedding planner",
            "wedding budget tracker",
            "wedding spreadsheet",
            "guest list template",
            "wedding checklist",
            "wedding organizer",
            "bride planner",
            "wedding timeline",
            "wedding budget planner",
            "wedding planning tool",
            "wedding vendor tracker",
            "engagement planner",
            "wedding day schedule"
        ]
    },
    "workout_tracker": {
        "title": "Workout Tracker Google Sheets | Gym Progress Spreadsheet | Exercise Log Template | Fitness Planner",
        "tags": [
            "workout tracker",
            "gym tracker",
            "exercise log template",
            "fitness tracker sheet",
            "workout log",
            "gym progress tracker",
            "exercise planner",
            "workout spreadsheet",
            "strength training log",
            "fitness planner",
            "weight training tracker",
            "gym log google sheets",
            "workout journal"
        ]
    },
    "content_creator_planner": {
        "title": "Content Creator Planner Google Sheets | Social Media Content Calendar | YouTube Tracker | Instagram Planner",
        "tags": [
            "content creator planner",
            "social media calendar",
            "content calendar",
            "youtube tracker",
            "instagram planner",
            "content planner",
            "social media planner",
            "influencer planner",
            "content schedule",
            "tiktok planner",
            "creator dashboard",
            "posting schedule",
            "content strategy sheet"
        ]
    },
    "freelancer_invoice_tracker": {
        "title": "Freelancer Invoice Tracker Google Sheets | Client Management Spreadsheet | Income Tracker | Invoice Template",
        "tags": [
            "freelancer invoice",
            "client tracker",
            "invoice spreadsheet",
            "freelance income tracker",
            "client management",
            "invoice template",
            "freelancer dashboard",
            "project tracker",
            "payment tracker",
            "self employed tracker",
            "freelance organizer",
            "business invoice log",
            "income expense tracker"
        ]
    },
    "student_planner": {
        "title": "Student Planner Google Sheets | Academic Planner Spreadsheet | Study Schedule Template | Grade Tracker",
        "tags": [
            "student planner",
            "academic planner",
            "study planner",
            "grade tracker",
            "student spreadsheet",
            "college planner",
            "study schedule",
            "semester planner",
            "homework tracker",
            "student organizer",
            "class schedule",
            "school planner google",
            "assignment tracker"
        ]
    },
    "goals_planner": {
        "title": "Goal Planner Google Sheets | Annual Goal Tracker Spreadsheet | Vision Board Planner | Goal Setting Template",
        "tags": [
            "goal planner",
            "goal tracker",
            "goal setting template",
            "annual planner",
            "vision board planner",
            "goal spreadsheet",
            "yearly goals tracker",
            "goal achievement",
            "personal development",
            "milestone tracker",
            "bucket list planner",
            "life goals planner",
            "new year goals"
        ]
    },
    "weekly_planner": {
        "title": "Weekly Planner Google Sheets | Week at a Glance Spreadsheet | Productivity Planner | Daily Schedule Template",
        "tags": [
            "weekly planner",
            "week planner",
            "daily planner",
            "productivity planner",
            "weekly schedule",
            "google sheets planner",
            "weekly organizer",
            "task planner",
            "weekly schedule sheet",
            "time management",
            "weekly to do list",
            "work week planner",
            "agenda template"
        ]
    },
}

# ── Auth ───────────────────────────────────────────────
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

def etsy_auth(t):
    return {
        "Authorization": "Bearer " + t["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
        "Content-Type": "application/json"
    }

# ── Main ───────────────────────────────────────────────
def main():
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    done      = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}

    token = get_token()
    total = len(SEO_DATA)

    print(f"\n{'='*60}")
    print(f"  NasriTools - SEO Improvement  [Top {total} Products]")
    print(f"  Already done: {len(done)}")
    print(f"{'='*60}\n")

    ok = 0
    for i, (slug, data) in enumerate(SEO_DATA.items(), 1):
        lid = published.get(slug)

        if slug in done:
            print(f"[{i:02d}/{total}] SKIP (done): {slug}")
            continue
        if not lid:
            print(f"[{i:02d}/{total}] SKIP (no listing ID): {slug}")
            continue

        print(f"[{i:02d}/{total}] {slug}")

        payload = {
            "title": data["title"][:140],
            "tags":  data["tags"][:13],
        }

        r = requests.patch(
            API + f"/shops/{SHOP_ID}/listings/{lid}",
            headers=etsy_auth(token),
            json=payload,
            timeout=30,
        )
        time.sleep(0.6)

        if r.ok:
            ok += 1
            done[slug] = lid
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"    updated: OK")
        else:
            print(f"    ERROR: {r.text[:120]}")

        if i % 5 == 0:
            token = get_token()

    print(f"\n{'='*60}")
    print(f"  Done: {ok}/{total} listings SEO updated")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
