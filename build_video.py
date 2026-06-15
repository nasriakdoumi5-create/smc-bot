"""
Build a 60-second animated product demo video for Etsy listing
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def fnt(p, s):
    try:    return ImageFont.truetype(p, s)
    except: return ImageFont.load_default()

W, H   = 1280, 720
FPS    = 24
OUT    = "/home/user/smc-bot/product_demo.mp4"

# Colors
DARK    = (26,  26,  46)
PRIMARY = (22,  33,  62)
ACCENT  = (233, 69,  96)
GREEN   = (15,  155, 88)
YELLOW  = (255, 215, 0)
BLUE    = (74,  144, 217)
ORANGE  = (255, 107, 53)
WHITE   = (255, 255, 255)
GRAY    = (150, 150, 150)

def pil_to_cv(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def make_frame(bg=DARK):
    img = Image.new("RGB", (W, H), bg)
    d   = ImageDraw.Draw(img)
    return img, d

def gradient(img, top, bot):
    d = ImageDraw.Draw(img)
    for y in range(H):
        r = int(top[0]+(bot[0]-top[0])*y/H)
        g = int(top[1]+(bot[1]-top[1])*y/H)
        b = int(top[2]+(bot[2]-top[2])*y/H)
        d.line([(0,y),(W,y)], fill=(r,g,b))
    return img, ImageDraw.Draw(img)

def tc(d, text, y, f, color=WHITE, x=W//2):
    bb = d.textbbox((0,0), text, font=f)
    w  = bb[2]-bb[0]
    d.text((x-w//2, y), text, font=f, fill=color)

def rect(d, x0,y0,x1,y1, fill, radius=0):
    if radius: d.rounded_rectangle([x0,y0,x1,y1], radius=radius, fill=fill)
    else:       d.rectangle([x0,y0,x1,y1], fill=fill)

writer = cv2.VideoWriter(OUT, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (W,H))

def write_frames(frames_list):
    for frame in frames_list:
        writer.write(pil_to_cv(frame))

def lerp(a, b, t):
    return int(a + (b-a)*t)

# ══════════════════════════════════════════════════════
# SCENE 1 — Intro (0-3s = 72 frames)
# ══════════════════════════════════════════════════════
print("Scene 1: Intro...")
for i in range(72):
    t = i/71
    img, d = make_frame(DARK)
    gradient(img, DARK, (10,20,50))

    # Animated accent bar
    bar_w = int(W * t)
    d.rectangle([0,0,bar_w,8], fill=ACCENT)

    # Icon fade in
    alpha = min(1.0, t*2)
    icon_y = int(150 + (1-t)*50)
    tc(d, "🍽️", icon_y, fnt(FONT_REG,100), WHITE)

    # Title slide in
    title_x = int(W//2 + (1-t)*300)
    bb = d.textbbox((0,0), "RESTAURANT & CAFE MANAGER", font=fnt(FONT_BOLD,52))
    w = bb[2]-bb[0]
    d.text((title_x-w//2, 290), "RESTAURANT & CAFE MANAGER",
           font=fnt(FONT_BOLD,52), fill=WHITE)

    sub_alpha = max(0, t-0.5)*2
    d.text((W//2-280, 370), "Smart Business Automation Template",
           font=fnt(FONT_REG,28), fill=tuple(int(c*sub_alpha) for c in GRAY))

    write_frames([img]*1)

# ══════════════════════════════════════════════════════
# SCENE 2 — Problem (3-8s = 120 frames)
# ══════════════════════════════════════════════════════
print("Scene 2: Problem...")
for i in range(120):
    t = i/119
    img, d = make_frame()
    gradient(img, (40,10,10), DARK)

    d.rectangle([0,0,W,8], fill=ACCENT)
    tc(d, "😓  The Problem", 60, fnt(FONT_BOLD,48), ACCENT)

    problems = [
        "❌  Tracking sales on paper — hours wasted",
        "❌  No idea which items are running low",
        "❌  Staff schedules are a mess",
        "❌  No clear profit & loss picture",
    ]
    for pi, prob in enumerate(problems):
        delay = pi * 0.25
        alpha = max(0, min(1, (t-delay)*4))
        py = 200 + pi*110
        rect(d, 80, py, W-80, py+85, tuple(int(c*alpha) for c in (40,15,15)), radius=12)
        d.text((110, py+22), prob, font=fnt(FONT_BOLD,26),
               fill=tuple(int(c*alpha) for c in WHITE))

    write_frames([img]*1)

# ══════════════════════════════════════════════════════
# SCENE 3 — Solution reveal (8-11s = 72 frames)
# ══════════════════════════════════════════════════════
print("Scene 3: Solution...")
for i in range(72):
    t = i/71
    img, d = make_frame(DARK)
    gradient(img, DARK, (10,30,15))

    d.rectangle([0,0,W,8], fill=GREEN)

    # Big checkmark
    check_size = int(80 + t*40)
    cx = W//2
    d.ellipse([cx-check_size,200-check_size,cx+check_size,200+check_size],
              fill=GREEN)
    tc(d, "✓", 155, fnt(FONT_BOLD,check_size), WHITE)

    tc(d, "MEET YOUR SOLUTION", 310, fnt(FONT_BOLD,52), WHITE)
    if t > 0.5:
        alpha = (t-0.5)*2
        tc(d, "Restaurant & Cafe Manager Template",
           390, fnt(FONT_REG,30), tuple(int(c*alpha) for c in YELLOW))

    write_frames([img]*1)

# ══════════════════════════════════════════════════════
# SCENE 4 — Dashboard demo (11-20s = 216 frames)
# ══════════════════════════════════════════════════════
print("Scene 4: Dashboard...")
for i in range(216):
    t  = i/215
    img, d = make_frame(PRIMARY)

    # Browser mockup
    rect(d, 40,30, W-40, H-30, (18,28,55), radius=16)
    rect(d, 40,30, W-40,75,    DARK,       radius=16)
    d.text((60,42), "📊  Dashboard — Restaurant & Cafe Manager",
           font=fnt(FONT_BOLD,20), fill=YELLOW)

    # KPI Cards animate in
    cards = [
        ("💰", "TODAY'S SALES", f"${int(1250*min(1,t*3)):,}", GREEN),
        ("📦", "LOW STOCK",     f"{int(3*min(1,t*3))} Items",  ACCENT),
        ("👥", "STAFF TODAY",   f"{int(8*min(1,t*3))} People",  BLUE),
    ]
    for ci,(icon,title,val,color) in enumerate(cards):
        cx = 120 + ci*380
        rect(d, cx,95, cx+340,230, color, radius=14)
        d.text((cx+15,108), icon,  font=fnt(FONT_REG,40),  fill=WHITE)
        d.text((cx+15,158), title, font=fnt(FONT_BOLD,18), fill=WHITE)
        d.text((cx+15,185), val,   font=fnt(FONT_BOLD,30), fill=WHITE)

    # Weekly table
    rect(d, 40,245, W-40,265, DARK, radius=4)
    d.text((60,248), "WEEKLY SUMMARY", font=fnt(FONT_BOLD,16), fill=YELLOW)

    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    sales= [1200, 980, 1450, 1100, 1680, 2100, 890]
    for di,(day,sale) in enumerate(zip(days,sales)):
        dx = 60 + di*170
        dy = 280
        rect(d, dx,dy, dx+155,dy+35, (22,33,62), radius=6)
        d.text((dx+8,dy+8),  day,  font=fnt(FONT_BOLD,15), fill=GRAY)
        # Animated bar
        bar_h = int(120 * (sale/2100) * min(1, t*2))
        rect(d, dx+8,dy+60+120-bar_h, dx+145,dy+180, GREEN, radius=4)
        if t > 0.3:
            d.text((dx+15,dy+50), f"${sale:,}", font=fnt(FONT_BOLD,13), fill=YELLOW)

    # Label
    if t > 0.7:
        rect(d, 40,H-80, W-40,H-35, ACCENT, radius=10)
        tc(d, "✅  All data updates automatically — no formulas needed!",
           H-68, fnt(FONT_BOLD,22), WHITE)

    write_frames([img]*1)

# ══════════════════════════════════════════════════════
# SCENE 5 — Inventory demo (20-28s = 192 frames)
# ══════════════════════════════════════════════════════
print("Scene 5: Inventory...")
for i in range(192):
    t = i/191
    img, d = make_frame(PRIMARY)

    rect(d, 40,30, W-40,H-30, (18,28,55), radius=16)
    rect(d, 40,30, W-40,75,   DARK,       radius=16)
    d.text((60,42), "📦  Inventory Tracker",
           font=fnt(FONT_BOLD,22), fill=YELLOW)

    headers = ["Item","Category","Stock","Min","Status","Value"]
    hx = [65,250,440,560,660,820]
    for hi,h in enumerate(headers):
        d.text((hx[hi],90), h, font=fnt(FONT_BOLD,18), fill=BLUE)

    items = [
        ("Coffee Beans","Beverage","50","10","✅ OK",  "$125",GREEN),
        ("Milk",        "Beverage","30","10","✅ OK",  "$45", GREEN),
        ("Sugar",       "Dry Good","4", "5", "⚠️ LOW","$8",  ACCENT),
        ("Olive Oil",   "Condiment","2","2", "⚠️ LOW","$18", ACCENT),
        ("Flour",       "Dry Good","15","5", "✅ OK",  "$22", GREEN),
        ("Chicken",     "Protein", "8", "3", "✅ OK",  "$64", GREEN),
    ]

    for ri,row in enumerate(items):
        if ri/len(items) > t: break
        ry = 125 + ri*72
        bg = (22,33,62) if ri%2==0 else (26,38,72)
        rect(d, 50,ry, W-50,ry+62, bg, radius=8)

        # Typing animation for stock
        name,cat,stock,mn,status,val,color = row
        stock_show = stock[:max(1,int(len(stock)*(t*6-ri)))]

        d.text((hx[0],ry+18), name,        font=fnt(FONT_BOLD,17), fill=WHITE)
        d.text((hx[1],ry+18), cat,         font=fnt(FONT_REG,16),  fill=GRAY)

        # Yellow input cell
        rect(d, hx[2]-4,ry+10, hx[2]+70,ry+50, (255,215,0), radius=6)
        d.text((hx[2]+4,ry+18), stock_show, font=fnt(FONT_BOLD,18), fill=DARK)

        d.text((hx[3],ry+18), mn,     font=fnt(FONT_REG,16),  fill=GRAY)
        d.text((hx[4],ry+18), status, font=fnt(FONT_BOLD,18), fill=color)
        d.text((hx[5],ry+18), val,    font=fnt(FONT_BOLD,18), fill=GREEN)

    if t > 0.8:
        rect(d, 40,H-75, W-40,H-30, GREEN, radius=10)
        tc(d, "⚠️  Low stock items appear automatically — never run out again!",
           H-63, fnt(FONT_BOLD,20), WHITE)

    write_frames([img]*1)

# ══════════════════════════════════════════════════════
# SCENE 6 — Features grid (28-38s = 240 frames)
# ══════════════════════════════════════════════════════
print("Scene 6: Features...")
for i in range(240):
    t = i/239
    img, d = make_frame(DARK)
    gradient(img, DARK, (8,18,40))

    d.rectangle([0,0,W,8], fill=BLUE)
    tc(d, "EVERYTHING YOU NEED", 30, fnt(FONT_BOLD,44), WHITE)
    tc(d, "in one file", 85, fnt(FONT_REG,26), GRAY)

    feats = [
        ("📊","Dashboard",    GREEN,  "Real-time KPIs"),
        ("📦","Inventory",    BLUE,   "50+ items tracked"),
        ("📈","Daily Sales",  ORANGE, "Auto daily total"),
        ("👥","Staff",        ACCENT, "Weekly schedule"),
        ("📋","Reports",      (120,80,200), "Auto P&L"),
        ("⚡","Automation",   YELLOW, "Zero manual work"),
    ]

    for fi,(icon,title,color,sub) in enumerate(feats):
        if fi/len(feats) > min(1,t*1.5): continue
        col = fi%3
        row = fi//3
        fx = 60 + col*415
        fy = 140 + row*230

        ft = max(0,min(1,(t*len(feats)-fi)*1.5))
        box_y = int(fy + (1-ft)*50)

        rect(d, fx,box_y, fx+390,box_y+200, (18,28,55), radius=16)
        rect(d, fx,box_y, fx+390,box_y+8,   color,      radius=8)

        d.ellipse([fx+15,box_y+20,fx+85,box_y+90], fill=color)
        tc(d, icon, box_y+28, fnt(FONT_REG,48), WHITE, fx+50)
        d.text((fx+100,box_y+28), title, font=fnt(FONT_BOLD,28), fill=WHITE)
        d.text((fx+100,box_y+70), sub,   font=fnt(FONT_REG,20),  fill=GRAY)

    write_frames([img]*1)

# ══════════════════════════════════════════════════════
# SCENE 7 — How it works (38-46s = 192 frames)
# ══════════════════════════════════════════════════════
print("Scene 7: How it works...")
for i in range(192):
    t = i/191
    img, d = make_frame(DARK)
    gradient(img, (8,18,40), DARK)

    d.rectangle([0,0,W,8], fill=GREEN)
    tc(d, "HOW IT WORKS", 30, fnt(FONT_BOLD,48), WHITE)
    tc(d, "3 simple steps", 88, fnt(FONT_REG,26), GRAY)

    steps = [
        (GREEN,  "1","DOWNLOAD","Purchase → instant .xlsx download"),
        (BLUE,   "2","OPEN",    "Upload to Google Sheets or Excel"),
        (ORANGE, "3","USE",     "Fill yellow cells → auto-calculates"),
    ]

    for si,(color,num,title,desc) in enumerate(steps):
        delay = si*0.3
        ft = max(0, min(1,(t-delay)*3))
        sx = int(60 + (1-ft)*100)
        sy = 150 + si*165

        rect(d, sx,sy, sx+80,sy+130, color, radius=14)
        tc(d, num, sy+20, fnt(FONT_BOLD,80), WHITE, sx+40)

        rect(d, sx+95,sy, W-60,sy+130, (18,28,55), radius=14)
        d.text((sx+115,sy+18), title, font=fnt(FONT_BOLD,34), fill=color)
        d.text((sx+115,sy+70), desc,  font=fnt(FONT_REG,24),  fill=WHITE)

    write_frames([img]*1)

# ══════════════════════════════════════════════════════
# SCENE 8 — Price CTA (46-60s = 336 frames)
# ══════════════════════════════════════════════════════
print("Scene 8: CTA...")
for i in range(336):
    t = i/335
    img, d = make_frame(DARK)
    gradient(img, (5,15,35), DARK)

    d.rectangle([0,0,W,8], fill=YELLOW)

    # Stars
    for si in range(5):
        star_t = max(0, min(1,(t-si*0.08)*5))
        d.text((W//2-100+si*48, 40), "★",
               font=fnt(FONT_REG,44),
               fill=tuple(int(c*star_t) for c in YELLOW))

    tc(d, "GET IT TODAY", 110, fnt(FONT_BOLD,64), WHITE)
    tc(d, "One-time purchase — use forever", 188, fnt(FONT_REG,28), GRAY)

    # Price box pulse
    pulse = 0.97 + 0.03*np.sin(t*10)
    pw = int(380*pulse)
    ph = int(160*pulse)
    px = W//2-pw//2
    py = 240

    rect(d, px,py, px+pw,py+ph, PRIMARY, radius=20)
    rect(d, px,py, px+pw,py+8,  ACCENT,  radius=10)
    tc(d, "$27", py+30, fnt(FONT_BOLD,80), YELLOW)
    tc(d, "One-Time  •  No Subscription", py+120, fnt(FONT_REG,22), WHITE)

    # Checkmarks
    checks = ["✓ Instant Download","✓ Google Sheets & Excel","✓ PDF Guide Included","✓ 30-Day Free Support"]
    for ci,ch in enumerate(checks):
        cx2 = 120 + (ci%2)*600
        cy2 = 430 + (ci//2)*55
        ft  = max(0,min(1,(t-0.4-ci*0.1)*3))
        d.text((cx2,cy2), ch, font=fnt(FONT_BOLD,24),
               fill=tuple(int(c*ft) for c in GREEN))

    # Bottom bar
    rect(d, 0,H-55, W,H, ACCENT)
    tc(d, "nasritools.etsy.com  •  Search: Restaurant Manager Template",
       H-42, fnt(FONT_BOLD,22), WHITE)

    write_frames([img]*1)

writer.release()
print(f"✅ Video created: {OUT}")
size = os.path.getsize(OUT)
print(f"📦 Size: {size/1024/1024:.1f} MB  |  Duration: ~60s")
