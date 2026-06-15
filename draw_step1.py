from PIL import Image, ImageDraw, ImageFont
import math

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def fnt(p,s):
    try: return ImageFont.truetype(p,s)
    except: return ImageFont.load_default()

W,H = 520, 440
img = Image.new("RGB",(W,H),(255,255,255))
d   = ImageDraw.Draw(img)

# ── Dropdown menu (exact copy of screenshot) ──────
d.rectangle([0,0,W,H], fill=(255,255,255), outline=(200,200,200), width=1)

# Header — user info
d.rectangle([0,0,W,58], fill=(250,250,250))
d.ellipse([14,10,52,48], fill=(242,84,91))
d.text((18,20), "N", font=fnt(FONT_BOLD,24), fill=(255,255,255))
d.text((62,12), "Nasri Akdoumi", font=fnt(FONT_BOLD,18), fill=(30,30,30))
d.text((62,36), "View your profile", font=fnt(FONT_REG,14), fill=(100,100,100))
d.line([(0,58),(W,58)], fill=(230,230,230), width=1)

# Menu items
items = [
    ("🛍️", "Purchases and reviews", False),
    ("💬", "Messages",              False),
    ("💳", "Balance: € 0.00",       False),
    ("🎁", "Special offers",         False),
    ("📋", "Etsy gift lists",        False),
    ("🏪", "Sell on Etsy",           True ),   # ← TARGET
    ("❓", "Help Center",            False),
    ("⚙️", "Account settings",       False),
    ("🚪", "Go out",                 False),
]

for i,(icon,label,target) in enumerate(items):
    y = 65 + i*40
    bg = (255,245,245) if target else (255,255,255)
    d.rectangle([0,y,W,y+38], fill=bg)
    d.text((16,y+8), icon,  font=fnt(FONT_REG,18),  fill=(80,80,80))
    d.text((52,y+10), label, font=fnt(FONT_BOLD if target else FONT_REG, 17),
           fill=(220,50,50) if target else (50,50,50))
    d.line([(0,y+38),(W,y+38)], fill=(240,240,240), width=1)

# ── RED CIRCLE + ARROW on "Sell on Etsy" ──────────
ty = 65 + 5*40  # row index 5
cx, cy = W//2, ty+19

# Pulsing rings
for r,a in [(70,40),(58,80),(46,140)]:
    d.ellipse([cx-r,cy-r,cx+r,cy+r], outline=(220,0,0,a), width=2)

# Bold red rectangle highlight
d.rectangle([4, ty+2, W-4, ty+36], outline=(220,0,0), width=4)

# Arrow from right pointing to the item
for i in range(6):
    ax = W-20 - i*2
    d.ellipse([ax,cy-3,ax+4,cy+3], fill=(220,0,0))

# Arrowhead
d.polygon([(W-8,cy),(W-26,cy-12),(W-26,cy+12)], fill=(220,0,0))

# ── Label box ─────────────────────────────────────
d.rounded_rectangle([10,390,510,430], radius=8, fill=(220,0,0))
d.text((30,398), "اضغط هنا  ←  Sell on Etsy", font=fnt(FONT_BOLD,24), fill=(255,255,255))

img.save("/home/user/smc-bot/click_sell_on_etsy.jpg", quality=96)
print("✅ done")
