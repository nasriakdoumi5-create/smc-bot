"""
Draw annotated guide showing where to add alt text on Etsy
"""
from PIL import Image, ImageDraw, ImageFont
import math

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def fnt(path, size):
    try:    return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

W, H = 1600, 1000
img = Image.new("RGB", (W, H), (240, 242, 247))
d   = ImageDraw.Draw(img)

# ── Background ─────────────────────────────────────
d.rectangle([0,0,W,H], fill=(240,242,247))

# ── Title ──────────────────────────────────────────
d.rectangle([0,0,W,55], fill=(26,26,46))
d.text((W//2 - 300, 12), "دليل إضافة النص البديل على Etsy",
       font=fnt(FONT_BOLD, 28), fill=(255,215,0))

# ══ STEP 1 — Listings page ════════════════════════
# Browser bar
d.rectangle([40, 80, 900, 430], fill=(255,255,255), outline=(180,180,180), width=2)
d.rectangle([40, 80, 900, 115], fill=(248,248,248), outline=(180,180,180), width=1)
d.text((55, 87), "etsy.com/your/listings", font=fnt(FONT_REG, 20), fill=(100,100,100))

# Etsy header bar
d.rectangle([40,115,900,150], fill=(242,84,91))
d.text((55, 122), "Etsy  |  Shop Manager", font=fnt(FONT_BOLD, 22), fill=(255,255,255))

# Sidebar
d.rectangle([40,150,200,430], fill=(248,248,248), outline=(220,220,220), width=1)
sidebar_items = ["Orders", "Listings", "Stats", "Finance", "Marketing"]
for i, item in enumerate(sidebar_items):
    y = 170 + i*48
    bg = (242,84,91) if item == "Listings" else (248,248,248)
    fg = (255,255,255) if item == "Listings" else (80,80,80)
    d.rectangle([40, y, 200, y+40], fill=bg)
    d.text((55, y+10), item, font=fnt(FONT_BOLD if item=="Listings" else FONT_REG, 18), fill=fg)

# Listing card
d.rectangle([210, 165, 890, 295], fill=(255,255,255), outline=(220,220,220), width=1)
d.rectangle([220, 175, 310, 285], fill=(200,200,210), outline=(180,180,180), width=1)
d.text((228, 215), "IMG", font=fnt(FONT_BOLD, 22), fill=(150,150,150))
d.text((325, 185), "Restaurant & Cafe Manager", font=fnt(FONT_BOLD, 20), fill=(30,30,30))
d.text((325, 215), "Google Sheets Template", font=fnt(FONT_REG, 17), fill=(100,100,100))
d.text((325, 245), "$27.00  •  Active", font=fnt(FONT_REG, 16), fill=(15,155,88))

# Edit button
d.rounded_rectangle([700,230,840,270], radius=6, fill=(242,84,91))
d.text((730, 241), "Edit", font=fnt(FONT_BOLD, 22), fill=(255,255,255))

# Step 1 label
d.ellipse([930,140,990,200], fill=(242,84,91))
d.text((949, 150), "1", font=fnt(FONT_BOLD, 38), fill=(255,255,255))
d.text((1005, 155), 'اضغط "Edit"', font=fnt(FONT_BOLD, 28), fill=(26,26,46))

# Arrow 1
for i in range(20):
    ax = 700 - i*8
    ay = 250
    d.ellipse([ax-3,ay-3,ax+3,ay+3], fill=(242,84,91))
pts = [(700,250),(710,240),(710,260)]
d.polygon(pts, fill=(242,84,91))

# ══ STEP 2 — Image editing page ══════════════════
d.rectangle([40, 470, 900, 960], fill=(255,255,255), outline=(180,180,180), width=2)
d.rectangle([40, 470, 900, 505], fill=(242,84,91))
d.text((55, 477), "Edit Listing — Restaurant & Cafe Manager",
       font=fnt(FONT_BOLD, 20), fill=(255,255,255))

# Photos section
d.text((60, 525), "PHOTOS", font=fnt(FONT_BOLD, 22), fill=(60,60,60))

# Image thumbnails
img_labels = ["01_hero", "02_included", "03_how", "04_feat", "05_cta"]
img_colors = [(233,69,96),(74,144,217),(15,155,88),(255,107,53),(120,80,200)]
for i, (label, color) in enumerate(zip(img_labels, img_colors)):
    x = 60 + i * 155
    # Thumbnail box
    d.rectangle([x, 555, x+140, 680], fill=color, outline=(180,180,180), width=1)
    d.text((x+30, 610), label[:7], font=fnt(FONT_BOLD, 16), fill=(255,255,255))

    if i == 0:  # highlight first image
        d.rectangle([x-4, 551, x+144, 684], fill=None, outline=(242,84,91), width=4)

# Alt text field
d.rectangle([60, 700, 880, 760], fill=(252,252,252), outline=(242,84,91), width=3)
d.text((75, 715), 'Alt text: "Restaurant and cafe manager Google Sheets template..."',
       font=fnt(FONT_REG, 19), fill=(80,80,80))

# Character counter
d.text((700, 768), "75/250 characters", font=fnt(FONT_REG, 16), fill=(150,150,150))

# Save button
d.rounded_rectangle([60, 800, 250, 845], radius=8, fill=(26,26,46))
d.text((95, 812), "Save changes", font=fnt(FONT_BOLD, 20), fill=(255,255,255))

# Step 2 label
d.ellipse([930, 490, 990, 550], fill=(74,144,217))
d.text((949, 500), "2", font=fnt(FONT_BOLD, 38), fill=(255,255,255))
d.text((1005, 505), "اختر الصورة", font=fnt(FONT_BOLD, 28), fill=(26,26,46))

# Step 3
d.ellipse([930, 600, 990, 660], fill=(15,155,88))
d.text((949, 610), "3", font=fnt(FONT_BOLD, 38), fill=(255,255,255))
d.text((1005, 615), "انسخ النص هنا", font=fnt(FONT_BOLD, 28), fill=(26,26,46))

# Step 4
d.ellipse([930, 700, 990, 760], fill=(255,107,53))
d.text((949, 710), "4", font=fnt(FONT_BOLD, 38), fill=(255,255,255))
d.text((1005, 715), 'اضغط "Save"', font=fnt(FONT_BOLD, 28), fill=(26,26,46))

# Arrows for steps 2,3,4
def arrow(x1,y1,x2,y2,color):
    d.line([(x1,y1),(x2,y2)], fill=color, width=4)
    # arrowhead
    angle = math.atan2(y2-y1, x2-x1)
    size  = 15
    for da in [0.5, -0.5]:
        ax = x2 - size*math.cos(angle-da)
        ay = y2 - size*math.sin(angle-da)
        d.line([(x2,y2),(int(ax),int(ay))], fill=color, width=4)

arrow(930, 520, 210, 580,  (74,144,217))    # step 2 → thumbnail
arrow(930, 630, 880, 730,  (15,155,88))     # step 3 → alt text field
arrow(930, 730, 255, 822,  (255,107,53))    # step 4 → save button

# ── Side panel — copy text ─────────────────────────
d.rectangle([1000, 80, 1580, 960], fill=(26,26,46), outline=(60,60,90), width=2)
d.rectangle([1000, 80, 1580, 120], fill=(233,69,96))
d.text((1150, 88), "نص جاهز للنسخ", font=fnt(FONT_BOLD, 26), fill=(255,255,255))

alts = [
    ("01", (233,69,96),
     "Restaurant and cafe manager\nGoogle Sheets template with\ndashboard inventory and\nsales automation spreadsheet"),
    ("02", (74,144,217),
     "What is included: dashboard,\ninventory tracker, daily sales,\nstaff schedule and automated\nprofit loss reports"),
    ("03", (15,155,88),
     "How to use the restaurant\ntemplate in 3 steps: download,\nopen in Google Sheets,\nfill and auto-calculate"),
    ("04", (255,107,53),
     "Restaurant cafe business\nfeatures: saves 5 hours weekly,\nworks on mobile, no\nsubscription needed"),
    ("05", (120,80,200),
     "Restaurant template 5 stars,\none time purchase 27 dollars,\ninstant download xlsx file\nand PDF user guide"),
]

for i, (num, color, text) in enumerate(alts):
    y = 135 + i * 163
    d.rectangle([1010, y, 1570, y+150], fill=(35,35,60), outline=color, width=2)

    # Number badge
    d.ellipse([1018, y+8, 1058, y+48], fill=color)
    d.text((1027, y+14), num, font=fnt(FONT_BOLD, 22), fill=(255,255,255))

    # Text
    for li, line in enumerate(text.split("\n")):
        d.text((1070, y+12+li*32), line, font=fnt(FONT_REG, 18), fill=(200,200,220))

# Bottom note
d.rectangle([0, 940, W, H], fill=(26,26,46))
d.text((W//2-380, 955),
       "كرر نفس العملية لكل صورة من الصور الـ 5 — ثم احفظ",
       font=fnt(FONT_BOLD, 24), fill=(255,215,0))

img.save("/home/user/smc-bot/etsy_alttext_guide.jpg", quality=95)
print("✅ Guide image saved")
