"""
generate_mockups_v3.py

Three creative product images per hero listing:
  Image 3 — STATS HERO      : dark premium, 4 floating stat cards with charts
  Image 4 — TRANSFORMATION  : diagonal split before/after story
  Image 5 — FEATURE CARDS   : clean 2x2 feature highlight grid

Category-aware data per listing. Uploads at ranks 3, 4, 5.
"""
import json, os, glob, time, requests, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
OUT_DIR    = Path("thumbnails/mockups_v3")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SIZE = 2000

TARGET_KEYWORDS = [
    "budget tracker", "invoice tracker", "kpi dashboard",
    "workout tracker", "weekly planner",
]

CATEGORY_DATA = {
    "finance": {
        "accent": "#2563EB",
        "stats": [
            ("INCOME", "EUR 3,200", "Monthly Budget Tracked"),
            ("SAVED",  "EUR 1,305", "Saved This Month"),
            ("CATS",   "8 Types",   "Expense Categories"),
            ("SETUP",  "< 2 min",   "Time To Get Started"),
        ],
        "pct": 41, "bars": [3200, 3400, 3100, 3600],
        "before_title": "FINANCIAL CHAOS",
        "after_title":  "TOTAL CONTROL",
        "before_items": ["Guessing where money goes", "No savings plan at all", "Missing bill deadlines"],
        "after_items":  ["Track every single euro", "Save more consistently", "Never miss a payment"],
        "result_num": "EUR 1,305", "result_label": "SAVED LAST MONTH",
        "features": [
            ("$", "Monthly Budget Grid", "Income & expenses by category"),
            ("#", "Auto-Calculating",    "No manual math, ever"),
            ("+", "Savings Progress",    "Watch your balance grow"),
            ("*", "Works Everywhere",    "Phone, tablet & desktop"),
        ],
    },
    "invoice": {
        "accent": "#0EA5E9",
        "stats": [
            ("TOTAL",  "EUR 12,500", "Invoices Tracked"),
            ("PAID",   "89%",        "On-Time Payment Rate"),
            ("PEND",   "EUR 1,200",  "Pending Balance"),
            ("AUTO",   "Alerts",     "Payment Reminders"),
        ],
        "pct": 89, "bars": [8500, 11200, 9800, 12500],
        "before_title": "INVOICE CHAOS",
        "after_title":  "ALWAYS PAID",
        "before_items": ["Lost invoices & late fees", "No record of what's owed", "Chasing clients manually"],
        "after_items":  ["Every invoice tracked", "Paid vs pending at a glance", "Professional client records"],
        "result_num": "89%", "result_label": "PAID ON TIME",
        "features": [
            ("=", "Invoice Log",    "Track all sent invoices"),
            (">", "Payment Status", "Paid, pending, overdue"),
            ("@", "Client Tracker", "Per-client history"),
            ("%", "Tax Summary",    "Export-ready totals"),
        ],
    },
    "kpi": {
        "accent": "#0EA5E9",
        "stats": [
            ("GROW", "+24%",    "Revenue Growth"),
            ("HITS", "94%",     "KPI Hit Rate"),
            ("LEAD", "340",     "New Leads This Month"),
            ("KPIS", "12 KPIs", "Tracked Daily"),
        ],
        "pct": 94, "bars": [18000, 20500, 22000, 24000],
        "before_title": "FLYING BLIND",
        "after_title":  "DATA-DRIVEN",
        "before_items": ["No clear business metrics", "Guessing what works", "Missing growth signals"],
        "after_items":  ["All KPIs in one dashboard", "Spot trends instantly", "Data-driven decisions"],
        "result_num": "+24%", "result_label": "REVENUE GROWTH",
        "features": [
            ("^", "KPI Dashboard", "All metrics in one place"),
            ("~", "Trend Charts",  "Visual growth tracking"),
            ("!", "Goal vs Actual","Hit your targets"),
            ("&", "Export Ready",  "Share with your team"),
        ],
    },
    "fitness": {
        "accent": "#059669",
        "stats": [
            ("WORK", "4x/week", "Workouts Logged"),
            ("CAL",  "18,400",  "Calories Tracked"),
            ("PROG", "-4.2 kg", "Progress This Month"),
            ("HAB",  "87%",     "Habit Consistency"),
        ],
        "pct": 87, "bars": [3, 4, 3, 5],
        "before_title": "NO PROGRESS",
        "after_title":  "REAL RESULTS",
        "before_items": ["Skipping workout sessions", "No progress tracking", "Motivation disappears"],
        "after_items":  ["Every workout logged", "See real weekly progress", "Stay 100% consistent"],
        "result_num": "-4.2 kg", "result_label": "LOST THIS MONTH",
        "features": [
            ("W", "Workout Log",    "Track every session"),
            ("P", "Progress Charts","Weight & reps history"),
            ("M", "Meal Planner",   "Daily nutrition tracking"),
            ("G", "Weekly Goals",   "Consistency streaks"),
        ],
    },
    "productivity": {
        "accent": "#7C3AED",
        "stats": [
            ("DONE", "94%",    "Task Completion"),
            ("GOAL", "3 Goals","Achieved This Week"),
            ("FOCUS","6.2 hrs","Deep Focus Daily"),
            ("PLAN", "7/7",    "Days Planned Ahead"),
        ],
        "pct": 94, "bars": [22, 28, 25, 31],
        "before_title": "OVERWHELMED",
        "after_title":  "PEAK FOCUS",
        "before_items": ["Drowning in endless tasks", "Always missing deadlines", "Zero weekly structure"],
        "after_items":  ["Plan every week clearly", "Hit every single goal", "Zero missed deadlines"],
        "result_num": "94%", "result_label": "TASKS COMPLETED",
        "features": [
            ("7", "Weekly Planner",  "Plan all 7 days ahead"),
            ("G", "Goal Tracker",    "Monthly goal setting"),
            ("P", "Priority System", "Focus on what matters"),
            ("H", "Habit Tracker",   "Build better routines"),
        ],
    },
}


