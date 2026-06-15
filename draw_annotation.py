"""
Annotated mockup of the ACTUAL Etsy listing editor showing EXACTLY where to add alt text
"""
from PIL import Image, ImageDraw, ImageFont
import math

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def fnt(path, size):
    try:    return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

W, H = 1400, 900
img = Image.new("RGB", (W, H), (255, 255, 255))
d   = ImageDraw.Draw(img)

# ─── Browser chrome ───────────────────────────────
d.rectangle([0,0,W,36], fill=(240,240,240))
d.rectangle([0,36,W,38], fill=(200,200,200))
# URL bar
d.rounded_rectangle([300,6,1100,30], radius=4, fill=(255,255,255), outline=(200,200,200), width=1)
d.text((310,10), "etsy.com/your/listings/edit/123456789", font=fnt(FONT_REG,14), fill=(80,80,80))

# ─── Etsy top nav ─────────────────────────────────
d.rectangle([0,38,W,78], fill=(255,255,255))
d.rectangle([0,78,W,80], fill=(230,230,230))
d.text((20,50), "etsy", font=fnt(FONT_BOLD,28), fill=(242,84,91))
d.text((120,56), "Shop Manager", font=fnt(FONT_REG,18), fill=(100,100,100))

# ─── Left sidebar ─────────────────────────────────
d.rectangle([0,80,200,H], fill=(247,247,247))
d.rectangle([0,80,200,82], fill=(230,230,230))
items = [("Shop Manager",False),("Listings",True),("Orders",False),
         ("Stats",False),("Finances",False),("Marketing",False)]
for i,(label,active) in enumerate(items):
    y = 100+i*52
    if active:
        d.rectangle([0,y,200,y+40], fill=(255,241,241))
        d.rectangle([0,y,4,y+40], fill=(242,84,91))
    d.text((16,y+10), label, font=fnt(FONT_BOLD if active else FONT_REG,16),
           fill=(242,84,91) if active else (80,80,80))

# ─── Main content ─────────────────────────────────
d.rectangle([200,80,W,H], fill=(255,255,255))

# Page title
d.text((220,95), "Edit Listing", font=fnt(FONT_BOLD,24), fill=(30,30,30))

# ─── PHOTOS SECTION ───────────────────────────────
d.text((220,140), "Photos", font=fnt(FONT_BOLD,18), fill=(30,30,30))
d.text((220,168), "Add up to 10 photos", font=fnt(FONT_REG,14), fill=(120,120,120))

# Photo thumbnails
photo_colors = [(233,69,96),(74,144,217),(15,155,88),(255,107,53),(120,80,200)]
photo_labels = ["01_hero","02_incl","03_how","04_feat","05_cta"]

for i,(color,label) in enumerate(zip(photo_colors,photo_labels)):
    x = 220 + i*138
    # thumbnail box with hover overlay on FIRST image
    d.rectangle([x,190,x+125,300], fill=color)
    d.text((x+18,235), label, font=fnt(FONT_BOLD,14), fill=(255,255,255))

    if i == 0:
        # Hover overlay (semi-dark)
        overlay = Image.new("RGBA",(125,110),(0,0,0,160))
        img.paste(Image.new("RGB",(125,110),(20,20,20)), (x,190),
                  Image.new("L",(125,110), 130))
        # "Add alt text" button that appears on hover
        d.rounded_rectangle([x+8,245,x+117,268], radius=4, fill=(255,255,255))
        d.text((x+14,250), "Add alt text", font=fnt(FONT_BOLD,13), fill=(30,30,30))

# ─── Alt text dialog / field ──────────────────────
# Dialog box that opens when you click "Add alt text"
dx,dy = 220,320
d.rectangle([dx,dy,dx+600,dy+220], fill=(255,255,255),
            outline=(180,180,180), width=1)
d.rectangle([dx,dy,dx+600,dy+44], fill=(247,247,247), outline=(180,180,180), width=1)
d.text((dx+16,dy+12), "Alt text for this image", font=fnt(FONT_BOLD,17), fill=(30,30,30))
# X button
d.ellipse([dx+568,dy+8,dx+590,dy+30], fill=(220,220,220))
d.text((dx+573,dy+10), "x", font=fnt(FONT_BOLD,16), fill=(80,80,80))

d.text((dx+16,dy+56), "Describe this image for shoppers who use screen readers.",
       font=fnt(FONT_REG,13), fill=(100,100,100))

# Input field — THE KEY AREA
d.rectangle([dx+12,dy+84,dx+588,dy+140],
            fill=(255,255,255), outline=(242,84,91), width=3)
