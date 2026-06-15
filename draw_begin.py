from PIL import Image, ImageDraw, ImageFont
import math

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def fnt(p,s):
    try: return ImageFont.truetype(p,s)
    except: return ImageFont.load_default()

W,H = 800, 500
img = Image.new("RGB",(W,H),(18,24,58))
d   = ImageDraw.Draw(img)

# Background shapes (like Etsy page)
d.polygon([(0,80),(220,80),(180,380),(0,380)], fill=(230,165,0))
d.polygon([(600,0),(800,0),(800,220),(700,180)], fill=(200,80,40))
d.ellipse([(620,350),(800,500)], fill=(220,100,50))

# Main text
d.text((W//2-340, 160), "There are millions of buyers", font=fnt(FONT_REG,32), fill=(255,255,255))
d.text((W//2-310, 205), "eager to see what you'll put", font=fnt(FONT_REG,32), fill=(255,255,255))
d.text((W//2-100, 250), "up for sale.", font=fnt(FONT_REG,32), fill=(255,255,255))

# Begin button
bx,by = W//2-70, 315
d.rounded_rectangle([bx,by,bx+140,by+52], radius=26, fill=(255,255,255))
d.text((bx+32,by+12), "Begin", font=fnt(FONT_BOLD,26), fill=(30,30,30))

# ── RED ANNOTATION ────────────────────────────────
cx,cy = bx+70, by+26

# Pulsing rings
for r in [75,62,50]:
    d.ellipse([cx-r,cy-r,cx+r,cy+r], outline=(220,0,0), width=3)

# Arrow from bottom-right
def arrow(x1,y1,x2,y2):
    d.line([(x1,y1),(x2,y2)], fill=(220,0,0), width=5)
    ang = math.atan2(y2-y1,x2-x1)
    for da in [0.45,-0.45]:
        ax = x2-20*math.cos(ang-da)
        ay = y2-20*math.sin(ang-da)
        d.line([(x2,y2),(int(ax),int(ay))], fill=(220,0,0), width=5)

arrow(680,420, cx+40, cy+40)

# Label
d.rounded_rectangle([480,420,790,475], radius=10, fill=(220,0,0))
d.text((498,430), "اضغط هنا ← Begin", font=fnt(FONT_BOLD,28), fill=(255,255,255))

img.save("/home/user/smc-bot/click_begin.jpg", quality=96)
print("✅ done")
