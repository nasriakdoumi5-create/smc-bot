"""
NasriTools - Pinterest Auto-Pinner
Creates all 10 pins automatically via Pinterest API v5
Setup: see instructions below
Run: python pinterest_pins.py
"""
import json, os, time, requests, base64, sys
from pathlib import Path

# ── Config ─────────────────────────────────────────────
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"   # replace after OAuth
IMAGES_DIR   = Path(os.path.expanduser("~")) / "nasri_hero_images"
DONE_FILE    = Path(os.path.expanduser("~")) / "pinterest_done.json"
API          = "https://api.pinterest.com/v5"

# ── Pin data ────────────────────────────────────────────
PINS = [
    {
        "slug":  "budget_tracker",
        "image": "budget_tracker_01_hero.jpg",
        "title": "Free Budget Tracker Google Sheets Template",
        "desc":  "Take control of your money. Track income, expenses & savings automatically. Google Sheets budget tracker — instant download, works on any device. #budgettracker #googlesheets #personalfinance #budgetplanner #savemoney",
        "link":  "https://nasritools.etsy.com",
    },
    {
        "slug":  "habit_tracker",
        "image": "habit_tracker_01_hero.jpg",
        "title": "Habit Tracker Google Sheets | Daily Routine Tracker Template",
        "desc":  "Build better habits automatically. Track daily routines, streaks & goals in one place. Google Sheets habit tracker — instant download, no app needed. #habittracker #googlesheets #productivity #habitplanner #dailyroutine",
        "link":  "https://nasritools.etsy.com",
    },
    {
        "slug":  "meal_planner",
        "image": "meal_planner_01_hero.jpg",
        "title": "Weekly Meal Planner Google Sheets | Grocery List Template",
        "desc":  "Plan meals for the whole week in minutes. Includes grocery list, nutrition tracker & meal prep guide. Google Sheets meal planner — free instant download. #mealplanner #googlesheets #mealprep #grocerylist #healthyeating",
        "link":  "https://nasritools.etsy.com",
    },
    {
        "slug":  "wedding_planner",
        "image": "wedding_planner_01_hero.jpg",
        "title": "Wedding Planner Spreadsheet | Budget & Guest List Template",
        "desc":  "Plan your perfect wedding stress-free. Budget tracker, guest list, vendor contacts & timeline — all in one Google Sheet. Instant download. #weddingplanner #weddingtips #weddingbudget #bridetobe #weddingchecklist",
        "link":  "https://nasritools.etsy.com",
    },
    {
        "slug":  "workout_tracker",
        "image": "workout_tracker_01_hero.jpg",
        "title": "Workout Tracker Google Sheets | Gym Progress Log Template",
        "desc":  "Track every rep, set & personal record. Google Sheets workout log — see your gym progress week by week. Instant download. #workouttracker #gymtracker #fitnessgoals #googlesheets #workoutlog",
        "link":  "https://nasritools.etsy.com",
    },
    {
        "slug":  "content_creator_planner",
        "image": "content_creator_planner_01_hero.jpg",
        "title": "Content Creator Planner | Social Media Calendar Google Sheets",
        "desc":  "Never miss a post again. Plan YouTube, Instagram & TikTok content in one place. Google Sheets content calendar — instant download. #contentcreator #socialmedia #contentcalendar #youtuber #instagramtips",
        "link":  "https://nasritools.etsy.com",
    },
    {
        "slug":  "freelancer_invoice_tracker",
        "image": "freelancer_invoice_tracker_01_hero.jpg",
        "title": "Freelancer Invoice Tracker | Client & Income Management Sheet",
        "desc":  "Track every invoice, client & payment automatically. Google Sheets freelancer dashboard — stay on top of your business finances. #freelancer #invoicetracker #freelancetips #googlesheets #selfemployed",
        "link":  "https://nasritools.etsy.com",
    },
    {
        "slug":  "student_planner",
        "image": "student_planner_01_hero.jpg",
        "title": "Student Planner Google Sheets | Study Schedule & Grade Tracker",
        "desc":  "Organize your classes, assignments & grades in one Google Sheet. Student planner template — instant download, free to customize. #studentplanner #studytips #googlesheets #collegelife #studyorganization",
        "link":  "https://nasritools.etsy.com",
    },
    {
        "slug":  "goals_planner",
        "image": "goals_planner_01_hero.jpg",
        "title": "Goal Planner Google Sheets | Annual Goal Tracker Template",
        "desc":  "Turn your dreams into a plan. Track yearly goals, milestones & habits in one Google Sheet. Goal planner — instant download. #goalplanner #goalsetting #googlesheets #personaldevelopment #newyeargoals",
        "link":  "https://nasritools.etsy.com",
    },
    {
        "slug":  "weekly_planner",
        "image": "weekly_planner_01_hero.jpg",
        "title": "Weekly Planner Google Sheets | Productivity Planner Template",
        "desc":  "Plan your entire week in 5 minutes. Tasks, schedule & priorities — all in one Google Sheet. Weekly productivity planner — instant download. #weeklyplanner #productivitytips #googlesheets #timemanagement #weeklyorganizer",
        "link":  "https://nasritools.etsy.com",
    },
]

