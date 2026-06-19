"""
NasriTools - Generate Phone Mockup Images (rank 4)
Creates a smartphone frame containing a spreadsheet preview for all 10 main product listings.
Run: python generate_mobile_mockups.py
"""
import json, os, time, requests, io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_mockups_done.json"
SIZE       = 2000

PRODUCTS = [
    {
        "listing": 4487745643,
        "name": "Budget Tracker",
        "color": (31, 107, 59),
        "light": (220, 247, 233),
        "emoji": "💰",
        "rows": [
            ("Category",   "Budget",   "Spent",   "Remaining"),
            ("Rent",       "€800",     "€800",    "€0"),
            ("Groceries",  "€200",     "€145",    "€55"),
            ("Transport",  "€100",     "€78",     "€22"),
            ("Savings",    "€300",     "€300",    "€0"),
            ("Total",      "€1,400",   "€1,323",  "€77"),
        ],
    },
    {
        "listing": 4487740567,
        "name": "Habit Tracker",
        "color": (192, 57, 43),
        "light": (253, 228, 224),
        "emoji": "✅",
        "rows": [
            ("Habit",        "Mon", "Tue", "Wed"),
            ("Exercise",     "✓",   "✓",   "✓"),
            ("Read 30 min",  "✓",   "—",   "✓"),
            ("Meditate",     "✓",   "✓",   "—"),
            ("No Junk Food", "—",   "✓",   "✓"),
            ("8h Sleep",     "✓",   "✓",   "✓"),
        ],
    },
    {
        "listing": 4487742011,
        "name": "Meal Planner",
        "color": (39, 174, 141),
        "light": (209, 250, 229),
        "emoji": "🥗",
        "rows": [
            ("Day",         "Breakfast",    "Lunch",       "Dinner"),
            ("Monday",      "Oatmeal",      "Salad",       "Pasta"),
            ("Tuesday",     "Eggs",         "Sandwich",    "Rice Bowl"),
            ("Wednesday",   "Yogurt",       "Soup",        "Chicken"),
            ("Thursday",    "Smoothie",     "Wrap",        "Tacos"),
            ("Friday",      "Toast",        "Pizza Slice", "Steak"),
        ],
    },
    {
        "listing": 4487743321,
        "name": "Wedding Planner",
        "color": (210, 82, 162),
        "light": (252, 228, 243),
        "emoji": "💍",
        "rows": [
            ("Task",             "Budget",  "Paid",    "Status"),
            ("Venue",            "€3,000",  "€1,500",  "Deposit"),
            ("Catering",         "€2,000",  "€0",      "Pending"),
            ("Photography",      "€1,200",  "€600",    "Booked"),
            ("Flowers",          "€500",    "€500",    "Done"),
            ("Total",            "€6,700",  "€2,600",  "39% Paid"),
        ],
    },
    {
        "listing": 4487744011,
        "name": "Workout Tracker",
        "color": (192, 57, 43),
        "light": (253, 228, 224),
        "emoji": "💪",
        "rows": [
            ("Exercise",    "Sets", "Reps", "Weight"),
            ("Squat",       "4",    "8",    "80kg"),
            ("Bench Press", "4",    "10",   "60kg"),
            ("Deadlift",    "3",    "6",    "100kg"),
            ("Pull Ups",    "3",    "12",   "BW"),
            ("Plank",       "3",    "60s",  "—"),
        ],
    },
    {
        "listing": 4487745211,
        "name": "Content Creator Planner",
        "color": (230, 126, 34),
        "light": (254, 243, 224),
        "emoji": "📱",
        "rows": [
            ("Date",    "Platform",   "Topic",        "Status"),
            ("Jun 1",   "Instagram",  "Morning Reel", "Published"),
            ("Jun 3",   "YouTube",    "Tutorial",     "Scheduled"),
            ("Jun 5",   "TikTok",     "Trending",     "Draft"),
            ("Jun 7",   "Blog",       "Guide",        "Writing"),
            ("Jun 9",   "Instagram",  "Story",        "Idea"),
        ],
    },
    {
        "listing": 4487744321,
        "name": "Freelancer Invoice Tracker",
        "color": (52, 152, 219),
        "light": (214, 234, 248),
        "emoji": "📄",
        "rows": [
            ("Client",    "Invoice", "Amount",  "Status"),
            ("Acme Co.",  "#001",    "€850",    "Paid"),
            ("StarTech",  "#002",    "€1,200",  "Pending"),
            ("BlueBrand", "#003",    "€650",    "Overdue"),
            ("GreenCorp", "#004",    "€2,100",  "Sent"),
            ("Total",     "4 inv.",  "€4,800",  ""),
        ],
    },
    {
        "listing": 4487742911,
        "name": "Student Planner",
        "color": (108, 52, 131),
        "light": (237, 228, 252),
        "emoji": "🎓",
        "rows": [
            ("Subject",   "Assignment",    "Due",    "Grade"),
            ("Math",      "Chapter 5",     "Jun 3",  "A"),
            ("English",   "Essay",         "Jun 5",  "B+"),
            ("Science",   "Lab Report",    "Jun 8",  "—"),
            ("History",   "Presentation",  "Jun 10", "—"),
            ("GPA",       "",              "",       "3.8"),
        ],
    },
    {
        "listing": 4487743721,
        "name": "Goals Planner",
        "color": (30, 100, 180),
        "light": (220, 235, 252),
        "emoji": "🎯",
        "rows": [
            ("Goal",         "Target",   "Progress", "Status"),
            ("Save €5,000",  "Dec 2024", "60%",      "On Track"),
            ("Run 5k",       "Sep 2024", "80%",      "Almost"),
            ("Read 24 books","Dec 2024", "50%",      "On Track"),
            ("Learn Python", "Jul 2024", "90%",      "Almost"),
            ("Side Income",  "Dec 2024", "30%",      "Lagging"),
        ],
    },
    {
        "listing": 4487742511,
        "name": "Weekly Planner",
        "color": (108, 52, 131),
        "light": (237, 228, 252),
        "emoji": "📅",
        "rows": [
            ("Time",     "Monday",   "Tuesday",  "Wednesday"),
            ("08:00",    "Workout",  "Emails",   "Meeting"),
            ("10:00",    "Work",     "Work",     "Work"),
            ("12:00",    "Lunch",    "Lunch",    "Lunch"),
            ("14:00",    "Project",  "Training", "Project"),
            ("18:00",    "Study",    "Gym",      "Study"),
        ],
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
            "x-api-key": CLIENT_ID}


def load_font(size):
    for f in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
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
    ]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def make_phone_mockup(product):
    color = product["color"]
    light = product["light"]
    name  = product["name"]
    rows  = product["rows"]

    img  = Image.new("RGB", (SIZE, SIZE), light)
    draw = ImageDraw.Draw(img)

    # ── Background gradient strip (top) ──────────────────────────────────────
    draw.rectangle([0, 0, SIZE, 640], fill=color)

    # Product name
    draw.text((SIZE // 2, 120), name.upper(), font=load_font(80),
              fill=(255, 255, 255), anchor="mm")
    draw.text((SIZE // 2, 220), "Google Sheets Template", font=load_font_reg(44),
              fill=(255, 255, 220), anchor="mm")

    # Divider
    draw.rectangle([SIZE // 2 - 180, 270, SIZE // 2 + 180, 276], fill=(255, 255, 255))

    # Tagline
    draw.text((SIZE // 2, 340), "Works on Desktop & Mobile", font=load_font_reg(40),
              fill=(255, 255, 220), anchor="mm")
    draw.text((SIZE // 2, 400), "No App Needed · Free Google Sheets", font=load_font_reg(34),
              fill=(255, 255, 200), anchor="mm")

    # ── Phone frame ───────────────────────────────────────────────────────────
    phone_w, phone_h = 700, 1100
    phone_x = (SIZE - phone_w) // 2
    phone_y = 500

    # Phone shadow
    draw.rounded_rectangle([phone_x + 10, phone_y + 10,
                             phone_x + phone_w + 10, phone_y + phone_h + 10],
                            radius=60, fill=(100, 100, 110))
    # Phone body (dark frame)
    draw.rounded_rectangle([phone_x, phone_y, phone_x + phone_w, phone_y + phone_h],
                            radius=60, fill=(30, 30, 35))
    # Screen bezel
    bezel = 22
    screen_x = phone_x + bezel
    screen_y = phone_y + 60
    screen_w = phone_w - 2 * bezel
    screen_h = phone_h - 100
    draw.rounded_rectangle([screen_x, screen_y,
                             screen_x + screen_w, screen_y + screen_h],
                            radius=10, fill=(255, 255, 255))

    # Notch
    notch_w, notch_h = 120, 30
    notch_x = screen_x + (screen_w - notch_w) // 2
    draw.rounded_rectangle([notch_x, screen_y - 2,
                             notch_x + notch_w, screen_y + notch_h],
                            radius=14, fill=(30, 30, 35))

    # Spreadsheet content inside screen
    row_h  = 52
    col_ws = [screen_w // 4] * 4
    header_colors = [color, color, color, color]

    for ri, row_data in enumerate(rows):
        for ci, cell in enumerate(row_data):
            cx = screen_x + sum(col_ws[:ci])
            cy = screen_y + 40 + ri * row_h
            cw = col_ws[ci]

            is_header = ri == 0
            bg = color if is_header else ((245, 250, 245) if ri % 2 == 0 else (255, 255, 255))
            fg = (255, 255, 255) if is_header else (40, 40, 40)

            # Clip to screen bounds
            if cy + row_h > screen_y + screen_h or cx + cw > screen_x + screen_w:
                continue

            draw.rectangle([cx, cy, cx + cw - 2, cy + row_h - 2], fill=bg)
            font_cell = load_font(24) if is_header else load_font_reg(22)
            # Truncate text to fit cell
            text = str(cell)
            while len(text) > 1 and draw.textlength(text, font=font_cell) > cw - 10:
                text = text[:-1]
            draw.text((cx + 5, cy + (row_h // 2 - 12)), text, font=font_cell, fill=fg)

    # Home bar
    bar_y = phone_y + phone_h - 28
    draw.rounded_rectangle([phone_x + phone_w // 2 - 60, bar_y,
                             phone_x + phone_w // 2 + 60, bar_y + 8],
                            radius=4, fill=(100, 100, 110))

    # ── Bottom section ────────────────────────────────────────────────────────
    bottom_y = phone_y + phone_h + 60
    r, g, b  = color
    light2   = (min(r + 30, 255), min(g + 30, 255), min(b + 30, 255))
    draw.rounded_rectangle([SIZE // 2 - 380, bottom_y, SIZE // 2 + 380, bottom_y + 100],
                            radius=24, fill=color)
    draw.text((SIZE // 2, bottom_y + 50), "Works on Google Sheets App (Free)",
              font=load_font(36), fill=(255, 255, 255), anchor="mm")

    # Small feature pills row
    pills = ["📱 Mobile Ready", "💻 Desktop Ready", "📊 Auto-Calculates"]
    pill_y = bottom_y + 130
    pill_x = 200
    for pill in pills:
        pw = 420
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pw, pill_y + 70],
                                radius=35, fill=(255, 255, 255))
        draw.text((pill_x + pw // 2, pill_y + 35), pill,
                  font=load_font_reg(30), fill=color, anchor="mm")
        pill_x += pw + 30

    # Bottom strip
    draw.rectangle([0, SIZE - 110, SIZE, SIZE], fill=color)
    draw.text((SIZE // 2, SIZE - 65),
              "Instant Download  •  Google Sheets  •  nasritools.etsy.com",
              font=load_font_reg(34), fill=(255, 255, 255), anchor="mm")

    return img


def upload_image(token, listing_id, img, rank=4):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=92)
    buf.seek(0)
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/images",
        headers=auth_headers(token),
        files={"image": ("mockup.jpg", buf, "image/jpeg")},
        data={"rank": rank, "overwrite": "true"},
        timeout=60,
    )
    return r


def main():
    done = {}
    if DONE_FILE.exists():
        done = json.loads(DONE_FILE.read_text())

    token = get_token()

    print(f"\n{'='*60}")
    print(f"  NasriTools - Phone Mockup Images (rank 4)")
    print(f"{'='*60}\n")

    ok = 0
    for p in PRODUCTS:
        key = str(p["listing"])
        if done.get(key):
            print(f"  [{p['name']}] skipped (already done)")
            ok += 1
            continue

        print(f"  [{p['name']}] listing {p['listing']}", end=" ")
        img = make_phone_mockup(p)
        r = upload_image(token, p["listing"], img, rank=4)
        time.sleep(1)
        if r.ok:
            print("✓")
            done[key] = True
            ok += 1
        else:
            print(f"✗  {r.status_code}: {r.text[:100]}")

        DONE_FILE.write_text(json.dumps(done, indent=2))
        token = get_token()

    print(f"\n{'='*60}")
    print(f"  Done: {ok}/{len(PRODUCTS)} mockups uploaded")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
