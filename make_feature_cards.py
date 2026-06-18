"""
NasriTools - Feature Card Image Generator
Creates "What's Included" cards (2000x2000px) for all 10 products
No authentication needed — runs fully offline
Run: python make_feature_cards.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

CARDS_DIR = Path(os.path.expanduser("~")) / "nasri_feature_cards"
CARDS_DIR.mkdir(exist_ok=True)
SIZE = 2000

PRODUCTS = [
    {
        "slug": "budget_tracker", "color": (34,139,87), "light": (220,247,233),
        "title": "Budget Tracker",
        "subtitle": "Google Sheets Template",
        "features": [
            "Monthly income & expense tracker",
            "Auto-calculate savings & balance",
            "Bill payment tracker with due dates",
            "Savings goal progress bar",
            "Spending by category charts",
            "Annual financial summary",
        ],
        "tag": "MOST POPULAR",
    },
    {
        "slug": "habit_tracker", "color": (108,67,176), "light": (237,228,252),
        "title": "Habit Tracker",
        "subtitle": "Google Sheets Template",
        "features": [
            "Track up to 30 daily habits",
            "Automatic streak counter",
            "Monthly completion percentage",
            "Weekly review & reflection section",
            "Habit categories (health, work, wellness)",
            "Progress comparison charts",
        ],
        "tag": "TOP SELLER",
    },
    {
        "slug": "meal_planner", "color": (214,90,49), "light": (252,232,224),
        "title": "Meal Planner",
        "subtitle": "Google Sheets Template",
        "features": [
            "7-day meal planning grid",
            "Auto-generated grocery list by category",
            "Pantry inventory tracker",
            "Nutritional notes per meal",
            "Monthly meal calendar view",
            "Recipe link organizer",
        ],
        "tag": "",
    },
    {
        "slug": "wedding_planner", "color": (185,50,100), "light": (252,225,237),
        "title": "Wedding Planner",
        "subtitle": "Spreadsheet Template",
        "features": [
            "Full wedding budget tracker",
            "Guest list & RSVP manager",
            "Vendor contact & payment tracker",
            "Wedding day timeline & schedule",
            "Seating chart helper",
            "12-month to-do checklist",
        ],
        "tag": "",
    },
    {
        "slug": "workout_tracker", "color": (30,100,180), "light": (220,235,252),
        "title": "Workout Tracker",
        "subtitle": "Google Sheets Template",
        "features": [
            "Log sets, reps & weight per exercise",
            "Personal record (PR) tracker",
            "Body measurements tracker",
            "Cardio & session log",
            "Monthly fitness goals section",
            "Strength progress charts",
        ],
        "tag": "",
    },
    {
        "slug": "content_creator_planner", "color": (200,60,60), "light": (252,225,225),
        "title": "Content Creator Planner",
        "subtitle": "Google Sheets Template",
        "features": [
            "Monthly content calendar (all platforms)",
            "Video & post idea bank",
            "Publishing schedule tracker",
            "Analytics tracking (views, followers)",
            "Brand deal & sponsorship tracker",
            "Content pillars planning section",
        ],
        "tag": "",
    },
    {
        "slug": "freelancer_invoice_tracker", "color": (20,120,140), "light": (215,242,246),
        "title": "Freelancer Invoice Tracker",
        "subtitle": "Google Sheets Template",
        "features": [
            "Invoice log with paid/pending/overdue status",
            "Client database & contact info",
            "Monthly & annual income summary",
            "Project tracker with hours & rates",
            "Tax preparation summary",
            "Late payment alerts",
        ],
        "tag": "",
    },
    {
        "slug": "student_planner", "color": (50,130,70), "light": (220,245,225),
        "title": "Student Planner",
        "subtitle": "Google Sheets Template",
        "features": [
            "Weekly class schedule",
            "Assignment tracker with due dates",
            "Grade calculator per subject",
            "GPA tracker & progress",
            "Exam preparation checklist",
            "Semester overview calendar",
        ],
        "tag": "",
    },
    {
        "slug": "goals_planner", "color": (160,100,20), "light": (252,243,218),
        "title": "Goal Planner",
        "subtitle": "Google Sheets Template",
        "features": [
            "Annual goal setting (12 goals)",
            "90-day action plan breakdown",
            "Weekly milestone tracker",
            "Habit alignment section",
            "Vision & inspiration board notes",
            "Monthly review & reflection prompts",
        ],
        "tag": "",
    },
    {
        "slug": "weekly_planner", "color": (80,80,160), "light": (230,230,252),
        "title": "Weekly Planner",
        "subtitle": "Google Sheets Template",
        "features": [
            "Week-at-a-glance daily schedule",
            "Top 3 priority task list",
            "Time blocking grid",
            "Notes & ideas section",
            "Weekly goals & intentions",
            "Habit check-in tracker",
        ],
        "tag": "",
    },
]

def load_font(size):
    for f in ["C:/Windows/Fonts/arialbd.ttf",
              "C:/Windows/Fonts/arial.ttf",
              "C:/Windows/Fonts/calibrib.ttf"]:
        if Path(f).exists():
            try: return ImageFont.truetype(f, size)
            except: pass
    return ImageFont.load_default()

def make_card(p):
    r, g, b = p["color"]
    lr, lg, lb = p["light"]

    img = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # ── Background ────────────────────────────────────
    # top colored section
    draw.rectangle([0, 0, SIZE, 520], fill=p["color"])
    # bottom light section
    draw.rectangle([0, 520, SIZE, SIZE], fill=p["light"])

    # ── Decorative circles ────────────────────────────
    for cx, cy, rad in [(1700,100,280),(100,480,200),(1850,600,150)]:
        overlay = Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx-rad, cy-rad, cx+rad, cy+rad],
                   fill=(255, 255, 255, 20))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # ── Tag pill ──────────────────────────────────────
    if p["tag"]:
        f_tag = load_font(32)
        tw = 280; th = 52
        tx = SIZE - tw - 60; ty = 50
        draw.rounded_rectangle([tx, ty, tx+tw, ty+th],
                               radius=26, fill=(255,255,255))
        draw.text((tx+tw//2, ty+26), p["tag"], font=f_tag,
                  fill=p["color"], anchor="mm")

    # ── Title area ────────────────────────────────────
    f_title = load_font(90)
    f_sub   = load_font(44)
    draw.text((SIZE//2, 160), p["title"], font=f_title,
              fill=(255,255,255), anchor="mm")
    draw.text((SIZE//2, 270), p["subtitle"], font=f_sub,
              fill=(255,255,255,200), anchor="mm")

    # ── Divider ───────────────────────────────────────
    draw.rectangle([SIZE//2-120, 320, SIZE//2+120, 326],
                   fill=(255,255,255,150))

    # ── "WHAT'S INCLUDED" label ───────────────────────
    f_wh = load_font(38)
    draw.text((SIZE//2, 400), "✔  WHAT'S INCLUDED", font=f_wh,
              fill=(255,255,255), anchor="mm")

    # ── Feature rows ─────────────────────────────────
    f_feat = load_font(48)
    feat_y = 580
    for feat in p["features"]:
        # card row
        draw.rounded_rectangle([80, feat_y, SIZE-80, feat_y+100],
                               radius=16, fill=(255,255,255))
        # checkmark circle
        draw.ellipse([110, feat_y+20, 170, feat_y+80], fill=p["color"])
        draw.text((140, feat_y+50), "✓", font=load_font(40),
                  fill=(255,255,255), anchor="mm")
        # feature text
        draw.text((210, feat_y+50), feat, font=f_feat,
                  fill=(40,40,40), anchor="lm")
        feat_y += 122

    # ── Bottom strip ──────────────────────────────────
    strip_y = SIZE - 140
    draw.rectangle([0, strip_y, SIZE, SIZE], fill=p["color"])
    f_bot = load_font(40)
    draw.text((SIZE//2, strip_y+45), "Instant Download  •  Works on Any Device  •  100% Customizable",
              font=f_bot, fill=(255,255,255), anchor="mm")
    f_url = load_font(34)
    draw.text((SIZE//2, strip_y+100), "nasritools.etsy.com",
              font=f_url, fill=(255,255,200), anchor="mm")

    out = CARDS_DIR / f"{p['slug']}_features.jpg"
    img.save(out, "JPEG", quality=93)
    print(f"  Saved: {out.name}")

def main():
    print(f"\n{'='*55}")
    print(f"  NasriTools - Feature Card Generator")
    print(f"  Output: {CARDS_DIR}")
    print(f"{'='*55}\n")
    for i, p in enumerate(PRODUCTS, 1):
        print(f"[{i:02d}/{len(PRODUCTS)}] {p['slug']}")
        make_card(p)
    print(f"\n{'='*55}")
    print(f"  Done! {len(PRODUCTS)} feature cards saved to:")
    print(f"  {CARDS_DIR}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    main()
