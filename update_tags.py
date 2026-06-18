"""
NasriTools - Update Etsy Listing Tags for SEO
Updates all 10 main products with 13 optimized tags each
Run: python update_tags.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"

# 13 tags per product, max 20 chars each — high-volume Etsy search terms
TAGS = {
    "budget_tracker": [
        "budget tracker", "google sheets budget", "expense tracker",
        "monthly budget", "personal finance", "budget spreadsheet",
        "income tracker", "budget planner", "financial tracker",
        "money tracker", "household budget", "spending tracker",
        "digital download",
    ],
    "habit_tracker": [
        "habit tracker", "daily habit tracker", "google sheets habit",
        "habit planner", "routine tracker", "productivity tracker",
        "30 day habits", "habit log", "self improvement",
        "wellness tracker", "goal tracker", "morning routine",
        "streak counter",
    ],
    "meal_planner": [
        "meal planner", "weekly meal plan", "grocery list template",
        "meal prep planner", "food planner", "dinner planner",
        "meal tracker", "recipe organizer", "pantry tracker",
        "nutrition tracker", "meal planning", "google sheets meal",
        "digital planner",
    ],
    "wedding_planner": [
        "wedding planner", "wedding budget", "guest list template",
        "wedding checklist", "vendor tracker", "wedding organizer",
        "bride to be gift", "wedding timeline", "seating chart",
        "rsvp tracker", "wedding coordinator", "wedding template",
        "wedding spreadsheet",
    ],
    "workout_tracker": [
        "workout tracker", "gym log", "exercise tracker",
        "fitness planner", "weight training log", "strength tracker",
        "workout log", "fitness spreadsheet", "body measurement",
        "pr tracker", "cardio log", "fitness template",
        "google sheets gym",
    ],
    "content_creator_planner": [
        "content planner", "social media planner", "content calendar",
        "creator planner", "instagram planner", "youtube planner",
        "content tracker", "posting schedule", "influencer planner",
        "brand deal tracker", "analytics tracker", "content creator",
        "digital planner",
    ],
    "freelancer_invoice_tracker": [
        "invoice tracker", "freelancer tracker", "client tracker",
        "freelance invoice", "business tracker", "income tracker",
        "project tracker", "freelance planner", "invoice template",
        "tax tracker", "client database", "payment tracker",
        "freelance tools",
    ],
    "student_planner": [
        "student planner", "academic planner", "college planner",
        "assignment tracker", "grade tracker", "study planner",
        "school planner", "gpa tracker", "exam planner",
        "class schedule", "homework tracker", "student template",
        "back to school",
    ],
    "goals_planner": [
        "goal planner", "goal tracker", "annual goals template",
        "vision board notes", "goal setting", "action plan",
        "milestone tracker", "habit planner", "life planner",
        "self improvement", "90 day plan", "goal spreadsheet",
        "productivity planner",
    ],
    "weekly_planner": [
        "weekly planner", "time blocking", "weekly schedule",
        "productivity planner", "task planner", "to do list",
        "daily planner", "weekly organizer", "time management",
        "priority list", "week planner", "schedule template",
        "digital planner",
    ],
}


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


def update_listing_tags(token, listing_id, tags):
    headers = {
        "Authorization": "Bearer " + token["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
        "Content-Type": "application/json",
    }
    payload = {"tags": tags}
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}",
        headers=headers,
        json=payload,
        timeout=30,
    )
    return r


def main():
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    token     = get_token()
    total     = len(TAGS)

    print(f"\n{'='*60}")
    print(f"  NasriTools - Update Tags for SEO  [{total} products]")
    print(f"{'='*60}\n")

    ok = 0
    for i, (slug, tags) in enumerate(TAGS.items(), 1):
        lid = published.get(slug)
        if not lid:
            print(f"[{i:02d}/{total}] SKIP (no listing ID): {slug}")
            continue

        print(f"[{i:02d}/{total}] {slug}  (listing {lid})")
        r = update_listing_tags(token, lid, tags)
        time.sleep(1)

        if r.ok:
            ok += 1
            print(f"    tags updated: OK")
        else:
            print(f"    ERROR {r.status_code}: {r.text[:200]}")

        if i % 5 == 0:
            token = get_token()

    print(f"\n{'='*60}")
    print(f"  Done: {ok}/{total} listings updated with SEO tags")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