# ─── Utilities ────────────────────────────────────────────────────────────────
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def load_font(size):
    for c in ["arialbd.ttf","calibrib.ttf","arial.ttf",
              "C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/arial.ttf",
              "C:/Windows/Fonts/calibri.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(c, size)
        except: continue
    for p in ["C:/Windows/Fonts/*.ttf","/usr/share/fonts/**/*.ttf"]:
        for f in glob.glob(p, recursive=True):
            try: return ImageFont.truetype(f, size)
            except: continue
    try: return ImageFont.load_default(size=size)
    except: return ImageFont.load_default()

def rrect(draw, xy, r, fill):
    x0,y0,x1,y1 = xy
    draw.rectangle([x0+r,y0,x1-r,y1], fill=fill)
    draw.rectangle([x0,y0+r,x1,y1-r], fill=fill)
    for cx,cy in [(x0,y0),(x1-r*2,y0),(x0,y1-r*2),(x1-r*2,y1-r*2)]:
        draw.ellipse([cx,cy,cx+r*2,cy+r*2], fill=fill)

def ctext(draw, text, font, y, color, width=SIZE):
    try:
        bb = font.getbbox(text)
        x = max(20, (width-(bb[2]-bb[0]))//2)
        draw.text((x, y-bb[1]), text, font=font, fill=color)
        return bb[3]-bb[1]
    except: return 60

def rotated_quad(cx, cy, w, h, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    hw, hh = w/2, h/2
    return [(cx+x*ca-y*sa, cy+x*sa+y*ca) for x,y in [(-hw,-hh),(hw,-hh),(hw,hh),(-hw,hh)]]


# ─── IMAGE 3: STATS HERO ──────────────────────────────────────────────────────
def make_stats_hero(lid, title, data):
    accent = data["accent"]
    stats  = data["stats"]
    pct    = data["pct"]
    bars   = data["bars"]
    ac     = hex2rgb(accent)

    img  = Image.new("RGB", (SIZE,SIZE))
    draw = ImageDraw.Draw(img)

    for i in range(SIZE):
        t = i/SIZE
        draw.rectangle([0,i,SIZE,i+1], fill=(int(8+t*14), int(18+t*22), int(34+t*35)))

    # Subtle glow blob
    for rad in range(700, 0, -30):
        t = 1 - rad/700
        shade = (int(ac[0]*t*0.12), int(ac[1]*t*0.12), int(8+ac[2]*t*0.25))
        draw.ellipse([SIZE//2-rad, 500-rad//2, SIZE//2+rad, 500+rad//2], fill=shade)

    f40  = load_font(40)
    f88  = load_font(88)
    f110 = load_font(110)
    f52  = load_font(52)
    f44  = load_font(44)
    f30  = load_font(30)

    # Brand strip
    draw.rectangle([0,0,SIZE,88], fill=ac)
    ctext(draw, "NASRITOOLS  |  Professional Google Sheets Templates", f40, 22,
          color=hex2rgb("#DBEAFE"))

    # Title
    clean = title.split("|")[0].strip().upper()
    if len(clean) > 30: clean = clean[:28]+"..."
    ctext(draw, clean, f88, 108, color=(255,255,255))
    draw.rectangle([120,244,1880,250], fill=ac)

    # ── 4 Stat cards ─────────────────────────────────────────────────────────
    CW, CH = 920, 600
    GAP    = 40
    CX0    = (SIZE - CW*2 - GAP) // 2
    CY0    = 278

    positions = [
        (CX0, CY0), (CX0+CW+GAP, CY0),
        (CX0, CY0+CH+GAP), (CX0+CW+GAP, CY0+CH+GAP),
    ]

    for idx, ((cx,cy),(lbl,num,desc)) in enumerate(zip(positions, stats)):
        # Shadow
        draw.rounded_rectangle([cx+10,cy+10,cx+CW+10,cy+CH+10], radius=22,
                               fill=(3,8,18))
        # Card body
        draw.rounded_rectangle([cx,cy,cx+CW,cy+CH], radius=22, fill=hex2rgb("#0B1F3A"))
        # Accent header stripe
        draw.rounded_rectangle([cx,cy,cx+CW,cy+12], radius=22, fill=ac)
        # Accent left stripe
        draw.rectangle([cx,cy+12,cx+10,cy+CH-22], fill=ac)
        draw.rectangle([cx,cy+CH-22,cx+10,cy+CH], fill=hex2rgb("#0B1F3A"))

        pad = 52
        # Short label tag
        try:
            rrect(draw,(cx+pad,cy+30,cx+pad+140,cy+76),8,hex2rgb("#1E3A5F"))
            draw.text((cx+pad+16,cy+34), lbl, font=f30, fill=ac)
        except: pass

        # Big number
        try:
            nb = f110.getbbox(num)
            draw.text((cx+pad, cy+100-nb[1]), num, font=f110, fill=(255,255,255))
        except: pass

        # Description
        try:
            db = f44.getbbox(desc)
            draw.text((cx+pad, cy+280-db[1]), desc, font=f44, fill=hex2rgb("#94A3B8"))
        except: pass

        # Decorative: card 0 = bar chart
        if idx == 0 and bars:
            bw = 54; gap = 16; chart_h = 190
            n    = len(bars); mx = max(bars)
            cx0  = cx + CW - n*(bw+gap) - 50
            cy0  = cy + CH - chart_h - 48
            for bi,bv in enumerate(bars):
                bh2 = int((bv/mx)*chart_h)
                bx2 = cx0 + bi*(bw+gap)
                col = ac if bi == n-1 else hex2rgb("#1E3A5F")
                rrect(draw,(bx2,cy0+chart_h-bh2,bx2+bw,cy0+chart_h),6,col)
            for bi,mo in enumerate(["J","F","M","A"]):
                mx2 = cx0+bi*(bw+gap)+bw//2-8
                try: draw.text((mx2,cy0+chart_h+6),mo,font=f30,fill=hex2rgb("#475569"))
                except: pass

        # Card 1 = donut arc
        elif idx == 1:
            acx2 = cx+CW-220; acy2 = cy+CH//2+80
            R = 120; r2 = 80
            draw.arc([acx2-R,acy2-R,acx2+R,acy2+R], 0, 360,
                     fill=hex2rgb("#1E3A5F"), width=R-r2)
            draw.arc([acx2-R,acy2-R,acx2+R,acy2+R], -90,
                     int(-90+pct*3.6), fill=ac, width=R-r2)
            pt = f"{pct}%"
            try:
                pb = f44.getbbox(pt)
                draw.text((acx2-(pb[2]-pb[0])//2, acy2-(pb[3]-pb[1])//2-pb[1]),
                         pt, font=f44, fill=(255,255,255))
            except: pass

        # Card 2 = horizontal progress bars
        elif idx == 2:
            rows = [("Category A",0.32),("Category B",0.54),("Category C",0.38)]
            for bi,(rl,rp) in enumerate(rows):
                ry = cy+380+bi*68
                try: draw.text((cx+pad,ry+2),rl,font=f30,fill=hex2rgb("#94A3B8"))
                except: pass
                tx = cx+pad+200; tw = CW-pad-220
                draw.rounded_rectangle([tx,ry,tx+tw,ry+26],radius=13,fill=hex2rgb("#1E3A5F"))
                draw.rounded_rectangle([tx,ry,tx+int(tw*rp),ry+26],radius=13,fill=ac)

        # Card 3 = checkmarks
        elif idx == 3:
            checks = ["Works on any device","No account needed","Instant access"]
            for bi,chk in enumerate(checks):
                chy = cy+375+bi*72
                draw.ellipse([cx+pad,chy,cx+pad+44,chy+44],fill=hex2rgb("#059669"))
                try: draw.text((cx+pad+6,chy+2),"v",font=f44,fill=(255,255,255))
                except: pass
                try: draw.text((cx+pad+58,chy+4),chk,font=f44,fill=hex2rgb("#94A3B8"))
                except: pass

    # Bottom badges
    bdg_y = CY0+CH*2+GAP+55
    badges = ["Instant Download","Any Device","Fully Editable","No Setup Needed"]
    bx = CX0
    for badge in badges:
        try:
            bb = f44.getbbox(badge)
            bw2 = bb[2]-bb[0]+48; bh2 = bb[3]-bb[1]+24
            rrect(draw,(bx,bdg_y,bx+bw2,bdg_y+bh2),14,ac)
            draw.text((bx+24,bdg_y+12-bb[1]),badge,font=f44,fill=(255,255,255))
            bx += bw2+20
        except: pass

    try:
        wb = f44.getbbox("nasritools.etsy.com")
        draw.text((SIZE-(wb[2]-wb[0])-60,SIZE-60),"nasritools.etsy.com",
                 font=f44,fill=hex2rgb("#334155"))
    except: pass

    path = OUT_DIR / f"v3_stats_{lid}.png"
    img.save(path,"PNG",quality=95)
    return path


# ─── IMAGE 4: TRANSFORMATION (diagonal split) ────────────────────────────────
def make_transformation(lid, title, data):
    accent     = data["accent"]
    bef_title  = data["before_title"]
    aft_title  = data["after_title"]
    bef_items  = data["before_items"]
    aft_items  = data["after_items"]
    res_num    = data["result_num"]
    res_lbl    = data["result_label"]
    ac         = hex2rgb(accent)

    img  = Image.new("RGB",(SIZE,SIZE))
    draw = ImageDraw.Draw(img)

    # BEFORE bg: dark maroon gradient
    for i in range(SIZE):
        t = i/SIZE
        draw.rectangle([0,i,SIZE,i+1], fill=(int(22+t*12),int(8+t*4),int(8+t*4)))

    # AFTER bg: polygon (right side of diagonal)
    # Diagonal from (1100,0) to (900,2000)
    after_poly = [(1100,0),(SIZE,0),(SIZE,SIZE),(900,SIZE)]
    draw.polygon(after_poly, fill=(238,246,255))

    # Diagonal band — accent color glow
    for off in range(-18,19):
        alpha = max(0, 1.0 - abs(off)/20)
        shade = tuple(int(c*alpha*0.9) for c in ac)
        if any(s > 0 for s in shade):
            draw.line([(1100+off,0),(900+off,SIZE)], fill=shade, width=3)

    f40  = load_font(40)
    f90  = load_font(90)
    f100 = load_font(100)
    f60  = load_font(60)
    f50  = load_font(50)

    # Arrow circle in center
    draw.ellipse([SIZE//2-85,SIZE//2-85,SIZE//2+85,SIZE//2+85], fill=ac)
    try: draw.text((SIZE//2-42,SIZE//2-68),"->",font=f90,fill=(255,255,255))
    except: pass

    # ── BEFORE content ────────────────────────────────────────────────────────
    # Scattered chaos rectangles
    chaos = [
        (200,280,200,44,15),(400,180,140,38,-22),(150,480,180,36,10),
        (350,400,160,34,-14),(260,650,220,42,24),(110,760,160,36,-9),
        (490,680,150,32,20),(310,850,200,40,-17),(210,970,180,34,8),
        (430,920,160,36,-12),(120,1100,200,40,18),(550,480,130,30,28),
        (600,700,120,28,-18),(500,1000,160,34,14),(660,1180,175,38,-10),
    ]
    for cx,cy,w,h,ang in chaos:
        pts = rotated_quad(cx,cy,w,h,ang)
        draw.polygon(pts, fill=hex2rgb("#4A0E0E"))

    # X marks (chaos indicators)
    for cx,cy in [(170,350),(320,255),(490,440),(155,620),(410,555),(560,800)]:
        try: draw.text((cx-22,cy-28),"X",font=f60,fill=hex2rgb("#7F1D1D"))
        except: pass

    # BEFORE title + subtitle
    try: draw.text((50,120), bef_title, font=f100, fill=hex2rgb("#FCA5A5"))
    except: pass
    try: draw.text((50,258), "Without a system", font=f50, fill=hex2rgb("#7F1D1D"))
    except: pass

    # Before bullet points
    for i,item in enumerate(bef_items[:3]):
        by = 970+i*130
        draw.ellipse([50,by+8,96,by+52],fill=hex2rgb("#7F1D1D"))
        try: draw.text((60,by+4),"X",font=f50,fill=hex2rgb("#FCA5A5"))
        except: pass
        try: draw.text((112,by+6),item,font=f50,fill=hex2rgb("#FCA5A5"))
        except: pass

    # ── AFTER content ─────────────────────────────────────────────────────────
    ax = 1150

    # AFTER title + subtitle
    try: draw.text((ax,120), aft_title, font=f100, fill=ac)
    except: pass
    try: draw.text((ax,258), "With NasriTools", font=f50, fill=hex2rgb("#1E3A5F"))
    except: pass

    # Big result card
    draw.rounded_rectangle([ax,380,ax+780,620], radius=20, fill=hex2rgb(accent))
    try:
        rb = f100.getbbox(res_num)
        draw.text((ax+(780-(rb[2]-rb[0]))//2, 395-rb[1]),
                 res_num, font=f100, fill=(255,255,255))
    except: pass
    try:
        rlb = f50.getbbox(res_lbl)
        draw.text((ax+(780-(rlb[2]-rlb[0]))//2, 530),
                 res_lbl, font=f50, fill=hex2rgb("#DBEAFE"))
    except: pass

    # After bullet points
    for i,item in enumerate(aft_items[:3]):
        ay2 = 970+i*130
        draw.ellipse([ax,ay2+8,ax+46,ay2+52],fill=hex2rgb("#059669"))
        try: draw.text((ax+8,ay2+4),"v",font=f50,fill=(255,255,255))
        except: pass
        try: draw.text((ax+60,ay2+6),item,font=f50,fill=hex2rgb("#1E3A5F"))
        except: pass

    # Clean grid illustration bottom-right
    gx,gy = ax,1450; gw,gh = 730,360
    draw.rectangle([gx,gy,gx+gw,gy+gh], fill=hex2rgb("#EFF6FF"))
    draw.rectangle([gx,gy,gx+gw,gy+44], fill=ac)
    try: draw.text((gx+14,gy+8),"Google Sheets Template",font=f40,fill=(255,255,255))
    except: pass
    cw2,rh2 = gw//5,(gh-44)//5
    for r in range(5):
        for c in range(5):
            rc = hex2rgb("#EFF6FF") if (r+c)%2==0 else (255,255,255)
            draw.rectangle([gx+c*cw2+1,gy+44+r*rh2+1,gx+(c+1)*cw2-1,gy+44+(r+1)*rh2-1],fill=rc)

    # Bottom brand strip
    draw.rectangle([0,SIZE-88,SIZE,SIZE], fill=ac)
    ctext(draw,"nasritools.etsy.com  |  Instant Download  |  No Setup Required",
          f40,SIZE-68,color=(255,255,255))

    path = OUT_DIR / f"v3_transform_{lid}.png"
    img.save(path,"PNG",quality=95)
    return path


# ─── IMAGE 5: FEATURE CARDS ───────────────────────────────────────────────────
def make_feature_cards(lid, title, data):
    accent   = data["accent"]
    features = data["features"]
    ac       = hex2rgb(accent)

    img  = Image.new("RGB",(SIZE,SIZE))
    draw = ImageDraw.Draw(img)

    for i in range(SIZE):
        t = i/SIZE
        draw.rectangle([0,i,SIZE,i+1],
                       fill=(int(248-t*22),int(250-t*20),int(255-t*12)))

    f40 = load_font(40)
    f70 = load_font(70)
    f55 = load_font(55)
    f44 = load_font(44)
    f38 = load_font(38)
    f90 = load_font(90)

    # Top accent bar
    draw.rectangle([0,0,SIZE,178], fill=ac)
    ctext(draw,"NASRITOOLS",f38,14,color=hex2rgb("#DBEAFE"))
    clean = title.split("|")[0].strip()
    if len(clean) > 38: clean = clean[:36]+"..."
    ctext(draw,clean,f70,70,color=(255,255,255))

    # Subtitle
    ctext(draw,"Professional Google Sheets Template  |  Instant Download",
          f38,198,color=ac)
    draw.rectangle([80,256,1920,262],fill=hex2rgb("#DBEAFE"))

    # ── 4 Feature cards (2x2) ─────────────────────────────────────────────────
    CW,CH = 900,600; GAP=40
    CX0   = (SIZE-CW*2-GAP)//2
    CY0   = 290

    alt = [
        (ac,(255,255,255),(255,255,255),hex2rgb("#DBEAFE")),
        ((255,255,255),ac,hex2rgb("#1E293B"),ac),
        ((255,255,255),ac,hex2rgb("#1E293B"),ac),
        (ac,(255,255,255),(255,255,255),hex2rgb("#DBEAFE")),
    ]
    positions = [(CX0,CY0),(CX0+CW+GAP,CY0),(CX0,CY0+CH+GAP),(CX0+CW+GAP,CY0+CH+GAP)]

    for idx,((fx,fy),(icon,feat_title,feat_desc)) in enumerate(zip(positions,features)):
        card_bg,icon_bg,text_col,desc_col = alt[idx]

        # Shadow
        draw.rounded_rectangle([fx+8,fy+8,fx+CW+8,fy+CH+8],
                               radius=24,fill=hex2rgb("#C7D2FE"))
        # Card
        draw.rounded_rectangle([fx,fy,fx+CW,fy+CH],radius=24,fill=card_bg)

        # Large icon circle
        ic_cx=fx+CW//2; ic_cy=fy+170; ic_r=110
        draw.ellipse([ic_cx-ic_r,ic_cy-ic_r,ic_cx+ic_r,ic_cy+ic_r],fill=icon_bg)

        # Icon letter/symbol (large)
        try:
            ib = f90.getbbox(icon)
            draw.text((ic_cx-(ib[2]-ib[0])//2, ic_cy-ic_r+26),
                     icon, font=f90, fill=card_bg)
        except: pass

        # Feature title
        try:
            tb = f55.getbbox(feat_title)
            draw.text((fx+(CW-(tb[2]-tb[0]))//2, fy+315-tb[1]),
                     feat_title, font=f55, fill=text_col)
        except: pass

        # Feature description
        try:
            db = f38.getbbox(feat_desc)
            draw.text((fx+(CW-(db[2]-db[0]))//2, fy+400-db[1]),
                     feat_desc, font=f38, fill=desc_col)
        except: pass

        # Number badge in corner
        ns = str(idx+1)
        draw.ellipse([fx+CW-72,fy+16,fx+CW-16,fy+72],fill=icon_bg)
        try:
            nb = f44.getbbox(ns)
            draw.text((fx+CW-44-(nb[2]-nb[0])//2, fy+16), ns, font=f44, fill=card_bg)
        except: pass

    # Bottom banner
    by = CY0+CH*2+GAP+50
    draw.rectangle([0,by+110,SIZE,by+210], fill=ac)
    ctext(draw,"Instant Download   |   Any Device   |   Fully Editable   |   No Account Needed",
          f38,by+130,color=(255,255,255))

    try:
        wm="nasritools.etsy.com"
        wb=f38.getbbox(wm)
        draw.text((SIZE-(wb[2]-wb[0])-60,SIZE-60),wm,font=f38,fill=hex2rgb("#94A3B8"))
    except: pass

    path = OUT_DIR / f"v3_features_{lid}.png"
    img.save(path,"PNG",quality=95)
    return path


# ─── API ──────────────────────────────────────────────────────────────────────
def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at",0)-60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type":"refresh_token","client_id":CLIENT_ID,
            "refresh_token":t["refresh_token"]})
        r.raise_for_status(); t=r.json()
        t["expires_at"] = time.time()+t.get("expires_in",3600)-60
        TOKEN_FILE.write_text(json.dumps(t,indent=2))
    return t

def auth_headers(token):
    return {"Authorization":"Bearer "+token["access_token"],"x-api-key":CLIENT_ID+":"+SECRET}

def get_all_listings(token):
    listings,offset=[],0
    while True:
        r=requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                       headers=auth_headers(token),params={"limit":100,"offset":offset})
        if not r.ok: break
        results=r.json().get("results",[])
        listings.extend(results)
        if len(results)<100: break
        offset+=100; time.sleep(0.3)
    return listings

def upload_image(token, lid, path, rank):
    for attempt in range(3):
        try:
            with open(path,"rb") as f:
                r=requests.post(f"{API}/shops/{SHOP_ID}/listings/{lid}/images",
                                headers=auth_headers(token),
                                files={"image":(path.name,f,"image/png")},
                                data={"rank":rank},timeout=60)
            return r.ok, r.status_code
        except requests.exceptions.ConnectionError:
            if attempt<2: time.sleep((attempt+1)*4)
            else: return False, 0

def get_category(title):
    tl = title.lower()
    if any(k in tl for k in ["budget","expense","finance","cash","debt"]): return "finance"
    if any(k in tl for k in ["invoice","billing","client","freelancer"]):  return "invoice"
    if any(k in tl for k in ["kpi","dashboard","business","sales"]):       return "kpi"
    if any(k in tl for k in ["workout","fitness","health","meal","weight"]): return "fitness"
    return "productivity"

def match_listing(listings, keyword):
    for l in listings:
        if keyword.lower() in l["title"].lower(): return l
    return None


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("="*65)
    print("  NasriTools — Creative Mockups v3")
    print("  Stats Hero | Transformation | Feature Cards")
    print("="*65)

    token    = get_token()
    listings = get_all_listings(token)
    print(f"[*] {len(listings)} listings\n")

    ok = fail = 0
    for kw in TARGET_KEYWORDS:
        l = match_listing(listings, kw)
        if not l:
            print(f"  [SKIP] '{kw}' not found"); continue

        lid   = l["listing_id"]
        title = l["title"]
        cat   = get_category(title)
        d     = CATEGORY_DATA[cat]
        print(f"  [{kw}] {title[:42]}...")

        try:
            p3 = make_stats_hero(lid, title, d)
            p4 = make_transformation(lid, title, d)
            p5 = make_feature_cards(lid, title, d)
            print(f"    Generated 3 images", end=" ")
        except Exception as e:
            print(f"    GEN-FAIL: {e}")
            import traceback; traceback.print_exc()
            fail += 1; continue

        token = get_token()
        all_ok = True
        for rank,path in [(3,p3),(4,p4),(5,p5)]:
            r_ok,code = upload_image(token, lid, path, rank)
            print(f"rank{rank}={'OK' if r_ok else f'FAIL({code})'}", end=" ")
            if not r_ok: all_ok = False
            time.sleep(1)
        print()

        if all_ok: ok+=1
        else: fail+=1
        time.sleep(2)

    print(f"\n{'='*65}")
    print(f"  Done: {ok} OK | {fail} failed")
    print(f"  Saved in: {OUT_DIR.resolve()}")
    print(f"{'='*65}")

if __name__=="__main__":
    main()