# Placeholder / example text
d.text((dx+18,dy+95),
       "Restaurant and cafe manager Google Sheets template with",
       font=fnt(FONT_REG,13), fill=(80,80,80))
d.text((dx+18,dy+113),
       "dashboard, inventory tracker, daily sales and reports",
       font=fnt(FONT_REG,13), fill=(80,80,80))
# cursor
d.line([(dx+440,dy+88),(dx+440,dy+130)], fill=(242,84,91), width=2)

d.text((dx+480,dy+148), "0/250", font=fnt(FONT_REG,12), fill=(150,150,150))

# Save button
d.rounded_rectangle([dx+480,dy+162,dx+588,dy+196], radius=6, fill=(242,84,91))
d.text((dx+505,dy+170), "Save", font=fnt(FONT_BOLD,17), fill=(255,255,255))
# Cancel
d.text((dx+400,dy+172), "Cancel", font=fnt(FONT_REG,16), fill=(100,100,100))

# ══ ANNOTATIONS ══════════════════════════════════

def draw_arrow(x1,y1,x2,y2,color=(255,0,0),w=4):
    d.line([(x1,y1),(x2,y2)], fill=color, width=w)
    angle = math.atan2(y2-y1,x2-x1)
    for da in [0.45,-0.45]:
        ax = x2-18*math.cos(angle-da)
        ay = y2-18*math.sin(angle-da)
        d.line([(x2,y2),(int(ax),int(ay))], fill=color, width=w)

def red_circle(x,y,r,label_text,label_x,label_y):
    d.ellipse([x-r,y-r,x+r,y+r], outline=(220,0,0), width=4)
    # pulse rings
    d.ellipse([x-r-8,y-r-8,x+r+8,y+r+8], outline=(255,80,80), width=2)
    d.text((label_x,label_y), label_text, font=fnt(FONT_BOLD,22), fill=(200,0,0))

# Step 1 — hover the first image
red_circle(283,245,45,"1",950,195)
draw_arrow(950+30,206,340,240,(220,0,0),4)
d.rounded_rectangle([940,185,1390,240], radius=6, fill=(255,240,240), outline=(220,0,0),width=2)
d.text((960,193), "اضغط على الصورة الأولى ← ستظهر", font=fnt(FONT_BOLD,18), fill=(180,0,0))
d.text((960,213), 'زر "Add alt text" تلقائياً', font=fnt(FONT_BOLD,18), fill=(180,0,0))

# Step 2 — the "Add alt text" button
red_circle(283,256,18,"",0,0)
d.rounded_rectangle([940,255,1390,300], radius=6, fill=(255,240,240), outline=(220,0,0),width=2)
d.text((960,258), '2  اضغط على "Add alt text"', font=fnt(FONT_BOLD,20), fill=(180,0,0))
draw_arrow(940,275,405,258,(220,0,0),4)

# Step 3 — the input field (THE MAIN POINT)
red_circle(400,365,55,"",0,0)
d.rounded_rectangle([940,330,1390,440], radius=6, fill=(255,240,240), outline=(220,0,0),width=2)
d.text((960,338), "3  هنا تكتب النص البديل", font=fnt(FONT_BOLD,22), fill=(180,0,0))
d.text((960,368), "انسخ النص من ملف", font=fnt(FONT_REG,18), fill=(120,0,0))
d.text((960,390), "Etsy_Listing.txt الذي أرسلته لك", font=fnt(FONT_REG,18), fill=(120,0,0))
d.text((960,412), "والصقه هنا مباشرة", font=fnt(FONT_REG,18), fill=(120,0,0))
draw_arrow(940,380,820,375,(220,0,0),4)

# Step 4 — Save button
red_circle(534,461+52,20,"",0,0)
d.rounded_rectangle([940,470,1390,520], radius=6, fill=(255,240,240), outline=(220,0,0),width=2)
d.text((960,480), '4  اضغط "Save" للحفظ', font=fnt(FONT_BOLD,20), fill=(180,0,0))
draw_arrow(940,492,595,495,(220,0,0),4)

# ─── Bottom bar ───────────────────────────────────
d.rectangle([0,845,W,H], fill=(26,26,46))
d.text((W//2-380,860),
       "كرر الخطوات 1→4 لكل صورة من الصور الخمس",
       font=fnt(FONT_BOLD,26), fill=(255,215,0))
d.text((W//2-280,893),
       "صورة 01 ← صورة 02 ← صورة 03 ← صورة 04 ← صورة 05",
       font=fnt(FONT_REG,20), fill=(200,200,200))

img.save("/home/user/smc-bot/etsy_where_to_type.jpg", quality=96)
print("✅ Done")
