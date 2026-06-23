"""
generate_mockups_v2.py
Generates professional device mockup images showing the product
inside a laptop/phone screen — like top competitors.
Creates 3 images per listing and uploads as images 3,4,5.
"""
from PIL import Image, ImageDraw, ImageFont
import json, os, glob, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
OUT_DIR    = Path("thumbnails/mockups")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SIZE       = 2000

# ── Target listings (add more as needed) ──────────────────────────────────────
TARGET_KEYWORDS = [
    "budget tracker",
    "invoice tracker",
    "kpi dashboard",
    "workout tracker",
    "weekly planner",
]

# ── Palette ───────────────────────────────────────────────────────────────────
BG_DARK   = "#0D1B2A"
BG_LIGHT  = "#F0F4FF"
ACCENT    = "#2563EB"
GREEN     = "#059669"
AMBER     = "#F59E0B"
GRAY_DARK = "#1E293B"
GRAY_MID  = "#334155"
GRAY_LITE = "#94A3B8"
WHITE     = "#FFFFFF"
SHEET_BG  = "#FFFFFF"
SHEET_HDR = "#1E3A5F"
SHEET_ALT = "#F1F5F9"
SHEET_GRN = "#D1FAE5"
SHEET_RED = "#FEE2E2"

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

def draw_rounded_rect(draw, xy, r, fill, outline=None, outline_width=0):
    x0,y0,x1,y1 = xy
    draw.rectangle([x0+r,y0,x1-r,y1],fill=fill)
    draw.rectangle([x0,y0+r,x1,y1-r],fill=fill)
    for cx,cy in [(x0,y0),(x1-r*2,y0),(x0,y1-r*2),(x1-r*2,y1-r*2)]:
        draw.ellipse([cx,cy,cx+r*2,cy+r*2],fill=fill)
    if outline and outline_width:
        draw.rounded_rectangle([x0,y0,x1,y1], radius=r,
                                outline=hex2rgb(outline), width=outline_width)

