"""
NasriTools - Professional 7-Image Design System
Generates all 7 image types for each of the 10 core products:
  1. Thumbnail (rank 1)   - Bold, minimal, click-worthy
  2. Value Hook (rank 2)  - Problem → Solution
  3. Before/After (rank 3)
  4. Contents (rank 4)    - What's inside
  5. How It Works (rank 5)- 3 steps
  6. Results (rank 6)     - Benefits/outcomes
  7. Trust (rank 7)       - Guarantees + social proof

Run: python generate_pro_images.py
"""
import json, os, time, requests, io, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_pro_images_done.json"
SIZE       = 2000

WHITE  = (255, 255, 255)
DARK   = (18, 22, 35)
GRAY   = (110, 115, 130)
LGRAY  = (240, 242, 248)
GOLD   = (255, 195, 0)

PRODUCTS = [
    {
        "listing":  4487745643,
        "name":     "Budget Tracker",
        "color":    (22, 100, 52),
        "light":    (214, 245, 228),
        "emoji":    "💰",
        "tagline":  "Take control of your money",
        "problem":  ["Don't know where money goes?", "Overspending every month?", "Living paycheck to paycheck?", "No savings plan at all?"],
        "solution": ["Track every euro automatically", "Clear monthly budget overview", "Savings goal progress tracker", "Full financial clarity in minutes"],
        "contents": [
            ("📊", "Monthly Budget Dashboard", "Full income/expense overview"),
            ("📅", "12-Month Budget Sheets",   "One sheet per month, full year"),
            ("💸", "50+ Expense Categories",   "Pre-built, fully editable"),
            ("📈", "Savings Goal Tracker",     "Track progress to your target"),
            ("🧾", "Bill Payment Tracker",     "Never miss a payment again"),
            ("💹", "Net Worth Calculator",     "See your total financial picture"),
        ],
        "results":  [
            ("💰", "Save €200–€500/month", "Know exactly what to cut"),
            ("📊", "Full Financial Clarity", "See it all in one dashboard"),
            ("⏱️", "Save 3 hours/week",     "No manual calculations ever"),
            ("🎯", "Hit financial goals",   "Systematic saving strategy"),
        ],
        "price":    "€6.99",
    },
    {
        "listing":  4487740567,
        "name":     "Habit Tracker",
        "color":    (168, 45, 30),
        "light":    (252, 220, 215),
        "emoji":    "✅",
        "tagline":  "Build habits that actually stick",
        "problem":  ["Starting habits and giving up?", "No system to stay consistent?", "Can't remember what you're tracking?", "Breaking streaks with no recovery?"],
        "solution": ["Track 30 habits simultaneously", "Auto streak counter keeps score", "Monthly visual progress grid", "Never lose your progress again"],
        "contents": [
            ("📅", "Monthly Habit Grid",       "30 habits × 31 days at a glance"),
            ("🔥", "Auto Streak Counter",      "Calculates streaks automatically"),
            ("📊", "Weekly Completion Rate",   "% completed each week"),
            ("🎯", "Monthly Progress Score",   "Overall performance at a glance"),
            ("📝", "Habit Notes Section",      "Track why you skipped days"),
            ("📈", "Annual Habit Overview",    "See all 12 months together"),
        ],
        "results":  [
            ("✅", "30 habits tracked",    "All in one simple sheet"),
            ("🔥", "Longest streaks ever", "Visual motivation to continue"),
            ("📊", "80%+ completion rate", "Beat your previous personal best"),
            ("💪", "New lifestyle built",  "Habits become automatic in 66 days"),
        ],
        "price":    "€5.99",
    },
    {
        "listing":  4487742011,
        "name":     "Meal Planner",
        "color":    (32, 158, 124),
        "light":    (205, 248, 236),
        "emoji":    "🥗",
        "tagline":  "Plan healthy meals in minutes",
        "problem":  ["No idea what to cook tonight?", "Overspending on groceries?", "Eating unhealthy from no plan?", "Wasting food every week?"],
        "solution": ["7-day meals planned in 15 min", "Auto-generated grocery list", "Track nutrition automatically", "Zero food waste with planning"],
        "contents": [
            ("📅", "7-Day Meal Planner",      "Breakfast, lunch, dinner, snacks"),
            ("🛒", "Auto Grocery List",        "Generates from your meal plan"),
            ("🥦", "Nutrition Tracker",        "Calories, protein, carbs, fat"),
            ("📚", "Recipe Database",          "Store your favourite recipes"),
            ("💰", "Grocery Budget Tracker",   "Keep food spending in check"),
            ("📆", "Monthly Meal Calendar",    "Plan the full month ahead"),
        ],
        "results":  [
            ("🥗", "Eat healthier daily",    "No more last-minute junk food"),
            ("💰", "Save €100+/month",       "No more unplanned grocery runs"),
            ("⏱️", "Plan in 15 minutes",     "Every Sunday sorted quickly"),
            ("🚫", "Zero food waste",         "Buy only what you'll use"),
        ],
        "price":    "€5.99",
    },
    {
        "listing":  4487743321,
        "name":     "Wedding Planner",
        "color":    (185, 65, 145),
        "light":    (250, 220, 240),
        "emoji":    "💍",
        "tagline":  "Plan your perfect wedding",
        "problem":  ["Overwhelmed by wedding details?", "Budget spiraling out of control?", "Vendor chaos and missed tasks?", "Forgetting important guests?"],
        "solution": ["Everything in ONE spreadsheet", "Live budget vs. actual tracking", "All vendors organized by deadline", "Full guest list with RSVPs"],
        "contents": [
            ("💰", "Wedding Budget Tracker",   "Budget vs. actual every line item"),
            ("👥", "Guest List Manager",       "RSVPs, meals & seating"),
            ("🏢", "Vendor Tracker",           "Contacts, deposits & deadlines"),
            ("✅", "Wedding Checklist",        "Month-by-month tasks & timeline"),
            ("⏰", "Wedding Day Timeline",     "Hour-by-hour perfect day schedule"),
            ("📊", "Budget Summary Dashboard", "Total spend at a glance"),
        ],
        "results":  [
            ("💍", "Stress-free planning",   "Everything organized in one place"),
            ("💰", "Stay on budget",         "No surprise overspend"),
            ("✅", "Nothing forgotten",       "Every detail tracked"),
            ("❤️", "Enjoy the journey",      "Focus on love, not logistics"),
        ],
        "price":    "€7.99",
    },
    {
        "listing":  4487744011,
        "name":     "Workout Tracker",
        "color":    (168, 45, 30),
        "light":    (252, 220, 215),
        "emoji":    "💪",
        "tagline":  "Track every rep, hit every PR",
        "problem":  ["Forgetting what weights you lifted?", "No idea if you're getting stronger?", "No structure to your training?", "Same workout for months with no progress?"],
        "solution": ["Log every set, rep & weight", "Auto-tracks personal records", "Visual strength progress charts", "Structured training programs"],
        "contents": [
            ("📝", "Workout Log Sheet",        "Sets, reps, weight, notes"),
            ("🏆", "Personal Record Tracker",  "Auto-highlights new PRs"),
            ("📅", "Weekly Training Schedule", "Plan all sessions in advance"),
            ("📈", "Progress Charts",          "Visual strength gains over time"),
            ("💪", "100+ Exercise Database",   "Pre-filled exercise library"),
            ("📏", "Body Measurements",        "Track body composition changes"),
        ],
        "results":  [
            ("💪", "Get visibly stronger",   "See progress every 4 weeks"),
            ("🏆", "Break personal records", "Beat your best every month"),
            ("📊", "Training is structured", "No more guessing at the gym"),
            ("⏱️", "Efficient workouts",     "No wasted time or sets"),
        ],
        "price":    "€5.99",
    },
    {
        "listing":  4487745211,
        "name":     "Content Creator Planner",
        "color":    (200, 108, 25),
        "light":    (253, 238, 210),
        "emoji":    "📱",
        "tagline":  "Plan 3 months of content in one weekend",
        "problem":  ["Running out of content ideas?", "Missing posting deadlines?", "No idea if your content performs?", "Brand deals falling through cracks?"],
        "solution": ["Content planned 3 months ahead", "Never miss a posting deadline", "Analytics all tracked in one place", "Every brand deal fully managed"],
        "contents": [
            ("📅", "Monthly Content Calendar",  "All platforms in one view"),
            ("💡", "Content Ideas Bank",         "100+ idea prompts included"),
            ("📊", "Analytics Tracker",          "Followers, reach & engagement"),
            ("🤝", "Brand Deal Tracker",         "Deadlines, payments & deliverables"),
            ("💰", "Creator Revenue Tracker",    "Sponsorships, affiliate, products"),
            ("🎯", "Content Performance Sheet",  "Which posts work best"),
        ],
        "results":  [
            ("📱", "Consistent posting",     "Never miss another deadline"),
            ("📈", "Growing audience",       "Strategy beats luck every time"),
            ("💰", "More brand revenue",     "Never lose a deal again"),
            ("⏱️", "Save 5 hours/week",     "Less planning stress"),
        ],
        "price":    "€6.99",
    },
    {
        "listing":  4487744321,
        "name":     "Freelancer Invoice Tracker",
        "color":    (40, 130, 195),
        "light":    (210, 235, 252),
        "emoji":    "📄",
        "tagline":  "Get paid on time, every time",
        "problem":  ["Forgetting to invoice clients?", "Clients paying late constantly?", "Dreading tax season chaos?", "No idea what you earned this month?"],
        "solution": ["All invoices tracked in one place", "Payment status at a glance", "Tax prep takes 10 minutes", "Monthly revenue summary automatic"],
        "contents": [
            ("📋", "Invoice Tracker",           "All invoices, status & due dates"),
            ("👥", "Client Database",           "Contact info & project history"),
            ("🚦", "Payment Status Dashboard",  "Paid / Pending / Overdue view"),
            ("💰", "Monthly Revenue Summary",   "Income at a glance"),
            ("🧾", "Tax Prep Sheet",            "Income + deductible expenses"),
            ("⏱️", "Project Time Tracker",     "Billable hours log"),
        ],
        "results":  [
            ("💰", "Get paid faster",       "Overdue alerts prevent late payment"),
            ("🧾", "Easy tax season",       "Everything documented already"),
            ("📊", "Know your revenue",     "Real income, tracked monthly"),
            ("⏱️", "Save 3 hours/month",   "No more manual invoice chasing"),
        ],
        "price":    "€6.99",
    },
    {
        "listing":  4487742911,
        "name":     "Student Planner",
        "color":    (90, 38, 115),
        "light":    (232, 220, 252),
        "emoji":    "🎓",
        "tagline":  "Ace your semester, hit your GPA",
        "problem":  ["Missing assignment deadlines?", "Shocked by your grades each semester?", "Studying randomly with no plan?", "Forgetting exam dates?"],
        "solution": ["Every deadline tracked automatically", "GPA calculated in real time", "Structured weekly study schedule", "Exam countdown calendar"],
        "contents": [
            ("📝", "Assignment Tracker",       "All subjects, deadlines & status"),
            ("🎓", "Grade Tracker + GPA Calc", "Auto-calculated cumulative GPA"),
            ("📅", "Weekly Study Schedule",    "Time-blocked study sessions"),
            ("⏰", "Exam Countdown Calendar",  "Days remaining to each exam"),
            ("📊", "Semester Dashboard",       "All subjects at a glance"),
            ("📚", "Study Hours Log",          "Track time spent per subject"),
        ],
        "results":  [
            ("🎓", "GPA improves",           "No more grade surprises"),
            ("✅", "Zero missed deadlines",  "Tracked in advance"),
            ("📚", "Better study habits",    "Structured schedule = better results"),
            ("😌", "Less academic stress",   "Organized = confident"),
        ],
        "price":    "€5.99",
    },
    {
        "listing":  4487743721,
        "name":     "Goals Planner",
        "color":    (22, 82, 158),
        "light":    (215, 232, 252),
        "emoji":    "🎯",
        "tagline":  "Set goals that actually get achieved",
        "problem":  ["Setting goals that never happen?", "No system to track progress?", "Losing motivation after week 2?", "Goals too vague to actually pursue?"],
        "solution": ["Annual goals → 90-day sprints", "Weekly actions tracked daily", "Progress % calculated automatically", "Monthly reviews keep you on track"],
        "contents": [
            ("🎯", "Annual Goals Dashboard",   "All life areas: health, money, career"),
            ("📅", "90-Day Sprint Planner",    "Break big goals into quarterly plans"),
            ("✅", "Weekly Action Tracker",    "Daily tasks that move goals forward"),
            ("📊", "Progress Calculator",      "% complete updates automatically"),
            ("🔄", "Monthly Review Sheet",     "Reflect, adjust, accelerate"),
            ("🔗", "Habit-to-Goal Connector",  "Link daily habits to big goals"),
        ],
        "results":  [
            ("🎯", "Goals become reality",    "System beats motivation every time"),
            ("📈", "50%+ faster progress",   "Quarterly focus removes distractions"),
            ("💪", "Built-in accountability", "Weekly check-ins prevent drifting"),
            ("🌟", "Life you planned",        "Every area improving together"),
        ],
        "price":    "€5.99",
    },
    {
        "listing":  4487742511,
        "name":     "Weekly Planner",
        "color":    (90, 38, 115),
        "light":    (232, 220, 252),
        "emoji":    "📅",
        "tagline":  "Plan your best week, every week",
        "problem":  ["Ending weeks without progress?", "Always busy but never productive?", "No priorities — reacting to everything?", "Work bleeding into personal time?"],
        "solution": ["Time-blocked week planned Sunday", "Top 3 priorities set every day", "Work-life balance built in", "Focus on what actually matters"],
        "contents": [
            ("⏰", "Time-Block Schedule",      "30-min slots from 6am to 10pm"),
            ("🎯", "Daily Top 3 Priorities",   "The 3 tasks that actually matter"),
            ("✅", "Daily To-Do Lists",        "Complete task management"),
            ("📊", "Weekly Goals & Review",    "Plan Sunday, review Friday"),
            ("📅", "Meeting/Appointment Tracker","Never double-book"),
            ("⚡", "Energy Level Planner",    "Match task difficulty to energy"),
        ],
        "results":  [
            ("⚡", "3x more productive",     "Focus replaces busyness"),
            ("😌", "Less overwhelm",          "Everything has a designated time"),
            ("🎯", "Top priorities done",     "Important beats urgent"),
            ("⚖️", "Work-life balance",      "Personal time is protected"),
        ],
        "price":    "€5.99",
    },
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
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}


