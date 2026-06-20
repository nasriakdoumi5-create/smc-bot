"""
NasriTools - Shop Banner Generator
Output: banner.jpg (3360x840)
Upload manually: Etsy → Shop Manager → Sales Channels → Edit shop → Banner
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 3360, 840

_BOLD = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
    "C:/Windows/Fonts/verdanab.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
_REG = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/verdana.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def _f(p, s):
    for path in p:
        if Path(path).exists():
            return ImageFont.truetype(path, s)
    return ImageFont.load_default()

def fb(s): return _f(_BOLD, s)
def fr(s): return _f(_REG, s)

def mix(c1, c2, t):
    return tuple(int(c1[i]*(1-t) + c2[i]*t) for i in range(3))

def tw(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]

def pill(draw, x0, y0, x1, y1, fill, r=None):
    r = r or (y1-y0)//2
    r = min(r, (x1-x0)//2, (y1-y0)//2)
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx, cy in [(x0,y0),(x1-2*r,y0),(x0,y1-2*r),(x1-2*r,y1-2*r)]:
        draw.ellipse([cx,cy,cx+2*r,cy+2*r], fill=fill)

# ── Canvas & gradient ─────────────────────────────────────────────────────────
C_LEFT  = (8, 22, 52)     # dark navy
C_RIGHT = (10, 52, 72)    # dark teal
img  = Image.new("RGB", (W, H), C_LEFT)
draw = ImageDraw.Draw(img)

for x in range(W):
    col = mix(C_LEFT, C_RIGHT, x / W)
    draw.line([(x, 0), (x, H)], fill=col)

# Top accent stripe
ACCENT = (30, 145, 220)
draw.rectangle([0, 0, W, 10], fill=ACCENT)

# Subtle diagonal overlay (top-right corner darkening)
for i in range(400):
    t = i / 400
    col = mix(C_RIGHT, (4, 12, 30), t * 0.5)
    draw.line([(W - i * 3, 0), (W, i * 2)], fill=col)

# ── LEFT SIDE — Brand & messaging ────────────────────────────────────────────
PAD = 160

# Brand name
draw.text((PAD, 80), "NASRI", font=fb(200), fill=(255, 255, 255))
TW_NASRI = tw(draw, "NASRI", fb(200))
draw.text((PAD + TW_NASRI + 14, 80), "TOOLS", font=fb(200), fill=ACCENT)

# Accent line below brand
LINE_Y = 330
draw.rectangle([PAD, LINE_Y, PAD + 700, LINE_Y + 6], fill=ACCENT)

# Tagline
draw.text((PAD, LINE_Y + 28),
          "Premium Google Sheets Templates",
          font=fb(66), fill=(220, 235, 255))
draw.text((PAD, LINE_Y + 112),
          "Finance  ·  Health  ·  Business  ·  Life",
          font=fr(50), fill=(150, 185, 230))

# USPs row
USPS = ["✓  Instant Download", "✓  Works on Any Device", "✓  Lifetime Access"]
bx = PAD
by = 570
for i, u in enumerate(USPS):
    f = fr(44)
    col = (120, 200, 255) if i == 0 else (170, 210, 245)
    draw.text((bx, by), u, font=f, fill=col)
    bx += tw(draw, u, f) + 70

# Website
draw.text((PAD, 668), "nasritools.etsy.com", font=fr(38), fill=(80, 130, 180))

# ── RIGHT SIDE — Category tiles ───────────────────────────────────────────────
TILES = [
    {"label": "FINANCE",      "sub": "Budget · Invoice · Goals", "color": (20, 115, 60)},
    {"label": "HEALTH",       "sub": "Workout · Meals · Habits", "color": (192, 57, 43)},
    {"label": "BUSINESS",     "sub": "Content · Clients · Growth","color": (230, 126, 34)},
    {"label": "PRODUCTIVITY", "sub": "Weekly · Goals · Student",  "color": (108, 52, 131)},
    {"label": "BUNDLES",      "sub": "Save up to 65%",            "color": (28, 138, 102)},
    {"label": "100+",         "sub": "Templates Available",       "color": (52, 120, 210)},
]

TX0   = 1850   # left edge of tile area
TW    = 450    # tile width
TH    = 310    # tile height
TGAP  = 26     # gap between tiles
TROWS = 2

for i, tile in enumerate(TILES):
    col_i = i % 3
    row_i = i // 3
    tx = TX0 + col_i * (TW + TGAP)
    ty = 60 + row_i * (TH + TGAP)

    # tile background
    dark = tuple(max(0, int(c * 0.75)) for c in tile["color"])
    draw.rectangle([tx, ty, tx+TW, ty+TH], fill=tile["color"])
    # diagonal accent
    draw.polygon([(tx+TW-120, ty), (tx+TW, ty), (tx+TW, ty+120)], fill=dark)
    # top accent bar
    draw.rectangle([tx, ty, tx+TW, ty+7], fill=tuple(min(255, int(c*1.3)) for c in tile["color"]))

    # label
    lf = fb(52)
    draw.text((tx+22, ty+20), tile["label"], font=lf, fill=(255, 255, 255))
    # subtitle
    sf = fr(32)
    draw.text((tx+22, ty+TH-60), tile["sub"], font=sf,
              fill=tuple(min(255, int(c*1.6)) for c in tile["color"]))

# ── Save ──────────────────────────────────────────────────────────────────────
out = Path("banner.jpg")
img.save(str(out), format="JPEG", quality=97)
print(f"\nSaved: {out.resolve()}")
print("\nTo upload:")
print("  Etsy → Shop Manager → Sales Channels → Edit shop → Banner")
print("  Select banner.jpg → Save")