# ── Auth headers ────────────────────────────────────────
def headers():
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type":  "application/json",
    }

# ── Get board ID ────────────────────────────────────────
def get_board_id():
    r = requests.get(f"{API}/boards", headers=headers(), timeout=15)
    r.raise_for_status()
    boards = r.json().get("items", [])
    for b in boards:
        if "google sheets" in b["name"].lower():
            print(f"  Board found: {b['name']} ({b['id']})")
            return b["id"]
    # fallback: use first board
    if boards:
        print(f"  Using board: {boards[0]['name']} ({boards[0]['id']})")
        return boards[0]["id"]
    raise RuntimeError("No boards found — create 'Google Sheets Templates' board on Pinterest first.")

# ── Create one pin ──────────────────────────────────────
def create_pin(board_id, pin, img_path):
    img_data = base64.b64encode(img_path.read_bytes()).decode()
    payload = {
        "board_id":     board_id,
        "title":        pin["title"][:100],
        "description":  pin["desc"][:500],
        "link":         pin["link"],
        "media_source": {
            "source_type":    "image_base64",
            "content_type":   "image/jpeg",
            "data":           img_data,
        },
    }
    r = requests.post(f"{API}/pins", headers=headers(), json=payload, timeout=60)
    return r

# ── Main ────────────────────────────────────────────────
def main():
    if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("\n  ERROR: Replace ACCESS_TOKEN at the top of the script.")
        print("  Get it from: https://developers.pinterest.com/apps/\n")
        sys.exit(1)

    done = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    board_id = get_board_id()
    total = len(PINS)

    print(f"\n{'='*60}")
    print(f"  NasriTools - Pinterest Auto-Pinner  [{total} pins]")
    print(f"  Already done: {len(done)}")
    print(f"{'='*60}\n")

    ok = 0
    for i, pin in enumerate(PINS, 1):
        slug = pin["slug"]

        if slug in done:
            print(f"[{i:02d}/{total}] SKIP (done): {slug}")
            ok += 1
            continue

        img_path = IMAGES_DIR / pin["image"]
        if not img_path.exists():
            print(f"[{i:02d}/{total}] SKIP (image not found): {img_path}")
            continue

        print(f"[{i:02d}/{total}] Creating pin: {slug}")
        r = create_pin(board_id, pin, img_path)
        time.sleep(2)  # avoid rate limit

        if r.ok:
            ok += 1
            done[slug] = r.json().get("id", "ok")
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"         OK  — pin ID: {done[slug]}")
        else:
            print(f"         ERROR: {r.status_code} — {r.text[:150]}")

    print(f"\n{'='*60}")
    print(f"  Done: {ok}/{total} pins created")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
