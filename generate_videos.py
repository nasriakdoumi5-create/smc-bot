"""
NasriTools - Generate & Upload Product Demo Videos
Creates a 12-second MP4 for each of the 10 main products:
  - Branded title reveal
  - 6 features sliding in
  - Animated spreadsheet simulation
  - CTA frame
Run: pip install opencv-python numpy && python generate_videos.py
"""
import json, os, time, math, requests
from pathlib import Path
from io import BytesIO

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python", "numpy", "Pillow"])
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"
OUT_DIR    = Path(os.path.expanduser("~")) / "nasri_videos"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_videos_done.json"
OUT_DIR.mkdir(exist_ok=True)

W, H   = 1920, 1080
FPS    = 30
TOTAL  = 12   # seconds → 360 frames

PRODUCTS = {
    "budget_tracker": {
        "label":    "Budget Tracker",
        "subtitle": "Track Income, Expenses & Savings",
        "color":    (31, 107, 59),
        "light":    (220, 247, 233),
        "features": [
            "Track all income & expenses",
            "Auto-calculate totals & balance",
            "Bill payment due date tracker",
            "Monthly & annual summary",
            "Spending by category charts",
            "Savings goal progress",
        ],
        "sheet_headers": ["Month", "Category", "Description", "Amount", "Type"],
        "sheet_rows": [
            ["January", "Salary",      "Monthly salary",    "€3,200", "Income"],
            ["January", "Rent",         "Monthly rent",     "€850",   "Expense"],
            ["January", "Groceries",    "Weekly shopping",  "€280",   "Expense"],
            ["January", "Freelance",    "Web project",      "€600",   "Income"],
            ["January", "Transport",    "Metro pass",       "€80",    "Expense"],
            ["January", "Savings",      "Emergency fund",   "€500",   "Expense"],
            ["", "",    "TOTAL INCOME",  "",                "€3,800", ""],
            ["", "",    "TOTAL EXPENSES","",                "€1,710", ""],
        ],
        "highlight_row": 7,
    },
    "habit_tracker": {
        "label":    "Habit Tracker",
        "subtitle": "Track 30 Daily Habits with Streak Counter",
        "color":    (46, 134, 171),
        "light":    (213, 234, 242),
        "features": [
            "Track up to 30 daily habits",
            "Automatic streak counter",
            "Monthly completion percentage",
            "Weekly review section",
            "Habit category organizer",
            "Progress comparison charts",
        ],
        "sheet_headers": ["Habit", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Streak"],
        "sheet_rows": [
            ["Wake up early",  "✓", "✓", "✓", "✓", "✓", "✓", "✓", "7"],
            ["Exercise",       "✓", "✓", "",  "✓", "✓", "",  "✓", "3"],
            ["Drink 2L water", "✓", "✓", "✓", "✓", "✓", "✓", "✓", "7"],
            ["Read 20 min",    "✓", "",  "✓", "✓", "",  "✓", "✓", "2"],
            ["Meditate",       "✓", "✓", "✓", "",  "✓", "✓", "✓", "3"],
            ["No junk food",   "✓", "✓", "✓", "✓", "",  "✓", "✓", "4"],
        ],
        "highlight_row": -1,
    },
    "meal_planner": {
        "label":    "Meal Planner",
        "subtitle": "7-Day Meal Planning + Auto Grocery List",
        "color":    (39, 174, 96),
        "light":    (212, 246, 227),
        "features": [
            "7-day meal planning grid",
            "Auto-generated grocery list",
            "Pantry inventory tracker",
            "Nutritional notes per meal",
            "Monthly meal calendar view",
            "Recipe link organizer",
        ],
        "sheet_headers": ["Day", "Breakfast", "Lunch", "Dinner", "Calories"],
        "sheet_rows": [
            ["Monday",    "Oats + berries",   "Grilled chicken",  "Salmon + veggies", "1,820"],
            ["Tuesday",   "Eggs + toast",     "Tuna salad",       "Pasta + sauce",    "1,950"],
            ["Wednesday", "Smoothie bowl",    "Veggie wrap",      "Steak + potatoes", "2,100"],
            ["Thursday",  "Greek yogurt",     "Lentil soup",      "Chicken curry",    "1,780"],
            ["Friday",    "Pancakes",         "Caesar salad",     "Pizza (homemade)", "2,200"],
            ["Saturday",  "Avocado toast",    "Sushi",            "BBQ ribs",         "2,350"],
            ["Sunday",    "Waffles",          "Roast chicken",    "Leftovers",        "1,900"],
        ],
        "highlight_row": -1,
    },
    "wedding_planner": {
        "label":    "Wedding Planner",
        "subtitle": "Budget, Guests, Vendors & Timeline",
        "color":    (142, 68, 173),
        "light":    (235, 222, 240),
        "features": [
            "Full event budget tracker",
            "Guest list & RSVP manager",
            "Vendor contact & payment log",
            "Day-of timeline planner",
            "Checklist & to-do tracker",
            "Seating chart helper",
        ],
        "sheet_headers": ["Category", "Vendor", "Budgeted", "Actual", "Deposit", "Status"],
        "sheet_rows": [
            ["Venue",       "Grand Palace Hotel",  "€8,000", "€7,500", "€2,000", "✓ Booked"],
            ["Catering",    "Taste of Italy",      "€5,000", "€4,800", "€1,500", "✓ Booked"],
            ["Photography", "Mia Studios",         "€2,500", "€2,500", "€500",   "✓ Booked"],
            ["Music",       "DJ Max",              "€1,200", "€1,000", "€300",   "Pending"],
            ["Flowers",     "Rose Garden Decor",   "€800",   "€750",   "€200",   "✓ Booked"],
            ["Cake",        "Sweet Dreams Bakery", "€500",   "€480",   "€100",   "✓ Booked"],
        ],
        "highlight_row": -1,
    },
    "workout_tracker": {
        "label":    "Workout Tracker",
        "subtitle": "Log Sets, Reps, Weight & Personal Records",
        "color":    (192, 57, 43),
        "light":    (250, 219, 216),
        "features": [
            "Log sets, reps & weight",
            "Personal record tracker",
            "Body measurements log",
            "Cardio & session notes",
            "Monthly fitness goals",
            "Strength progress charts",
        ],
        "sheet_headers": ["Exercise", "Muscle", "Sets", "Reps", "Weight", "PR?"],
        "sheet_rows": [
            ["Bench Press",   "Chest",     "4", "8",  "80 kg",  "✓ PR!"],
            ["Squat",         "Legs",      "4", "6",  "100 kg", ""],
            ["Deadlift",      "Back",      "3", "5",  "120 kg", "✓ PR!"],
            ["Pull-ups",      "Back",      "3", "10", "BW",     ""],
            ["OHP",           "Shoulders", "3", "8",  "55 kg",  ""],
            ["Bicep Curl",    "Arms",      "3", "12", "25 kg",  ""],
        ],
        "highlight_row": 0,
    },
    "content_creator_planner": {
        "label":    "Content Creator Planner",
        "subtitle": "Content Calendar, Analytics & Brand Deals",
        "color":    (230, 126, 34),
        "light":    (253, 235, 208),
        "features": [
            "Monthly content calendar",
            "Platform publishing schedule",
            "Analytics & growth tracker",
            "Brand deal & sponsor log",
            "Hashtag & caption planner",
            "Audience growth charts",
        ],
        "sheet_headers": ["Date", "Platform", "Content Idea", "Format", "Status", "Reach"],
        "sheet_rows": [
            ["Jun 1",  "Instagram", "Morning routine tips",    "Reel",    "Posted",     "12.4K"],
            ["Jun 3",  "YouTube",   "Full day of eating",      "Video",   "Posted",     "8.2K"],
            ["Jun 5",  "TikTok",    "5 productivity hacks",    "Short",   "Posted",     "45K"],
            ["Jun 7",  "Instagram", "Brand collab post",       "Carousel","Scheduled",  "—"],
            ["Jun 10", "YouTube",   "Room tour 2024",          "Video",   "Scripted",   "—"],
            ["Jun 12", "Twitter",   "Thread: content tips",    "Thread",  "Idea",       "—"],
        ],
        "highlight_row": -1,
    },
    "freelancer_invoice_tracker": {
        "label":    "Freelancer Invoice Tracker",
        "subtitle": "Manage Clients, Invoices & Payments",
        "color":    (41, 128, 185),
        "light":    (210, 234, 252),
        "features": [
            "Log all invoices & payments",
            "Paid / pending / overdue status",
            "Client contact database",
            "Monthly income summary",
            "Tax preparation helper",
            "Project status board",
        ],
        "sheet_headers": ["Invoice #", "Client", "Project", "Amount", "Due Date", "Status"],
        "sheet_rows": [
            ["INV-001", "TechStart Inc",    "Website redesign", "€2,400", "Jun 15", "✓ Paid"],
            ["INV-002", "Brand Co",         "Logo design",      "€800",   "Jun 20", "✓ Paid"],
            ["INV-003", "Media Group",      "SEO package",      "€1,200", "Jun 25", "Pending"],
            ["INV-004", "StartUp XYZ",      "App UI design",    "€3,500", "Jul 1",  "Pending"],
            ["INV-005", "Local Business",   "Social media",     "€600",   "Jun 10", "⚠ Overdue"],
            ["INV-006", "E-shop Ltd",       "Product photos",   "€950",   "Jul 5",  "Draft"],
        ],
        "highlight_row": 4,
    },
    "student_planner": {
        "label":    "Student Planner",
        "subtitle": "Assignments, Grades, GPA & Exam Prep",
        "color":    (26, 82, 118),
        "light":    (210, 234, 252),
        "features": [
            "Weekly class schedule",
            "Assignment due date tracker",
            "Grade calculator per subject",
            "GPA tracker & progress",
            "Exam preparation checklist",
            "Semester overview calendar",
        ],
        "sheet_headers": ["Subject", "Assignment", "Due Date", "Priority", "Status", "Grade"],
        "sheet_rows": [
            ["Mathematics",  "Chapter 5 exercises",  "Jun 10", "High",   "✓ Done",   "92%"],
            ["Physics",      "Lab report",            "Jun 12", "High",   "In Progress","—"],
            ["History",      "Essay: WW2",            "Jun 15", "Medium", "Not Started","—"],
            ["English",      "Book review",           "Jun 18", "Medium", "✓ Done",   "88%"],
            ["Chemistry",    "Problem set",           "Jun 20", "High",   "Not Started","—"],
            ["Economics",    "Case study",            "Jun 22", "Low",    "Not Started","—"],
        ],
        "highlight_row": -1,
    },
    "goals_planner": {
        "label":    "Goals Planner",
        "subtitle": "Annual Goals, 90-Day Plans & Milestones",
        "color":    (17, 122, 101),
        "light":    (212, 246, 239),
        "features": [
            "Annual goal setting (12 goals)",
            "90-day action plan breakdown",
            "Weekly milestone tracker",
            "Habit alignment section",
            "Monthly review prompts",
            "Vision board notes",
        ],
        "sheet_headers": ["#", "Goal", "Category", "Target Date", "Progress", "Status"],
        "sheet_rows": [
            ["1", "Run a half marathon",     "Health",   "Oct 2024",  "65%", "On Track"],
            ["2", "Save €10,000",            "Finance",  "Dec 2024",  "40%", "On Track"],
            ["3", "Read 24 books",           "Learning", "Dec 2024",  "50%", "On Track"],
            ["4", "Launch online course",    "Career",   "Sep 2024",  "20%", "Behind"],
            ["5", "Travel to 3 countries",   "Travel",   "Dec 2024",  "33%", "On Track"],
            ["6", "Learn Spanish (B2)",      "Personal", "Dec 2024",  "15%", "Behind"],
        ],
        "highlight_row": -1,
    },
    "weekly_planner": {
        "label":    "Weekly Planner",
        "subtitle": "Time Blocking, Priority Tasks & Weekly Schedule",
        "color":    (108, 52, 131),
        "light":    (237, 228, 252),
        "features": [
            "Week-at-a-glance daily schedule",
            "Top 3 priority task list",
            "Time blocking grid",
            "Notes & ideas section",
            "Weekly goals & intentions",
            "Habit check-in tracker",
        ],
        "sheet_headers": ["Time", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "sheet_rows": [
            ["8:00",  "Team standup",   "Deep work",     "Client call",   "Deep work",   "Weekly review"],
            ["9:00",  "Deep work",      "Deep work",     "Deep work",     "Meeting",     "Deep work"],
            ["10:00", "Email inbox",    "Content write", "Email inbox",   "Deep work",   "Planning"],
            ["11:00", "Project work",   "Project work",  "Project work",  "Project work","Wrap up"],
            ["13:00", "Lunch + walk",   "Lunch + walk",  "Lunch + walk",  "Lunch + walk","Lunch"],
            ["14:00", "Admin tasks",    "Learning",      "Admin tasks",   "Learning",    "Free time"],
        ],
        "highlight_row": -1,
    },
}


# ── Font loader ────────────────────────────────────────────────────────────────

def load_font(size, bold=True):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for f in candidates:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ── Easing ────────────────────────────────────────────────────────────────────

def ease_out(t):
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


# ── PIL → numpy ───────────────────────────────────────────────────────────────

def pil_to_bgr(img):
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


# ── Frame builders ─────────────────────────────────────────────────────────────

def hex_to_rgb(color):
    r, g, b = color
    return r, g, b


def make_base(color, light):
    img = Image.new("RGB", (W, H), light)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, H // 3], fill=color)
    return img, draw


def draw_title_frame(t, product):
    """0 → 1: fade+scale in the title."""
    color  = product["color"]
    light  = product["light"]
    label  = product["label"]
    sub    = product["subtitle"]
    r, g, b = color

    prog = ease_out(min(t * 2, 1.0))

    img  = Image.new("RGB", (W, H), (245, 245, 248))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(H):
        frac = y / H
        cr = int(r + (245 - r) * frac)
        cg = int(g + (245 - g) * frac)
        cb = int(b + (245 - b) * frac)
        draw.line([(0, y), (W, y)], fill=(min(cr,255), min(cg,255), min(cb,255)))

    # Decorative circles
    for cx, cy, rad in [(1700, 100, 320), (200, 900, 240), (1850, 700, 180)]:
        ov = Image.new("RGBA", (W, H), (0,0,0,0))
        od = ImageDraw.Draw(ov)
        od.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=(255,255,255,25))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Logo pill
    pill_w, pill_h = 320, 60
    pill_x = W // 2 - pill_w // 2
    pill_y = int(lerp(H // 2 - 200, 160, prog))
    if prog > 0.1:
        draw.rounded_rectangle([pill_x, pill_y, pill_x+pill_w, pill_y+pill_h],
                                radius=30, fill=(255,255,255))
        draw.text((W//2, pill_y+30), "NasriTools", font=load_font(30),
                  fill=color, anchor="mm")

    # Main title
    alpha_title = int(255 * prog)
    title_y = int(lerp(H // 2 + 50, H // 2 - 60, prog))
    f_title = load_font(100)
    draw.text((W//2, title_y), label, font=f_title, fill=(255,255,255), anchor="mm")

    # Subtitle
    if prog > 0.5:
        sub_prog = (prog - 0.5) * 2
        sub_y = int(lerp(H // 2 + 60, H // 2 + 50, sub_prog))
        draw.text((W//2, sub_y), sub, font=load_font(44, bold=False),
                  fill=(255,255,220), anchor="mm")

    # Divider
    if prog > 0.7:
        div_prog = (prog - 0.7) / 0.3
        div_w    = int(300 * div_prog)
        draw.rectangle([W//2 - div_w, H//2 + 10, W//2 + div_w, H//2 + 14],
                        fill=(255,255,255))

    return img


def draw_features_frame(t, product):
    """t = 0→1 over 4s, features slide in one by one."""
    color = product["color"]
    light = product["light"]
    feats = product["features"]
    r, g, b = color

    img  = Image.new("RGB", (W, H), (250, 250, 252))
    draw = ImageDraw.Draw(img)

    # Sidebar
    draw.rectangle([0, 0, 420, H], fill=color)

    # Decorative
    for cx, cy, rad in [(200, 900, 280), (300, 150, 180)]:
        ov = Image.new("RGBA", (W, H), (0,0,0,0))
        od = ImageDraw.Draw(ov)
        od.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=(255,255,255,18))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Sidebar text
    draw.text((210, 100), "✔", font=load_font(80), fill=(255,255,255), anchor="mm")
    draw.text((210, 200), "WHAT'S", font=load_font(46), fill=(255,255,255), anchor="mm")
    draw.text((210, 260), "INCLUDED", font=load_font(46), fill=(255,255,255), anchor="mm")
    draw.rectangle([110, 295, 310, 300], fill=(255,255,255))
    draw.text((210, H//2), product["label"], font=load_font(38),
              fill=(255,255,200), anchor="mm")

    # Features
    feat_start_y = 140
    feat_gap     = 118
    n            = len(feats)

    for i, feat in enumerate(feats):
        thresh = i / n
        if t < thresh:
            break
        prog = min((t - thresh) / (1.0 / n), 1.0)
        prog = ease_out(prog)

        fy = feat_start_y + i * feat_gap
        fx = int(lerp(W + 100, 480, prog))

        # Only draw when card is on-screen
        if fx >= W - 60:
            continue

        # Card
        draw.rounded_rectangle([fx, fy, W - 60, fy + 96], radius=16,
                                fill=(255,255,255))
        # Check circle
        circ_x1 = min(fx + 62, W - 62)
        draw.ellipse([fx + 18, fy + 18, circ_x1, fy + 76], fill=color)
        if circ_x1 > fx + 18:
            draw.text((fx + 40, fy + 50), "✓", font=load_font(32),
                      fill=(255,255,255), anchor="mm")
        if fx + 88 < W - 60:
            draw.text((fx + 88, fy + 50), feat, font=load_font(42),
                      fill=(40, 40, 40), anchor="lm")

    return img


def draw_sheet_frame(t, product):
    """t = 0→1 over 4s: spreadsheet rows appear one by one."""
    color   = product["color"]
    light   = product["light"]
    headers = product["sheet_headers"]
    rows    = product["sheet_rows"]
    hi_row  = product.get("highlight_row", -1)
    r, g, b = color

    img  = Image.new("RGB", (W, H), (248, 249, 250))
    draw = ImageDraw.Draw(img)

    # Top strip
    draw.rectangle([0, 0, W, 100], fill=color)
    draw.text((W//2, 50), f"{product['label']} — Live Preview",
              font=load_font(40), fill=(255,255,255), anchor="mm")

    # Sheet area
    sx, sy = 80, 120
    col_w  = (W - 160) // len(headers)
    row_h  = 72
    hdr_h  = 56

    # Header row
    for j, hdr in enumerate(headers):
        cx = sx + j * col_w
        draw.rectangle([cx, sy, cx + col_w, sy + hdr_h], fill=color)
        draw.text((cx + col_w//2, sy + hdr_h//2), hdr,
                  font=load_font(32), fill=(255,255,255), anchor="mm")

    # Data rows
    n_rows = len(rows)
    for i, row in enumerate(rows):
        thresh = i / n_rows
        if t < thresh:
            break
        row_prog = min((t - thresh) / (1.0 / n_rows), 1.0)
        row_prog = ease_out(row_prog)

        ry = sy + hdr_h + i * row_h
        row_alpha = int(255 * row_prog)

        bg = light if i % 2 == 0 else (255, 255, 255)
        if i == hi_row:
            bg = tuple(min(255, int(c * 0.85)) for c in light)

        # Row background slides from right
        row_x = int(lerp(W, sx, row_prog))
        draw.rectangle([sx, ry, W - 80, ry + row_h - 2], fill=bg)

        for j, cell_val in enumerate(row):
            if j >= len(headers):
                break
            cx = sx + j * col_w
            is_money = cell_val.startswith("€") if cell_val else False
            is_check = cell_val in ("✓", "✓ PR!", "✓ Paid", "✓ Booked", "✓ Done")
            is_warn  = "⚠" in cell_val if cell_val else False
            is_bold  = i == hi_row or cell_val in ("✓ PR!", "✓ Paid", "✓ Booked")

            txt_color = (34, 139, 59) if is_check else \
                        (192, 57, 43) if is_warn  else \
                        (r, g, b)     if is_money else \
                        (40, 40, 40)

            if row_prog > 0.3:
                draw.text((cx + 14, ry + row_h//2), cell_val or "",
                          font=load_font(30, bold=is_bold),
                          fill=txt_color, anchor="lm")

    # Grid lines
    for j in range(len(headers) + 1):
        cx = sx + j * col_w
        draw.line([(cx, sy), (cx, sy + hdr_h + n_rows * row_h)],
                  fill=(200, 200, 200), width=1)
    for i in range(n_rows + 2):
        ry = sy + hdr_h + i * row_h - 2
        draw.line([(sx, ry), (W - 80, ry)], fill=(220, 220, 220), width=1)

    # Bottom label
    draw.text((W//2, H - 40), "nasritools.etsy.com",
              font=load_font(32, bold=False), fill=(160, 160, 160), anchor="mm")
    return img


def draw_cta_frame(t, product):
    """Final CTA: brand, price suggestion, call to action."""
    color = product["color"]
    light = product["light"]
    r, g, b = color

    prog = ease_out(min(t * 2, 1.0))

    img  = Image.new("RGB", (W, H), (245, 245, 248))
    draw = ImageDraw.Draw(img)

    # Gradient
    for y in range(H):
        frac = y / H
        cr = int(r + (245 - r) * frac)
        cg = int(g + (245 - g) * frac)
        cb = int(b + (245 - b) * frac)
        draw.line([(0, y), (W, y)],
                  fill=(min(cr,255), min(cg,255), min(cb,255)))

    # Central card
    cw, ch = 900, 520
    cx0 = (W - cw) // 2
    cy0 = (H - ch) // 2
    scale = lerp(0.85, 1.0, prog)
    cw_s  = int(cw * scale)
    ch_s  = int(ch * scale)
    cx0_s = (W - cw_s) // 2
    cy0_s = (H - ch_s) // 2
    draw.rounded_rectangle([cx0_s, cy0_s, cx0_s+cw_s, cy0_s+ch_s],
                            radius=28, fill=(255,255,255))

    if prog > 0.3:
        p2 = (prog - 0.3) / 0.7
        mid_x = W // 2
        draw.text((mid_x, cy0_s + 90),  "✔ Instant Digital Download",
                  font=load_font(48), fill=color, anchor="mm")
        draw.text((mid_x, cy0_s + 160), product["label"],
                  font=load_font(72), fill=(30,30,30), anchor="mm")
        draw.rectangle([mid_x-180, cy0_s+200, mid_x+180, cy0_s+205], fill=color)
        draw.text((mid_x, cy0_s + 260), "Works on Google Sheets & Excel",
                  font=load_font(38, bold=False), fill=(80,80,80), anchor="mm")
        draw.text((mid_x, cy0_s + 330), "Fully Customizable  •  Lifetime Access",
                  font=load_font(36, bold=False), fill=(100,100,100), anchor="mm")

        # CTA button
        btn_y = cy0_s + 400
        draw.rounded_rectangle([mid_x-200, btn_y, mid_x+200, btn_y+80],
                                radius=40, fill=color)
        draw.text((mid_x, btn_y+40), "Shop Now →",
                  font=load_font(42), fill=(255,255,255), anchor="mm")

    draw.text((W//2, H - 50), "nasritools.etsy.com",
              font=load_font(36, bold=False), fill=(200,200,200), anchor="mm")

    return img


# ── Video generator ────────────────────────────────────────────────────────────

def generate_video(slug, product):
    out_path = OUT_DIR / f"{slug}.mp4"
    if out_path.exists():
        print(f"    Already exists — skipping")
        return out_path

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw     = cv2.VideoWriter(str(out_path), fourcc, FPS, (W, H))

    total_frames = FPS * TOTAL  # 360

    # Sections (frames):
    # 0-59:   Title (2s)
    # 60-179: Features (4s)
    # 180-299: Spreadsheet (4s)
    # 300-359: CTA (2s)

    for f in range(total_frames):
        if f < 60:
            t   = f / 60.0
            img = draw_title_frame(t, product)
        elif f < 180:
            t   = (f - 60) / 120.0
            img = draw_features_frame(t, product)
        elif f < 300:
            t   = (f - 180) / 120.0
            img = draw_sheet_frame(t, product)
        else:
            t   = (f - 300) / 60.0
            img = draw_cta_frame(t, product)

        vw.write(pil_to_bgr(img))

    vw.release()
    print(f"    Video saved: {out_path.name} ({out_path.stat().st_size//1024}KB)")
    return out_path


# ── Etsy upload ───────────────────────────────────────────────────────────────

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
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}


def upload_video(token, listing_id, video_path):
    with open(video_path, "rb") as f:
        r = requests.post(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/videos",
            headers=auth_headers(token),
            files={"video": (video_path.name, f, "video/mp4")},
            data={"name": video_path.name},
            timeout=120,
        )
    return r


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    done      = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    token     = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Generate & Upload Product Videos")
    print(f"  Already done: {len(done)}")
    print(f"{'='*65}\n")

    ok = 0
    for slug, product in PRODUCTS.items():
        lid = published.get(slug)
        if not lid:
            print(f"  [{slug}] SKIP — no listing ID")
            continue

        if slug in done:
            print(f"  [{slug}] SKIP — already uploaded")
            ok += 1
            continue

        print(f"  [{slug}]  (listing {lid})")

        # Generate
        print(f"    Generating {TOTAL}s video...", end=" ", flush=True)
        video_path = generate_video(slug, product)
        print("done")

        # Upload
        print(f"    Uploading to Etsy...", end=" ", flush=True)
        r = upload_video(token, lid, video_path)
        time.sleep(2)

        if r.ok:
            ok += 1
            done[slug] = {"listing": lid, "file": str(video_path)}
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print("✓")
        else:
            print(f"✗  {r.status_code}: {r.text[:120]}")

        token = get_token()
        print()

    print(f"{'='*65}")
    print(f"  Done: {ok}/{len(PRODUCTS)} videos uploaded")
    print(f"  Files saved to: {OUT_DIR}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
