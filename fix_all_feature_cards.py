"""
NasriTools - Create & Upload Feature Cards for ALL Listings
Generates "What's Included" cards (2000x2000px) and uploads as image #3
Builds 6 features automatically from the listing title keywords
Run: python fix_all_feature_cards.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from io import BytesIO
import json, os, hashlib, time, requests

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_all_feature_cards_done.json"

SIZE = 2000

PALETTES = [
    ((34, 139, 87),  (220, 247, 233)),
    ((108, 67, 176), (237, 228, 252)),
    ((214, 90, 49),  (252, 232, 224)),
    ((185, 50, 100), (252, 225, 237)),
    ((30, 100, 180), (220, 235, 252)),
    ((200, 60, 60),  (252, 225, 225)),
    ((20, 120, 140), (215, 242, 246)),
    ((50, 130, 70),  (220, 245, 225)),
    ((160, 100, 20), (252, 243, 218)),
    ((80, 80, 160),  (230, 230, 252)),
    ((120, 40, 120), (245, 220, 245)),
    ((40, 100, 140), (215, 235, 250)),
]

FEATURE_RULES = [
    (["budget", "expense", "spending"],
     ["Track all income & expenses", "Auto-calculate totals & balance",
      "Bill payment due date tracker", "Monthly & annual summary",
      "Spending by category charts", "Savings goal progress"]),
    (["profit", "loss", "revenue", "cash flow"],
     ["Record all sales & costs", "Auto-calculate gross profit",
      "Monthly P&L statement", "Revenue trend charts",
      "Expense category breakdown", "Annual financial overview"]),
    (["invoice", "billing"],
     ["Log all invoices & payments", "Paid / pending / overdue status",
      "Client contact database", "Monthly income summary",
      "Tax preparation tracker", "Late payment follow-up"]),
    (["trading", "stock", "investment", "portfolio", "crypto", "options"],
     ["Log all trades & positions", "Auto P&L calculation",
      "Win/loss rate tracker", "Portfolio value overview",
      "Trade notes & analysis", "Monthly performance report"]),
    (["startup", "financial model", "break even"],
     ["Revenue & cost projections", "Break-even analysis",
      "Monthly cash flow model", "Investor-ready summary",
      "Scenario planning section", "Annual forecast charts"]),
    (["kpi", "dashboard", "metrics", "analytics"],
     ["Track all key metrics in one view", "Auto-updating data charts",
      "Monthly vs target comparison", "Color-coded performance alerts",
      "Team performance overview", "Custom KPI setup"]),
    (["project", "task", "deadline", "gantt"],
     ["Track all tasks & deadlines", "Team assignment management",
      "Progress status tracker", "Priority & urgency labels",
      "Milestone completion chart", "Project timeline view"]),
    (["crm", "lead", "sales pipeline", "deal"],
     ["Full client contact database", "Lead status pipeline",
      "Follow-up reminder system", "Deal value tracker",
      "Conversion rate calculator", "Monthly sales summary"]),
    (["hr", "employee", "payroll", "staff", "onboarding", "attendance", "performance"],
     ["Employee contact database", "Attendance & time-off log",
      "Payroll calculation sheet", "Performance review tracker",
      "Onboarding checklist", "Team overview dashboard"]),
    (["social media", "instagram", "youtube", "content", "posting", "influencer", "repurposing"],
     ["Monthly content calendar", "Platform publishing schedule",
      "Analytics & growth tracker", "Brand deal & sponsor log",
      "Hashtag & caption planner", "Audience growth charts"]),
    (["habit", "routine", "wellness", "mindfulness"],
     ["Track up to 30 daily habits", "Automatic streak counter",
      "Monthly completion percentage", "Weekly review section",
      "Habit category organizer", "Progress comparison charts"]),
    (["meal", "food", "grocery", "nutrition", "diet", "calorie"],
     ["7-day meal planning grid", "Auto-generated grocery list",
      "Pantry inventory tracker", "Nutritional notes per meal",
      "Monthly meal calendar view", "Recipe link organizer"]),
    (["workout", "gym", "fitness", "exercise"],
     ["Log sets, reps & weight", "Personal record tracker",
      "Body measurements log", "Cardio & session notes",
      "Monthly fitness goals", "Strength progress charts"]),
    (["weight loss", "keto", "diet plan"],
     ["Daily calorie & macro log", "Weekly weigh-in tracker",
      "Food diary & notes", "Progress chart visualizer",
      "Goal weight milestones", "Cheat day tracker"]),
    (["wedding", "event", "party"],
     ["Full event budget tracker", "Guest list & RSVP manager",
      "Vendor contact & payment log", "Day-of timeline planner",
      "Checklist & to-do tracker", "Seating chart helper"]),
    (["travel", "trip", "vacation", "itinerary"],
     ["Day-by-day itinerary planner", "Travel budget tracker",
      "Packing list checklist", "Accommodation & flight notes",
      "Local tips & recommendations", "Currency & cost converter"]),
    (["student", "academic", "college", "grade", "exam", "study", "gpa"],
     ["Weekly class schedule", "Assignment due date tracker",
      "Grade calculator per subject", "GPA tracker & progress",
      "Exam preparation checklist", "Semester overview calendar"]),
    (["scholarship", "job application", "career"],
     ["Application status tracker", "Deadline reminder system",
      "Contact & notes database", "Interview preparation log",
      "Offer comparison sheet", "Goal & milestone tracker"]),
    (["goal", "vision", "action plan", "objective"],
     ["Annual goal setting (12 goals)", "90-day action plan breakdown",
      "Weekly milestone tracker", "Habit alignment section",
      "Monthly review prompts", "Vision board notes"]),
    (["weekly planner", "daily planner", "schedule", "time block"],
     ["Week-at-a-glance daily schedule", "Top 3 priority task list",
      "Time blocking grid", "Notes & ideas section",
      "Weekly goals & intentions", "Habit check-in tracker"]),
    (["real estate", "property", "rental", "mortgage", "landlord"],
     ["Property details database", "Rental income & expense log",
      "Tenant contact tracker", "Mortgage payment schedule",
      "Annual income summary", "Maintenance cost tracker"]),
    (["freelancer", "freelance", "contractor", "consulting"],
     ["Client project database", "Invoice & payment tracker",
      "Monthly income summary", "Time & hourly rate log",
      "Tax preparation helper", "Project status board"]),
    (["photography", "photographer", "creative", "musician", "artist", "author", "booking"],
     ["Client & booking database", "Income & expense tracker",
      "Project notes organizer", "Invoice & payment log",
      "Revenue by month charts", "Goal & milestone tracker"]),
    (["amazon", "fba", "shopify", "ecommerce", "dropshipping", "print on demand", "etsy shop"],
     ["Product listing database", "Sales & revenue tracker",
      "Inventory level monitor", "Supplier contact list",
      "Profit margin calculator", "Monthly performance report"]),
    (["restaurant", "cafe", "salon", "hair", "beauty", "barbershop"],
     ["Daily sales & revenue log", "Appointment & booking tracker",
      "Staff schedule manager", "Inventory & supplies log",
      "Service menu pricing", "Monthly P&L summary"]),
    (["nonprofit", "charity", "donation", "grant"],
     ["Donor database & contacts", "Donation tracking log",
      "Grant application tracker", "Budget vs actual report",
      "Volunteer management", "Campaign performance log"]),
    (["supply chain", "inventory", "warehouse", "stock"],
     ["Supplier contact database", "Stock level monitor",
      "Order tracking system", "Delivery status tracker",
      "Cost & pricing analysis", "Low-stock alert system"]),
    (["marketing", "campaign", "roi", "advertising", "brand", "media kit"],
     ["Campaign budget tracker", "Channel ROI comparison",
      "Lead generation log", "Conversion rate tracker",
      "Monthly spend summary", "Campaign performance charts"]),
    (["health", "medical", "symptom", "medication", "sleep", "pregnancy", "baby"],
     ["Daily health log entries", "Symptom & notes tracker",
      "Medication & supplement log", "Progress trend charts",
      "Health goal setting", "Doctor visit history"]),
    (["home", "household", "cleaning", "maintenance", "moving"],
     ["Room-by-room task tracker", "Maintenance schedule log",
      "Household budget planner", "Supplier & contractor list",
      "Monthly expense summary", "Checklist & reminders"]),
]

DEFAULT_FEATURES = [
    "Easy-to-use data entry", "Auto-calculating formulas",
    "Fully customizable layout", "Works on Google Sheets & Excel",
    "Color-coded status system", "Instant digital download",
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
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}


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
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(0.4)
    return listings


def pick_features(title):
    t = title.lower()
    for keywords, features in FEATURE_RULES:
        if any(kw in t for kw in keywords):
            return features
    return DEFAULT_FEATURES


def pick_palette(title):
    idx = int(hashlib.md5(title.encode()).hexdigest()[:4], 16) % len(PALETTES)
    return PALETTES[idx]


def clean_title(title):
    label = title.split("|")[0].strip()
    for s in ["Google Sheets Template", "Google Sheets", "Spreadsheet Template",
              "Spreadsheet", "Template"]:
        label = label.replace(s, "").strip()
    return label[:48].strip()


def load_font(size):
    for f in ["C:/Windows/Fonts/arialbd.ttf",
              "C:/Windows/Fonts/arial.ttf",
              "C:/Windows/Fonts/calibrib.ttf"]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def make_card(title):
    color, light = pick_palette(title)
    features      = pick_features(title)
    label         = clean_title(title)
    r, g, b       = color

    img  = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, SIZE, 520], fill=color)
    draw.rectangle([0, 520, SIZE, SIZE], fill=light)

    for cx, cy, rad in [(1700, 100, 280), (100, 480, 200), (1850, 600, 150)]:
        overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(255, 255, 255, 20))
        img  = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    f_title = load_font(82)
    f_sub   = load_font(42)
    draw.text((SIZE // 2, 155), label,  font=f_title, fill=(255, 255, 255), anchor="mm")
    draw.text((SIZE // 2, 265), "Google Sheets Template", font=f_sub,
              fill=(255, 255, 255), anchor="mm")
    draw.rectangle([SIZE // 2 - 120, 315, SIZE // 2 + 120, 321], fill=(255, 255, 255))

    f_wh = load_font(38)
    draw.text((SIZE // 2, 400), "✔  WHAT'S INCLUDED",
              font=f_wh, fill=(255, 255, 255), anchor="mm")

    f_feat = load_font(46)
    feat_y = 575
    for feat in features[:6]:
        draw.rounded_rectangle([80, feat_y, SIZE - 80, feat_y + 98], radius=16,
                               fill=(255, 255, 255))
        draw.ellipse([110, feat_y + 18, 168, feat_y + 76], fill=color)
        draw.text((139, feat_y + 47), "✓", font=load_font(38),
                  fill=(255, 255, 255), anchor="mm")
        draw.text((208, feat_y + 47), feat, font=f_feat, fill=(40, 40, 40), anchor="lm")
        feat_y += 120

    strip_y = SIZE - 138
    draw.rectangle([0, strip_y, SIZE, SIZE], fill=color)
    f_bot = load_font(38)
    draw.text((SIZE // 2, strip_y + 44),
              "Instant Download  •  Works on Any Device  •  100% Customizable",
              font=f_bot, fill=(255, 255, 255), anchor="mm")
    f_url = load_font(32)
    draw.text((SIZE // 2, strip_y + 96), "nasritools.etsy.com",
              font=f_url, fill=(255, 255, 200), anchor="mm")
    return img


def upload_image(token, listing_id, img):
    buf = BytesIO()
    img.save(buf, "JPEG", quality=93)
    buf.seek(0)
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images",
        headers=auth_headers(token),
        files={"image": ("feature_card.jpg", buf, "image/jpeg")},
        data={"rank": 3, "overwrite": "true"},
        timeout=60,
    )
    return r


def main():
    done  = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Feature Cards for ALL Listings")
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
            print(f"[{i:03d}/{total}] SKIP (done): {title[:55]}")
            ok += 1
            continue

        print(f"[{i:03d}/{total}] {title[:60]}")
        card = make_card(title)
        r    = upload_image(token, lid, card)
        time.sleep(1)

        if r.ok:
            ok += 1
            done[lid] = title[:60]
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"    uploaded: OK")
        else:
            print(f"    ERROR {r.status_code}: {r.text[:120]}")

        if i % 10 == 0:
            token = get_token()

    print(f"\n{'='*65}")
    print(f"  Done: {ok}/{total} feature cards uploaded")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