def load_font(size):
    for f in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def load_font_reg(size):
    for f in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_centered(draw, text, font, cx, y, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((cx - w // 2, y), text, font=font, fill=fill)


def draw_card(draw, x0, y0, x1, y1, r, fill, shadow=True):
    if shadow:
        draw.rounded_rectangle([x0+5, y0+5, x1+5, y1+5], radius=r, fill=(180, 185, 195))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill)


def add_header(draw, color, title, subtitle=None):
    draw.rectangle([0, 0, SIZE, 540], fill=color)
    # Decorative circle top-right
    r, g, b = color
    c2 = (min(r+30, 255), min(g+30, 255), min(b+30, 255))
    draw.ellipse([SIZE-320, -160, SIZE+160, 320], fill=c2)
    # Brand
    draw.text((60, 50), "NasriTools", font=load_font(44), fill=(255, 255, 200))
    # Title
    draw_centered(draw, title, load_font(100), SIZE//2, 150, WHITE)
    if subtitle:
        draw_centered(draw, subtitle, load_font_reg(48), SIZE//2, 310, (230, 240, 255))

def add_footer(draw, color, text="Instant Download  •  Google Sheets  •  nasritools.etsy.com"):
    draw.rectangle([0, SIZE-110, SIZE, SIZE], fill=color)
    draw_centered(draw, text, load_font_reg(36), SIZE//2, SIZE-72, WHITE)


# ── IMAGE 1: Thumbnail ────────────────────────────────────────────────────────

def make_thumbnail(p):
    color = p["color"]
    light = p["light"]
    r, g, b = color

    img  = Image.new("RGB", (SIZE, SIZE), color)
    draw = ImageDraw.Draw(img)

    # Top-right large circle decoration
    c2 = (min(r+35, 255), min(g+35, 255), min(b+35, 255))
    draw.ellipse([SIZE-580, -280, SIZE+280, 580], fill=c2)

    # Bottom-left small circle
    draw.ellipse([-180, SIZE-380, 280, SIZE+180], fill=c2)

    # Brand name top-left
    draw.text((70, 60), "NasriTools", font=load_font(52), fill=(255, 255, 200))

    # "INSTANT DOWNLOAD" badge top-right
    draw.rounded_rectangle([SIZE-360, 55, SIZE-55, 120], radius=30, fill=GOLD)
    draw.text((SIZE-208, 88), "INSTANT DOWNLOAD", font=load_font(28),
              fill=(50, 30, 0), anchor="mm")

    # Product emoji
    try:
        draw.text((SIZE//2, 420), p["emoji"], font=load_font(200), fill=WHITE, anchor="mm")
    except Exception:
        draw.text((SIZE//2, 420), p["emoji"], font=load_font(200), anchor="mm", fill=WHITE)

    # Product name — very large
    name = p["name"].upper()
    draw_centered(draw, name, load_font(120), SIZE//2, 700, WHITE)

    # Tagline
    draw_centered(draw, p["tagline"], load_font_reg(52), SIZE//2, 860, (220, 235, 255))

    # White divider
    draw.rectangle([SIZE//2-280, 950, SIZE//2+280, 958], fill=WHITE)

    # Feature pills row
    pills = ["Google Sheets", "Excel", "Editable"]
    pw, ph = 340, 68
    total_w = len(pills) * pw + (len(pills)-1) * 24
    px = (SIZE - total_w) // 2
    for pill in pills:
        draw.rounded_rectangle([px, 990, px+pw, 990+ph], radius=34,
                                fill=(255, 255, 255, 0))
        draw.rounded_rectangle([px, 990, px+pw, 990+ph], radius=34,
                                outline=WHITE, width=2)
        draw_centered(draw, pill, load_font_reg(32), px+pw//2, 1000, WHITE)
        px += pw + 24

    # Price box
    draw.rounded_rectangle([SIZE//2-160, 1110, SIZE//2+160, 1210], radius=30, fill=GOLD)
    draw_centered(draw, p["price"], load_font(70), SIZE//2, 1125, (50, 30, 0))

    # Bottom bar
    draw.rectangle([0, SIZE-110, SIZE, SIZE], fill=(r//3, g//3, b//3))
    draw_centered(draw, "100% Customizable  •  Lifetime Access  •  No Subscription",
                  load_font_reg(34), SIZE//2, SIZE-72, WHITE)

    return img


# ── IMAGE 2: Value Hook ───────────────────────────────────────────────────────

def make_value_hook(p):
    color = p["color"]
    img  = Image.new("RGB", (SIZE, SIZE), DARK)
    draw = ImageDraw.Draw(img)

    # Top section: dark problem area
    draw.rectangle([0, 0, SIZE, SIZE//2 - 30], fill=DARK)

    # Bottom section: brand color solution
    draw.rectangle([0, SIZE//2 + 30, SIZE, SIZE], fill=color)

    # Middle connector
    draw.rectangle([0, SIZE//2-30, SIZE, SIZE//2+30], fill=WHITE)
    draw_centered(draw, "→  THE SOLUTION  ←", load_font(48), SIZE//2,
                  SIZE//2-28, color)

    # Problem area
    draw.text((80, 80), "THE PROBLEM", font=load_font(52), fill=GOLD)
    draw.text((80, 160), p["name"], font=load_font(80), fill=WHITE)

    prob_y = 280
    for prob in p["problem"]:
        draw.text((80, prob_y), "✗  " + prob, font=load_font_reg(46), fill=(220, 100, 90))
        prob_y += 70

    # Solution area
    sol_y = SIZE//2 + 100
    draw.text((80, sol_y), "WITH " + p["name"].upper(), font=load_font(52), fill=GOLD)
    sol_y += 80
    for sol in p["solution"]:
        draw.text((80, sol_y), "✓  " + sol, font=load_font_reg(46), fill=WHITE)
        sol_y += 70

    add_footer(draw, (20, 20, 30))
    return img


# ── IMAGE 3: Before / After ───────────────────────────────────────────────────

def make_before_after(p):
    color = p["color"]
    r, g, b = color

    img  = Image.new("RGB", (SIZE, SIZE), LGRAY)
    draw = ImageDraw.Draw(img)

    # Header
    add_header(draw, color, "BEFORE  vs  AFTER", f"Why you need the {p['name']}")

    # Two columns
    col_w = SIZE//2 - 40
    left_x, right_x = 30, SIZE//2 + 10
    col_top = 580
    col_bot = SIZE - 140

    # LEFT: Before (dark/grey)
    draw_card(draw, left_x, col_top, left_x+col_w, col_bot, 20, (45, 48, 58))
    draw_centered(draw, "BEFORE", load_font(58), left_x+col_w//2, col_top+30, (220, 90, 80))

    by = col_top + 120
    for prob in p["problem"]:
        txt = "✗  " + prob
        draw.text((left_x+30, by), txt, font=load_font_reg(38), fill=(220, 100, 90))
        by += 65

    # RIGHT: After (brand color)
    draw_card(draw, right_x, col_top, right_x+col_w, col_bot, 20, color)
    draw_centered(draw, "AFTER", load_font(58), right_x+col_w//2, col_top+30, GOLD)

    ay = col_top + 120
    for sol in p["solution"]:
        txt = "✓  " + sol
        draw.text((right_x+30, ay), txt, font=load_font_reg(38), fill=WHITE)
        ay += 65

    # Center arrow
    arrow_x = SIZE//2 - 50
    arrow_y = (col_top + col_bot) // 2
    draw.rounded_rectangle([arrow_x, arrow_y-50, arrow_x+100, arrow_y+50],
                            radius=28, fill=GOLD)
    draw_centered(draw, "→", load_font(64), arrow_x+50, arrow_y-36, DARK)

    add_footer(draw, color)
    return img


# ── IMAGE 4: Contents ─────────────────────────────────────────────────────────

def make_contents(p):
    color = p["color"]
    r, g, b = color
    items = p["contents"]

    img  = Image.new("RGB", (SIZE, SIZE), LGRAY)
    draw = ImageDraw.Draw(img)

    add_header(draw, color, "WHAT'S INCLUDED", f"{len(items)} sheets inside the {p['name']}")

    card_top = 580
    card_h   = 190
    card_gap = 22
    margin   = 60
    card_w   = SIZE - 2*margin

    for i, (icon, title, desc) in enumerate(items):
        cy = card_top + i * (card_h + card_gap)

        # Shadow
        draw.rounded_rectangle([margin+5, cy+5, margin+card_w+5, cy+card_h+5],
                                radius=20, fill=(175, 180, 192))
        # White card
        draw.rounded_rectangle([margin, cy, margin+card_w, cy+card_h],
                                radius=20, fill=WHITE)
        # Color accent left
        draw.rounded_rectangle([margin, cy, margin+14, cy+card_h],
                                radius=7, fill=color)
        # Number circle
        nc = margin + 65
        draw.ellipse([nc-32, cy+card_h//2-32, nc+32, cy+card_h//2+32], fill=color)
        draw_centered(draw, str(i+1), load_font(36), nc, cy+card_h//2-20, WHITE)
        # Icon
        try:
            draw.text((margin+130, cy+card_h//2), icon, font=load_font(52),
                      fill=color, anchor="lm")
        except Exception:
            pass
        # Title
        draw.text((margin+210, cy+28), title, font=load_font(50), fill=color)
        # Description
        draw.text((margin+210, cy+100), desc, font=load_font_reg(36), fill=GRAY)
        # Checkmark right
        draw.text((margin+card_w-60, cy+card_h//2), "✓", font=load_font(52),
                  fill=color, anchor="mm")

    add_footer(draw, color, f"All {len(items)} sheets in ONE file  •  Google Sheets & Excel")
    return img


# ── IMAGE 5: How It Works ─────────────────────────────────────────────────────

STEPS = [
    ("🛒", "1. Purchase & Download",  "After checkout, Etsy sends your download link instantly."),
    ("📋", "2. Open in Google Sheets", "Click the link, then File → Make a Copy → saved to your Drive."),
    ("✏️", "3. Customize & Use",       "Edit your data, change colors — and start using immediately!"),
]


def make_how_it_works(p):
    color = p["color"]
    r, g, b = color
    c2 = (min(r+25, 255), min(g+25, 255), min(b+25, 255))

    img  = Image.new("RGB", (SIZE, SIZE), LGRAY)
    draw = ImageDraw.Draw(img)

    add_header(draw, color, "HOW IT WORKS", "Up and running in under 5 minutes")

    step_top  = 580
    step_h    = 300
    step_gap  = 50
    margin    = 70
    step_w    = SIZE - 2*margin

    for i, (icon, title, desc) in enumerate(STEPS):
        sy = step_top + i * (step_h + step_gap)

        # Shadow + white card
        draw.rounded_rectangle([margin+5, sy+5, margin+step_w+5, sy+step_h+5],
                                radius=24, fill=(175, 180, 192))
        draw.rounded_rectangle([margin, sy, margin+step_w, sy+step_h],
                                radius=24, fill=WHITE)

        # Large step number circle (left)
        nc = margin + 90
        draw.ellipse([nc-70, sy+step_h//2-70, nc+70, sy+step_h//2+70], fill=color)
        draw_centered(draw, str(i+1), load_font(80), nc, sy+step_h//2-48, WHITE)

        # Connector arrow between steps
        if i < 2:
            ar = margin + step_w//2
            ay = sy + step_h + step_gap//2 - 20
            draw.rounded_rectangle([ar-30, ay, ar+30, ay+40], radius=10, fill=color)
            draw_centered(draw, "↓", load_font(36), ar, ay-4, WHITE)

        # Icon
        try:
            draw.text((margin+200, sy+step_h//2), icon, font=load_font(80),
                      fill=color, anchor="lm")
        except Exception:
            pass

        # Title
        draw.text((margin+310, sy+55), title, font=load_font(60), fill=color)
        # Description
        draw.text((margin+310, sy+150), desc, font=load_font_reg(42), fill=GRAY)

    # Time badge
    draw_card(draw, SIZE//2-220, step_top + 3*(step_h+step_gap) - 10,
              SIZE//2+220, step_top + 3*(step_h+step_gap) + 90, 28, GOLD)
    draw_centered(draw, "⚡  Setup time: Under 5 minutes", load_font(42),
                  SIZE//2, step_top + 3*(step_h+step_gap) + 18, DARK)

    add_footer(draw, color)
    return img


# ── IMAGE 6: Results ──────────────────────────────────────────────────────────

def make_results(p):
    color = p["color"]
    r, g, b = color
    results = p["results"]

    img  = Image.new("RGB", (SIZE, SIZE), color)
    draw = ImageDraw.Draw(img)

    # Subtle background circles
    c2 = (min(r+30, 255), min(g+30, 255), min(b+30, 255))
    draw.ellipse([SIZE-500, -200, SIZE+200, 500], fill=c2)
    draw.ellipse([-200, SIZE-400, 300, SIZE+200], fill=c2)

    # Header
    draw.text((70, 60), "NasriTools", font=load_font(48), fill=(255, 255, 200))
    draw_centered(draw, "WHAT YOU'LL ACHIEVE", load_font(90), SIZE//2, 180, WHITE)
    draw_centered(draw, f"After using the {p['name']}", load_font_reg(46), SIZE//2, 320, (220, 235, 255))
    draw.rectangle([SIZE//2-220, 400, SIZE//2+220, 408], fill=WHITE)

    # 4 result cards (2×2 grid)
    cols, rows_n = 2, 2
    margin, gap  = 70, 40
    grid_top     = 460
    grid_bot     = SIZE - 140
    card_w = (SIZE - 2*margin - gap*(cols-1)) // cols
    card_h = (grid_bot - grid_top - gap*(rows_n-1)) // rows_n

    c_light = (min(r+40, 255), min(g+40, 255), min(b+40, 255))

    for idx, (icon, title, sub) in enumerate(results):
        row = idx // cols
        col = idx % cols
        x0  = margin + col * (card_w + gap)
        y0  = grid_top + row * (card_h + gap)
        x1  = x0 + card_w
        y1  = y0 + card_h

        draw_card(draw, x0, y0, x1, y1, 24, c_light, shadow=False)

        # Icon
        try:
            draw.text(((x0+x1)//2, y0+80), icon, font=load_font(80), fill=WHITE, anchor="mm")
        except Exception:
            pass

        # Title
        draw_centered(draw, title, load_font(50), (x0+x1)//2, y0+140, WHITE)
        # Sub
        draw_centered(draw, sub, load_font_reg(36), (x0+x1)//2, y0+220, (220, 235, 255))

    add_footer(draw, (r//3, g//3, b//3))
    return img


# ── IMAGE 7: Trust ────────────────────────────────────────────────────────────

GUARANTEES = [
    ("⚡", "Instant Download"),
    ("♾️", "Lifetime Access"),
    ("🔒", "Secure Checkout"),
    ("💬", "24h Support"),
    ("✏️", "100% Editable"),
    ("📵", "No Subscription"),
]


def make_trust(p):
    color = p["color"]
    r, g, b = color

    img  = Image.new("RGB", (SIZE, SIZE), LGRAY)
    draw = ImageDraw.Draw(img)

    add_header(draw, color, "WHY TRUST US?", "NasriTools — Trusted Digital Templates")

    # Stars
    star_y = 580
    draw_centered(draw, "⭐ ⭐ ⭐ ⭐ ⭐", load_font(80), SIZE//2, star_y, GOLD)
    draw_centered(draw, "5.0 Star Rating on Etsy", load_font(52), SIZE//2, star_y+110, color)

    # Divider
    draw.rectangle([SIZE//2-240, star_y+190, SIZE//2+240, star_y+198], fill=color)

    # Review quote card
    quote_y = star_y + 230
    draw_card(draw, 60, quote_y, SIZE-60, quote_y+200, 20, WHITE)
    draw.text((100, quote_y+25), "❝", font=load_font(80), fill=color)
    draw_centered(draw, "This template completely changed how I manage",
                  load_font_reg(40), SIZE//2, quote_y+50, DARK)
    draw_centered(draw, "my money. Setup took 3 minutes. Highly recommend!",
                  load_font_reg(40), SIZE//2, quote_y+102, DARK)
    draw.text((SIZE-120, quote_y+120), "❞", font=load_font(80), fill=color, anchor="rm")
    draw_centered(draw, "— Verified Buyer  ⭐⭐⭐⭐⭐",
                  load_font_reg(34), SIZE//2, quote_y+155, GRAY)

    # Guarantee grid (2 rows × 3 cols)
    g_top = quote_y + 240
    g_bot = SIZE - 130
    g_w   = SIZE - 120
    gx    = 60
    cw    = (g_w - 2*30) // 3
    ch    = (g_bot - g_top - 30) // 2

    for idx, (icon, label) in enumerate(GUARANTEES):
        row = idx // 3
        col = idx % 3
        x0  = gx + col * (cw + 30)
        y0  = g_top + row * (ch + 30)
        x1  = x0 + cw
        y1  = y0 + ch

        draw_card(draw, x0, y0, x1, y1, 20, WHITE)
        try:
            draw.text(((x0+x1)//2, y0+50), icon, font=load_font(52), fill=color, anchor="mm")
        except Exception:
            pass
        draw_centered(draw, label, load_font(36), (x0+x1)//2, y0+80, color)

    add_footer(draw, color)
    return img


# ── Upload ────────────────────────────────────────────────────────────────────

def upload_image(token, listing_id, img, rank):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=93)
    buf.seek(0)
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images",
        headers=auth_headers(token),
        files={"image": (f"image_rank{rank}.jpg", buf, "image/jpeg")},
        data={"rank": rank, "overwrite": "true"},
        timeout=60,
    )
    return r


# ── Main ──────────────────────────────────────────────────────────────────────

GENERATORS = [
    (1, "Thumbnail",     make_thumbnail),
    (2, "Value Hook",    make_value_hook),
    (3, "Before/After",  make_before_after),
    (4, "Contents",      make_contents),
    (5, "How It Works",  make_how_it_works),
    (6, "Results",       make_results),
    (7, "Trust",         make_trust),
]

# Keywords to find each product in the active listings
SEARCH_KEYWORDS = [
    ["budget", "tracker"],
    ["habit", "tracker"],
    ["meal", "planner"],
    ["wedding", "planner"],
    ["workout", "tracker"],
    ["content", "creator"],
    ["invoice", "tracker"],
    ["student", "planner"],
    ["goals", "planner"],
    ["weekly", "planner"],
]


def fetch_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings


def find_listing_id(active_listings, keywords):
    for lst in active_listings:
        title = (lst.get("title") or "").lower()
        if all(kw.lower() in title for kw in keywords):
            return lst["listing_id"]
    return None


def main():
    done = {}
    if DONE_FILE.exists():
        done = json.loads(DONE_FILE.read_text())

    token = get_token()

    print(f"\n{'='*70}")
    print(f"  NasriTools - Pro Image System (7 images × {len(PRODUCTS)} products)")
    print(f"{'='*70}\n")

    print("  Discovering listing IDs…")
    active = fetch_all_listings(token)
    print(f"  Found {len(active)} active listings\n")
    token = get_token()

    total_ok = 0
    for i, p in enumerate(PRODUCTS):
        keywords = SEARCH_KEYWORDS[i] if i < len(SEARCH_KEYWORDS) else []
        lid = find_listing_id(active, keywords)

        if lid is None:
            print(f"\n  [{p['name']}] NOT FOUND (keywords: {keywords}) — skipping")
            continue

        pid = str(lid)
        print(f"\n  [{p['name']}]  listing {lid}")

        for rank, label, generator in GENERATORS:
            img_key = f"{pid}_rank{rank}"
            if done.get(img_key):
                print(f"    rank {rank} ({label}) — skipped")
                total_ok += 1
                continue

            print(f"    rank {rank} ({label}) … ", end="", flush=True)
            try:
                img = generator(p)
                r   = upload_image(token, lid, img, rank)
                time.sleep(1.2)
                if r.ok:
                    print("✓")
                    done[img_key] = True
                    total_ok += 1
                else:
                    print(f"✗  {r.status_code}: {r.text[:80]}")
            except Exception as e:
                print(f"✗  error: {e}")

            DONE_FILE.write_text(json.dumps(done, indent=2))

        token = get_token()

    total = len(PRODUCTS) * len(GENERATORS)
    print(f"\n{'='*70}")
    print(f"  Done: {total_ok}/{total} images uploaded")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