def draw_spreadsheet(draw, x, y, w, h, title="Budget Tracker", fonts=None):
    """Draw a realistic Google Sheets mockup inside given area."""
    f_hdr, f_cell, f_tiny = fonts or (None,None,None)

    # Sheet background
    draw.rectangle([x,y,x+w,y+h], fill=hex2rgb(WHITE))

    # Google Sheets top bar (gray)
    bar_h = max(22, h//18)
    draw.rectangle([x,y,x+w,y+bar_h], fill=hex2rgb("#F8F9FA"))
    draw.rectangle([x,y+bar_h,x+w,y+bar_h+1], fill=hex2rgb("#E2E8F0"))

    # Tabs
    tab_w = min(120, w//5)
    draw.rectangle([x+4,y+bar_h+2,x+4+tab_w,y+bar_h*2], fill=hex2rgb(WHITE))
    draw.rectangle([x+4,y+bar_h*2,x+4+tab_w,y+bar_h*2+2], fill=hex2rgb(ACCENT))
    if f_tiny:
        try: draw.text((x+8,y+bar_h+4), title[:12], font=f_tiny, fill=hex2rgb(GRAY_DARK))
        except: pass

    header_h = max(28, h//14)
    row_h    = max(20, h//20)
    col_w    = w // 6
    data_y   = y + bar_h*2 + 4

    # Column headers row
    draw.rectangle([x,data_y,x+w,data_y+header_h], fill=hex2rgb(SHEET_HDR))
    cols = ["CATEGORY","JAN","FEB","MAR","APR","TOTAL"]
    for i,col in enumerate(cols):
        cx = x + i*col_w + 4
        if f_tiny:
            try: draw.text((cx,data_y+4), col, font=f_tiny, fill=hex2rgb(WHITE))
            except: pass

    # Data rows
    rows = [
        ("💰 INCOME",  "3,200","3,400","3,100","3,500","13,200", SHEET_GRN),
        ("🏠 Rent",    "1,200","1,200","1,200","1,200","4,800",  None),
        ("🍔 Food",    "420",  "380",  "450",  "410",  "1,660",  None),
        ("🚗 Transport","180", "190",  "170",  "200",  "740",    None),
        ("📱 Bills",   "95",   "95",   "95",   "95",   "380",    None),
        ("🎯 Savings", "420",  "580",  "310",  "720",  "2,030",  SHEET_GRN),
        ("❌ TOTAL EXP","1,895","1,865","1,915","1,905","7,580", SHEET_RED),
        ("✅ BALANCE", "1,305","1,535","1,185","1,595","5,620",  SHEET_GRN),
    ]

    for i,(cat,*vals,bg) in enumerate(rows):
        ry = data_y + header_h + i*row_h
        row_bg = bg or (SHEET_ALT if i%2==0 else WHITE)
        draw.rectangle([x,ry,x+w,ry+row_h], fill=hex2rgb(row_bg))
        draw.rectangle([x,ry+row_h-1,x+w,ry+row_h], fill=hex2rgb("#E2E8F0"))
        if f_tiny:
            try: draw.text((x+4,ry+3), cat, font=f_tiny, fill=hex2rgb(GRAY_DARK))
            except: pass
            for j,val in enumerate(vals,1):
                try: draw.text((x+j*col_w+4,ry+3), val, font=f_tiny, fill=hex2rgb(GRAY_DARK))
                except: pass

    # Mini chart (bottom right)
    chart_x = x + w - col_w*2 - 8
    chart_y = data_y + header_h + len(rows)*row_h + 4
    chart_h = h - (chart_y - y) - 4
    if chart_h > 20:
        draw.rectangle([chart_x, chart_y, x+w-4, chart_y+chart_h],
                       fill=hex2rgb("#F8FAFF"))
        bar_colors = [ACCENT,"#38BDF8",ACCENT,"#38BDF8"]
        bar_w = max(6, col_w//3)
        max_val = 3500
        for bi,bval in enumerate([3200,3400,3100,3500]):
            bx = chart_x + 8 + bi*(bar_w+4)
            bh = int((bval/max_val)*(chart_h-12))
            by = chart_y + chart_h - bh - 4
            draw.rectangle([bx,by,bx+bar_w,chart_y+chart_h-4],
                           fill=hex2rgb(bar_colors[bi]))


# ── Mockup 1: Laptop ──────────────────────────────────────────────────────────
def make_laptop_mockup(listing_id, title, accent_color="#2563EB"):
    img  = Image.new("RGB", (SIZE,SIZE), hex2rgb(BG_DARK))
    draw = ImageDraw.Draw(img)

    f_title = load_font(82)
    f_sub   = load_font(52)
    f_badge = load_font(44)
    f_small = load_font(36)
    f_sheet = load_font(16)
    f_tiny  = load_font(14)

    # Background gradient (simulate with rectangles)
    for i in range(SIZE):
        t = i / SIZE
        r = int(13 + t*8);  g = int(27 + t*15);  b = int(42 + t*25)
        draw.rectangle([0,i,SIZE,i+1], fill=(r,g,b))

    # Glow behind laptop
    for r in range(500,0,-1):
        alpha = int(30 * (1 - r/500))
        draw.ellipse([SIZE//2-r, SIZE//2-r//2, SIZE//2+r, SIZE//2+r//2],
                     fill=(37,99,235,0))

    # ── Laptop frame ──────────────────────────────────────────────────────────
    lx, ly = 200, 240      # top-left of laptop lid
    lw, lh = 1600, 980     # laptop lid size
    bezel  = 30            # bezel thickness
    base_h = 60            # keyboard base height

    # Shadow
    for s in range(20,0,-1):
        draw.rounded_rectangle([lx+s,ly+s,lx+lw+s,ly+lh+base_h+s],
                                radius=18, fill=(0,0,0,0))

    # Laptop lid (screen)
    draw.rounded_rectangle([lx,ly,lx+lw,ly+lh], radius=14,
                            fill=hex2rgb("#1A1A2E"), outline=hex2rgb("#2D2D4E"), width=2)

    # Screen area
    sx = lx + bezel; sy = ly + bezel
    sw = lw - bezel*2; sh = lh - bezel*2
    draw.rectangle([sx,sy,sx+sw,sy+sh], fill=hex2rgb(WHITE))

    # Draw spreadsheet inside screen
    draw_spreadsheet(draw, sx, sy, sw, sh,
                     title=title[:15], fonts=(f_tiny,f_tiny,f_tiny))

    # Laptop base/keyboard
    draw.rounded_rectangle([lx-20,ly+lh,lx+lw+20,ly+lh+base_h],
                            radius=8, fill=hex2rgb("#141428"))
    # Trackpad
    tp_w, tp_h = 200, 30
    draw.rounded_rectangle([lx+lw//2-tp_w//2, ly+lh+12,
                             lx+lw//2+tp_w//2, ly+lh+12+tp_h],
                            radius=4, fill=hex2rgb("#1E1E3A"))
    # Camera dot
    draw.ellipse([lx+lw//2-5,ly+8,lx+lw//2+5,ly+18], fill=hex2rgb("#333355"))

    # ── Text overlay ──────────────────────────────────────────────────────────
    clean = title.split("|")[0].strip().upper()[:30]
    try:
        tb = f_title.getbbox(clean)
        draw.text(((SIZE-(tb[2]-tb[0]))//2, ly+lh+base_h+50),
                  clean, font=f_title, fill=hex2rgb(WHITE))
    except: pass

    sub = "Google Sheets Template  •  Instant Download"
    try:
        sb = f_sub.getbbox(sub)
        draw.text(((SIZE-(sb[2]-sb[0]))//2, ly+lh+base_h+150),
                  sub, font=f_sub, fill=hex2rgb(GRAY_LITE))
    except: pass

    # Badges
    badges = ["⚡ Instant Download", "📱 Works on Any Device", "✏️ Fully Customizable"]
    bx = 200
    for badge in badges:
        try:
            bb = f_badge.getbbox(badge)
            bw = bb[2]-bb[0]+40; bh2 = bb[3]-bb[1]+20
            draw_rounded_rect(draw,(bx,ly+lh+base_h+230,bx+bw,ly+lh+base_h+230+bh2),
                              12,hex2rgb(accent_color))
            draw.text((bx+20,ly+lh+base_h+230+10-bb[1]),
                      badge,font=f_badge,fill=hex2rgb(WHITE))
            bx += bw + 20
        except: pass

    # Watermark
    try:
        wb = f_small.getbbox("nasritools.etsy.com")
        draw.text((SIZE-wb[2]-wb[0]-40,SIZE-50),
                  "nasritools.etsy.com",font=f_small,fill=hex2rgb("#475569"))
    except: pass

    path = OUT_DIR / f"mockup_laptop_{listing_id}.png"
    img.save(path,"PNG",quality=95)
    return path


# ── Mockup 2: Laptop + Phone side by side ─────────────────────────────────────
def make_multidevice_mockup(listing_id, title, accent_color="#2563EB"):
    img  = Image.new("RGB", (SIZE,SIZE), hex2rgb("#F0F4FF"))
    draw = ImageDraw.Draw(img)

    f_title = load_font(80)
    f_sub   = load_font(50)
    f_check = load_font(48)
    f_small = load_font(36)
    f_tiny  = load_font(13)

    # Light background gradient
    for i in range(SIZE):
        t = i/SIZE
        r = int(240-t*10); g = int(244-t*8); b = int(255-t*5)
        draw.rectangle([0,i,SIZE,i+1], fill=(r,g,b))

    # Accent circle decoration
    draw.ellipse([-200,-200,600,600], fill=hex2rgb("#DBEAFE"))
    draw.ellipse([1400,1400,2200,2200], fill=hex2rgb("#DBEAFE"))

    # ── Laptop (left side, smaller) ───────────────────────────────────────────
    lx,ly = 60, 300; lw,lh = 1050,650; bezel=22; base_h=45
    draw.rounded_rectangle([lx,ly,lx+lw,ly+lh], radius=12,
                            fill=hex2rgb("#1E1E2E"),outline=hex2rgb("#2D2D4E"),width=2)
    sx,sy = lx+bezel,ly+bezel; sw,sh = lw-bezel*2,lh-bezel*2
    draw.rectangle([sx,sy,sx+sw,sy+sh], fill=hex2rgb(WHITE))
    draw_spreadsheet(draw,sx,sy,sw,sh,title=title[:12],fonts=(f_tiny,f_tiny,f_tiny))
    draw.rounded_rectangle([lx-15,ly+lh,lx+lw+15,ly+lh+base_h],
                            radius=6,fill=hex2rgb("#141428"))

    # ── Phone (right side) ────────────────────────────────────────────────────
    px,py = 1180, 250; pw,ph = 360,640; p_bezel=16; p_radius=36
    # Phone shadow
    draw.rounded_rectangle([px+8,py+8,px+pw+8,py+ph+8], radius=p_radius,
                            fill=hex2rgb("#C7D2FE"))
    # Phone body
    draw.rounded_rectangle([px,py,px+pw,py+ph], radius=p_radius,
                            fill=hex2rgb("#0F0F1E"),outline=hex2rgb("#2D2D4E"),width=3)
    # Phone notch
    draw.rounded_rectangle([px+pw//2-40,py+8,px+pw//2+40,py+22],
                            radius=7,fill=hex2rgb("#0A0A18"))
    # Phone screen
    psx,psy = px+p_bezel,py+30; psw,psh = pw-p_bezel*2,ph-50
    draw.rectangle([psx,psy,psx+psw,psy+psh], fill=hex2rgb(WHITE))
    # Spreadsheet in phone (portrait, compact)
    draw_spreadsheet(draw,psx,psy,psw,psh,title="Budget",fonts=(f_tiny,f_tiny,f_tiny))
    # Home bar
    draw.rounded_rectangle([px+pw//2-35,py+ph-16,px+pw//2+35,py+ph-8],
                            radius=4,fill=hex2rgb("#2D2D4E"))

    # ── Text section (bottom) ─────────────────────────────────────────────────
    text_y = ly + lh + base_h + 60

    clean = title.split("|")[0].strip().upper()[:28]
    try:
        tb = f_title.getbbox(clean)
        draw.text(((SIZE-(tb[2]-tb[0]))//2, text_y), clean,
                  font=f_title, fill=hex2rgb(GRAY_DARK))
    except: pass

    sub = "Works on Desktop • Tablet • Phone"
    try:
        sb = f_sub.getbbox(sub)
        draw.text(((SIZE-(sb[2]-sb[0]))//2, text_y+100), sub,
                  font=f_sub, fill=hex2rgb(GRAY_MID))
    except: pass

    # Check features
    feats = ["✓  Auto-Calculating Formulas",
             "✓  Instant Download — No Setup",
             "✓  Fully Customizable"]
    feat_x = SIZE//2 - 380
    for i,feat in enumerate(feats):
        try:
            draw.text((feat_x, text_y+190+i*70), feat,
                      font=f_check, fill=hex2rgb(ACCENT))
        except: pass

    try:
        wb = f_small.getbbox("nasritools.etsy.com")
        draw.text((SIZE-wb[2]-wb[0]-40,SIZE-50),
                  "nasritools.etsy.com",font=f_small,fill=hex2rgb(GRAY_LITE))
    except: pass

    path = OUT_DIR / f"mockup_multi_{listing_id}.png"
    img.save(path,"PNG",quality=95)
    return path


# ── Mockup 3: Close-up spreadsheet features ───────────────────────────────────
def make_closeup_mockup(listing_id, title, accent_color="#2563EB"):
    img  = Image.new("RGB",(SIZE,SIZE),hex2rgb(WHITE))
    draw = ImageDraw.Draw(img)

    f_big   = load_font(90)
    f_mid   = load_font(58)
    f_small = load_font(40)
    f_tiny  = load_font(22)
    f_wm    = load_font(36)

    # Accent top bar
    draw.rectangle([0,0,SIZE,180], fill=hex2rgb(accent_color))

    # Title in bar
    clean = title.split("|")[0].strip()[:35]
    try:
        tb = f_mid.getbbox(clean)
        draw.text(((SIZE-(tb[2]-tb[0]))//2, 60-tb[1]),
                  clean, font=f_mid, fill=hex2rgb(WHITE))
    except: pass

    # Large spreadsheet area
    sx,sy = 60,200; sw,sh = SIZE-120, 1200
    draw.rounded_rectangle([sx-4,sy-4,sx+sw+4,sy+sh+4], radius=12,
                            fill=hex2rgb("#E2E8F0"))
    draw.rectangle([sx,sy,sx+sw,sy+sh], fill=hex2rgb(WHITE))
    draw_spreadsheet(draw,sx,sy,sw,sh,title=title[:15],
                     fonts=(f_tiny,f_tiny,f_tiny))

    # Bottom features
    feats = [
        ("⚡","INSTANT DOWNLOAD","Ready in 2 minutes"),
        ("📊","AUTO-CALCULATING","No manual math"),
        ("📱","ANY DEVICE","Phone, tablet, desktop"),
        ("✏️","CUSTOMIZABLE","Change anything"),
    ]
    fw = SIZE // len(feats)
    for i,(icon,title_f,sub) in enumerate(feats):
        fx = i*fw + fw//2
        fy = sy+sh+60
        draw.ellipse([fx-44,fy,fx+44,fy+88],fill=hex2rgb(accent_color))
        try: draw.text((fx-22,fy+10),icon,font=f_mid,fill=hex2rgb(WHITE))
        except: pass
        try:
            tb = f_small.getbbox(title_f)
            draw.text((fx-(tb[2]-tb[0])//2,fy+110),title_f,
                      font=f_small,fill=hex2rgb(GRAY_DARK))
            sb = f_wm.getbbox(sub)
            draw.text((fx-(sb[2]-sb[0])//2,fy+160),sub,
                      font=f_wm,fill=hex2rgb(GRAY_LITE))
        except: pass

    try:
        wb = f_wm.getbbox("nasritools.etsy.com")
        draw.text((SIZE-wb[2]-wb[0]-40,SIZE-50),
                  "nasritools.etsy.com",font=f_wm,fill=hex2rgb(GRAY_LITE))
    except: pass

    path = OUT_DIR / f"mockup_closeup_{listing_id}.png"
    img.save(path,"PNG",quality=95)
    return path


# ── API ───────────────────────────────────────────────────────────────────────
def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at",0)-60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token",data={
            "grant_type":"refresh_token","client_id":CLIENT_ID,
            "refresh_token":t["refresh_token"]})
        r.raise_for_status(); t = r.json()
        t["expires_at"] = time.time()+t.get("expires_in",3600)-60
        TOKEN_FILE.write_text(json.dumps(t,indent=2))
    return t

def auth_headers(token):
    return {"Authorization":"Bearer "+token["access_token"],
            "x-api-key":CLIENT_ID+":"+SECRET}

def get_all_listings(token):
    listings,offset = [],0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit":100,"offset":offset})
        if not r.ok: break
        results = r.json().get("results",[])
        listings.extend(results)
        if len(results)<100: break
        offset+=100; time.sleep(0.3)
    return listings

def upload_image(token, lid, path, rank):
    with open(path,"rb") as f:
        r = requests.post(f"{API}/shops/{SHOP_ID}/listings/{lid}/images",
                          headers=auth_headers(token),
                          files={"image":(path.name,f,"image/png")},
                          data={"rank":rank},timeout=60)
    return r.ok, r.status_code

def get_category_accent(title):
    tl = title.lower()
    if any(k in tl for k in ["budget","finance","invoice","cash","debt"]): return "#2563EB"
    if any(k in tl for k in ["kpi","business","sales","marketing"]): return "#0EA5E9"
    if any(k in tl for k in ["workout","health","meal","fitness"]): return "#059669"
    if any(k in tl for k in ["planner","productivity","goal","habit"]): return "#7C3AED"
    if any(k in tl for k in ["bundle","os","complete","system"]): return "#F59E0B"
    return "#2563EB"

def match_listing(listings, keyword):
    for l in listings:
        if keyword.lower() in l["title"].lower():
            return l
    return None

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("="*65)
    print("  NasriTools — Generate Device Mockup Images")
    print("="*65)
    token    = get_token()
    listings = get_all_listings(token)
    print(f"[*] {len(listings)} listings\n")

    ok = fail = 0
    for kw in TARGET_KEYWORDS:
        l = match_listing(listings, kw)
        if not l:
            print(f"  [SKIP] '{kw}' not found")
            continue
        lid    = l["listing_id"]
        title  = l["title"]
        accent = get_category_accent(title)
        print(f"  [{kw}] {title[:45]}...")

        # Generate 3 mockups
        try:
            p1 = make_laptop_mockup(lid, title, accent)
            p2 = make_multidevice_mockup(lid, title, accent)
            p3 = make_closeup_mockup(lid, title, accent)
            print(f"    Generated 3 mockups ✓", end=" ")
        except Exception as e:
            print(f"    GEN-FAIL: {e}")
            fail += 1
            continue

        # Upload as ranks 3,4,5
        token = get_token()
        all_ok = True
        for rank, path in [(3,p1),(4,p2),(5,p3)]:
            r_ok, code = upload_image(token, lid, path, rank)
            if not r_ok:
                print(f"    UPLOAD-FAIL rank{rank} ({code})")
                all_ok = False
            time.sleep(1)

        if all_ok:
            print("Uploaded ✅")
            ok += 1
        else:
            fail += 1
        time.sleep(2)

    print(f"\n{'='*65}")
    print(f"  Mockups done: {ok} OK | {fail} failed")
    print(f"  Images saved in: {OUT_DIR.resolve()}")
    print(f"{'='*65}")

if __name__=="__main__":
    main()
