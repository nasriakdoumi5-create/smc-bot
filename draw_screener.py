from PIL import Image, ImageDraw, ImageFont
import math

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def fnt(p,s):
    try: return ImageFont.truetype(p,s)
    except: return ImageFont.load_default()

W,H = 760, 500
img = Image.new("RGB",(W,H),(250,248,244))
d   = ImageDraw.Draw(img)

# ── Page title ────────────────────────────────────
d.text((20,20), "What brings you to Etsy?", font=fnt(FONT_BOLD,30), fill=(30,30,30))
d.text((20,62), "We'll guide you to make your store run smoothly.", font=fnt(FONT_REG,16), fill=(100,100,100))

# ── 4 options ─────────────────────────────────────
options = [
    "I'd like to sell on Etsy, but I don't know what yet.",
    "I have items that I design, make, or collect,\nand I want to sell them for the first time.",
    "I currently sell my items elsewhere and would\nlike to sell them on Etsy as well.",
    "I already have an Etsy shop and I want to\nopen another one.",
]

for i, opt in enumerate(options):
    y = 105 + i*88
    is_target = (i == 1)

    # highlight row
    if is_target:
        d.rounded_rectangle([10,y-8,W-10,y+72], radius=10,
                            fill=(255,245,245), outline=(220,0,0), width=3)

    # radio button
    rx,ry = 30, y+18
    d.ellipse([rx,ry,rx+22,ry+22],
              fill=(220,0,0) if is_target else (255,255,255),
              outline=(220,0,0) if is_target else (150,150,150), width=2)
    if is_target:
        d.ellipse([rx+6,ry+6,rx+16,ry+16], fill=(255,255,255))

    # text
    color = (30,30,30)
    for li,line in enumerate(opt.split("\n")):
        d.text((65, y+10+li*26), line,
               font=fnt(FONT_BOLD if is_target else FONT_REG, 17), fill=color)

# ── RED ARROW + LABEL ─────────────────────────────
def arrow(x1,y1,x2,y2):
    d.line([(x1,y1),(x2,y2)], fill=(220,0,0), width=5)
    ang = math.atan2(y2-y1,x2-x1)
    for da in [0.45,-0.45]:
        ax = x2-18*math.cos(ang-da)
        ay = y2-18*math.sin(ang-da)
        d.line([(x2,y2),(int(ax),int(ay))], fill=(220,0,0), width=5)

arrow(680,193, 60,200)

d.rounded_rectangle([480,160,750,215], radius=8, fill=(220,0,0))
d.text((496,168), "اختر هذا الخيار", font=fnt(FONT_BOLD,26), fill=(255,255,255))

# ── Following button ──────────────────────────────
d.rounded_rectangle([580,435,740,472], radius=24, fill=(30,30,30))
d.text((608,443), "Following", font=fnt(FONT_BOLD,20), fill=(255,255,255))

# Bottom note
d.rounded_rectangle([10,440,460,480], radius=8, fill=(255,215,0))
d.text((22,450), 'بعد الاختيار اضغط "Following"', font=fnt(FONT_BOLD,22), fill=(30,30,30))

img.save("/home/user/smc-bot/click_option2.jpg", quality=96)
print("✅ done")
