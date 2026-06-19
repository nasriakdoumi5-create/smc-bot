"""
NasriTools - Pinterest Pin Generator
Creates 3 pin designs per product (30 pins total) in 1000x1500px format.
Saved to ~/nasri_pinterest_pins/ — ready to upload or schedule via Tailwind.
Run: python generate_pinterest_pins.py
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H   = 1000, 1500
OUT    = Path(os.path.expanduser("~")) / "nasri_pinterest_pins"
WHITE  = (255, 255, 255)
DARK   = (25,  25,  35)
GRAY   = (100, 105, 120)

PRODUCTS = [
    {
        "slug": "budget_tracker",
        "name": "Budget Tracker",
        "emoji": "💰",
        "color": (31, 107, 59),
        "light": (220, 247, 233),
        "pain":     "Overspending every month?",
        "hook":     "This Google Sheets template tracks EVERY expense automatically.",
        "result":   "Users save an average of €200 extra per month.",
        "features": ["Monthly Budget Dashboard", "Income & Expense Tracker", "Savings Goal Tracker", "Net Worth Calculator"],
        "cta":      "Instant Download · €8.99",
        "price":    "€8.99",
    },
    {
        "slug": "habit_tracker",
        "name": "Habit Tracker",
        "emoji": "✅",
        "color": (192, 57, 43),
        "light": (253, 228, 224),
        "pain":     "Always breaking your habits?",
        "hook":     "Track 30 habits with automatic streak counting.",
        "result":   "Build life-changing routines in just 30 days.",
        "features": ["30-Habit Monthly Grid", "Auto Streak Counter", "Weekly Completion %", "Annual Habit Review"],
        "cta":      "Instant Download · €7.99",
        "price":    "€7.99",
    },
    {
        "slug": "meal_planner",
        "name": "Meal Planner",
        "emoji": "🥗",
        "color": (39, 174, 141),
        "light": (209, 250, 229),
        "pain":     "Wasting money on groceries?",
        "hook":     "Plan 7 days of healthy meals in just 15 minutes.",
        "result":   "Save €80+ on groceries every single week.",
        "features": ["7-Day Meal Planner", "Auto Grocery List", "Nutrition Tracker", "Recipe Database"],
        "cta":      "Instant Download · €7.99",
        "price":    "€7.99",
    },
    {
        "slug": "wedding_planner",
        "name": "Wedding Planner",
        "emoji": "💍",
        "color": (210, 82, 162),
        "light": (252, 228, 243),
        "pain":     "Wedding planning feels overwhelming?",
        "hook":     "Plan every detail of your wedding in one spreadsheet.",
        "result":   "Stay on budget and completely stress-free.",
        "features": ["Wedding Budget Tracker", "Guest List & RSVPs", "Vendor Tracker", "Month-by-Month Checklist"],
        "cta":      "Instant Download · €9.99",
        "price":    "€9.99",
    },
    {
        "slug": "workout_tracker",
        "name": "Workout Tracker",
        "emoji": "💪",
        "color": (192, 57, 43),
        "light": (253, 228, 224),
        "pain":     "Not seeing gym progress?",
        "hook":     "Log every rep, set, and personal record automatically.",
        "result":   "Beat your own records every single week.",
        "features": ["Workout Session Log", "PR Tracker", "Auto Progress Charts", "100+ Exercise Database"],
        "cta":      "Instant Download · €7.99",
        "price":    "€7.99",
    },
    {
        "slug": "content_creator",
        "name": "Content Creator Planner",
        "emoji": "📱",
        "color": (230, 126, 34),
        "light": (254, 243, 224),
        "pain":     "Posting without a real strategy?",
        "hook":     "Plan 3 months of content in one weekend.",
        "result":   "Grow your audience 3× faster with a system.",
        "features": ["Monthly Content Calendar", "Analytics Tracker", "Brand Deal Tracker", "Revenue Dashboard"],
        "cta":      "Instant Download · €9.99",
        "price":    "€9.99",
    },
    {
        "slug": "invoice_tracker",
        "name": "Invoice Tracker",
        "emoji": "📄",
        "color": (52, 152, 219),
        "light": (214, 234, 248),
        "pain":     "Chasing unpaid invoices again?",
        "hook":     "Track every client, invoice, and payment in one place.",
        "result":   "Get paid on time — every time.",
        "features": ["Invoice Tracker", "Client Database", "Payment Status Dashboard", "Tax Prep Sheet"],
        "cta":      "Instant Download · €8.99",
        "price":    "€8.99",
    },
    {
        "slug": "student_planner",
        "name": "Student Planner",
        "emoji": "🎓",
        "color": (108, 52, 131),
        "light": (237, 228, 252),
        "pain":     "Missing deadlines & dropping grades?",
        "hook":     "Organize your entire semester in one spreadsheet.",
        "result":   "Improve your GPA by 0.5+ points this semester.",
        "features": ["Assignment Tracker", "Auto GPA Calculator", "Exam Countdown", "Study Hours Log"],
        "cta":      "Instant Download · €7.99",
        "price":    "€7.99",
    },
    {
        "slug": "goals_planner",
        "name": "Goals Planner",
        "emoji": "🎯",
        "color": (30, 100, 180),
        "light": (220, 235, 252),
        "pain":     "Setting goals but never achieving them?",
        "hook":     "Break annual goals into 90-day action sprints.",
        "result":   "Achieve more in 90 days than most people do in a year.",
        "features": ["Annual Goals Dashboard", "90-Day Sprint Planner", "Weekly Action Tracker", "Progress Calculator"],
        "cta":      "Instant Download · €8.99",
        "price":    "€8.99",
    },
    {
        "slug": "weekly_planner",
        "name": "Weekly Planner",
        "emoji": "📅",
        "color": (108, 52, 131),
        "light": (237, 228, 252),
        "pain":     "Ending every week feeling unproductive?",
        "hook":     "Plan your perfect week using time-blocking in 15 minutes.",
        "result":   "Get 2× more done with 50% less stress.",
        "features": ["Time-Block Schedule", "Top 3 Priority Tasks", "Energy Level Planner", "Weekly Review"],
        "cta":      "Instant Download · €7.99",
        "price":    "€7.99",
    },
]


def load_font(size):
    for f in [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def load_font_reg(size):
    for f in [
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textlength(test, font=font) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_text_block(draw, text, font, x, y, max_w, fill, line_gap=10):
    lines = wrap_text(draw, text, font, max_w)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_gap
    return y


# ── Pin 1: Pain point + solution ──────────────────────────────────────────────

def make_pin_pain(p):
    color = p["color"]
    light = p["light"]

    img  = Image.new("RGB", (W, H), light)
    draw = ImageDraw.Draw(img)

    # Top solid color block
    draw.rectangle([0, 0, W, 480], fill=color)

    # Emoji
    try:
        draw.text((W // 2, 100), p["emoji"], font=load_font(90), fill=WHITE, anchor="mm")
    except Exception:
        pass

    # Brand
    draw.text((W // 2, 180), "NasriTools", font=load_font(42), fill=(255, 255, 200), anchor="mm")

    # Pain question (large)
    f_pain = load_font(64)
    pain_lines = wrap_text(draw, p["pain"].upper(), f_pain, W - 80)
    py = 240
    for line in pain_lines:
        w_line = draw.textlength(line, font=f_pain)
        draw.text(((W - w_line) // 2, py), line, font=f_pain, fill=WHITE)
        py += 74

    # Solution section
    draw.rectangle([0, 490, W, 900], fill=WHITE)

    # "HERE'S THE SOLUTION" badge
    draw.rounded_rectangle([60, 510, 680, 570], radius=28, fill=color)
    draw.text((370, 540), "HERE'S THE SOLUTION", font=load_font(32), fill=WHITE, anchor="mm")

    # Hook text
    f_hook = load_font(50)
    hy = 590
    hy = draw_text_block(draw, p["hook"], f_hook, 60, hy, W - 120, DARK, line_gap=12)

    # Result strip
    ry = max(hy + 30, 760)
    draw.rounded_rectangle([40, ry, W - 40, ry + 110], radius=20, fill=color)
    f_res = load_font_reg(36)
    res_lines = wrap_text(draw, "Result: " + p["result"], f_res, W - 120)
    rly = ry + (110 - len(res_lines) * 48) // 2
    for line in res_lines:
        draw.text((W // 2, rly), line, font=f_res, fill=WHITE, anchor="mm")
        rly += 48

    # Product name area
    draw.rectangle([0, 910, W, 1160], fill=DARK)
    draw.text((W // 2, 970), p["name"].upper(), font=load_font(60), fill=WHITE, anchor="mm")
    draw.text((W // 2, 1060), "Google Sheets Template", font=load_font_reg(38), fill=(200, 220, 255), anchor="mm")
    draw.text((W // 2, 1120), p["price"] + "  •  Instant Download", font=load_font(40), fill=(255, 220, 80), anchor="mm")

    # Bottom CTA strip
    draw.rectangle([0, 1160, W, H], fill=color)
    draw.text((W // 2, 1270), "nasritools.etsy.com", font=load_font(44), fill=WHITE, anchor="mm")
    draw.text((W // 2, 1360), "Search 'NasriTools' on Etsy", font=load_font_reg(34), fill=(255, 255, 200), anchor="mm")
    draw.text((W // 2, 1440), "Google Sheets · Instant Download · Lifetime Access", font=load_font_reg(28), fill=(220, 240, 220), anchor="mm")

    return img


# ── Pin 2: What's included ────────────────────────────────────────────────────

def make_pin_features(p):
    color = p["color"]
    light = p["light"]
    r, g, b = color

    img  = Image.new("RGB", (W, H), light)
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, W, 350], fill=color)
    try:
        draw.text((W // 2, 80), p["emoji"], font=load_font(80), fill=WHITE, anchor="mm")
    except Exception:
        pass
    draw.text((W // 2, 180), p["name"].upper(), font=load_font(58), fill=WHITE, anchor="mm")
    draw.text((W // 2, 270), "WHAT'S INCLUDED", font=load_font(40), fill=(255, 255, 200), anchor="mm")

    # Feature cards
    feat_top = 380
    feat_h   = 170
    gap      = 20

    for i, feat in enumerate(p["features"]):
        fy = feat_top + i * (feat_h + gap)
        # Card shadow
        draw.rounded_rectangle([54, fy + 5, W - 44, fy + feat_h + 5], radius=20,
                                fill=(min(r+40, 255), min(g+40, 255), min(b+40, 255)))
        # Card
        draw.rounded_rectangle([50, fy, W - 50, fy + feat_h], radius=20, fill=WHITE)
        # Accent bar
        draw.rounded_rectangle([50, fy, 68, fy + feat_h], radius=8, fill=color)
        # Check circle
        cx, cy = 110, fy + feat_h // 2
        draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=color)
        draw.text((cx, cy), "✓", font=load_font(30), fill=WHITE, anchor="mm")
        # Feature text
        draw.text((155, fy + feat_h // 2 - 14), feat, font=load_font(44), fill=DARK)

    # Price + CTA
    cta_y = feat_top + len(p["features"]) * (feat_h + gap) + 30
    draw.rounded_rectangle([60, cta_y, W - 60, cta_y + 100], radius=24, fill=color)
    draw.text((W // 2, cta_y + 50), p["cta"] + "  →  nasritools.etsy.com",
              font=load_font(36), fill=WHITE, anchor="mm")

    # Bottom
    bot_y = cta_y + 130
    draw.rectangle([0, bot_y, W, H], fill=DARK)
    draw.text((W // 2, bot_y + 60), "Google Sheets Template", font=load_font(40), fill=WHITE, anchor="mm")
    draw.text((W // 2, bot_y + 130), "Works free on any device", font=load_font_reg(34), fill=(200, 220, 255), anchor="mm")
    draw.text((W // 2, bot_y + 200), "No subscription ever", font=load_font_reg(32), fill=GRAY, anchor="mm")
    draw.text((W // 2, H - 80), "nasritools.etsy.com", font=load_font(38), fill=(255, 220, 80), anchor="mm")

    return img


# ── Pin 3: Results / CTA ──────────────────────────────────────────────────────

def make_pin_cta(p):
    color = p["color"]
    r, g, b = color
    accent = (255, 200, 50)

    img  = Image.new("RGB", (W, H), color)
    draw = ImageDraw.Draw(img)

    # Background decorative circle
    draw.ellipse([-200, -200, 900, 900], fill=(min(r+30,255), min(g+30,255), min(b+30,255)))

    # NasriTools brand
    draw.text((W // 2, 80), "NasriTools", font=load_font(44), fill=(255,255,200), anchor="mm")

    # Big emoji
    try:
        draw.text((W // 2, 200), p["emoji"], font=load_font(130), fill=WHITE, anchor="mm")
    except Exception:
        pass

    # Product name
    draw.text((W // 2, 340), p["name"].upper(), font=load_font(68), fill=WHITE, anchor="mm")

    # Divider
    draw.rectangle([W // 2 - 200, 410, W // 2 + 200, 416], fill=accent)

    # Result (large)
    draw.rounded_rectangle([40, 440, W - 40, 680], radius=28, fill=(0, 0, 0, 0))
    draw.rounded_rectangle([40, 440, W - 40, 680], radius=28,
                           fill=(min(r+20,255), min(g+20,255), min(b+20,255)))
    f_res = load_font(46)
    res_lines = wrap_text(draw, p["result"], f_res, W - 120)
    rly = 480
    for line in res_lines:
        draw.text((W // 2, rly), line, font=f_res, fill=WHITE, anchor="mm")
        rly += 58

    # Price badge
    py = 720
    draw.ellipse([W // 2 - 130, py, W // 2 + 130, py + 260], fill=accent)
    draw.text((W // 2, py + 60), "ONLY", font=load_font(36), fill=DARK, anchor="mm")
    draw.text((W // 2, py + 120), p["price"], font=load_font(80), fill=DARK, anchor="mm")
    draw.text((W // 2, py + 198), "one-time", font=load_font_reg(32), fill=DARK, anchor="mm")

    # Features brief
    fy = 1020
    for feat in p["features"][:3]:
        draw.text((W // 2, fy), "✔ " + feat, font=load_font_reg(36), fill=(255,255,200), anchor="mm")
        fy += 52

    # CTA button
    by = 1200
    draw.rounded_rectangle([80, by, W - 80, by + 100], radius=50, fill=WHITE)
    draw.text((W // 2, by + 50), "Buy on Etsy → Instant Download", font=load_font(38), fill=color, anchor="mm")

    # Footer
    draw.text((W // 2, 1360), "nasritools.etsy.com", font=load_font(40), fill=accent, anchor="mm")
    draw.text((W // 2, 1430), "Google Sheets  •  No Subscription  •  Lifetime Access",
              font=load_font_reg(28), fill=(200, 230, 200), anchor="mm")

    return img


def main():
    OUT.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  NasriTools - Pinterest Pin Generator")
    print(f"{'='*60}\n")
    print(f"  Output folder: {OUT}\n")

    total = 0
    for p in PRODUCTS:
        slug = p["slug"]

        print(f"  [{p['name']}]")

        pin1 = make_pin_pain(p)
        pin1.save(OUT / f"{slug}_pin1_pain.jpg", "JPEG", quality=92)
        print(f"    pin1 (pain/solution) ✓")

        pin2 = make_pin_features(p)
        pin2.save(OUT / f"{slug}_pin2_features.jpg", "JPEG", quality=92)
        print(f"    pin2 (features) ✓")

        pin3 = make_pin_cta(p)
        pin3.save(OUT / f"{slug}_pin3_cta.jpg", "JPEG", quality=92)
        print(f"    pin3 (results/CTA) ✓")

        total += 3

    print(f"\n{'='*60}")
    print(f"  Done: {total} pins saved to {OUT}")
    print(f"  Upload to Pinterest → schedule 1 per day via Tailwind or Buffer")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
