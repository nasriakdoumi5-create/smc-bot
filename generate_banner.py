"""
generate_banner.py
Creates nasritools-banner.png (3360x840) — Etsy Big Banner
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 3360, 840
OUT  = "nasritools-banner.png"

ORANGE = (249, 115, 22)
CREAM  = (255, 250, 247)
BLACK  = (17, 17, 17)
GREY   = (192, 184, 176)
WHITE  = (255, 255, 255)
GREEN  = (34, 197, 94)
BLUE   = (59, 130, 246)
BORDER = (236, 234, 230)

BOLD   = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
REG    = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"

def rounded_rect(draw, x, y, w, h, r, fill):
    draw.rectangle([x+r, y, x+w-r, y+h], fill=fill)
    draw.rectangle([x, y+r, x+w, y+h-r], fill=fill)
    draw.ellipse([x, y, x+2*r, y+2*r], fill=fill)
    draw.ellipse([x+w-2*r, y, x+w, y+2*r], fill=fill)
    draw.ellipse([x, y+h-2*r, x+2*r, y+h], fill=fill)
    draw.ellipse([x+w-2*r, y+h-2*r, x+w, y+h], fill=fill)

def draw_mark(draw, cx, cy, S):
    r = int(S * 0.18)
    rounded_rect(draw, cx-S//2, cy-S//2, S, S, r, ORANGE)
    cols, rows = 3, 2
    pad = int(S * 0.15)
    gap = int(S * 0.05)
    cW = (S - pad*2 - gap*(cols-1)) // cols
    cH = (S - pad*2 - gap*(rows-1)) // rows
    cr = max(2, int(S * 0.035))
    for row in range(rows):
        for col in range(cols):
            px = cx - S//2 + pad + col*(cW+gap)
            py = cy - S//2 + pad + row*(cH+gap)
            color = WHITE if (row==0 and col==0) else (0, 0, 0, 55)
            fill = WHITE if (row==0 and col==0) else (0,0,0,56)
            # use alpha for dark cells
            if row==0 and col==0:
                rounded_rect(draw, px, py, cW, cH, cr, WHITE)
            else:
                rounded_rect(draw, px, py, cW, cH, cr, (30, 20, 10))

img  = Image.new("RGB", (W, H), CREAM)
draw = ImageDraw.Draw(img)

# warm grid lines
for x in range(0, W, 60):
    draw.line([(x,0),(x,H)], fill=(249,115,22,15), width=1)
for y in range(0, H, 60):
    draw.line([(0,y),(W,y)], fill=(249,115,22,15), width=1)

# actually draw grid with a slightly visible color
for x in range(0, W, 60):
    draw.line([(x,0),(x,H)], fill=(240,230,220), width=1)
for y in range(0, H, 60):
    draw.line([(0,y),(W,y)], fill=(240,230,220), width=1)

# top & bottom orange bars
draw.rectangle([0, 0, W, 12], fill=ORANGE)
draw.rectangle([0, H-12, W, H], fill=ORANGE)

# logo mark
MARK = 180
draw_mark(draw, 210, H//2, MARK)

# wordmark fonts
fn_xl  = ImageFont.truetype(BOLD, 155)
fn_tag = ImageFont.truetype(ITALIC, 52)
fn_sub = ImageFont.truetype(REG, 34)
fn_card= ImageFont.truetype(BOLD, 48)
fn_url = ImageFont.truetype(REG, 32)

# "Nasri" in black
tx, ty = 430, H//2 - 95
draw.text((tx, ty), "Nasri", font=fn_xl, fill=BLACK)
nw = fn_xl.getlength("Nasri")
# "Tools" in orange
draw.text((tx + nw, ty), "Tools", font=fn_xl, fill=ORANGE)

# tagline
draw.text((tx+2, ty+162), '"Good tools don\'t expire."', font=fn_tag, fill=GREY)

# right cards
cards = [
    ("116 Templates",    ORANGE),
    ("No Subscription",  GREEN),
    ("from €1.21",       BLUE),
]
cx2 = W - 780
sy  = H//2 - 115

for i, (label, color) in enumerate(cards):
    cy2 = sy + i * 116
    cw2, ch2 = 660, 90
    # white card with light shadow
    shadow_img = Image.new("RGBA", (cw2+10, ch2+10), (0,0,0,0))
    sd = ImageDraw.Draw(shadow_img)
    rounded_rect(sd, 4, 4, cw2, ch2, 18, (0,0,0,30))
    img.paste(Image.new("RGB",(cw2,ch2), WHITE), (cx2, cy2),
              mask=shadow_img.split()[3].crop((0,0,cw2,ch2)))

    rounded_rect(draw, cx2, cy2, cw2, ch2, 18, WHITE)
    # color bar
    rounded_rect(draw, cx2, cy2, 10, ch2, 4, color)
    # label
    draw.text((cx2+32, cy2+22), label, font=fn_card, fill=BLACK)

# url bottom right
draw.text((cx2, H-22), "nasritools.etsy.com", font=fn_url, fill=(200,195,190), anchor="lb")

img.save(OUT, "PNG", optimize=True)
print(f"Saved: {OUT}  ({W}×{H})")
