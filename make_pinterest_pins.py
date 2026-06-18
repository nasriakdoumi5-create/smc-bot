"""
NasriTools - Pinterest Pin Image Generator
Creates vertical 1000x1500px pin images for all 10 products
No authentication needed — runs fully offline
Run: python make_pinterest_pins.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os, textwrap

IMAGES_DIR = Path(os.path.expanduser("~")) / "nasri_hero_images"
PINS_DIR   = Path(os.path.expanduser("~")) / "nasri_pinterest_pins"
PINS_DIR.mkdir(exist_ok=True)

PIN_W, PIN_H = 1000, 1500

PINS = [
    {
        "slug":    "budget_tracker",
        "hero":    "budget_tracker_01_hero.jpg",
        "title":   "Budget Tracker\nGoogle Sheets",
        "bullets": ["Track income & expenses", "Auto-calculate savings", "Bill payment reminders"],
        "badge":   "FREE TEMPLATE",
        "color":   (34, 139, 87),      # green
        "light":   (220, 247, 233),
    },
    {
        "slug":    "habit_tracker",
        "hero":    "habit_tracker_01_hero.jpg",
        "title":   "Habit Tracker\nGoogle Sheets",
        "bullets": ["Track 30+ daily habits", "Auto streak counter", "Monthly completion %"],
        "badge":   "INSTANT DOWNLOAD",
        "color":   (108, 67, 176),     # purple
        "light":   (237, 228, 252),
    },
    {
        "slug":    "meal_planner",
        "hero":    "meal_planner_01_hero.jpg",
        "title":   "Meal Planner\nGoogle Sheets",
        "bullets": ["7-day meal planning", "Auto grocery list", "Save money on food"],
        "badge":   "INSTANT DOWNLOAD",
        "color":   (214, 90, 49),      # orange
        "light":   (252, 232, 224),
    },
    {
        "slug":    "wedding_planner",
        "hero":    "wedding_planner_01_hero.jpg",
        "title":   "Wedding Planner\nSpreadsheet",
        "bullets": ["Full budget tracker", "Guest list & RSVP", "Vendor contacts"],
        "badge":   "INSTANT DOWNLOAD",
        "color":   (185, 50, 100),     # pink
        "light":   (252, 225, 237),
    },
    {
        "slug":    "workout_tracker",
        "hero":    "workout_tracker_01_hero.jpg",
        "title":   "Workout Tracker\nGoogle Sheets",
        "bullets": ["Log sets, reps & weight", "Track personal records", "See strength gains"],
        "badge":   "INSTANT DOWNLOAD",
        "color":   (30, 100, 180),     # blue
        "light":   (220, 235, 252),
    },
    {
        "slug":    "content_creator_planner",
        "hero":    "content_creator_planner_01_hero.jpg",
        "title":   "Content Creator\nPlanner",
        "bullets": ["Plan all platforms", "Track analytics", "Never miss a post"],
        "badge":   "INSTANT DOWNLOAD",
        "color":   (200, 60, 60),      # red
        "light":   (252, 225, 225),
    },
    {
        "slug":    "freelancer_invoice_tracker",
        "hero":    "freelancer_invoice_tracker_01_hero.jpg",
        "title":   "Freelancer Invoice\nTracker",
        "bullets": ["Track all invoices", "Client database", "Income summary"],
        "badge":   "INSTANT DOWNLOAD",
        "color":   (20, 120, 140),     # teal
        "light":   (215, 242, 246),
    },
    {
        "slug":    "student_planner",
        "hero":    "student_planner_01_hero.jpg",
        "title":   "Student Planner\nGoogle Sheets",
        "bullets": ["Assignment tracker", "Grade calculator", "Exam prep checklist"],
        "badge":   "INSTANT DOWNLOAD",
        "color":   (50, 130, 70),      # dark green
        "light":   (220, 245, 225),
    },
    {
        "slug":    "goals_planner",
        "hero":    "goals_planner_01_hero.jpg",
        "title":   "Goal Planner\nGoogle Sheets",
        "bullets": ["Set 12 annual goals", "90-day action plan", "Weekly milestone track"],
        "badge":   "INSTANT DOWNLOAD",
        "color":   (160, 100, 20),     # gold
        "light":   (252, 243, 218),
    },
    {
        "slug":    "weekly_planner",
        "hero":    "weekly_planner_01_hero.jpg",
        "title":   "Weekly Planner\nGoogle Sheets",
        "bullets": ["Plan your full week", "Priority task list", "Time blocking grid"],
        "badge":   "INSTANT DOWNLOAD",
        "color":   (80, 80, 160),      # indigo
        "light":   (230, 230, 252),
    },
]

def load_font(size):
    try:
        # Try Windows fonts
        for f in ["C:/Windows/Fonts/arialbd.ttf",
                  "C:/Windows/Fonts/arial.ttf",
                  "C:/Windows/Fonts/calibrib.ttf"]:
            if Path(f).exists():
                return ImageFont.truetype(f, size)
    except Exception:
        pass
    return ImageFont.load_default()

def make_pin(pin_data):
    hero_path = IMAGES_DIR / pin_data["hero"]
    if not hero_path.exists():
        print(f"  SKIP — image not found: {hero_path}")
        return

    color  = pin_data["color"]
    light  = pin_data["light"]
    r, g, b = color

    # ── Canvas ─────────────────────────────────────────
    img = Image.new("RGB", (PIN_W, PIN_H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # ── Top colored band ───────────────────────────────
    draw.rectangle([0, 0, PIN_W, 80], fill=color)

    # ── Badge pill ─────────────────────────────────────
    badge_text = pin_data["badge"]
    f_badge = load_font(26)
    bw = 260; bh = 44
    bx = (PIN_W - bw) // 2; by = 18
    draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=22, fill=(255,255,255))
    draw.text((PIN_W//2, by+22), badge_text, font=f_badge, fill=color, anchor="mm")

    # ── Hero image (top section) ────────────────────────
    hero = Image.open(hero_path).convert("RGB")
    hero_h = 560
    hero_resized = hero.resize((PIN_W, hero_h), Image.LANCZOS)
    img.paste(hero_resized, (0, 80))

    # ── Gradient overlay on hero bottom ────────────────
    fade_start = 80 + hero_h - 120
    for y in range(120):
        alpha = int(y / 120 * 200)
        draw.rectangle([0, fade_start+y, PIN_W, fade_start+y+1],
                       fill=(255, 255, 255, alpha))

    # ── Content area background ────────────────────────
    content_y = 80 + hero_h
    draw.rectangle([0, content_y, PIN_W, PIN_H], fill=(255, 255, 255))

    # ── Color accent bar ───────────────────────────────
    draw.rectangle([0, content_y, PIN_W, content_y+6], fill=color)

    # ── Title ──────────────────────────────────────────
    title_y = content_y + 30
    f_title = load_font(62)
    for line in pin_data["title"].split("\n"):
        draw.text((PIN_W//2, title_y), line, font=f_title, fill=(30,30,30), anchor="mm")
        title_y += 72

    # ── Subtitle ───────────────────────────────────────
    sub_y = title_y + 10
    f_sub = load_font(30)
    draw.text((PIN_W//2, sub_y), "Free Template • Instant Download", font=f_sub,
              fill=(120,120,120), anchor="mm")

    # ── Bullets ────────────────────────────────────────
    bullet_y = sub_y + 55
    f_bullet = load_font(34)
    for bullet in pin_data["bullets"]:
        # pill background
        draw.rounded_rectangle([60, bullet_y-4, PIN_W-60, bullet_y+44],
                               radius=22, fill=light)
        # dot
        draw.ellipse([80, bullet_y+12, 104, bullet_y+36], fill=color)
        # text
        draw.text((120, bullet_y+20), bullet, font=f_bullet, fill=(40,40,40), anchor="lm")
        bullet_y += 66

    # ── Bottom CTA bar ─────────────────────────────────
    cta_y = PIN_H - 130
    draw.rectangle([0, cta_y, PIN_W, PIN_H], fill=color)
    f_cta = load_font(36)
    draw.text((PIN_W//2, cta_y+35), "Get it FREE on Etsy", font=f_cta,
              fill=(255,255,255), anchor="mm")
    f_url = load_font(28)
    draw.text((PIN_W//2, cta_y+80), "nasritools.etsy.com", font=f_url,
              fill=(255, 255, 200), anchor="mm")

    # ── Save ───────────────────────────────────────────
    out = PINS_DIR / f"{pin_data['slug']}_pin.jpg"
    img.save(out, "JPEG", quality=92)
    print(f"  Saved: {out.name}")

def main():
    print(f"\n{'='*55}")
    print(f"  NasriTools - Pinterest Pin Generator")
    print(f"  Output: {PINS_DIR}")
    print(f"{'='*55}\n")

    for i, pin in enumerate(PINS, 1):
        print(f"[{i:02d}/{len(PINS)}] {pin['slug']}")
        make_pin(pin)

    print(f"\n{'='*55}")
    print(f"  Done! {len(PINS)} pins saved to:")
    print(f"  {PINS_DIR}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    main()
